"""
Calculus Bridge - Gamification Data Models.

Defines schemas for Faculties, Learning Tree Nodes, Question Bank,
User Gamification Profiles, and Skill Progress Records.
"""

import uuid
from datetime import timedelta

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


class SourceDocument(models.Model):
    """
    Satu berkas sumber materi (mis. "1_Materi_Umum_Kalkulus.pdf").

    Mechanism: setiap SkillNode, LessonSection, dan Question menunjuk ke berkas
    asalnya, sehingga konten bisa ditelusuri, difilter, dan diperbarui per berkas
    tanpa mencampur materi umum dengan materi khusus fakultas.
    """
    CATEGORY_CHOICES = [
        ('materi', 'Materi'),
        ('soal', 'Soal & Pembahasan'),
        ('lampiran', 'Lampiran'),
        ('buku', 'Buku Referensi'),
    ]

    slug = models.SlugField(max_length=80, unique=True, help_text="mis. 'materi-umum'")
    filename = models.CharField(max_length=150, help_text="Nama berkas asli, mis. '1_Materi_Umum_Kalkulus.pdf'")
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='materi')
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_documents",
        help_text="Kosongkan jika berkas berlaku untuk semua fakultas atau berisi beberapa fakultas"
    )
    order = models.PositiveIntegerField(default=1, help_text="Urutan berkas (nomor di depan nama file)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.filename


class MainLevel(models.Model):
    """
    Level utama kurikulum (PreCalculus, Kalkulus Dasar, Menengah, Lanjut).

    Mechanism: level utama hanya berupa judul pengelompokan di skill tree.
    Isi belajarnya ada di SkillNode (sub-level) yang menunjuk ke level ini.
    """
    slug = models.SlugField(max_length=60, unique=True)
    order = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=10, default="🏔️")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class SkillNode(models.Model):
    """
    Represents an individual node along the Duolingo-style Skill Tree roadmap.
    Nodes can be faculty-specific or universal.
    """
    main_level = models.ForeignKey(
        MainLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sublevels",
        help_text="Level utama tempat sub-level ini berada",
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skill_nodes",
        help_text="Associated faculty; leave blank for universal core stages"
    )
    source_document = models.ForeignKey(
        SourceDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skill_nodes",
        help_text="Berkas materi yang menjadi sumber node ini"
    )
    stage_number = models.PositiveIntegerField(help_text="Stage sequence number (1, 2, 3...)")
    title = models.CharField(max_length=200, help_text="e.g., 'Tahap 1: Precalculus Bridge'")
    slug = models.SlugField(max_length=100, unique=True)
    badge_label = models.CharField(max_length=80, default="Materi Inti", help_text="e.g., 'Fondasi Aljabar'")
    subtitle = models.CharField(max_length=255, help_text="Short subtitle explanation")
    KIND_CHOICES = [
        ('lesson', 'Node skill tree (materi + kuis)'),
        ('reference', 'Bacaan referensi (hanya di halaman Lesson)'),
    ]
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='lesson')
    icon = models.CharField(max_length=10, default="📘", help_text="Emoji ikon node")
    is_boss = models.BooleanField(default=False, help_text="Node ujian akhir (soal tingkat sulit)")
    summary_html = models.TextField(blank=True, help_text="Ringkasan singkat isi node (ditampilkan di katalog)")
    
    # Video & Resource integration
    video_title = models.CharField(max_length=200, blank=True, help_text="Title of integrated video module")
    video_url = models.CharField(max_length=300, blank=True, help_text="Video embed or stream URL")
    video_duration = models.CharField(max_length=50, blank=True, default="10:00")
    order = models.PositiveIntegerField(default=1, help_text="Display order in the tree")

    class Meta:
        ordering = ['order', 'stage_number']

    def __str__(self):
        return f"Stage {self.stage_number}: {self.title}"


class Topic(models.Model):
    """
    Sub-topik di dalam sub-level (mis. "Pertidaksamaan" di "Sistem Bilangan dan Fungsi").

    Mechanism: setiap topik punya materi sendiri (LessonSection.topic) dan
    5 sesi latihan berlapis (PracticeSession). Sub-level dianggap tuntas bila
    semua topiknya lulus sesi wajib (lihat sessions.REQUIRED_SESSIONS).
    """
    node = models.ForeignKey(SkillNode, on_delete=models.CASCADE, related_name="topics")
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=10, default="📗")
    summary = models.CharField(max_length=300, blank=True)
    references = models.CharField(max_length=300, blank=True,
                                  help_text="Rujukan bab buku, mis. 'Stewart Lamp. A; Whitman 1.1'")

    class Meta:
        ordering = ['node', 'order']

    def __str__(self):
        return f"{self.node.slug} › {self.title}"


