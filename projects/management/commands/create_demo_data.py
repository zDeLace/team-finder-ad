from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project, Skill

User = get_user_model()

USERS = [
    {"email": "alice@example.com", "name": "Алиса", "surname": "Иванова", "password": "password123", "about": "Python-разработчик, люблю open source"},
    {"email": "bob@example.com", "name": "Боб", "surname": "Смирнов", "password": "password123", "about": "Frontend на React, ищу команду"},
    {"email": "carol@example.com", "name": "Карина", "surname": "Козлова", "password": "password123", "about": "UI/UX дизайнер"},
    {"email": "admin@example.com", "name": "Админ", "surname": "Системный", "password": "admin123", "is_staff": True, "is_superuser": True},
]

SKILLS = ["Python", "Django", "React", "PostgreSQL", "Docker", "JavaScript", "TypeScript", "Figma", "FastAPI", "Vue.js"]

PROJECTS = [
    {"name": "TaskFlow", "description": "Менеджер задач с Kanban-доской и аналитикой производительности команды.", "owner_email": "alice@example.com", "skills": ["Python", "Django", "PostgreSQL"], "status": "open"},
    {"name": "DevPortfolio", "description": "Платформа для создания красивых портфолио разработчиков за 5 минут.", "owner_email": "alice@example.com", "skills": ["React", "JavaScript"], "status": "open"},
    {"name": "QuizMaster", "description": "Сервис для создания и прохождения интерактивных тестов и опросов.", "owner_email": "bob@example.com", "skills": ["Vue.js", "FastAPI", "PostgreSQL"], "status": "open"},
    {"name": "BudgetBuddy", "description": "Приложение для учёта личных финансов с визуализацией расходов.", "owner_email": "bob@example.com", "skills": ["React", "TypeScript", "Docker"], "status": "closed"},
    {"name": "DesignSystem", "description": "Библиотека UI-компонентов с документацией и дизайн-токенами.", "owner_email": "carol@example.com", "skills": ["Figma", "React", "TypeScript"], "status": "open"},
    {"name": "OpenChat", "description": "Открытый мессенджер с end-to-end шифрованием и группами.", "owner_email": "carol@example.com", "skills": ["Python", "Django", "Docker"], "status": "open"},
]


class Command(BaseCommand):
    help = "Создаёт демо-пользователей, навыки и проекты"

    def handle(self, *args, **options):
        # Навыки
        skill_objs = {}
        for name in SKILLS:
            skill, _ = Skill.objects.get_or_create(name=name)
            skill_objs[name] = skill
        self.stdout.write(f"  Навыки: {len(skill_objs)}")

        # Пользователи
        user_objs = {}
        for data in USERS:
            email = data["email"]
            if User.objects.filter(email=email).exists():
                user_objs[email] = User.objects.get(email=email)
                continue
            is_staff = data.pop("is_staff", False)
            is_superuser = data.pop("is_superuser", False)
            password = data.pop("password")
            user = User(**data)
            user.set_password(password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            user_objs[email] = user
        self.stdout.write(f"  Пользователи: {len(user_objs)}")

        # Проекты
        count = 0
        for data in PROJECTS:
            if Project.objects.filter(name=data["name"]).exists():
                continue
            skills = data.pop("skills")
            owner_email = data.pop("owner_email")
            project = Project.objects.create(owner=user_objs[owner_email], **data)
            for s in skills:
                if s in skill_objs:
                    project.skills.add(skill_objs[s])
            count += 1
        self.stdout.write(f"  Проекты: {count}")
        self.stdout.write(self.style.SUCCESS("Демо-данные созданы!"))
        self.stdout.write("  Логин: alice@example.com / password123")
        self.stdout.write("  Логин: bob@example.com / password123")
        self.stdout.write("  Логин: admin@example.com / admin123")
