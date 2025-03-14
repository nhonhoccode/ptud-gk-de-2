from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from .models import Task, UserProfile
from .forms import TaskForm, UserRegistrationForm, UserProfileForm
from django.contrib import messages
import random
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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
    return render(request, 'tasks/home.html', {'tasks': tasks})

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
            avatar_id = request.POST.get('avatar_id')
            upload_avatar = request.FILES.get('avatar')
            
            if upload_avatar:
                profile.avatar = upload_avatar
                profile.avatar_id = None
                profile.avatar_url = None
            elif avatar_id:
                profile.avatar = None
                profile.avatar_id = avatar_id
                profile.avatar_url = None
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            
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
