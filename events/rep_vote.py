import asyncio
import io
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
import discord
import database

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


POLL_TIMEOUT_SECONDS = 120
POLL_DELETE_DELAY_SECONDS = 5 * 60
RECENT_ACTIVITY_WINDOW_SECONDS = 15 * 60
AUTO_REPVOTE_INTERVAL_SECONDS = 3 * 60 * 60
AUTO_REPVOTE_ACTIVITY_WINDOW_SECONDS = 60 * 60
AUTO_REPVOTE_CHANNEL_IDS = (
    1389947781778772132,
    1476989026274902198,
)
WINNER_REP_REWARD = 5
CANVAS_WIDTH = 960
CANVAS_HEIGHT = 540
HALF_WIDTH = CANVAS_WIDTH // 2
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = PROJECT_ROOT / "fonts"


def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if not PIL_AVAILABLE:
        return ImageFont.load_default()

    candidates: List[str] = []

    if FONTS_DIR.exists():
        if bold:
            candidates.extend(
                [
                    str(FONTS_DIR / "RedHatDisplay-ExtraBold.otf"),
                    str(FONTS_DIR / "RedHatDisplay-Bold.otf"),
                    str(FONTS_DIR / "RedHatDisplay-SemiBold.otf"),
                    str(FONTS_DIR / "RedHatDisplay[wght].ttf"),
                ]
            )
        else:
            candidates.extend(
                [
                    str(FONTS_DIR / "RedHatDisplay-Regular.otf"),
                    str(FONTS_DIR / "RedHatText-Regular.otf"),
                    str(FONTS_DIR / "RedHatDisplay[wght].ttf"),
                ]
            )

    for path in candidates:
        if not Path(path).exists():
            continue
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


async def _download_avatar(user: discord.abc.User, size: int = 256) -> bytes:
    avatar_url = user.display_avatar.replace(size=size, format="png").url
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(avatar_url) as response:
            response.raise_for_status()
            return await response.read()


def _create_base_canvas() -> Image.Image:
    return Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 255))


def _fit_avatar(img: Image.Image, width: int, height: int) -> Image.Image:
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    return ImageOps.fit(img, (width, height), method=resample, centering=(0.5, 0.5))


def _draw_vote_bars(draw: ImageDraw.ImageDraw, left_votes: int, right_votes: int) -> Tuple[int, int]:
    total_votes = left_votes + right_votes
    if total_votes == 0:
        left_pct, right_pct = 0, 0
    else:
        left_pct = int(round((left_votes / total_votes) * 100))
        right_pct = 100 - left_pct

    bar_y_top = 495
    bar_height = 20
    left_bar_x = 24
    right_bar_x = HALF_WIDTH + 24
    bar_max_width = HALF_WIDTH - 48

    # Trilhos.
    draw.rounded_rectangle(
        [(left_bar_x, bar_y_top), (left_bar_x + bar_max_width, bar_y_top + bar_height)],
        radius=10,
        fill=(30, 34, 43, 220),
    )
    draw.rounded_rectangle(
        [(right_bar_x, bar_y_top), (right_bar_x + bar_max_width, bar_y_top + bar_height)],
        radius=10,
        fill=(30, 34, 43, 220),
    )

    # Preenchimento.
    left_width = int((left_pct / 100) * bar_max_width)
    right_width = int((right_pct / 100) * bar_max_width)
    if left_width > 0:
        draw.rounded_rectangle(
            [(left_bar_x, bar_y_top), (left_bar_x + left_width, bar_y_top + bar_height)],
            radius=10,
            fill=(26, 137, 255, 255),
        )
    if right_width > 0:
        draw.rounded_rectangle(
            [(right_bar_x, bar_y_top), (right_bar_x + right_width, bar_y_top + bar_height)],
            radius=10,
            fill=(207, 89, 255, 255),
        )

    return left_pct, right_pct


