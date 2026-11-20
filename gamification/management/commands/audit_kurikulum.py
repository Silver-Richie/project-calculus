"""
python manage.py audit_kurikulum — cakupan kurikulum v2 (content/syllabus_v2.py) terhadap database.

Per topik target: status (ADA = slug sudah ada, UPGRADE = digabung dari topik lama, BARU),
jumlah slide eksplisit (LessonSlide) vs target, dan jumlah bagian materi yang masih memuat
rumus sebagai teks biasa (pangkat <sup>, ^, √, ∫, θ … tanpa LaTeX $…$).
"""

import re

from django.core.management.base import BaseCommand

from gamification.content import syllabus_v2
from gamification.models import Topic

RAW_MATH = re.compile(r"<sup>|<sub>|\^|√|∫|∑|∂|θ|²|³")


class Command(BaseCommand):
    help = "Audit cakupan kurikulum v2 (silabus target vs topik & slide yang ada)."

    def handle(self, *args, **opts):
        topics = {t.slug: t for t in Topic.objects.prefetch_related("slides", "sections")}
        rows, counts = [], {"ADA": 0, "UPGRADE": 0, "BARU": 0}
        for group, t in syllabus_v2.all_topics():
            have = [s for s in t["covers"] if s in topics]
            status = "ADA" if t["slug"] in topics and t["covers"] == [t["slug"]] else "UPGRADE" if have else "BARU"
            counts[status] += 1
            # Level 4 berjalur fakultas: bila slug target tidak ada, hitung slide di salinan/topik yang digabung.
            where = [t["slug"]] if t["slug"] in topics else [*t.get("slides_on", []), *have]
            slides = max((topics[s].slides.count() for s in where if s in topics), default=0)
            raw = sum(1 for s in have for sec in topics[s].sections.all() if RAW_MATH.search(sec.body_html) and "$" not in sec.body_html)
            rows.append((group, t["track"], t["slug"], t["title"], status, slides, f"{t['slides'][0]}–{t['slides'][1]}", raw))

        w = max(len(r[3]) for r in rows)
        self.stdout.write(f"{'LEVEL/JALUR':18} {'TOPIK':{w}}  STATUS   SLIDE  TARGET  RUMUS-TEKS")
        for g, _tr, _slug, title, status, slides, target, raw in rows:
            self.stdout.write(f"{g:18} {title:{w}}  {status:7}  {slides:5}  {target:6}  {raw}")
        self.stdout.write("")
        self.stdout.write(f"Total {len(rows)} topik: {counts['ADA']} sudah ada, {counts['UPGRADE']} digabung/di-upgrade, "
                          f"{counts['BARU']} baru. Slide eksplisit: {sum(r[5] for r in rows)}. "
                          f"Bagian materi berumus teks biasa: {sum(r[7] for r in rows)}.")
