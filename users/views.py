from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView

from users.forms import RegisterForm, LoginForm, ProfileEditForm, CustomPasswordChangeForm
from users.models import User
from django.conf import settings


class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("projects:list")
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("projects:list")
        form = LoginForm(request)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
            return redirect(next_url)
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("projects:list")

    def post(self, request):
        logout(request)
        return redirect("projects:list")


class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"


class UserListView(View):
    template_name = "users/participants.html"

    def get(self, request):
        users_qs = User.objects.filter(is_active=True).order_by("-id")
        paginator = Paginator(users_qs, settings.PAGINATE_BY)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        query_params = request.GET.copy()
        query_params.pop("page", None)
        query_prefix = query_params.urlencode()
        if query_prefix:
            query_prefix += "&"

        context = {
            "participants": page_obj,
            "page_obj": page_obj,
            "query_prefix": query_prefix,
        }
        return render(request, self.template_name, context)


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "users/edit_profile.html"

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return render(request, self.template_name, {"form": form, "user": request.user})

    def post(self, request):
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
        return render(request, self.template_name, {"form": form, "user": request.user})


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "users/change_password.html"

    def get(self, request):
        form = CustomPasswordChangeForm(request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменён")
            return redirect("users:detail", pk=request.user.pk)
        return render(request, self.template_name, {"form": form})
