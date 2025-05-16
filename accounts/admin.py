from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FreelancerProfile, ClientProfile

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('User Type & Status', {'fields': ('user_type',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('username',)

class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability_status', 'skills', 'hourly_rate')
    list_filter = ('availability_status',)
    search_fields = ('user__username', 'skills')

class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'hiring_status',)
    list_filter = ('hiring_status',)
    search_fields = ('user__username',)

# Register models
admin.site.register(User, UserAdmin)
admin.site.register(FreelancerProfile, FreelancerProfileAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