class PracticeSession(models.Model):
    """
    Satu sesi latihan berlapis dalam sebuah topik (Sesi I Mudah … Sesi V Olimpiade).

    Mechanism: soal sesi TIDAK disimpan satu per satu. Sesi menyimpan kumpulan
    QuestionTemplate (generator berparameter) dan boleh juga soal tetap
    (Question.session). Saat user memulai sesi, server mengundi `question_count`
    soal dari kumpulan itu memakai seed (user, sesi, percobaan) sehingga setiap
    user mendapat angka berbeda, tetapi penilaian tetap bisa diulang di server.
    """
    TIER_CHOICES = [
        ('mudah', 'Mudah'),
        ('sedang', 'Sedang'),
        ('sulit', 'Sulit'),
        ('tantangan', 'Tantangan'),
        ('olimpiade', 'Olimpiade'),
    ]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="sessions")
    number = models.PositiveSmallIntegerField(help_text="1–5")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    title = models.CharField(max_length=120)
    question_count = models.PositiveSmallIntegerField(default=10)
    pass_ratio = models.FloatField(default=0.7)
    xp_per_question = models.PositiveSmallIntegerField(default=10)

    class Meta:
        ordering = ['topic', 'number']
        constraints = [
            models.UniqueConstraint(fields=['topic', 'number'], name='unique_session_number_per_topic')
        ]

    def __str__(self):
        return f"{self.topic.slug} · Sesi {self.number} ({self.tier})"


