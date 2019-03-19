from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListAPIView,
)
from rest_framework.permissions import (IsAdminUser, AllowAny,
                                        IsAuthenticated)
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .pagination import ArticlePagination
from .models import (LikeDislike, Category, Article, Bookmark, Tag, Comment)
from .serializers import (CategorySerializer, ArticleSerializer,
                          TagSerializer, CommentSerializer,
                          BookmarkSerializer, RatingSerializer)
from authors.apps.articles.renderers import (CategoryJSONRenderer,
                                             BookmarkJSONRenderer,
                                             TagJSONRenderer,
                                             ArticleJSONRenderer)

from rest_framework import filters


class CreateListCategory(ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    renderer_classes = (CategoryJSONRenderer,)
    queryset = Category.objects.all()
    pagination_class = ArticlePagination

    def create(self, request, *args, **kwargs):
        category = request.data.get("category", {})
        serializer = self.get_serializer(data=category)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class RetrieveUpdateDestroyCategory(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    queryset = Category.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "category deleted"},
                        status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (IsAuthenticated,)
    renderer_class = (ArticleJSONRenderer,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def update(self, request, *args, **kwargs):
        self.serializer_instance = self.get_object()
        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            self.serializer_instance, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChoiceView(ListCreateAPIView):
    """Implements the like and dislike endpoints."""
    serializer_class = ArticleSerializer
    model = None
    vote_type = None
    manager = None

    def post(self, request, slug):
        obj = self.model.objects.get(slug=slug)
        try:
            likedislike = LikeDislike.objects.get(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=request.user)
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])

            else:
                likedislike.delete()

        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)
        serializer = ArticleSerializer(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class BookmarkView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializer
    renderer_classes = (BookmarkJSONRenderer,)
    queryset = Bookmark.objects.all()

    def create(self, request, *args, **kwargs):
        slug = get_object_or_404(Article, slug=self.kwargs['slug'])
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = Bookmark.objects.filter(
            slug_id=slug.slug, user_id=request.user.id).first()
        if instance:
            return Response({"message": "article already bookmarked"},
                            status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer, slug)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, slug):
        serializer.save(user=self.request.user, slug=slug)


class UnBookmarkView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializer
    lookup_field = 'slug'
    queryset = Bookmark.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = Bookmark.objects.filter(
            user_id=request.user.id, slug_id=self.kwargs['slug'])
        if not instance:
            return Response({"message": "bookmark not found"},
                            status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response({"message": "deleted"},
                        status=status.HTTP_204_NO_CONTENT)


class ListBookmarksView(ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (BookmarkJSONRenderer,)
    queryset = Bookmark.objects.all()

    def get(self, request, *args, **kwargs):
        bookmarks = self.queryset.filter(
            user_id=request.user)
        serializer = self.serializer_class(bookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class RatingsView(ListCreateAPIView):
    """
    implements methods to handle rating articles
    """
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)

    def post(self, request, slug=None):
        """
        method to post a rating for an article
        """
        data = self.serializer_class.update_data(
            request.data.get("article", {}), slug, request.user)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListCreateComment(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    lookup_field = 'slug'
    queryset = Comment.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Comment.objects.filter(
            article_id=self.kwargs.get('slug'))
        serializer = CommentSerializer(queryset, many=True)
        if queryset.count() == 0:
            raise serializers.ValidationError("No comments found")

        if queryset.count() == 1:
            return Response({"Comment": serializer.data})

        return Response(
            {"Comments": serializer.data,
             "commentsCount": queryset.count()})

    def create(self, request, *args, **kwargs):
        comment = request.data.get('comment', {})
        serializer = self.get_serializer(data=comment)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        article=Article.objects.get(
                            slug=self.kwargs.get('slug'))
                        )


class RetrieveUpdateDestroyComment(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), id=self.kwargs.get('id'))

    def update(self, request, *args, **kwargs):
        self.serializer_instance = self.get_object()
        serializer_data = request.data.get('comment', {})

        serializer = self.serializer_class(
            self.serializer_instance, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ListTagsView(ListAPIView):
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (TagJSONRenderer,)
    queryset = Tag.objects.all()
