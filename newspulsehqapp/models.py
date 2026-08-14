from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

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