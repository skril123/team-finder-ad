import io
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


def avatar_upload_path(instance, filename):
    return f"avatars/{uuid.uuid4()}.png"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True)
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def get_short_name(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar.save(avatar_upload_path(self, ""), self._build_initial_avatar(), save=False)
        super().save(*args, **kwargs)

    def _build_initial_avatar(self):
        colors = ["#4F46E5", "#0F766E", "#BE123C", "#7C3AED", "#0369A1", "#15803D"]
        background = random.choice(colors)
        image = Image.new("RGB", (256, 256), background)
        draw = ImageDraw.Draw(image)
        initial = (self.name[:1] or "?").upper()
        font = self._avatar_font()

        try:
            bbox = draw.textbbox((0, 0), initial, font=font)
            x = (256 - (bbox[2] - bbox[0])) / 2
            y = (256 - (bbox[3] - bbox[1])) / 2 - 8
            draw.text((x, y), initial, fill="white", font=font)
        except UnicodeEncodeError:
            draw.text((104, 84), "?", fill="white", font=ImageFont.load_default())

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue())

    def _avatar_font(self):
        font_candidates = [
            settings.BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        for font_path in font_candidates:
            try:
                return ImageFont.truetype(str(font_path), 112)
            except OSError:
                continue
        return ImageFont.load_default()
