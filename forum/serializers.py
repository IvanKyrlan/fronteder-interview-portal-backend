from rest_framework import serializers
from forum.models import ForumTopic


class ForumTopicSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    comments_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_has_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = ForumTopic
        fields = [
            'id', 'title', 'content', 'category', 'category_display',
            'author', 'author_name', 'created_at', 'updated_at',
            'views', 'is_pinned', 'comments_count', 'has_code',
            'likes_count', 'user_has_liked', 'user_has_bookmarked'
        ]
        read_only_fields = ['views', 'is_pinned', 'author_name', 'comments_count',
                            'author', 'likes_count', 'user_has_liked', 'user_has_bookmarked']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False

    def get_user_has_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.bookmarks.all()
        return False