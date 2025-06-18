from rest_framework import serializers
from articles.models import Article, ArticleSection
from django.utils import timezone
from django.conf import settings
import pytz

class LocalDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value is None:
            return None

        if timezone.is_aware(value):
            local_timezone = pytz.timezone(settings.TIME_ZONE)
            value = value.astimezone(local_timezone)

        return value.strftime("%d.%m.%Y %H:%M")

class ArticleSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleSection
        fields = [
            'id', 'order', 'title',
            'content', 'image', 'image_caption',
            'code', 'language', 'code_description'
        ]

# class ArticleListSerializer(serializers.ModelSerializer):
#     author_name = serializers.CharField(source='author.username', read_only=True)
#     article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
#     published_at = LocalDateTimeField(read_only=True)
#
#     class Meta:
#         model = Article
#         fields = [
#             'id', 'title', 'slug', 'description', 'thumbnail',
#             'author_name', 'published_at', 'article_type', 'article_type_display'
#         ]

class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
    published_at = LocalDateTimeField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'description',
            'thumbnail', 'thumbnail_url',
            'author_name', 'published_at', 'article_type', 'article_type_display'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            from django.conf import settings
            return settings.MEDIA_URL + str(obj.thumbnail)
        return None

# class ArticleDetailSerializer(serializers.ModelSerializer):
#     author_name = serializers.CharField(source='author.username', read_only=True)
#     sections = ArticleSectionSerializer(many=True, read_only=True)
#     article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
#     published_at = LocalDateTimeField(read_only=True)
#
#     class Meta:
#         model = Article
#         fields = [
#             'id', 'title', 'slug', 'description', 'summary',
#             'thumbnail', 'author_name', 'published_at',
#             'article_type', 'article_type_display', 'sections'
#         ]

class ArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    sections = ArticleSectionSerializer(many=True, read_only=True)
    article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
    published_at = LocalDateTimeField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'description', 'summary',
            'thumbnail', 'thumbnail_url',
            'author_name', 'published_at',
            'article_type', 'article_type_display', 'sections'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            from django.conf import settings
            return settings.MEDIA_URL + str(obj.thumbnail)
        return None
