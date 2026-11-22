"""
Isi akun super (superuser) dengan semua poin dan materi terbuka.

Usage:
    python manage.py isi_akun_super                 # semua superuser
    python manage.py isi_akun_super --username admin

Mechanism: akun super dipakai untuk mengecek aplikasi, bukan bermain. Perintah ini
  * mengisi XP sampai Level SUPER_LEVEL, diamond SUPER_GEMS, heart penuh, Streak Shield maksimal;
  * memberi semua barang kosmetik toko;
  * menandai semua node skill tree selesai dan semua sesi latihan lulus (semua materi terbuka).
Bagian lain yang membedakan akun super ada di kode: heart tidak pernah berkurang
(UserProfile.lose_heart) dan tidak masuk papan peringkat (views.leaderboard_api).
Aman dijalankan berulang; jalankan lagi setelah kurikulum mendapat topik/sesi baru.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from gamification import shop
from gamification.leveling import total_xp_for
from gamification.models import (
    OwnedItem, PracticeSession, SkillNode, UserProfile, UserProgress, UserSessionProgress,
)

SUPER_LEVEL = 50
SUPER_GEMS = 99999


class Command(BaseCommand):
    help = "Isi akun super (superuser): XP Level 50, diamond, semua item toko, semua materi terbuka."

    def add_arguments(self, parser):
        parser.add_argument("--username", help="Hanya superuser ini (bawaan: semua superuser)")

    def handle(self, *args, **opts):
        users = get_user_model().objects.filter(is_superuser=True)
        if opts["username"]:
            users = users.filter(username=opts["username"])
        if not users.exists():
            raise CommandError("Tidak ada superuser yang cocok. Buat dulu dengan: python manage.py createsuperuser")
        for user in users:
            self.fill(user)
            self.stdout.write(self.style.SUCCESS(f"{user.username}: akun super terisi"))

    @transaction.atomic
    def fill(self, user):
        now = timezone.now()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.xp = max(profile.xp, total_xp_for(SUPER_LEVEL))
        profile.gems = max(profile.gems, SUPER_GEMS)
        profile.hearts, profile.hearts_lost_at = profile.max_hearts, None
        profile.star_shields = shop.MAX_SHIELDS
        profile.save(update_fields=["xp", "gems", "hearts", "hearts_lost_at", "star_shields"])

        cosmetics = [i["key"] for i in shop.CATALOG if i["kind"] == "cosmetic"]
        OwnedItem.objects.bulk_create([OwnedItem(user=user, item=k) for k in cosmetics], ignore_conflicts=True)

        for node in SkillNode.objects.all():
            UserProgress.objects.update_or_create(
                user=user, node=node, defaults={"status": "completed", "score": 100, "completed_at": now})
        for session in PracticeSession.objects.all():
            UserSessionProgress.objects.update_or_create(
                user=user, session=session,
                defaults={"passed": True, "passed_at": now, "best_score": 100, "last_score": 100})
