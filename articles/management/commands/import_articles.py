import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from articles.models import Article, ArticleSection

class Command(BaseCommand):
    help = "Імпортує статті та секції з JSON-файлу"

    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, 'data', 'articles', 'articles.json')
        if not os.path.exists(json_path):
            json_path = r'C:\Users\Ivan Kyrlan\Documents\Study\fronteder-interview-portal\fronteder-interview-portal-backend\data\articles\articles.json'
            if not os.path.exists(json_path):
                self.stdout.write(self.style.ERROR('Не знайдено articles.json'))
                return
            else:
                self.stdout.write(self.style.SUCCESS(f'Використовую альтернативний шлях: {json_path}'))

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        User = get_user_model()
        created_articles = {}
        created_count = 0

        for obj in data:
            if obj["model"] == "articles.article":
                fields = obj["fields"]
                pk = obj["pk"]

                # Автор
                try:
                    author = User.objects.get(pk=fields["author"])
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Автор з id={fields['author']} не знайдений, скіпаємо статтю {fields['title']}"))
                    continue

                article, created = Article.objects.get_or_create(
                    slug=fields["slug"],
                    defaults={
                        "title": fields["title"],
                        "article_type": fields["article_type"],
                        "description": fields.get("description", ""),
                        "summary": fields.get("summary", ""),
                        "author": author,
                        "published_at": fields.get("published_at"),
                        "featured": fields.get("featured", False),
                        "thumbnail": fields.get("thumbnail", None),
                    }
                )
                created_articles[pk] = article
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Імпортовано статей: {created_count}"))

        sections_count = 0
        for obj in data:
            if obj["model"] == "articles.articlesection":
                fields = obj["fields"]
                article_pk = fields["article"]

                article = created_articles.get(article_pk)
                if not article:
                    self.stdout.write(self.style.WARNING(f"Не знайдено статтю для секції (article pk={article_pk}), скіпаємо секцію"))
                    continue

                ArticleSection.objects.create(
                    article=article,
                    order=fields.get("order", 0),
                    title=fields.get("title", ""),
                    content=fields.get("content", ""),
                    image=fields.get("image", None),
                    image_caption=fields.get("image_caption", ""),
                    code=fields.get("code", ""),
                    language=fields.get("language", ""),
                    code_description=fields.get("code_description", "")
                )
                sections_count += 1

        self.stdout.write(self.style.SUCCESS(f"Імпортовано секцій статей: {sections_count}"))