class LessonSection(models.Model):
    """
    Satu bagian materi di dalam SkillNode (mis. "Tabel turunan dasar").

    Mechanism: materi sebuah node dipecah menjadi beberapa bagian berurutan.
    Setiap bagian berisi HTML dan daftar grafik interaktif (`graphs`) yang
    dirender oleh static/js/graphlab.js dengan slider parameter.
    """
    node = models.ForeignKey(SkillNode, on_delete=models.CASCADE, related_name="sections",
                             null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="sections",
                              null=True, blank=True, help_text="Diisi bila bagian ini materi sebuah topik")
    source_document = models.ForeignKey(
        SourceDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sections",
    )
    order = models.PositiveIntegerField(default=1)
    heading = models.CharField(max_length=200)
    body_html = models.TextField(blank=True, help_text="Isi materi dalam HTML")
    graphs = models.JSONField(default=list, blank=True, help_text="Daftar spec grafik interaktif (lihat gamification/content/README.md)")

    class Meta:
        ordering = ['node', 'order']
        constraints = [
            models.UniqueConstraint(fields=['node', 'order'], name='unique_section_order_per_node'),
            models.UniqueConstraint(fields=['topic', 'order'], name='unique_section_order_per_topic'),
            models.CheckConstraint(
                condition=(models.Q(node__isnull=False, topic__isnull=True)
                           | models.Q(node__isnull=True, topic__isnull=False)),
                name='section_belongs_to_node_xor_topic',
            ),
        ]

    def __str__(self):
        owner = self.topic.slug if self.topic_id else self.node.slug
        return f"{owner} #{self.order}: {self.heading}"


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

    code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text="Kode soal sesuai berkas sumber, mis. 'U-D1', 'FT-S2', 'FK-H3'"
    )
    source_document = models.ForeignKey(
        SourceDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        help_text="Berkas soal asal"
    )
    node = models.ForeignKey(
        SkillNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="questions",
        help_text="Skill node this question belongs to; null for standalone diagnostic questions"
    )
    session = models.ForeignKey(
        PracticeSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fixed_questions",
        help_text="Soal tetap yang ikut diundi dalam kumpulan soal sebuah sesi latihan",
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
    prompt = models.TextField(help_text="Teks soal (boleh HTML)")
    steps = models.JSONField(default=list, blank=True, help_text="Langkah pembahasan berurutan (list string HTML)")
    answer = models.TextField(blank=True, help_text="Jawaban akhir sesuai berkas sumber")
    explanation = models.TextField(blank=True, help_text="Ringkasan konsep / catatan tambahan untuk umpan balik")
    graphs = models.JSONField(default=list, blank=True, help_text="Grafik interaktif untuk pembahasan (spec GraphLab)")
    order = models.PositiveIntegerField(default=0, help_text="Urutan soal di dalam node")
    xp_reward = models.PositiveIntegerField(default=20, help_text="XP earned when answered correctly")

    class Meta:
        ordering = ['node', 'order', 'id']

    def __str__(self):
        if self.code:
            return f"{self.code} ({self.get_difficulty_display()})"
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
    hearts = models.PositiveIntegerField(default=10, help_text="Nyawa tersisa (maks. max_hearts)")
    max_hearts = models.PositiveIntegerField(default=10)
    hearts_lost_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Waktu nyawa pertama hilang pada siklus ini; nyawa penuh lagi 24 jam setelahnya",
    )
    gems = models.PositiveIntegerField(default=0, help_text="Diamond 💎: didapat saat naik level, topik tuntas, menang duel (shop.py)")
    star_shields = models.PositiveIntegerField(default=0, help_text="Perisai Bintang: otomatis menahan bintang saat kalah duel")
    equipped = models.JSONField(default=dict, blank=True,
                                help_text="Kosmetik terpasang per slot: head/face/neck/frame/title → kunci barang toko")
    campus = models.CharField(
        max_length=120, blank=True, default="",
        help_text="Asal kampus untuk papan peringkat per kampus; 'Umum' = bukan mahasiswa / tidak disebutkan; kosong = belum diisi",
    )
    
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

    # ── Sistem nyawa ────────────────────────────────────────────────────────
    HEART_REFILL = timedelta(hours=24)

    @property
    def hearts_refill_at(self):
        """Waktu nyawa kembali penuh, atau None bila nyawa sedang penuh."""
        return self.hearts_lost_at + self.HEART_REFILL if self.hearts_lost_at else None

    def refresh_hearts(self, now=None):
        """
        Isi ulang nyawa bila sudah 24 jam sejak nyawa pertama hilang.

        Mechanism: tidak ada tugas terjadwal. Setiap kali nyawa dibaca (buka sesi,
        kirim jawaban, muat beranda), fungsi ini dipanggil dulu; bila waktunya sudah
        lewat, nyawa kembali ke max_hearts dan siklus baru dimulai saat nyawa hilang lagi.
        """
        now = now or timezone.now()
        if self.hearts_lost_at and now >= self.hearts_refill_at:
            self.hearts, self.hearts_lost_at = self.max_hearts, None
            self.save(update_fields=["hearts", "hearts_lost_at"])
        return self.hearts

    def lose_heart(self, now=None):
        """Kurangi satu nyawa (dipakai saat gagal lulus sesi). Nyawa pertama yang hilang memulai hitungan 24 jam."""
        now = now or timezone.now()
        self.refresh_hearts(now)
        if self.hearts > 0:
            self.hearts -= 1
            self.hearts_lost_at = self.hearts_lost_at or now
            self.save(update_fields=["hearts", "hearts_lost_at"])
        return self.hearts

    def deduct_heart(self):
        """Alias lama untuk lose_heart()."""
        return self.lose_heart()

    def hearts_state(self, now=None):
        """Status nyawa untuk frontend: jumlah, maksimum, dan kapan penuh lagi."""
        now = now or timezone.now()
        self.refresh_hearts(now)
        refill = self.hearts_refill_at
        return {
            "hearts": self.hearts,
            "max_hearts": self.max_hearts,
            "refill_at": refill.isoformat() if refill else None,
            "refill_in": max(0, int((refill - now).total_seconds())) if refill else 0,
        }

    CAMPUS_UMUM = "Umum"

    def add_xp(self, amount):
        """Menambah XP (level dihitung dari XP, lihat leveling.py)."""
        self.xp += amount
        self.save(update_fields=['xp'])

    @property
    def level_info(self):
        from .leveling import level_info
        return level_info(self.xp)



