"""
Calculus Bridge - WebSocket duel kalkulus real-time (ws/duel/). Aturan & penyimpanan ada di duel.py.

Pesan dari browser : {"type": "queue"} · {"type": "cancel"} · {"type": "answer", "index": n, "option": id}
                     · {"type": "left"} (keluar tab/jendela, anti-curang)
Pesan ke browser   : queued · no_opponent · matched (you, opponent, tier, time_limit) · question (tanpa kunci)
                     · answered · progress (lawan sudah menjawab) · reveal (kunci + poin kedua pemain)
                     · tab_warning (keluar tab pertama: soal berjalan dianggap salah)
                     · finished (hasil, perubahan bintang, rank baru) · error

Mekanisme
* Dua pemain yang dipertemukan bergabung ke grup "duel_<id>"; semua pesan soal disiarkan ke grup.
* Soal ditutup saat kedua pemain menjawab, atau oleh pengatur waktu tiap consumer saat waktu habis.
  Penutupan & pembukaan soal di duel.py bersifat sekali-saja (atomik), jadi aman bila kedua consumer
  mencoba bersamaan: hanya satu yang berhasil lalu menyiarkan kelanjutannya.
* Pemain yang baru bergabung ke grup mengejar keadaan (catch_up) agar tidak melewatkan soal pertama.
* Menutup halaman / koneksi putus di tengah duel = keluar (forfeit) = kalah.
* Keluar tab: pertama = peringatan + soal berjalan dianggap salah; kedua = forfeit (duel.leave_tab).
"""

import asyncio

from channels.db import database_sync_to_async as db
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import duel
from .models import DuelMatch

POLL_SECONDS = 3       # jeda mencoba mencari lawan lagi (jendela kemampuan melebar seiring waktu)
VS_DELAY = 3.0         # layar VS sebelum soal pertama
REVEAL_DELAY = 3.0     # tampilan kunci & poin sebelum soal berikutnya


def _group(match_id):
    return f"duel_{match_id}"


class DuelConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.match_id = None
        self.tasks = set()
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return
        await self.accept()
        reason = await db(duel.eligibility)(self.user)
        if reason:
            await self.send_json({"type": "error", "code": "level", "message": reason})
            await self.close(code=4403)

    async def disconnect(self, code):
        for task in self.tasks:
            task.cancel()
        if not getattr(self, "user", None) or not self.user.is_authenticated:
            return
        await db(duel.leave_queue)(self.user)
        if self.match_id:
            result = await db(duel.finish_match)(self.match_id, forfeit_by=self.user.id)
            if result:
                await self.channel_layer.group_send(_group(self.match_id), {"type": "duel.finished", "result": result})
            await self.channel_layer.group_discard(_group(self.match_id), self.channel_name)

    def _spawn(self, coro):
        task = asyncio.ensure_future(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    # ── Pesan dari browser ──────────────────────────────────────────────────
    async def receive_json(self, content, **kwargs):
        kind = content.get("type")
        if kind == "queue" and not self.match_id:
            await self.search(first=True)
        elif kind == "cancel" and not self.match_id:
            for task in self.tasks:
                task.cancel()
            await db(duel.leave_queue)(self.user)
            await self.send_json({"type": "cancelled"})
        elif kind == "answer" and self.match_id:
            await self.answer(content)
        elif kind == "left" and self.match_id:
            await self.left_tab()

    async def search(self, first=False):
        match, opponent_channel = await db(duel.find_opponent)(self.user, self.channel_name)
        if match:
            await self.channel_layer.send(opponent_channel, {"type": "duel.matched", "match_id": str(match.pk)})
            await self.enter_match(str(match.pk), starter=True)
            return
        if first:
            await self.send_json({"type": "queued", "timeout": duel.QUEUE_TIMEOUT})
            self._spawn(self.poll())

    async def poll(self):
        while not self.match_id:
            await asyncio.sleep(POLL_SECONDS)
            if self.match_id:
                return
            if await db(duel.queue_expired)(self.user):
                await db(duel.leave_queue)(self.user)
                await self.send_json({"type": "no_opponent", "message": "Belum ada lawan online yang setara. Coba lagi sebentar lagi."})
                return
            await self.search()

    async def answer(self, content):
        try:
            index, option = int(content.get("index")), int(content.get("option"))
        except (TypeError, ValueError):
            await self.send_json({"type": "error", "message": "Jawaban tidak valid."})
            return
        ok, message, both = await db(duel.record_answer)(self.match_id, self.user, index, option)
        if not ok:
            await self.send_json({"type": "error", "message": message})
            return
        await self.send_json({"type": "answered", "index": index})
        await self.channel_layer.group_send(_group(self.match_id),
                                            {"type": "duel.progress", "user": self.user.id, "index": index})
        if both:
            await self.close_question(index)

    async def left_tab(self):
        info = await db(duel.leave_tab)(self.match_id, self.user)
        if not info:
            return
        if info["forfeit"]:
            result = await db(duel.finish_match)(self.match_id, forfeit_by=self.user.id)
            if result:
                await self.channel_layer.group_send(_group(self.match_id), {"type": "duel.finished", "result": result})
            return
        await self.send_json({"type": "tab_warning", **info})
        if info["voided"] is not None:
            await self.channel_layer.group_send(_group(self.match_id),
                                                {"type": "duel.progress", "user": self.user.id, "index": info["voided"]})
            if info["both"]:
                await self.close_question(info["voided"])

    # ── Alur duel ───────────────────────────────────────────────────────────
    async def enter_match(self, match_id, starter=False):
        for task in self.tasks:
            task.cancel()
        self.match_id = match_id
        await self.channel_layer.group_add(_group(match_id), self.channel_name)
        info = await db(self._match_info)(match_id)
        await self.send_json({"type": "matched", **info})
        if starter:
            self._spawn(self.open_question(0, delay=VS_DELAY))
        else:
            await self.catch_up()

    def _match_info(self, match_id):
        match = DuelMatch.objects.select_related("player_a", "player_b").get(pk=match_id)
        opponent = match.player_b if match.player_a_id == self.user.id else match.player_a
        return {"match": match_id, "you": duel.player_card(self.user), "opponent": duel.player_card(opponent),
                "tier": match.tier, "time_limit": match.time_limit, "total": len(match.questions)}

    async def catch_up(self):
        """Pemain yang bergabung belakangan langsung menerima soal yang sedang berjalan."""
        payload = await db(self._current_question)()
        if payload:
            await self.duel_question({"question": payload})

    def _current_question(self):
        match = DuelMatch.objects.filter(pk=self.match_id, status=DuelMatch.ACTIVE).first()
        if match and match.q_started_at:
            return duel.question_payload(match, match.current)
        return None

    async def open_question(self, index, delay=0.0):
        await asyncio.sleep(delay)
        payload = await db(duel.start_question)(self.match_id, index)
        if payload:
            await self.channel_layer.group_send(_group(self.match_id), {"type": "duel.question", "question": payload})

    async def close_question(self, index, force=False):
        summary = await db(duel.resolve_question)(self.match_id, index, force)
        if not summary:
            return
        await self.channel_layer.group_send(_group(self.match_id), {"type": "duel.reveal", "summary": summary})
        if summary["last"]:
            result = await db(duel.finish_match)(self.match_id)
            if result:
                await self.channel_layer.group_send(_group(self.match_id), {"type": "duel.finished", "result": result})
        else:
            self._spawn(self.open_question(index + 1, delay=REVEAL_DELAY))

    async def question_timer(self, index, seconds):
        await asyncio.sleep(seconds + duel.GRACE_MS / 1000 + 0.2)
        await self.close_question(index)

    # ── Pesan grup / kanal ──────────────────────────────────────────────────
    async def duel_matched(self, event):
        if not self.match_id:
            await self.enter_match(event["match_id"])

    async def duel_question(self, event):
        q = event["question"]
        await self.send_json({"type": "question", **q})
        self._spawn(self.question_timer(q["index"], q["time_limit"]))

    async def duel_progress(self, event):
        if event["user"] != self.user.id:
            await self.send_json({"type": "progress", "index": event["index"]})

    async def duel_reveal(self, event):
        await self.send_json({"type": "reveal", **event["summary"]})

    async def duel_finished(self, event):
        mine = event["result"]["players"].get(str(self.user.id))
        await self.send_json({"type": "finished", "you": mine, "players": event["result"]["players"],
                              "forfeit": bool(event["result"].get("forfeit_by"))})
        if self.match_id:
            await self.channel_layer.group_discard(_group(self.match_id), self.channel_name)
        self.match_id = None
