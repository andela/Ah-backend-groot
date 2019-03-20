from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from ..models import (CommentHistory, Comment, Article, LikeDislike)
from ..serializers import CommentSerializer, CommentHistorySerializer
from authors.apps.articles.renderers import CommentHistoryJSONRenderer


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

    def highlight_comment(self, request):
        article_slug = self.kwargs['slug']
        specific_article = get_object_or_404(Article, slug=article_slug)
        comment = request.data.get('comment', {})
        if 'end_position' in comment and 'start_position' in comment:
            end_position = comment.get('end_position', 0)
            start_position = comment.get('start_position', 0)
            article_section = specific_article.body[start_position:
                                                    end_position]
            comment['article_section'] = article_section
        return comment

    def create(self, request, *args, **kwargs):
        comment = self.highlight_comment(request)
        serializer = self.get_serializer(data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class ListCommentHistoryView(ListAPIView):
    serializer_class = CommentHistorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (CommentHistoryJSONRenderer,)
    queryset = CommentHistory.objects.all()

    def list(self, request, *args, **kwargs):
        history = self.queryset.filter(
            comment_id=self.kwargs['id'])
        if history.count() < 1:
            return Response({"message": "This comment has not been edited"},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class CommentChoiceView(ListCreateAPIView):
    """Implements the like and dislike endpoints."""
    serializer_class = CommentSerializer
    model = Comment
    vote_type = None
    manager = None

    def post(self, request, slug, pk):
        obj = self.model.objects.get(pk=pk)
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
        serializer = CommentSerializer(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
