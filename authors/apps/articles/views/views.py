from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListAPIView,
)
from rest_framework.permissions import (IsAdminUser, AllowAny, IsAuthenticated)
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from ..pagination import ArticlePagination
from ..models import (LikeDislike, ReportedArticle,
                      Category, Article, Bookmark, Tag, ReadingStats)
from ..serializers import (CategorySerializer, ArticleSerializer,
                           TagSerializer,
                           BookmarkSerializer, RatingSerializer,
                           ReportArticleSerializer, ReadStatsSerializer)
import jwt
from django.core.mail import send_mail
from authors.settings import EMAIL_HOST_USER, SECRET_KEY
from authors.apps.authentication.models import User
from authors.apps.articles.renderers import (CategoryJSONRenderer,
                                             BookmarkJSONRenderer,
                                             TagJSONRenderer,
                                             ArticleJSONRenderer)


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


class ArticleChoiceView(ListCreateAPIView):
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


class ListTagsView(ListAPIView):
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (TagJSONRenderer,)
    queryset = Tag.objects.all()


class CreateReportView(CreateAPIView):
    serializer_class = ReportArticleSerializer
    permission_classes = (IsAuthenticated,)

    def get_token(self, request):

        try:
            auth_header = authentication.get_authorization_header(request).\
                split()[1]
            token = jwt.decode(auth_header, SECRET_KEY, 'utf-8')
            author_id = token['id']
            return author_id
        except User.DoesNotExist:
            return ("Token is invalid")

    def post(self, request, slug, **kwargs):
        try:
            article_id = (Article.objects.get(slug=slug).id)
        except Article.DoesNotExist:
            return Response({
                "message": "Article does not exist!"
            }, status=status.HTTP_404_NOT_FOUND)

        reported_reason = request.data.get('reported_reason')

        author_id = (self.get_token(request))

        if ReportedArticle.objects.filter(
                reporter=author_id).filter(article=article_id).exists():
            return Response({
                "message": "You have already reported this Article",
            }, status=status.HTTP_400_BAD_REQUEST)
        article_data = Article.objects.get(pk=article_id)
        new_report = {
            "article": article_id,
            "article_title": article_data.title,
            "report_reported": True,
            "reported_reason": reported_reason,
            "reporter": author_id
        }

        serializer = self.serializer_class(data=new_report)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        subject = "ARTICLES VIOLATIONS ALERT"
        user = User.objects.get(pk=author_id)
        body = "Article: {0},     Article_title:{1} ,   Reported by: {2},    Reason: {3}".format(article_id, article_data.title, user.username, new_report['reported_reason']) # NOQA
        receipient = EMAIL_HOST_USER
        email_sender = EMAIL_HOST_USER
        send_mail(subject, body, email_sender, [
                  receipient], fail_silently=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReadStatsAPIView(ListAPIView):
    """
    this view class enables the author to view their reading
    stats
    """
    serializer_class = ReadStatsSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        """ this gets the readstats of an article """
        reading_stats = ReadingStats.objects.filter(user=request.author.id)
        reading_statsCount = reading_stats.count()
        serializer = self.serializer_class(reading_stats, many=True)
        return Response({
            "readstats": serializer.data,
            "readcount": reading_statsCount
        }, )
