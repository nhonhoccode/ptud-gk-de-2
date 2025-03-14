from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, UserProfile

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
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