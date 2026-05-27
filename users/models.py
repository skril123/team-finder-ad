from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from core.constants import ABOUT_MAX_LENGTH, PHONE_MAX_LENGTH, USER_NAME_MAX_LENGTH
from users.managers import UserManager
from users.services import avatar_upload_path, build_initial_avatar


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("электронная почта", unique=True)
    name = models.CharField("имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("фамилия", max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField("аватар", upload_to=avatar_upload_path, blank=True)
    phone = models.CharField(
        "телефон",
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField("ссылка на GitHub", blank=True)
    about = models.TextField("о себе", max_length=ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField("активен", default=True)
    is_staff = models.BooleanField("администратор", default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-id"]
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar.save(avatar_upload_path(self, ""), build_initial_avatar(self.name), save=False)
        super().save(*args, **kwargs)
