from rest_framework import generics, permissions
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer


class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(featured=True)

        article_type = self.request.query_params.get('article_type', None)
        if article_type:
            queryset = queryset.filter(article_type=article_type)

        return queryset


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'