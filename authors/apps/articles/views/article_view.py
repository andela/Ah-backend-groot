from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
    CreateAPIView,
)
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..pagination import ArticlePagination
from ..models import (Article, ReadingStats)
from ..serializers import ArticleSerializer
from authors.apps.articles.renderers import ArticleJSONRenderer
from ....apps.core.utils import send_an_email
from decouple import config

from rest_framework import filters


class CreateArticle(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    pagination_class = ArticlePagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tags__tag', 'author__username',
                     'title', 'body', 'description')

    def create(self, request):
        article = request.data.get('article', {})
        serializer = self.get_serializer(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = self.queryset
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__tag=tag)
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)
        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)
        favorite_author = self.request.query_params.get('favorited', None)
        if favorite_author:
            queryset = queryset.filter(author__username=favorite_author,
                                       favorited=True)
        return queryset


class ArticleRetrieveUpdate(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_class = (ArticleJSONRenderer,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = ArticleSerializer(article)
        current_user = request.user
        ReadingStats.objects.create(article=article,
                                    user=current_user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        self.serializer_instance = self.get_object()
        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            self.serializer_instance, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteArticle(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def create(self, request, *args, **kwargs):
        profile = self.request.user.profile
        article = self.get_object()

        if article.author_id == profile.user_id:
            return Response(
                {'message': 'can not favorite own article'},
                status=status.HTTP_400_BAD_REQUEST)
        if profile.has_favorited(article):
            return Response(
                {'message': 'article can not be favorited again'},
                status=status.HTTP_400_BAD_REQUEST)

        profile.favorite(article)
        article.favorited = True
        article.favorites_count += 1
        article.save()

        serializer = self.serializer_class(article)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnFavoriteArticle(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def destroy(self, request, *args, **kwargs):
        profile = self.request.user.profile
        article = self.get_object()

        if not profile.has_favorited(article):
            return Response(
                {'message': 'This article is not in your favorite list'},
                status=status.HTTP_400_BAD_REQUEST)

        profile.unfavorite(article)
        if article.favorites_count > 0:
            article.favorites_count -= 1
            if article.favorites_count == 0:
                article.favorited = False

        article.save()

        serializer = self.serializer_class(article)

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class PublishArticleUpdate(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def create(self, request, *args, **kwargs):
        profile = self.request.user.profile
        article = self.get_object()
        message = 'can not publish article that does not belong to you'

        if article.author_id != profile.user_id:
            return Response(
                {'message': message},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(article)
        article.is_published = True
        article.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShareArticleView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def create(self, request, *args, **kwargs):
        share_platform = self.kwargs.get('platform')
        article_link = 'http://{0}/api/article/{1}/'.format(
            request.get_host(),
            self.kwargs.get('slug'))
        article = self.get_object()
        if(share_platform == 'gmail'):
            receiver = request.data.get("share_with")
            send_an_email(receiver,
                          'share_article.html',
                          article_link,
                          request.user.username)
            return Response({"message": "article has been shared"},
                            status=status.HTTP_200_OK)

        elif(share_platform == "facebook"):
            share_link = "https://www.facebook.com/v2.9/dialog/share?app_id={0}&display=page&href={1}".format(config('FACEBOOK_APP_ID'), article_link) # NOQA

        elif(share_platform == "twitter"):
            share_link = "https://twitter.com/intent/tweet?text={0}%20by%20{1}%20{2}".format(article.title.replace(" ", "%20"), article.author.username, article_link) # NOQA

        else:
            return Response({"message": "invalid url"},
                            status=status.HTTP_400_BAD_REQUEST)
        article.save()
        return Response({"share link": share_link},
                        status=status.HTTP_200_OK)
