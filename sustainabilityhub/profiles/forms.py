from django import forms
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    interests_input = forms.CharField(
        required=False,
        help_text='Enter interests separated by commas',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., renewable energy, recycling, gardening'})
    )
    
    class Meta:
        model = Profile
        fields = ['location', 'skills']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['interests_input'].initial = ', '.join(self.instance.interests) if self.instance.interests else ''
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        interests_str = self.cleaned_data.get('interests_input', '')
        if interests_str:
            profile.interests = [interest.strip() for interest in interests_str.split(',') if interest.strip()]
        else:
            profile.interests = []
        if commit:
            profile.save()
        return profile


class UserForm(forms.ModelForm):
    """Form for editing User model fields (bio, avatar)"""
    
    class Meta:
        model = User
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'style': 'resize: vertical;'
            }),
            'avatar': forms.FileInput(attrs={
                'accept': 'image/*'
            })
        }
