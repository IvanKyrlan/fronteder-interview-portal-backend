from rest_framework import serializers
from interviews.models import InterviewVideo


class InterviewVideoSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = InterviewVideo
        fields = ['id', 'title', 'youtube_id', 'description', 'category',
                  'category_display', 'level', 'level_display', 'featured', 'created_at']