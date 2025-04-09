from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Email address'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Personalizar los widgets
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirm password'
        })

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Search for images...'
        })
    )
    
    copyright_filter = forms.ChoiceField(
        choices=[
            ('', 'Any copyright'),
            ('free', 'Free to use'),
            ('commercial', 'Free for commercial use'),
            ('noncommercial', 'Free for noncommercial use'),
            ('modification', 'Free to modify'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    transparent_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        })
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Add a comment...',
                'rows': 3
            })
        }