async def _render_vs_image(
    left_user: discord.Member,
    right_user: discord.Member,
    left_votes: int,
    right_votes: int,
) -> io.BytesIO:
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow não está disponível. Instale `Pillow` no ambiente.")

    canvas = _create_base_canvas()
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    left_avatar_bytes, right_avatar_bytes = await asyncio.gather(
        _download_avatar(left_user, size=1024),
        _download_avatar(right_user, size=1024),
    )
    left_avatar = _fit_avatar(Image.open(io.BytesIO(left_avatar_bytes)).convert("RGBA"), HALF_WIDTH, CANVAS_HEIGHT)
    right_avatar = _fit_avatar(Image.open(io.BytesIO(right_avatar_bytes)).convert("RGBA"), HALF_WIDTH, CANVAS_HEIGHT)

    # Fotos puras lado a lado (sem fundo cinza).
    canvas.paste(left_avatar, (0, 0))
    canvas.paste(right_avatar, (HALF_WIDTH, 0))

    # Faixa escura apenas para legibilidade do texto.
    draw.rectangle([(0, 420), (CANVAS_WIDTH, CANVAS_HEIGHT)], fill=(0, 0, 0, 120))
    draw.line([(HALF_WIDTH, 0), (HALF_WIDTH, CANVAS_HEIGHT)], fill=(255, 255, 255, 70), width=2)

    # VS maior no centro.
    vs_font = _load_font(124, bold=True)
    draw.text(
        (HALF_WIDTH - 90, 185),
        "VS",
        fill=(245, 245, 250, 255),
        font=vs_font,
        stroke_width=4,
        stroke_fill=(0, 0, 0, 180),
    )

    # Nicks maiores.
    name_font = _load_font(48, bold=True)
    left_name = left_user.display_name[:15]
    right_name = right_user.display_name[:15]
    draw.text((24, 412), left_name, fill=(245, 245, 250, 255), font=name_font, stroke_width=3, stroke_fill=(0, 0, 0, 180))
    draw.text((HALF_WIDTH + 24, 412), right_name, fill=(245, 245, 250, 255), font=name_font, stroke_width=3, stroke_fill=(0, 0, 0, 180))

    left_pct, right_pct = _draw_vote_bars(draw, left_votes, right_votes)

    pct_font = _load_font(52, bold=True)
    draw.text((325, 420), f"{left_pct}%", fill=(216, 230, 255, 255), font=pct_font, stroke_width=3, stroke_fill=(0, 0, 0, 180))
    draw.text((HALF_WIDTH + 325, 420), f"{right_pct}%", fill=(245, 220, 255, 255), font=pct_font, stroke_width=3, stroke_fill=(0, 0, 0, 180))

    final_image = Image.alpha_composite(canvas, overlay).convert("RGB")
    output = io.BytesIO()
    final_image.save(output, format="PNG")
    output.seek(0)
    return output


class ActiveChatTracker:
    def __init__(self):
        self._active_users_by_channel: Dict[int, Dict[int, float]] = {}

    def mark_message(self, channel_id: int, user_id: int):
        now = time.time()
        channel_map = self._active_users_by_channel.setdefault(channel_id, {})
        channel_map[user_id] = now

    def get_recent_users(self, channel_id: int, window_seconds: int) -> List[int]:
        now = time.time()
        channel_map = self._active_users_by_channel.get(channel_id, {})
        valid_users = [uid for uid, ts in channel_map.items() if now - ts <= window_seconds]
        # Limpeza de memória.
        self._active_users_by_channel[channel_id] = {uid: channel_map[uid] for uid in valid_users}
        return valid_users


