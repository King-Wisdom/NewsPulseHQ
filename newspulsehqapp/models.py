from django.db import models
from django.urls import reverse

from .utils import seed_like_count


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in navigation and on the homepage.",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_articles", kwargs={"slug": self.slug})


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    source_url = models.URLField(
         blank=True,
         null=True,
    )

    source_name = models.CharField(
        max_length=150,
        blank=True,
    )

    image_url = models.URLField(
        blank=True,
        null=True,
    )
        
    excerpt = models.TextField(blank=True)
    content = models.TextField()

    author = models.CharField(max_length=150, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="articles",
    )

    featured_image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True,
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Baseline engagement assigned when the article is imported, so the
    # site shows realistic like counts (including popular 1K+ stories)
    # instead of starting every article at zero. Real visitor likes
    # (see ArticleLike) are added on top of this baseline.
    base_likes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "article_detail",
            kwargs={"slug": self.slug},
        )

    def save(self, *args, **kwargs):
        if self.is_featured and self.base_likes < 650:
            self.base_likes = seed_like_count(is_featured=True)

        super().save(*args, **kwargs)

    @property
    def like_count(self):
        return self.base_likes + self.likes.count()


# ADD THESE TWO MODELS BELOW ARTICLE

class ArticleLike(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    visitor_key = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["article", "visitor_key"],
                name="unique_article_like",
            )
        ]

    def __str__(self):
        return f"Like for {self.article.title}"


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    content = models.TextField()

    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} - {self.article.title}"


class SponsoredAd(models.Model):
    PLACEMENT_HOME_FEED = "home_feed"
    PLACEMENT_CATEGORY_TOP = "category_top"
    PLACEMENT_ARTICLE_INLINE = "article_inline"

    PLACEMENT_CHOICES = [
        (PLACEMENT_HOME_FEED, "Homepage — between hero and latest stories"),
        (PLACEMENT_CATEGORY_TOP, "Category page — top banner"),
        (PLACEMENT_ARTICLE_INLINE, "Article page — inline within content"),
    ]

    advertiser_name = models.CharField(max_length=150)
    headline = models.CharField(max_length=200)
    body = models.CharField(max_length=300, blank=True)

    destination_url = models.URLField(
        help_text="Where visitors land after clicking the ad.",
    )

    image = models.ImageField(
        upload_to="sponsored_ads/",
        blank=True,
        null=True,
    )

    placement = models.CharField(
        max_length=30,
        choices=PLACEMENT_CHOICES,
    )

    is_active = models.BooleanField(default=True)

    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)

    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority ads are shown first when several are active for a placement.",
    )

    impression_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return f"{self.advertiser_name} — {self.headline}"

    def get_click_url(self):
        return reverse("sponsored_ad_click", kwargs={"pk": self.pk})