"""
Calculus Bridge - Form autentikasi & onboarding.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Faculty


class LoginForm(AuthenticationForm):
    """Login dengan username atau email."""

    username = forms.CharField(
        label="Username atau email",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username", "placeholder": "mis. budi23"}),
    )
    password = forms.CharField(
        label="Kata sandi",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "••••••••"}),
    )

    error_messages = {
        "invalid_login": "Username/email atau kata sandi salah.",
        "inactive": "Akun ini tidak aktif.",
    }

    def clean(self):
        # Izinkan login memakai email: ubah email menjadi username sebelum autentikasi.
        identifier = self.cleaned_data.get("username", "")
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user:
                self.cleaned_data["username"] = user.username
        return super().clean()


class RegisterForm(UserCreationForm):
    """
    Pendaftaran manual: username + kata sandi + konfirmasi, tanpa email.
    Mekanisme: email yang tersimpan hanya berasal dari Google (pasti aktif),
    sehingga form ini tidak menerima email yang tidak bisa diverifikasi.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
        labels = {"username": "Username"}
        help_texts = {"username": "Huruf, angka, dan @/./+/-/_ saja."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "mis. budi23", "autocomplete": "username"})
        self.fields["password1"].label = "Kata sandi"
        self.fields["password1"].help_text = "Minimal 8 karakter, tidak boleh hanya angka."
        self.fields["password2"].label = "Ulangi kata sandi"
        self.fields["password2"].help_text = ""


class FacultyForm(forms.Form):
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        to_field_name="slug",
        error_messages={"required": "Pilih salah satu fakultas.", "invalid_choice": "Fakultas tidak dikenal."},
    )
