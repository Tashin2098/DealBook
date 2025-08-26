from django.contrib import admin

# Register your models here.
from .models import StartupProfile

@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'startup_name', 'is_approved', 'submitted_at')
    search_fields = ('startup_name', 'user__email', 'user__username')
    list_filter = ('is_approved',)