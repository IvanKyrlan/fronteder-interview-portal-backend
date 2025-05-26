from rest_framework import generics, permissions
from .models import InterviewVideo
from .serializers import InterviewVideoSerializer

class InterviewVideoListView(generics.ListAPIView):
    queryset = InterviewVideo.objects.all()
    serializer_class = InterviewVideoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(level=level)

        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(featured=True)

        return queryset

class InterviewVideoDetailView(generics.RetrieveAPIView):
    queryset = InterviewVideo.objects.all()
    serializer_class = InterviewVideoSerializer
    permission_classes = [permissions.AllowAny]