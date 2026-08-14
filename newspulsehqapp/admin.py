from django.contrib import admin

from .models import Article, ArticleLike, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "is_published",
        "is_featured",
        "published_at",
    )

    list_filter = (
        "is_published",
        "is_featured",
        "category",
    )

    search_fields = (
        "title",
        "excerpt",
        "content",
        "author",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = ("category",)

    date_hierarchy = "published_at"

    ordering = (
        "-published_at",
        "-created_at",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "article",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "content",
        "article__title",
    )

    ordering = (
        "-created_at",
    )


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "created_at",
    )

    search_fields = (
        "article__title",
    )

    ordering = (
        "-created_at",
    )