class OwnedItem(models.Model):
    """Barang kosmetik toko (aksesori Archie, bingkai, gelar) yang sudah dibeli; katalog di shop.py."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_items")
    item = models.CharField(max_length=40)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "item"], name="unique_owned_item")]

    def __str__(self):
        return f"{self.user} · {self.item}"


class PlayerRank(models.Model):
    """
    Rank duel seorang pemain (aturan di ranking.py).

    Dibuat saat pertama dibutuhkan (rank_of); pemain tanpa baris ini dianggap Terra III 0★.
    `points` = posisi di tangga (ranking.ladder_points), disimpan agar papan peringkat bisa
    diurutkan di database; `mmr` = nilai kemampuan tersembunyi untuk mencari lawan setara.
    """
    TIER_CHOICES = [(t, t.title()) for t in ("terra", "luna", "solar", "nova", "apex")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="duel_rank")
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default="terra")
    division = models.PositiveSmallIntegerField(null=True, blank=True, default=3, help_text="3=III, 2=II, 1=I; kosong untuk Apex")
    stars = models.PositiveIntegerField(default=0)
    win_streak = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0, db_index=True)
    mmr = models.IntegerField(default=1000)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        from .ranking import label
        return f"{self.user.username}: {label(self.state)} {self.stars}★"

    @property
    def state(self):
        from .ranking import RankState
        return RankState(self.tier, self.division, self.stars, self.win_streak)

    def set_state(self, st):
        from .ranking import ladder_points
        self.tier, self.division, self.stars, self.win_streak = st.tier, st.division, st.stars, st.win_streak
        self.points = ladder_points(st)

    def record_draw(self, opponent_mmr):
        """Duel seri: bintang tetap, nilai kemampuan dihitung sebagai setengah menang."""
        from .ranking import elo_update
        self.mmr = elo_update(self.mmr, opponent_mmr, 0.5)
        self.save()

    def record_duel(self, won, opponent_mmr, protected=False):
        """Terapkan hasil satu duel: bintang (aturan ML) + nilai kemampuan (Elo). Mengembalikan perubahan bintang."""
        from .ranking import apply_result, elo_update
        st, delta = apply_result(self.state, won, protected)
        self.set_state(st)
        self.mmr = elo_update(self.mmr, opponent_mmr, 1 if won else 0)
        if won:
            self.wins += 1
        else:
            self.losses += 1
        self.save()
        return delta


def rank_of(user):
    """Rank duel pemain (dibuat Terra III 0★ bila belum ada)."""
    return PlayerRank.objects.get_or_create(user=user)[0]


class DuelQueue(models.Model):
    """Pemain yang sedang mencari lawan duel (satu baris per pemain; lihat duel.find_opponent)."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="duel_queue")
    channel_name = models.CharField(max_length=200, help_text="Kanal WebSocket pemain (untuk memberi tahu saat lawan ditemukan)")
    mmr = models.IntegerField()
    joined_at = models.DateTimeField(default=timezone.now)


class DuelMatch(models.Model):
    """
    Satu duel kalkulus real-time (aturan di duel.py).

    Soal disimpan sebagai resep generator (key, seed, tier) sehingga kedua pemain mendapat soal
    identik dan kunci jawaban hanya pernah dihitung di server.
    `current` = indeks soal yang sedang berjalan; `q_started_at` kosong saat jeda antarsoal.
    """
    ACTIVE, FINISHED = "active", "finished"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="duels_as_a")
    player_b = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="duels_as_b")
    tier = models.CharField(max_length=10, help_text="Tier yang menentukan tingkat kesulitan soal")
    questions = models.JSONField(default=list)
    time_limit = models.PositiveIntegerField(help_text="Detik per soal")
    current = models.PositiveSmallIntegerField(default=0)
    q_started_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default=ACTIVE)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="duels_won")
    result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Duel {self.player_a} vs {self.player_b} ({self.status})"

    def players(self):
        return [self.player_a_id, self.player_b_id]

    def opponent_of(self, user_id):
        return self.player_b_id if user_id == self.player_a_id else self.player_a_id


class DuelAnswer(models.Model):
    """Jawaban satu pemain untuk satu soal duel (tidak menjawab = baris dengan option_id kosong)."""
    match = models.ForeignKey(DuelMatch, on_delete=models.CASCADE, related_name="answers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField()
    option_id = models.IntegerField(null=True, blank=True)
    correct = models.BooleanField(default=False)
    ms = models.PositiveIntegerField(help_text="Waktu menjawab (milidetik) sejak soal tampil")
    points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("match", "user", "index")]

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


class QuestionTemplate(models.Model):
    """
    Penghubung sesi latihan dengan generator soal berparameter.

    Mechanism: `key` adalah nama generator di gamification/generators (registry).
    Generator menerima rng + nomor sesi dan menghasilkan soal lengkap (prompt,
    opsi, langkah pembahasan, grafik slider). `weight` menentukan peluang
    generator ini terpilih saat soal sesi diundi.
    """
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name="templates")
    key = models.CharField(max_length=80)
    weight = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['session', 'id']
        constraints = [
            models.UniqueConstraint(fields=['session', 'key'], name='unique_template_key_per_session')
        ]

    def __str__(self):
        return f"{self.session} ← {self.key}"


class UserSessionProgress(models.Model):
    """
    Progres user pada satu sesi latihan.

    Mechanism: `attempts` ikut menentukan seed soal, jadi setiap percobaan ulang
    memberi angka baru. Sesi berikutnya terbuka bila `passed` = True.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="session_progress")
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name="user_progress")
    attempts = models.PositiveIntegerField(default=0)
    last_score = models.PositiveSmallIntegerField(default=0)
    best_score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    passed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'session'], name='unique_user_session_progress')
        ]

    def __str__(self):
        return f"{self.user.username} · {self.session} · {self.best_score}"
