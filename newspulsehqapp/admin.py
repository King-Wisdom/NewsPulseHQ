from django.contrib import admin

from .models import Article, ArticleLike, Category, Comment, SponsoredAd


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering = ("order", "name")
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


@admin.register(SponsoredAd)
class SponsoredAdAdmin(admin.ModelAdmin):
    list_display = (
        "advertiser_name",
        "headline",
        "placement",
        "is_active",
        "priority",
        "impression_count",
        "click_count",
        "starts_at",
        "ends_at",
    )

    list_filter = (
        "placement",
        "is_active",
    )

    search_fields = (
        "advertiser_name",
        "headline",
        "body",
    )

    readonly_fields = (
        "impression_count",
        "click_count",
    )

    ordering = (
        "-priority",
        "-created_at",
    )