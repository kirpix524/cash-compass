from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from users.forms import ProfileForm


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("users:login")

class ProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileForm
    template_name: str = "users/profile.html"
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None) -> Any:
        return self.request.user