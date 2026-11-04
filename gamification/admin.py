"""
Calculus Bridge - Django Admin configuration for gamification models.
"""

from django.contrib import admin
from .models import (
    Faculty, SourceDocument, SkillNode, LessonSection, Question, Option, UserProfile, UserProgress,
)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


class LessonSectionInline(admin.StackedInline):
    model = LessonSection
    extra = 0
    fields = ('order', 'heading', 'body_html', 'graphs')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'short_name')


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('order', 'filename', 'title', 'category', 'faculty')
    list_filter = ('category', 'faculty')
    ordering = ('order',)


@admin.register(SkillNode)
class SkillNodeAdmin(admin.ModelAdmin):
    list_display = ('stage_number', 'title', 'faculty', 'kind', 'source_document', 'order')
    list_filter = ('faculty', 'kind', 'source_document')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'subtitle')
    inlines = [LessonSectionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('code', 'prompt_preview', 'node', 'faculty', 'difficulty', 'is_diagnostic', 'source_document')
    list_filter = ('source_document', 'faculty', 'difficulty', 'is_diagnostic', 'node')
    search_fields = ('code', 'prompt', 'answer')
    inlines = [OptionInline]

    @admin.display(description="Pertanyaan")
    def prompt_preview(self, obj):
        return obj.prompt[:60]


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
