from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from .models import Bookmark, BookmarkFile, Category, BookmarkLink
from .forms import BookmarkForm, CategoryForm, SingleBookmarkForm, MultiBookmarkLinkForm
from .utils import process_bookmark


# Home Page View
def home(request):
    cats = Category.objects.filter(parent__isnull=True)
    rec = Bookmark.objects.order_by("-created_at")[:5]
    popular_bookmarks = Bookmark.objects.order_by("-view_count")[:5]  # Most viewed bookmarks
    return render(request, "bookmarks/home.html", {
        "categories": cats,
        "recent_bookmarks": rec,
        "popular_bookmarks": popular_bookmarks
    })


# Add Category View
def add_category(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category created!")
        return redirect("upload_bookmark")
    return render(request, "bookmarks/add_category.html", {"form": form})


# Upload Bookmark View (Bookmark with multiple files and links)
def upload_bookmark(request):
    form = BookmarkForm(request.POST or None)
    link_form = MultiBookmarkLinkForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and link_form.is_valid():
            # Save the bookmark
            bookmark = form.save()

            # Save the files
            files = request.FILES.getlist("files")
            for f in files:
                BookmarkFile.objects.create(bookmark=bookmark, file=f)

            # Save the URLs from the link form
            links = link_form.cleaned_data['links']
            if links:
                urls = links.strip().splitlines()
                for url in urls:
                    BookmarkLink.objects.create(bookmark=bookmark, url=url)

            # Process the bookmark (e.g., for embeddings, etc.)
            process_bookmark(bookmark)

            messages.success(request, "Bookmark saved with attachments and URLs.")
            return redirect("bookmark_detail", pk=bookmark.id)
        else:
            messages.error(request, "Please fix the errors in the form.")

    return render(request, "bookmarks/upload.html", {
        "form": form,
        "link_form": link_form,
    })


# Search View
def search(request):
    q = request.GET.get("q", "").strip()
    results = []

    if q:
        # Search across multiple fields (title, description, tags, URLs)
        results = Bookmark.objects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(tags__name__icontains=q) |
            Q(files__file__icontains=q) |
            Q(links__url__icontains=q)  # Search URLs in BookmarkLink model
        ).distinct()

    return render(request, "bookmarks/search.html", {
        "query": q,
        "results": results
    })


# Category Detail View (with descendants)
def category_detail(request, pk: int):
    cat = get_object_or_404(Category, pk=pk)
    
    # Recursive function to collect all descendant category ids
    def collect_category_ids(category):
        category_ids = [category.id]
        for child in category.children.all():
            category_ids.extend(collect_category_ids(child))
        return category_ids

    # Collect all categories under this one (including descendants)
    ids = collect_category_ids(cat)
    
    # Fetch bookmarks related to these categories
    bmarks = Bookmark.objects.filter(category_id__in=ids).order_by("-created_at")
    
    return render(request, "bookmarks/category_detail.html", {
        "category": cat,
        "bookmarks": bmarks
    })


# Bookmark Detail View
def bookmark_detail(request, pk: int):
    bookmark = get_object_or_404(Bookmark, pk=pk)

    # Increment the view count by 1
    bookmark.view_count += 1
    bookmark.save()

    # Create a shareable URL for this bookmark
    share_url = request.build_absolute_uri(bookmark.get_absolute_url())

    return render(request, "bookmarks/bookmark_detail.html", {
        "bookmark": bookmark,
        "share_url": share_url,  # Pass the shareable URL to the template
    })


# Bookmark Edit View (to update bookmark details)
def bookmark_edit(request, pk: int):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            bm = form.save()

            # Handle file deletions and additions
            delete_ids = request.POST.getlist("delete_files")
            if delete_ids:
                BookmarkFile.objects.filter(id__in=delete_ids, bookmark=bm).delete()

            for f in request.FILES.getlist("new_files"):
                BookmarkFile.objects.create(bookmark=bm, file=f)

            # Re-run processing (e.g., embeddings, tagging)
            process_bookmark(bm)

            messages.success(request, "Bookmark updated.")
            return redirect("bookmark_detail", pk=bm.id)
    else:
        form = BookmarkForm(instance=bookmark)

    return render(request, "bookmarks/bookmark_edit.html", {
        "form": form,
        "bookmark": bookmark
    })


# Delete Bookmark View
def delete_bookmark(request, pk: int):
    bm = get_object_or_404(Bookmark, pk=pk)
    if request.method == "POST":
        bm.delete()
        messages.success(request, "Bookmark deleted successfully.")
        return redirect('home')  # Redirect to homepage after deletion
    return render(request, "bookmarks/confirm_delete.html", {"bookmark": bm})


# Delete Category View (and its associated bookmarks)
def delete_category(request, pk: int):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.bookmark_set.all().delete()  # Delete associated bookmarks
        category.delete()
        messages.success(request, "Category and its bookmarks deleted successfully.")
        return redirect('home')  # Redirect to homepage after deletion

    return render(request, "bookmarks/confirm_delete_category.html", {"category": category})


# Statistics View (overview of total bookmarks and bookmarks per category)
def statistics(request):
    total_bookmarks = Bookmark.objects.count()  # Total number of bookmarks
    categories_count = Bookmark.objects.values('category').annotate(num_bookmarks=Count('category'))  # Count bookmarks per category

    context = {
        "total_bookmarks": total_bookmarks,
        "categories_count": categories_count,
    }

    return render(request, "bookmarks/statistics.html", context)
