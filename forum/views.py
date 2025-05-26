from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models

from .models import ForumTopic
from .serializers import ForumTopicSerializer


class ForumTopicListView(generics.ListCreateAPIView):
    serializer_class = ForumTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def get_queryset(self):
        queryset = ForumTopic.objects.all()

        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(content__icontains=search)
            )

        sort_by = self.request.query_params.get('sort_by', None)
        if sort_by:
            sort_mapping = {
                'newest': '-created_at',
                'oldest': 'created_at',
                'updated': '-updated_at',
                'title_asc': 'title',
                'title_desc': '-title',
                'popular': '-views',
                'comments': '-comments_count'
            }

            if sort_by in sort_mapping:
                queryset = queryset.order_by(sort_mapping[sort_by])
            else:
                queryset = queryset.order_by('-is_pinned', '-created_at')
        else:
            queryset = queryset.order_by('-is_pinned', '-created_at')

        return queryset

    def perform_create(self, serializer):
        try:
            content = self.request.data.get('content', '')
            has_code = False
            if content and isinstance(content, str):
                has_code = "```" in content
            serializer.save(author=self.request.user, has_code=has_code)
        except Exception as e:
            import traceback
            print(f"ERROR creating forum topic: {str(e)}")
            print(traceback.format_exc())
            raise


class ForumTopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ForumTopic.objects.all()
    serializer_class = ForumTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def get(self, request, *args, **kwargs):
        topic = self.get_object()
        topic.views += 1
        topic.save(update_fields=['views'])
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        topic = self.get_object()
        if topic.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "У вас немає прав для редагування цієї теми."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        topic = self.get_object()
        if topic.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "У вас немає прав для видалення цієї теми."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class ForumCategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = [
            {"id": choice[0], "name": choice[1]}
            for choice in ForumTopic.CATEGORY_CHOICES
        ]
        return Response(categories)


class ForumTopicLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            topic = ForumTopic.objects.get(pk=pk)
            if request.user in topic.likes.all():
                return Response(
                    {"detail": "Ви вже оцінили цю тему."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            topic.likes.add(request.user)
            return Response({"likes_count": topic.likes.count()})
        except ForumTopic.DoesNotExist:
            return Response(
                {"detail": "Тему не знайдено."},
                status=status.HTTP_404_NOT_FOUND
            )


class ForumTopicUnlikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            topic = ForumTopic.objects.get(pk=pk)
            if request.user not in topic.likes.all():
                return Response(
                    {"detail": "Ви не оцінювали цю тему."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            topic.likes.remove(request.user)
            return Response({"likes_count": topic.likes.count()})
        except ForumTopic.DoesNotExist:
            return Response(
                {"detail": "Тему не знайдено."},
                status=status.HTTP_404_NOT_FOUND
            )


class ForumTopicBookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            topic = ForumTopic.objects.get(pk=pk)
            if request.user in topic.bookmarks.all():
                return Response(
                    {"detail": "Ця тема вже у ваших закладках."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            topic.bookmarks.add(request.user)
            return Response({"bookmarks_count": topic.bookmarks.count()})
        except ForumTopic.DoesNotExist:
            return Response(
                {"detail": "Тему не знайдено."},
                status=status.HTTP_404_NOT_FOUND
            )


class ForumTopicUnbookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            topic = ForumTopic.objects.get(pk=pk)
            if request.user not in topic.bookmarks.all():
                return Response(
                    {"detail": "Цієї теми немає у ваших закладках."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            topic.bookmarks.remove(request.user)
            return Response({"bookmarks_count": topic.bookmarks.count()})
        except ForumTopic.DoesNotExist:
            return Response(
                {"detail": "Тему не знайдено."},
                status=status.HTTP_404_NOT_FOUND
            )


class UserBookmarksView(generics.ListAPIView):
    serializer_class = ForumTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ForumTopic.objects.filter(bookmarks=self.request.user).order_by('-created_at')