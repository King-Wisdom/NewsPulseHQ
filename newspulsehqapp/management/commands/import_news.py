import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from newspulsehqapp.models import Article, Category


class Command(BaseCommand):
    help = (
        "Import Nigerian, world, politics, culture, business, "
        "technology, crypto and trading news."
    )

    API_URL = "https://newsapi.org/v2"

    FEEDS = [
        {
            "name": "Nigeria",
            "category": "Nigeria",
            "endpoint": "top-headlines",
            "params": {
                "country": "ng",
                "category": "general",
                "pageSize": 20,
            },
        },
        {
            "name": "Politics",
            "category": "Politics",
            "endpoint": "everything",
            "params": {
                "q": (
                    "politics OR government OR election "
                    "OR parliament OR president"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
        {
            "name": "World",
            "category": "World",
            "endpoint": "everything",
            "params": {
                "q": "world OR international OR global",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
        {
            "name": "Culture",
            "category": "Culture",
            "endpoint": "everything",
            "params": {
                "q": (
                    "culture OR entertainment OR music "
                    "OR film OR art OR lifestyle"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
        {
            "name": "Business",
            "category": "Business",
            "endpoint": "everything",
            "params": {
                "q": (
                    "business OR economy OR markets "
                    "OR companies OR finance"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
        {
            "name": "Technology",
            "category": "Technology",
            "endpoint": "everything",
            "params": {
                "q": (
                    "technology OR artificial intelligence "
                    "OR AI OR startups OR software"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
        {
            "name": "Crypto",
            "category": "Crypto",
            "endpoint": "everything",
            "params": {
                "q": (
                    "crypto OR cryptocurrency OR bitcoin "
                    "OR ethereum OR blockchain"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
        {
            "name": "Trading",
            "category": "Trading",
            "endpoint": "everything",
            "params": {
                "q": (
                    "forex OR trading OR stocks "
                    "OR commodities OR investing"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            },
        },
    ]

    def handle(self, *args, **options):

        api_key = getattr(settings, "NEWS_API_KEY", None)

        if not api_key:
            self.stdout.write(
                self.style.ERROR(
                    "NEWS_API_KEY is missing from settings.py"
                )
            )
            return

        total_created = 0
        total_updated = 0

        headers = {
            "X-Api-Key": api_key,
        }

        for feed in self.FEEDS:

            self.stdout.write(
                f"Fetching {feed['name']}..."
            )

            params = feed["params"].copy()

            try:
                response = requests.get(
                    f"{self.API_URL}/{feed['endpoint']}",
                    params=params,
                    headers=headers,
                    timeout=20,
                )

                response.raise_for_status()

                data = response.json()

            except requests.RequestException as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Request failed for "
                        f"{feed['name']}: {error}"
                    )
                )
                continue

            if data.get("status") != "ok":
                self.stdout.write(
                    self.style.ERROR(
                        f"News API error for "
                        f"{feed['name']}: "
                        f"{data.get('message', 'Unknown error')}"
                    )
                )
                continue

            articles = data.get("articles", [])

            category, _ = Category.objects.get_or_create(
                name=feed["category"],
                defaults={
                    "slug": slugify(feed["category"])
                },
            )

            for item in articles:

                title = (
                    item.get("title") or ""
                ).strip()

                source_url = (
                    item.get("url") or ""
                ).strip()

                if not title or not source_url:
                    continue

                source = item.get("source") or {}

                source_name = (
                    source.get("name") or ""
                ).strip()

                image_url = item.get("urlToImage") or ""
                self.stdout.write(
                    f"IMAGE DEBUG: {image_url}"
                )
                image_url = image_url.strip()

                description = (
                    item.get("description") or ""
                ).strip()

                content = (
                    item.get("content") or ""
                ).strip()

                author = (
                    item.get("author") or ""
                ).strip()

                published_at = parse_datetime(
                    item.get("publishedAt") or ""
                )

                existing = Article.objects.filter(
                    source_url=source_url
                ).first()

                if existing:

                    existing.source_name = source_name
                    existing.image_url = image_url
                    existing.author = author
                    existing.excerpt = description

                    if published_at:
                        existing.published_at = published_at

                    existing.category = category

                    existing.save(
                        update_fields=[
                            "source_name",
                            "image_url",
                            "author",
                            "excerpt",
                            "published_at",
                            "category",
                            "updated_at",
                        ]
                    )

                    total_updated += 1
                    continue

                base_slug = slugify(title)

                if not base_slug:
                    continue

                article_slug = base_slug
                counter = 2

                while Article.objects.filter(
                    slug=article_slug
                ).exists():

                    article_slug = (
                        f"{base_slug}-{counter}"
                    )

                    counter += 1

                if not content:
                    content = description

                if not content:
                    content = (
                        "Read the full story from "
                        f"{source_name or 'the original publisher'}."
                    )

                Article.objects.create(
                    title=title,
                    slug=article_slug,
                    source_url=source_url,
                    source_name=source_name,
                    image_url=image_url,
                    excerpt=description,
                    content=content,
                    author=author,
                    category=category,
                    published_at=published_at,
                    is_published=True,
                    is_featured=False,
                )

                total_created += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "News import complete. "
                f"{total_created} new articles created, "
                f"{total_updated} existing articles updated."
            )
        )