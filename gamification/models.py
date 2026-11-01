"""
Calculus Bridge - Gamification Data Models.

Defines schemas for Faculties, Learning Tree Nodes, Question Bank,
User Gamification Profiles, and Skill Progress Records.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Faculty(models.Model):
    """
    Represents university faculties (FT, Fasilkom, FMIPA).
    Each faculty customizes the student's learning path and contextual questions.
    """
    slug = models.SlugField(max_length=50, unique=True, help_text="Unique identifier, e.g., 'ft', 'fasilkom', 'fmipa'")
    name = models.CharField(max_length=150, help_text="Full faculty name, e.g., 'Fakultas Ilmu Komputer'")
    short_name = models.CharField(max_length=50, help_text="Abbreviation, e.g., 'Fasilkom'")
    icon = models.CharField(max_length=10, default="🎓", help_text="Emoji or icon identifier")
    description = models.TextField(help_text="Overview of calculus applications for this faculty")
    focus_areas = models.TextField(help_text="Bullet points or summary of curricular focus")

    class Meta:
        verbose_name_plural = "Faculties"
        ordering = ['name']

    def __str__(self):
        return f"{self.short_name} - {self.name}"


class SkillNode(models.Model):
    """
    Represents an individual node along the Duolingo-style Skill Tree roadmap.
    Nodes can be faculty-specific or universal.
    """
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skill_nodes",
        help_text="Associated faculty; leave blank for universal core stages"
    )
    stage_number = models.PositiveIntegerField(help_text="Stage sequence number (1, 2, 3...)")
    title = models.CharField(max_length=200, help_text="e.g., 'Tahap 1: Precalculus Bridge'")
    slug = models.SlugField(max_length=100, unique=True)
    badge_label = models.CharField(max_length=80, default="Materi Inti", help_text="e.g., 'Fondasi Aljabar'")
    subtitle = models.CharField(max_length=255, help_text="Short subtitle explanation")
    summary_html = models.TextField(help_text="Rich HTML summary of lesson concepts and formulas")
    
    # Video & Resource integration
    video_title = models.CharField(max_length=200, blank=True, help_text="Title of integrated video module")
    video_url = models.CharField(max_length=300, blank=True, help_text="Video embed or stream URL")
    video_duration = models.CharField(max_length=50, blank=True, default="10:00")
    order = models.PositiveIntegerField(default=1, help_text="Display order in the tree")

    class Meta:
        ordering = ['order', 'stage_number']

    def __str__(self):
        return f"Stage {self.stage_number}: {self.title}"


class Question(models.Model):
    """
    Bank of questions used for Diagnostic Evaluation or Level Quizzes.
    Supports LaTeX/Markdown prompts and step-by-step explanations.
    """
    DIFFICULTY_CHOICES = [
        ('basic', 'Dasar (Basic)'),
        ('medium', 'Menengah (Medium)'),
        ('high', 'Tinggi (High)'),
    ]

    node = models.ForeignKey(
        SkillNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="questions",
        help_text="Skill node this question belongs to; null for standalone diagnostic questions"
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_questions",
        help_text="Faculty customization if applicable"
    )
    is_diagnostic = models.BooleanField(
        default=False,
        help_text="Flag indicating whether this question appears in the initial adaptive diagnostic test"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='basic',
        help_text="Difficulty bracket used for adaptive decision logic"
    )
    prompt = models.TextField(help_text="Question prompt text with math equations")
    explanation = models.TextField(help_text="Detailed step-by-step mathematical reasoning shown on immediate feedback")
    xp_reward = models.PositiveIntegerField(default=20, help_text="XP earned when answered correctly")

    class Meta:
        ordering = ['node', 'difficulty', 'id']

    def __str__(self):
        diag_prefix = "[Diagnostic] " if self.is_diagnostic else ""
        return f"{diag_prefix}({self.get_difficulty_display()}) {self.prompt[:60]}..."


class Option(models.Model):
    """
    Multiple choice options for a Question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=500, help_text="Option label/content")
    is_correct = models.BooleanField(default=False, help_text="True if this is the correct answer")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        mark = "✓" if self.is_correct else "✗"
        return f"{mark} {self.text[:50]}"


class UserProfile(models.Model):
    """
    Gamification profile linked 1-to-1 with Django's User model.
    Tracks XP, streak, hearts (lives), selected faculty, and diagnostic results.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gamification_profile"
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrolled_users"
    )
    xp = models.PositiveIntegerField(default=0, help_text="Total earned Experience Points")
    streak_days = models.PositiveIntegerField(default=1, help_text="Consecutive days of active practice")
    hearts = models.PositiveIntegerField(default=5, help_text="Current hearts/lives remaining (max 5)")
    max_hearts = models.PositiveIntegerField(default=5)
    gems = models.PositiveIntegerField(default=100, help_text="Collectible gems currency")
    
    # Diagnostic status
    diagnostic_completed = models.BooleanField(default=False)
    diagnostic_level = models.CharField(max_length=50, blank=True, default="Belum Dievaluasi")
    recommended_node = models.ForeignKey(
        SkillNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended_to_users"
    )
    
    sound_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        fac_name = self.faculty.short_name if self.faculty else "General"
        return f"{self.user.username} ({fac_name}) - {self.xp} XP"

    def deduct_heart(self):
        """Deducts one life when an error is made."""
        if self.hearts > 0:
            self.hearts -= 1
            self.save(update_fields=['hearts'])

    def add_xp(self, amount):
        """Awards XP to user and updates level."""
        self.xp += amount
        self.save(update_fields=['xp'])


class UserProgress(models.Model):
    """
    Tracks a user's completion status and score on an individual SkillNode.
    Links the skill tree node directly with user state via Foreign Keys.
    """
    STATUS_CHOICES = [
        ('locked', 'Terkunci'),
        ('active', 'Sedang Aktif'),
        ('completed', 'Selesai'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_records"
    )
    node = models.ForeignKey(
        SkillNode,
        on_delete=models.CASCADE,
        related_name="user_progress_records"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')
    score = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'node'], name='unique_user_node_progress')
        ]
        verbose_name_plural = "User Progress Records"

    def __str__(self):
        return f"{self.user.username} -> {self.node.title} [{self.get_status_display()}]"

    def mark_completed(self, earned_score=100):
        """Marks the skill node as completed and records timestamp."""
        self.status = 'completed'
        self.score = earned_score
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'score', 'completed_at', 'updated_at'])