class RepVoteView(discord.ui.View):
    def __init__(self, bot: discord.Client, left_user: discord.Member, right_user: discord.Member):
        super().__init__(timeout=None)
        self.bot = bot
        self.left_user = left_user
        self.right_user = right_user
        self.votes = [0, 0]
        self.voters: Dict[int, int] = {}
        self.message: Optional[discord.Message] = None
        self.finished = False
        self.created_at = time.monotonic()
        self._finish_lock = asyncio.Lock()
        self._deadline_task = asyncio.create_task(self._deadline_worker())

        left_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label=f"Votar em {left_user.display_name[:15]}",
        )
        right_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"Votar em {right_user.display_name[:15]}",
        )

        async def left_callback(interaction: discord.Interaction):
            await self._handle_vote(interaction, target_index=0)

        async def right_callback(interaction: discord.Interaction):
            await self._handle_vote(interaction, target_index=1)

        left_btn.callback = left_callback
        right_btn.callback = right_callback
        self.add_item(left_btn)
        self.add_item(right_btn)

    async def _build_embed_and_file(self, finished_text: Optional[str] = None) -> Tuple[discord.Embed, discord.File]:
        image_bytes = await _render_vs_image(
            self.left_user,
            self.right_user,
            self.votes[0],
            self.votes[1],
        )
        file = discord.File(image_bytes, filename="rep_vote.png")
        embed = discord.Embed(
            title="Quem merece mais rep?",
            description=finished_text or "Vote no membro que você acha que mais merece reputação!",
            color=discord.Colour(3265791),
        )
        embed.set_image(url="attachment://rep_vote.png")
        embed.set_footer(text="☆゙ quem merece mais rep?...")
        return embed, file

    async def _handle_vote(self, interaction: discord.Interaction, target_index: int):
        if time.monotonic() - self.created_at >= POLL_TIMEOUT_SECONDS:
            await self._finish_poll()
            await interaction.response.send_message("A votação já terminou.", ephemeral=True)
            return

        if self.finished:
            await interaction.response.send_message("A votação já terminou.", ephemeral=True)
            return

        voter_id = interaction.user.id
        if voter_id in self.voters:
            await interaction.response.send_message("Você já votou nessa disputa.", ephemeral=True)
            return

        self.voters[voter_id] = target_index
        self.votes[target_index] += 1

        embed, file = await self._build_embed_and_file()
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)

    async def _deadline_worker(self):
        await asyncio.sleep(POLL_TIMEOUT_SECONDS)
        await self._finish_poll()

    async def _delete_message_later(self):
        if self.message is None:
            return
        await asyncio.sleep(POLL_DELETE_DELAY_SECONDS)
        try:
            await self.message.delete()
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"[REP_VOTE] erro ao apagar mensagem da votação: {e}")

    async def _finish_poll(self):
        async with self._finish_lock:
            if self.finished:
                return
            self.finished = True

            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True

            winner_text = "Empate! Nenhuma reputação foi adicionada."
            winner_member: Optional[discord.Member] = None

            if self.votes[0] > self.votes[1]:
                winner_member = self.left_user
            elif self.votes[1] > self.votes[0]:
                winner_member = self.right_user

            if winner_member is not None:
                bot_id = str(self.bot.user.id if self.bot.user else 0)
                guild_id = str(winner_member.guild.id)

                credited = 0
                try:
                    credited = database.add_rep_amount(
                        giver_id=bot_id,
                        receiver_id=str(winner_member.id),
                        guild_id=guild_id,
                        amount=WINNER_REP_REWARD,
                        reason="Rep vote winner",
                    )
                except Exception as e:
                    print(f"[REP_VOTE] erro ao creditar reputação do vencedor: {e}")
                    credited = 0

                try:
                    from commands.reputation import rep_system
                    rep_system._invalidate_cache()
                    receiver_data = rep_system.get_user_data(winner_member.id)
                    await rep_system.update_user_aura_roles(
                        winner_member.id,
                        winner_member.guild,
                        receiver_data["rep_total"],
                    )
                except Exception:
                    pass

                diff = abs(self.votes[0] - self.votes[1])
                if credited > 0:
                    winner_text = (
                        f"👑 {winner_member.mention} venceu por **{diff} voto(s)** "
                        f"e recebeu **+{credited} rep**!"
                    )
                else:
                    winner_text = (
                        f"👑 {winner_member.mention} venceu por **{diff} voto(s)**, "
                        "mas ocorreu um erro ao creditar a reputação."
                    )

                if self.message is not None:
                    try:
                        await self.message.channel.send(
                            (
                                f"📣 {winner_member.mention}, você venceu o rep vote "
                                f"com **{diff} voto(s)**!"
                            ),
                            allowed_mentions=discord.AllowedMentions(users=[winner_member]),
                        )
                    except Exception as e:
                        print(f"[REP_VOTE] erro ao notificar vencedor: {e}")

            if self.message is not None:
                embed, file = await self._build_embed_and_file(finished_text=winner_text)
                try:
                    await self.message.edit(embed=embed, attachments=[file], view=self)
                except Exception as e:
                    print(f"[REP_VOTE] erro ao finalizar votação: {e}")
                asyncio.create_task(self._delete_message_later())
            self.stop()

    async def on_timeout(self):
        await self._finish_poll()


