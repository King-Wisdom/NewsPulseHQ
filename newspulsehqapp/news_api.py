import requests

from django.conf import settings


GNEWS_URL = "https://gnews.io/api/v4"


def fetch_news(
    query=None,
    category=None,
    country=None,
    max_articles=10,
):
    endpoint = (
        f"{GNEWS_URL}/search"
        if query
        else f"{GNEWS_URL}/top-headlines"
    )

    params = {
        "lang": "en",
        "max": max_articles,
        "apikey": settings.GNEWS_API_KEY,
    }

    if query:
        params["q"] = query

    if category:
        params["category"] = category

    if country:
        params["country"] = country

    response = requests.get(
        endpoint,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("articles", [])