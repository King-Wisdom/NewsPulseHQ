from django.core.management.base import BaseCommand
from django.utils.text import slugify

from newspulsehqapp.models import Article, Category
from newspulsehqapp.news_api import fetch_news


class Command(BaseCommand):
    help = "Import news from GNews."

    FEEDS = [
        ("Nigeria", None, None, "ng"),
        ("Politics", "politics government election president", None, None),
        ("World", "world international global", None, None),
        ("Culture", "culture entertainment music film art lifestyle", None, None),
        ("Business", "business economy markets companies finance", None, None),
        ("Technology", "technology artificial intelligence AI startups software", None, None),
        ("Crypto", "crypto cryptocurrency bitcoin ethereum blockchain", None, None),
        ("Trading", "forex trading stocks commodities investing", None, None),
    ]

    def handle(self, *args, **options):
        total_created = 0
        total_updated = 0

        for category_name, query, category, country in self.FEEDS:
            self.stdout.write(f"Fetching {category_name}...")

            try:
                articles = fetch_news(
                    query=query,
                    category=category,
                    country=country,
                    max_articles=20,
                )
            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to fetch {category_name}: {error}"
                    )
                )
                continue

            category_obj, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name)},
            )

            for item in articles:
                title = (item.get("title") or "").strip()
                source_url = (item.get("url") or "").strip()

                if not title or not source_url:
                    continue

                source = item.get("source") or {}

                source_name = (
                    source.get("name") or ""
                ).strip()

                image_url = (
                    item.get("image") or ""
                ).strip()

                description = (
                    item.get("description") or ""
                ).strip()

                content = (
                    item.get("content") or ""
                ).strip()

                author = (
                    item.get("authors") or ""
                )

                if isinstance(author, list):
                    author = ", ".join(author)

                author = str(author).strip()

                published_at = item.get("publishedAt")

                existing = Article.objects.filter(
                    source_url=source_url
                ).first()

                if existing:
                    existing.source_name = source_name
                    existing.image_url = image_url
                    existing.author = author
                    existing.excerpt = description
                    existing.category = category_obj

                    if published_at:
                        existing.published_at = published_at

                    existing.save()

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
                    article_slug = f"{base_slug}-{counter}"
                    counter += 1

                if not content:
                    content = description

                if not content:
                    content = (
                        f"Read the full story from "
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
                    category=category_obj,
                    published_at=published_at,
                    is_published=True,
                    is_featured=False,
                )

                total_created += 1

                self.stdout.write(
                    f"  Image: {image_url or 'NO IMAGE'}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {total_created} created, "
                f"{total_updated} updated."
            )
        )