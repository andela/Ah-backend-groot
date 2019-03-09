from django.urls import path

from .views import (RetrieveUpdateDestroyCategory,
                    CreateListCategory,
                    CreateArticle,
                    ArticleRetrieveUpdate,
                    FavoriteArticle,
                    UnFavoriteArticle,
                    ChoiceView)
from .models import LikeDislike, LikeDislikeManager, Article

urlpatterns = [
    path('categories/', CreateListCategory.as_view(), name='create-category'),
    path('categories/<str:slug>', RetrieveUpdateDestroyCategory.as_view(),
         name='update-delete'),
    path('articles/', CreateArticle.as_view(), name='create-articles'),
    path('article/<str:slug>/', ArticleRetrieveUpdate.as_view(),
         name='update-articles'),
    path('articles/<str:slug>/like/',
         ChoiceView.as_view(vote_type=LikeDislike.LIKE, model=Article,
                            manager=LikeDislikeManager),
         name='article_like'),
    path(
        'articles/<str:slug>/dislike/',
        ChoiceView.as_view(
            vote_type=LikeDislike.DISLIKE, model=Article,
            manager=LikeDislikeManager),
        name='article_dislike'),
    path('article/<str:slug>/favorite/', FavoriteArticle.as_view(),
         name='favorite-article'),
    path('article/<str:slug>/unfavorite/', UnFavoriteArticle.as_view(),
         name='unfavorite-article')
]
