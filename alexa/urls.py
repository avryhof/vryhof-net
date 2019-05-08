from django.urls import path

from .my_skill import skill

from django_ask_sdk.skill_adapter import SkillAdapter

my_skill_view = SkillAdapter.as_view(skill=skill, verify_signature=False)

urlpatterns = [
    path('', my_skill_view, name='index'),
]
