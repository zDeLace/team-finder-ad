from django.db import migrations, models
import django.db.models.deletion
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, verbose_name='Email')),
                ('name', models.CharField(max_length=124, verbose_name='Имя')),
                ('surname', models.CharField(max_length=124, verbose_name='Фамилия')),
                ('avatar', models.ImageField(blank=True, upload_to='avatars/', verbose_name='Аватар')),
                ('phone', models.CharField(blank=True, default='', max_length=12, validators=[users.validators.validate_phone], verbose_name='Телефон')),
                ('github_url', models.URLField(blank=True, default='', validators=[users.validators.validate_github_url], verbose_name='GitHub')),
                ('about', models.TextField(blank=True, default='', max_length=256, verbose_name='О себе')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Администратор')),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ['id'],
                'indexes': [
                    models.Index(fields=['email'], name='users_user_email_idx'),
                    models.Index(fields=['surname', 'name'], name='users_user_surname_idx'),
                ],
            },
        ),
    ]