async def register(bot):
    tracker = ActiveChatTracker()

    async def _pick_two_active_members(
        channel: discord.abc.GuildChannel,
        window_seconds: int,
    ) -> Optional[Tuple[discord.Member, discord.Member]]:
        if not isinstance(channel, discord.TextChannel):
            return None

        active_user_ids = tracker.get_recent_users(channel.id, window_seconds=window_seconds)
        active_members: List[discord.Member] = []
        for uid in active_user_ids:
            member = channel.guild.get_member(uid)
            if member is None or member.bot:
                continue
            active_members.append(member)

        if len(active_members) < 2:
            return None

        left_member, right_member = random.sample(active_members, 2)
        return left_member, right_member

    async def _send_repvote_in_channel(
        channel: discord.abc.GuildChannel,
        window_seconds: int,
        source: str,
    ) -> bool:
        picked = await _pick_two_active_members(channel, window_seconds=window_seconds)
        if picked is None:
            if isinstance(channel, discord.TextChannel):
                print(
                    f"[REP_VOTE][{source}] sem usuários ativos suficientes em #{channel.name} "
                    f"(id={channel.id})"
                )
            return False

        left_member, right_member = picked
        view = RepVoteView(bot, left_member, right_member)
        embed, file = await view._build_embed_and_file()

        if not isinstance(channel, discord.TextChannel):
            return False

        message = await channel.send(embed=embed, file=file, view=view)
        view.message = message
        print(
            f"[REP_VOTE][{source}] votação criada em #{channel.name} "
            f"entre {left_member} ({left_member.id}) e {right_member} ({right_member.id})"
        )
        return True

    async def _repvote_hourly_task():
        await bot.wait_until_ready()
        print("[REP_VOTE] agendador horário iniciado")

        while not bot.is_closed():
            await asyncio.sleep(AUTO_REPVOTE_INTERVAL_SECONDS)

            for channel_id in AUTO_REPVOTE_CHANNEL_IDS:
                channel = bot.get_channel(channel_id)
                if channel is None:
                    try:
                        channel = await bot.fetch_channel(channel_id)
                    except Exception as e:
                        print(f"[REP_VOTE][auto] erro ao buscar canal {channel_id}: {e}")
                        continue

                try:
                    await _send_repvote_in_channel(
                        channel=channel,
                        window_seconds=AUTO_REPVOTE_ACTIVITY_WINDOW_SECONDS,
                        source="auto",
                    )
                except Exception as e:
                    print(f"[REP_VOTE][auto] erro ao enviar votação no canal {channel_id}: {e}")

    @bot.listen("on_message")
    async def rep_vote_track_chat(message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        tracker.mark_message(message.channel.id, message.author.id)

    bot.loop.create_task(_repvote_hourly_task())
