from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project, Skill

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo users, projects, participants, and project skills."

    def handle(self, *args, **options):
        users = [
            {
                "email": "anna@example.com",
                "name": "Анна",
                "surname": "Иванова",
                "phone": "+79000000001",
                "about": "Backend-разработчик, люблю Django и понятные API.",
                "github_url": "https://github.com/anna",
            },
            {
                "email": "pavel@example.com",
                "name": "Павел",
                "surname": "Смирнов",
                "phone": "+79000000002",
                "about": "Frontend-разработчик, собираю удобные интерфейсы.",
                "github_url": "https://github.com/pavel",
            },
            {
                "email": "maria@example.com",
                "name": "Мария",
                "surname": "Кузнецова",
                "phone": "+79000000003",
                "about": "Product-minded QA, ищу сильные учебные проекты.",
                "github_url": "https://github.com/maria",
            },
        ]

        created_users = []
        for user_data in users:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=user_data,
            )
            if created:
                user.set_password("password123")
                user.save()
            created_users.append(user)

        skill_names = ["Django", "PostgreSQL", "JavaScript", "UI", "Testing", "Docker"]
        skills = {name: Skill.objects.get_or_create(name=name)[0] for name in skill_names}

        projects = [
            {
                "owner": created_users[0],
                "name": "Team Finder API",
                "description": "Сервис для поиска участников в учебные и pet-проекты.",
                "github_url": "https://github.com/anna/team-finder-api",
                "skills": ["Django", "PostgreSQL", "Docker"],
                "participants": [created_users[1]],
            },
            {
                "owner": created_users[1],
                "name": "Design Sprint Board",
                "description": "Доска для быстрых продуктовых гипотез и командных обсуждений.",
                "github_url": "https://github.com/pavel/sprint-board",
                "skills": ["JavaScript", "UI"],
                "participants": [created_users[0], created_users[2]],
            },
            {
                "owner": created_users[2],
                "name": "QA Knowledge Base",
                "description": "База тест-кейсов и чек-листов для начинающих QA-инженеров.",
                "github_url": "https://github.com/maria/qa-base",
                "skills": ["Testing", "Django"],
                "participants": [created_users[0]],
            },
        ]

        for project_data in projects:
            project, _ = Project.objects.get_or_create(
                owner=project_data["owner"],
                name=project_data["name"],
                defaults={
                    "description": project_data["description"],
                    "github_url": project_data["github_url"],
                },
            )
            project.participants.add(project.owner, *project_data["participants"])
            project.skills.add(*(skills[name] for name in project_data["skills"]))

        self.stdout.write(self.style.SUCCESS("Demo data is ready. Password for demo users: password123"))
