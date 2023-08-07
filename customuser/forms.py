from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("pic", "about_me", "favorite_food")


class CustomUserUpdateForm(forms.ModelForm):
    password_change_form = PasswordChangeForm

    # Add the password field to the form
    old_password = forms.CharField(
        label="Old Password", widget=forms.PasswordInput, required=False
    )
    new_password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput, required=False
    )
    new_password2 = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = CustomUser
        fields = ["email", "about_me", "favorite_food", "pic"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_change_form.user = self.instance

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        # Check if new passwords match
        if new_password1 and new_password1 != new_password2:
            raise forms.ValidationError(
                "The new passwords do not match. Please try again."
            )

        # Check if old password is correct
        if old_password and not self.instance.check_password(old_password):
            raise forms.ValidationError("Invalid old password. Please try again.")

        return cleaned_data

    def save(self, commit=True):
        new_password1 = self.cleaned_data.get("new_password1")

        if new_password1:
            # Set the new password if it's provided
            self.instance.set_password(new_password1)

        return super().save(commit=commit)
