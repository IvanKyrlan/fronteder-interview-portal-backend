from rest_framework import serializers
from django.contrib.auth.models import User
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType


class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author_name', 'created_at',
            'user', 'parent', 'replies', 'data_processing_agreed',
            'has_code'
        ]
        read_only_fields = ['created_at', 'user']


class CommentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = [
            'content', 'author_name', 'parent',
            'content_type', 'object_id', 'data_processing_agreed',
            'has_code', 'code', 'code_language'
        ]

    def validate(self, data):
        content_type_str = data.pop('content_type')
        try:
            app_label, model = content_type_str.split('.')
            data['content_type'] = ContentType.objects.get(app_label=app_label, model=model)
        except (ValueError, ContentType.DoesNotExist):
            raise serializers.ValidationError({'content_type': 'Invalid content type format or not found'})

        if not data.get('data_processing_agreed'):
            raise serializers.ValidationError({'data_processing_agreed': 'Необхідно погодитись на обробку даних'})

        if 'content' in data and '```' in data['content']:
            data['has_code'] = True

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        return Comment.objects.create(**validated_data)