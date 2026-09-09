from django.db import migrations

from newspulsehqapp.utils import seed_like_count


def backfill_base_likes(apps, schema_editor):
    Article = apps.get_model("newspulsehqapp", "Article")

    for article in Article.objects.filter(base_likes=0):
        article.base_likes = seed_like_count(is_featured=article.is_featured)
        article.save(update_fields=["base_likes"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("newspulsehqapp", "0007_sponsoredad_alter_category_options_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_base_likes, noop),
    ]
