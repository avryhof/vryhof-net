from django.contrib import admin

from accounts.models import EmailDomain, AuthSession, UserPrefs


@admin.register(EmailDomain)
class EmailDomainAdmin(admin.ModelAdmin):
    list_display = ["domain", "site", "enabled"]
    list_editable = ["enabled"]


@admin.register(AuthSession)
class AuthSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "is_authenticated", "token", "expires_at"]


@admin.register(UserPrefs)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "email"]
