from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Post,Tag,Comment

class CustomRegistrationForm(forms.ModelForm):
    # password=forms.CharField(widget=forms.PasswordInput)
    # password_confirm=forms.CharField(widget=forms.PasswordInput,label='Confirm Password')

    password=forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password_confirm=forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class':'form-control'}))
    email=forms.EmailField(required=True)

    class Meta:
        model=User
        fields=['username','email','password','password_confirm']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data=super().clean()
        password=cleaned_data.get("password")
        password_confirm=cleaned_data.get("password_confirm")
        email=cleaned_data.get("email")
        username=cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username not available. Please try again")

        if password != password_confirm:
            raise forms.ValidationError("passwords do not match.")
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return cleaned_data

class CustomLoginForm(forms.Form):
    # username=forms.CharField(label="Username or Email")
    # password=forms.CharField(widget=forms.PasswordInput)
    username=forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'class':'form-control',
        'placeholder':'Username or Email',
        'id':'id_username'
        })
    )
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control',
        'placeholder':'Password',
        'id':'id_password'
        })
    )

class CustomPasswordResetForm(forms.Form):
    email=forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class':'form-control',
            'placeholder':'Enter your registered email'
        })
    )

class PostForm(forms.ModelForm):
    tags=forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class':'form-control tagify-input',
            'placeholder':'for example: funny, sad, romance'
        })
    )
    class Meta:
        model=Post
        fields=['title','content','tags']
        widgets={
            'title':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Post Title'
            }),
            'content':forms.Textarea(attrs={
                'class':'form-control markdown-area auto-expand',
                'placeholder':'Write your post in the Markdown...',
                'style': 'min-height: 400px; overflow:hidden;'
            }),
        }

class CommentForm(forms.ModelForm):
    body=forms.CharField(widget=forms.Textarea(attrs={
        'rows':4,
        'placeholder':'Write your comment here...',
        'class':'form-control'
    }), label='')

    class Meta:
        model=Comment
        fields=['body']