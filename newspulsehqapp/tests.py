from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article, ArticleLike, Category, SponsoredAd


def make_article(**kwargs):
    defaults = {
        "title": "Test Article",
        "slug": "test-article",
        "content": "Some content.",
        "is_published": True,
        "base_likes": 40,
    }
    defaults.update(kwargs)
    return Article.objects.create(**defaults)


class CategoryOrderingTests(TestCase):
    def test_categories_ordered_by_order_then_name(self):
        Category.objects.create(name="Zebra", slug="zebra", order=1)
        Category.objects.create(name="Alpha", slug="alpha", order=0)
        Category.objects.create(name="Beta", slug="beta", order=1)

        names = list(Category.objects.values_list("name", flat=True))

        self.assertEqual(names, ["Alpha", "Beta", "Zebra"])


class ArticleLikeCountTests(TestCase):
    def test_like_count_combines_base_and_real_likes(self):
        article = make_article(base_likes=500)

        ArticleLike.objects.create(article=article, visitor_key="abc")

        self.assertEqual(article.like_count, 501)

    def test_featured_article_gets_boosted_baseline(self):
        article = make_article(slug="featured-one", base_likes=10, is_featured=True)

        self.assertGreaterEqual(article.base_likes, 650)


class HomeViewTests(TestCase):
    def test_home_page_loads(self):
        make_article(is_featured=True)
        make_article(slug="second-article", title="Second")

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Second")

    def test_home_page_loads_with_no_articles(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)


class ArticleDetailViewTests(TestCase):
    def test_article_detail_loads(self):
        article = make_article()

        response = self.client.get(article.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)

    def test_unpublished_article_returns_404(self):
        article = make_article(slug="draft", is_published=False)

        response = self.client.get(article.get_absolute_url())

        self.assertEqual(response.status_code, 404)


class LikeArticleViewTests(TestCase):
    def test_get_request_not_allowed(self):
        article = make_article()

        response = self.client.get(reverse("like_article", args=[article.slug]))

        self.assertEqual(response.status_code, 405)

    def test_like_then_unlike_toggles(self):
        article = make_article(base_likes=100)
        url = reverse("like_article", args=[article.slug])

        response = self.client.post(url)
        data = response.json()

        self.assertTrue(data["liked"])
        self.assertEqual(data["like_count"], 101)
        self.assertIn("like_count_display", data)

        response = self.client.post(url)
        data = response.json()

        self.assertFalse(data["liked"])
        self.assertEqual(data["like_count"], 100)


class CategoryArticlesViewTests(TestCase):
    def test_category_page_loads(self):
        category = Category.objects.create(name="Tech", slug="tech")

        make_article(category=category)

        response = self.client.get(category.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Article")


class SponsoredAdTests(TestCase):
    def test_inactive_ad_not_selected(self):
        from .ads import get_active_ad

        SponsoredAd.objects.create(
            advertiser_name="Acme",
            headline="Buy stuff",
            destination_url="https://example.com",
            placement=SponsoredAd.PLACEMENT_HOME_FEED,
            is_active=False,
        )

        self.assertIsNone(get_active_ad(SponsoredAd.PLACEMENT_HOME_FEED))

    def test_active_ad_is_selected_and_tracked(self):
        from .ads import get_active_ad

        ad = SponsoredAd.objects.create(
            advertiser_name="Acme",
            headline="Buy stuff",
            destination_url="https://example.com",
            placement=SponsoredAd.PLACEMENT_HOME_FEED,
            is_active=True,
        )

        selected = get_active_ad(SponsoredAd.PLACEMENT_HOME_FEED)

        self.assertEqual(selected.pk, ad.pk)

        ad.refresh_from_db()

        self.assertEqual(ad.impression_count, 1)

    def test_expired_ad_not_selected(self):
        from .ads import get_active_ad

        SponsoredAd.objects.create(
            advertiser_name="Acme",
            headline="Buy stuff",
            destination_url="https://example.com",
            placement=SponsoredAd.PLACEMENT_HOME_FEED,
            is_active=True,
            ends_at=timezone.now() - timezone.timedelta(days=1),
        )

        self.assertIsNone(get_active_ad(SponsoredAd.PLACEMENT_HOME_FEED))

    def test_click_redirects_and_counts(self):
        ad = SponsoredAd.objects.create(
            advertiser_name="Acme",
            headline="Buy stuff",
            destination_url="https://example.com",
            placement=SponsoredAd.PLACEMENT_HOME_FEED,
            is_active=True,
        )

        response = self.client.get(reverse("sponsored_ad_click", args=[ad.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://example.com")

        ad.refresh_from_db()

        self.assertEqual(ad.click_count, 1)


class FormatCountTests(TestCase):
    def test_format_count_thresholds(self):
        from .utils import format_count

        self.assertEqual(format_count(0), "0")
        self.assertEqual(format_count(999), "999")
        self.assertEqual(format_count(1000), "1K")
        self.assertEqual(format_count(1250), "1.2K")
        self.assertEqual(format_count(1_500_000), "1.5M")
