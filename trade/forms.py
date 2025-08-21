from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label = "Confirm Password")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        # print("Role selected:", self.cleaned_data.get('role'))
        if password and password_confirm and password !=password_confirm:
            raise forms.ValidationError("Password do not match")
        return cleaned_data

    def save(self, commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            role = self.cleaned_data.get('role')
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.role=role
            user_profile.save()
            return user
        #     if not UserProfile.objects.filter(user=user).exists():
        #         UserProfile.objects.create(
        #             user=user,
        #             role = self.cleaned_data['role']
        #         )
        # return user


