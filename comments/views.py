from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        content_type_str = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if not content_type_str or not object_id:
            return Comment.objects.none()

        try:
            app_label, model = content_type_str.split('.')
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            return Comment.objects.filter(
                content_type=content_type,
                object_id=object_id,
                parent__isnull=True
            )
        except (ValueError, ContentType.DoesNotExist):
            return Comment.objects.none()


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            comment = Comment.objects.get(id=serializer.instance.id)
            response_serializer = CommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)