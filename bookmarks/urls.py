from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/",  views.upload_bookmark, name="upload_bookmark"),
    path("search/",  views.search,          name="search"),
    path("category/add/",     views.add_category,    name="add_category"),
    path("category/<int:pk>/", views.category_detail, name="category_detail"),
    path("bookmark/<int:pk>/",         views.bookmark_detail, name="bookmark_detail"),
    path("bookmark/<int:pk>/edit/",    views.bookmark_edit,   name="bookmark_edit"),
    path('bookmark/<int:pk>/delete/', views.delete_bookmark, name='delete_bookmark'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('bookmark/<int:pk>/', views.bookmark_detail, name='bookmark_detail'),
    path('statistics/', views.statistics, name='statistics'),  # Add this line for statistics

    
]
