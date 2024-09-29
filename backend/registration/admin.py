from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from .models import BaseUser, UserSubscription


class UserSubscriptionInline(admin.TabularInline):
    model = UserSubscription
    fk_name = 'user'


class BaseUserAdmin(UserAdmin):
    model = BaseUser
    list_display = (
        'username', 'email',
        'role'
    )
    search_fields = ('username', 'email')
    inlines = [UserSubscriptionInline]
    
    fieldsets = (
        ('Login details', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Avatar', {
            'fields': ('avatar',)
        }),
    )
    

admin.site.unregister(Group)
admin.site.register(BaseUser, BaseUserAdmin)
