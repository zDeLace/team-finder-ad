from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=124, unique=True, verbose_name='Навык')),
            ],
            options={
                'verbose_name': 'Навык',
                'verbose_name_plural': 'Навыки',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название проекта')),
                ('description', models.TextField(blank=True, default='', verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('github_url', models.URLField(blank=True, default='', validators=[users.validators.validate_github_url], verbose_name='GitHub')),
                ('status', models.CharField(
                    choices=[('open', 'Открыт'), ('closed', 'Закрыт')],
                    db_index=True,
                    default='open',
                    max_length=6,
                    verbose_name='Статус',
                )),
                ('owner', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='owned_projects',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Автор',
                )),
                ('participants', models.ManyToManyField(
                    blank=True,
                    related_name='participated_projects',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Участники',
                )),
                ('skills', models.ManyToManyField(
                    blank=True,
                    related_name='projects',
                    to='projects.skill',
                    verbose_name='Необходимые навыки',
                )),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['-created_at'], name='projects_pr_created_idx'),
                    models.Index(fields=['owner'], name='projects_pr_owner_idx'),
                    models.Index(fields=['status'], name='projects_pr_status_idx'),
                ],
            },
        ),
    ]
