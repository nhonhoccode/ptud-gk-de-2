from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from .models import Task, UserProfile, Category
from .forms import TaskForm, UserRegistrationForm, UserProfileForm, CategoryForm
from django.contrib import messages
import random
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.cache import cache

def landing_page(request):
    return render(request, 'landing.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            
            # Get or create the user profile (it might already exist due to signals)
            try:
                profile = user.userprofile
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=user)
            
            # Handle avatar selection
            upload_avatar = request.POST.get('upload_avatar', False)
            avatar_id = profile_form.cleaned_data.get('avatar_id')
            
            if upload_avatar and request.FILES.get('avatar'):
                # User uploaded a custom avatar
                profile.avatar = request.FILES.get('avatar')
                profile.avatar_id = None
                profile.avatar_url = None
            elif avatar_id:
                # User selected a predefined avatar
                profile.avatar_id = avatar_id
                profile.avatar = None  # Clear any uploaded avatar
                profile.avatar_url = None  # Clear any URL
            else:
                # No avatar selected, use a random one
                profile.avatar_id = random.randint(1, 92)
                
            profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/register.html', {
        'form': form,
        'profile_form': profile_form
    })

@login_required
def home(request):
    tasks = Task.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        tasks = tasks.filter(category_id=category_id)
        selected_category = get_object_or_404(Category, id=category_id, user=request.user)
    else:
        selected_category = None
    
    return render(request, 'tasks/home.html', {
        'tasks': tasks,
        'categories': categories,
        'selected_category': selected_category
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('home')
    else:
        form = TaskForm()
        # Only show categories belonging to the current user
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            if task.status == 'completed' and not task.finished:
                task.finished = timezone.now()
                task.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('home')
    else:
        form = TaskForm(instance=task)
        # Only show categories belonging to the current user
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Update Task'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('home')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.complete()
    messages.success(request, 'Task marked as completed!')
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    
    # Get or create the user profile
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        # Create a profile if it doesn't exist
        profile = UserProfile(user=user)
        profile.avatar_id = random.randint(1, 92)  # Assign a random avatar
        profile.save()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update basic profile information
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            # Handle avatar update
            upload_avatar = request.POST.get('upload_avatar') == 'on'
            avatar_id = request.POST.get('avatar_id')
            
            if upload_avatar and request.FILES.get('avatar'):
                # User uploaded a custom avatar
                profile.avatar = request.FILES.get('avatar')
                profile.avatar_id = None
                profile.avatar_url = None
                messages.success(request, 'Profile updated with custom avatar!')
            elif not upload_avatar and avatar_id:
                # User selected a predefined avatar
                try:
                    # Convert to integer and validate
                    avatar_id_int = int(avatar_id)
                    if 1 <= avatar_id_int <= 92:
                        profile.avatar = None
                        profile.avatar_id = avatar_id_int
                        profile.avatar_url = None
                        messages.success(request, f'Profile updated with avatar #{avatar_id_int}!')
                    else:
                        messages.error(request, 'Invalid avatar selection. Please try again.')
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid avatar selection. Please try again.')
            else:
                # No changes to avatar
                messages.success(request, 'Profile information updated!')
            
            # Save the profile regardless
            profile.save()
            
            # Clear the avatar cache for this user
            cache_keys = [
                f'user_avatar_{user.id}_None',
                f'user_avatar_{user.id}_38',
                f'user_avatar_{user.id}_96',
                f'user_avatar_{user.id}_200'
            ]
            for key in cache_keys:
                cache.delete(key)
            
        elif action == 'change_password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Your password was successfully updated!')
            else:
                for error in password_form.errors.values():
                    messages.error(request, error[0])
        
        return redirect('profile')
    
    # Get all tasks for the user
    tasks = Task.objects.filter(user=user)
    completed_tasks = tasks.filter(status='completed').count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    
    # Calculate task statistics
    total_tasks = tasks.count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    password_form = PasswordChangeForm(user)
    
    context = {
        'user': user,
        'profile': profile,
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': completion_rate,
        'password_form': password_form,
    }
    
    return render(request, 'tasks/profile.html', context)

# Category Management Views
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'tasks/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'tasks/category_form.html', {'form': form, 'title': 'Create Category'})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'tasks/category_form.html', {'form': form, 'title': 'Update Category'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        # Count tasks in this category
        task_count = Task.objects.filter(category=category).count()
        
        if task_count > 0:
            # Option to reassign tasks or delete them
            reassign_to = request.POST.get('reassign_to')
            if reassign_to:
                # Reassign tasks to another category
                if reassign_to != 'none':
                    new_category = get_object_or_404(Category, pk=reassign_to, user=request.user)
                    Task.objects.filter(category=category).update(category=new_category)
                else:
                    # Set category to None
                    Task.objects.filter(category=category).update(category=None)
            
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    
    # Get other categories for reassignment
    other_categories = Category.objects.filter(user=request.user).exclude(pk=pk)
    task_count = Task.objects.filter(category=category).count()
    
    return render(request, 'tasks/category_confirm_delete.html', {
        'category': category,
        'other_categories': other_categories,
        'task_count': task_count
    })
