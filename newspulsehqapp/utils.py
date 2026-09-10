import random


def seed_like_count(is_featured=False):
    """
    Pick a realistic baseline like count for a freshly imported (or newly
    featured) article. Featured stories and a small share of regular
    stories break 1,000 likes, the way genuinely popular articles do on
    a real news site.
    """
    if is_featured:
        return random.randint(650, 2400)

    roll = random.random()

    if roll < 0.12:
        return random.randint(1000, 5200)

    if roll < 0.45:
        return random.randint(180, 950)

    return random.randint(15, 300)


def format_count(value):
    """Render a raw integer as a compact engagement count (1200 -> '1.2K')."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if value < 1000:
        return str(value)

    for threshold, suffix in (
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    ):
        if value >= threshold:
            number = value / threshold
            text = f"{number:.1f}"

            if text.endswith(".0"):
                text = text[:-2]

            return f"{text}{suffix}"

    return str(value)
