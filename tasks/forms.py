from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, UserProfile, Category

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    COLOR_CHOICES = [
        ('primary', 'Blue'),
        ('secondary', 'Gray'),
        ('success', 'Green'),
        ('danger', 'Red'),
        ('warning', 'Yellow'),
        ('info', 'Light Blue'),
        ('dark', 'Black'),
    ]
    
    ICON_CHOICES = [
        ('fas fa-tasks', 'Tasks'),
        ('fas fa-home', 'Home'),
        ('fas fa-briefcase', 'Work'),
        ('fas fa-graduation-cap', 'Education'),
        ('fas fa-shopping-cart', 'Shopping'),
        ('fas fa-users', 'Social'),
        ('fas fa-dumbbell', 'Fitness'),
        ('fas fa-book', 'Reading'),
        ('fas fa-code', 'Coding'),
        ('fas fa-utensils', 'Food'),
        ('fas fa-plane', 'Travel'),
        ('fas fa-calendar', 'Events'),
        ('fas fa-money-bill', 'Finance'),
        ('fas fa-heart', 'Health'),
        ('fas fa-star', 'Important'),
    ]
    
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'color-select'}),
    )
    
    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'icon-select'}),
    )
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    AVATAR_CHOICES = [(i, f"Avatar {i}") for i in range(1, 93)]
    
    avatar_id = forms.ChoiceField(
        choices=AVATAR_CHOICES, 
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'avatar-select'}),
        label="Select an Avatar"
    )
    
    upload_avatar = forms.BooleanField(
        required=False, 
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Upload custom avatar instead"
    )
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'avatar_id']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'avatar': 'Upload Custom Avatar',
        } 