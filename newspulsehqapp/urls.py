from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "article/<slug:slug>/",
        views.article_detail,
        name="article_detail",
    ),

    path(
        "article/<slug:slug>/like/",
        views.like_article,
        name="like_article",
    ),

    path(
        "article/<slug:slug>/comment/",
        views.add_comment,
        name="add_comment",
    ),

    path(
        "category/<slug:slug>/",
        views.category_articles,
        name="category_articles",
    ),
]