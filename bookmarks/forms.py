from django import forms
from .models import Bookmark, BookmarkLink, Category

# This form is for creating a bookmark without URLs
class BookmarkForm(forms.ModelForm):
    class Meta:
        model = Bookmark
        fields = ["title", "description", "category"]  # No 'url' field here

# This form is for creating a single BookmarkLink (URLs)
class BookmarkLinkForm(forms.ModelForm):
    class Meta:
        model = BookmarkLink
        fields = ["url"]

# This form allows for multiple URLs
class MultiBookmarkLinkForm(forms.Form):
    links = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False, help_text="Add one URL per line.")

# This form is for creating a Category
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "parent"]

# This form is a simplified form for creating a bookmark (Title, Description, Category only)
class SingleBookmarkForm(forms.ModelForm):
    """Title/desc/category only – files handled in the view."""
    class Meta:
        model = Bookmark
        fields = ["title", "description", "category"]  # Only the relevant fields for a simple bookmark
