# Generated by Django 5.2.1 on 2025-05-20 06:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок теми')),
                ('content', models.TextField(verbose_name='Зміст теми')),
                ('category', models.CharField(choices=[('technical', 'Технічні питання'), ('interview', 'Питання до співбесід'), ('career', "Кар'єра"), ('other', 'Інше')], default='other', max_length=20, verbose_name='Категорія')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Кількість переглядів')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='Закріплена тема')),
                ('has_code', models.BooleanField(default=False, verbose_name='Містить код')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forum_topics', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('bookmarks', models.ManyToManyField(blank=True, related_name='bookmarked_topics', to=settings.AUTH_USER_MODEL, verbose_name='Закладки')),
                ('likes', models.ManyToManyField(blank=True, related_name='liked_topics', to=settings.AUTH_USER_MODEL, verbose_name='Лайки')),
            ],
            options={
                'verbose_name': 'Тема форуму',
                'verbose_name_plural': 'Теми форуму',
                'ordering': ['-is_pinned', '-created_at'],
            },
        ),
    ]
