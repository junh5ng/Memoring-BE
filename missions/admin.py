from django.contrib import admin

# Register your models here.
from .models import Mission, UserMission

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('id','content','is_active','created_at')
    list_filter = ('is_active',)
    search_fields = ('content',)

@admin.register(UserMission)
class UserMissionAdmin(admin.ModelAdmin):
    list_display = ('id','user','mission','completed','given_up','scheduled_at','created_at')
    list_filter = ('completed','given_up','mood')
    search_fields = ('user__username','mission__content','memo')