from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Article, ArticleLike, Category, Comment


def home(request):

    # Featured story
    featured_article = (
        Article.objects
        .filter(
            is_published=True,
            is_featured=True,
        )
        .select_related("category")
        .first()
    )

    # Latest published stories
    latest_articles = (
        Article.objects
        .filter(is_published=True)
        .select_related("category")
        .exclude(
            pk=featured_article.pk
            if featured_article
            else None
        )
        .order_by("-published_at", "-created_at")[:12]
    )

    # All categories
    categories = Category.objects.all()

    context = {
        "featured_article": featured_article,
        "latest_articles": latest_articles,
        "categories": categories,
    }

    return render(
        request,
        "newspulsehqapp/home.html",
        context,
    )

def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("category"),
        slug=slug,
        is_published=True,
    )

    comments = article.comments.filter(
        is_approved=True
    )

    visitor_key = request.session.session_key

    if not visitor_key:
        request.session.create()
        visitor_key = request.session.session_key

    user_has_liked = ArticleLike.objects.filter(
        article=article,
        visitor_key=visitor_key,
    ).exists()

    context = {
        "article": article,
        "comments": comments,
        "like_count": article.likes.count(),
        "comment_count": comments.count(),
        "user_has_liked": user_has_liked,
    }

    return render(
        request,
        "newspulsehqapp/article_detail.html",
        context,
    )


def like_article(request, slug):
    if request.method != "POST":
        return JsonResponse(
            {
                "error": "POST request required."
            },
            status=405,
        )

    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
    )

    visitor_key = request.session.session_key

    if not visitor_key:
        request.session.create()
        visitor_key = request.session.session_key

    like, created = ArticleLike.objects.get_or_create(
        article=article,
        visitor_key=visitor_key,
    )

    if created:
        liked = True
    else:
        like.delete()
        liked = False

    return JsonResponse(
        {
            "liked": liked,
            "like_count": article.likes.count(),
        }
    )


def add_comment(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
    )

    if request.method != "POST":
        return redirect(
            article.get_absolute_url()
        )

    name = request.POST.get(
        "name",
        "",
    ).strip()

    email = request.POST.get(
        "email",
        "",
    ).strip()

    content = request.POST.get(
        "content",
        "",
    ).strip()

    if not name or not content:
        messages.error(
            request,
            "Please enter your name and comment.",
        )

        return redirect(
            article.get_absolute_url()
        )

    Comment.objects.create(
        article=article,
        name=name,
        email=email,
        content=content,
    )

    messages.success(
        request,
        "Your comment has been posted.",
    )

    return redirect(
        article.get_absolute_url()
    )


def category_articles(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
    )

    articles = (
        Article.objects
        .filter(
            category=category,
            is_published=True,
        )
        .select_related("category")
    )

    context = {
        "category": category,
        "articles": articles,
    }

    return render(
        request,
        "newspulsehqapp/category.html",
        context,
    )