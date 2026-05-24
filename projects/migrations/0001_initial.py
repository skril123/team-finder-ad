from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=124, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("github_url", models.URLField(blank=True)),
                ("status", models.CharField(choices=[("open", "Open"), ("closed", "Closed")], default="open", max_length=6)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_projects", to=settings.AUTH_USER_MODEL)),
                ("participants", models.ManyToManyField(blank=True, related_name="participated_projects", to=settings.AUTH_USER_MODEL)),
                ("skills", models.ManyToManyField(blank=True, related_name="projects", to="projects.skill")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="skill",
            index=models.Index(fields=["name"], name="projects_sk_name_431a58_idx"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["-created_at"], name="projects_pr_created_775fe7_idx"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["status"], name="projects_pr_status_f023cb_idx"),
        ),
    ]
