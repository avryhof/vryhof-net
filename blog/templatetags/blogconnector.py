"""
@copyright Amos Vryhof

"""

from django import template
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe

from blog.models import BlogPost, BlogCategory

register = template.Library()


@register.filter
def paragraphs(html_code, number_of_paragraphs):
    all_paragraphs = html_code.replace('<p>', '').split('</p>')

    paragraphs = []
    for paragraph in all_paragraphs:
        if paragraph.strip() != '':
            paragraphs.append(paragraph)

    return '<p>%s</p>' % '</p><p>'.join(paragraphs[0:number_of_paragraphs])


@register.simple_tag
def posts(category=None):
    if category:
        blog_posts = BlogPost.objects.filter(category__slug=category, enabled=True).order_by('-pub_date')
    else:
        blog_posts = BlogPost.objects.filter(enabled=True).order_by('-pub_date')

    posts_list = []

    for post in blog_posts:
        context = dict(post=post)
        tpl = get_template('blog/post.html')
        rendered_template = tpl.render(context)
        post_link = reverse('blog_post', kwargs=dict(post_slug=post.slug))
        rendered_template_str = str(rendered_template).replace('[…]', '<a href="%s">[…]</a>' % post_link)
        posts_list.append(rendered_template_str)

    posts_html = '\n'.join(posts_list)

    return mark_safe(posts_html)


@register.simple_tag
def categories():
    blog_categories = BlogCategory.objects.filter(enabled=True)

    category_list = []

    for category in blog_categories:
        context = dict(category=category)
        tpl = get_template('blog/category_link.html')
        category_list.append(tpl.render(context))

    categories_html = '\n'.join(category_list)

    return mark_safe(categories_html)
