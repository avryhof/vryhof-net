from django.contrib import admin

from .models import BlogCategory, BlogUser, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name",)


@admin.register(BlogUser)
class BlogUserAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "pub_date", "enabled")
    list_filter = ("enabled", "creator", "category")
    search_fields = ("title", "description", "content", "creator", "category")
