import uuid

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db.models import Model, BooleanField, CharField, SlugField, ForeignKey, DO_NOTHING, DateTimeField, UUIDField
from django.utils.text import slugify


class BlogCategory(Model):
    enabled = BooleanField(default=True)
    name = CharField(max_length=200, blank=True, null=True)
    slug = SlugField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name if self.name else "Blog Category"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(BlogCategory, self).save(*args, **kwargs)


class BlogUser(Model):
    enabled = BooleanField(default=True)
    name = CharField(max_length=100, blank=True, null=True)
    user = ForeignKey(get_user_model(), blank=True, null=True, on_delete=DO_NOTHING)
    bio = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = "Blog User"
        verbose_name_plural = "Blog Users"

    def __str__(self):
        return self.name if self.name else "Blog User"


class BlogPost(Model):
    guid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enabled = BooleanField(default=True)
    title = CharField(max_length=200, blank=True, null=True)
    slug = SlugField(max_length=200, blank=True, null=True)
    pub_date = DateTimeField(blank=True, null=True)
    creator = ForeignKey(BlogUser, blank=True, null=True, on_delete=DO_NOTHING)
    category = ForeignKey(BlogCategory, blank=True, null=True, on_delete=DO_NOTHING)
    description = RichTextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    guid_is_permalink = BooleanField(default=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title if self.title else "Blog Post"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super(BlogPost, self).save(*args, **kwargs)
