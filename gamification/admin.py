"""
Calculus Bridge - Django Admin configuration for gamification models.
"""

from django.contrib import admin
from .models import Faculty, SkillNode, Question, Option, UserProfile, UserProgress


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'short_name')


@admin.register(SkillNode)
class SkillNodeAdmin(admin.ModelAdmin):
    list_display = ('stage_number', 'title', 'faculty', 'badge_label', 'order')
    list_filter = ('faculty', 'stage_number')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'subtitle')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('prompt_preview', 'node', 'faculty', 'difficulty', 'is_diagnostic', 'xp_reward')
    list_filter = ('is_diagnostic', 'difficulty', 'faculty', 'node')
    search_fields = ('prompt', 'explanation')
    inlines = [OptionInline]

    def prompt_preview(self, obj):
        return obj.prompt[:50]
    prompt_preview.short_description = "Pertanyaan"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty', 'xp', 'streak_days', 'hearts', 'diagnostic_completed')
    list_filter = ('faculty', 'diagnostic_completed')
    search_fields = ('user__username', 'user__email')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'node', 'status', 'score', 'completed_at')
    list_filter = ('status', 'node')
    search_fields = ('user__username', 'node__title')
