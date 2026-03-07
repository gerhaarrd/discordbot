import discord
import asyncio

role_id = 1475160585078308895
channel1 = 1389947781778772132
channel2 = 1476989026274902198
AUTO_DELETE_SECONDS = 8 * 60
STATUS_TOKENS = (
    ".gg/soulll",
    "dsc.gg/soulll",
    "discord.gg/soulll",
    "https://discord.gg/soulll",
)


class Components(discord.ui.LayoutView):    
    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content="### ᯓ★ Seja Esporos! ⋅ ˚✮\nAdicione **.gg/soulll** em sua bio ou nota do Discord e receba o cargo ദ്ദി 𝐄𝐒𝐏𝐎𝐑𝐎𝐒.ᵍᵍ/ˢᵒᵘˡˡˡ ꒱ 🍄 ᯓ★ com ícone e cor gradiente **exclusiva!!** Simples, né?\n\nᝰ.ᐟ Entre em contato com a equipe para reivindicar o cargo... ‧🌿｡⋆"),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1452857118934827221/1475184019271454953/file_0000000016ec71f5b802732d689c371b.png?ex=699c8fad&is=699b3e2d&hm=cddd69cc21dc99b601313304acdefbbdf1440f9495760590e6b5a240a3789365&",
            ),
        ),
        discord.ui.MediaGallery(
            discord.MediaGalleryItem(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1475191024757379205/1771783340263.png?ex=699c9634&is=699b44b4&hm=cf235d7b4aa5841c23f381d0b2aa67892314067918ab61b09ce313dc5ce3aaa6&",
            ),
        ),
        accent_colour=discord.Colour(15074687),
    )


async def register(bot):
    pending_queue: asyncio.Queue[tuple[int, int]] = asyncio.Queue()
    queued_members: set[tuple[int, int]] = set()
    WORKER_DELAY_SECONDS = 0.2
    WORKER_COUNT = 4
    RESYNC_INTERVAL_SECONDS = 5 * 60

    def _normalize_text(value: str) -> str:
        return (
            value.lower()
            .replace(" ", "")
            .replace("\u2060", "")  # word-joiner invisível
            .replace("\ufeff", "")  # bom invisível
        )

    def _activity_texts(member: discord.Member) -> list[str]:
        texts: list[str] = []
        for activity in member.activities or []:
            possible_values = [getattr(activity, "name", None), getattr(activity, "state", None)]
            for value in possible_values:
                if not isinstance(value, str):
                    continue
                texts.append(value)
        return texts

    def _status_has_soulll(member: discord.Member) -> bool:
        for value in _activity_texts(member):
            normalized = _normalize_text(value)
            if any(token in normalized for token in STATUS_TOKENS):
                return True
        return False

    async def _sync_member_role(member: discord.Member):
        if member.bot:
            return

        role = member.guild.get_role(role_id)
        if role is None:
            return

        should_have = _status_has_soulll(member)
        has_role = role in member.roles

        try:
            if should_have and not has_role:
                await member.add_roles(role, reason="Status contém invite soulll")
                print(f"[ESPOROS] cargo adicionado: {member} ({member.id})")
            elif not should_have and has_role:
                await member.remove_roles(role, reason="Status não contém invite soulll")
                print(f"[ESPOROS] cargo removido: {member} ({member.id})")
        except Exception as e:
            print(f"[ESPOROS] erro sincronizando cargo para {member} ({member.id}): {e}")

    async def _enqueue_member(member: discord.Member, source: str = "unknown"):
        if member.bot:
            return
        member_key = (member.guild.id, member.id)
        if member_key in queued_members:
            return
        queued_members.add(member_key)
        await pending_queue.put(member_key)
        print(
            f"[ESPOROS][QUEUE] enfileirado: {member} ({member.id}) "
            f"| source={source} | fila={pending_queue.qsize()}"
        )

    async def _role_worker(worker_id: int):
        await bot.wait_until_ready()
        print(f"[ESPOROS][WORKER-{worker_id}] iniciado")
        while not bot.is_closed():
            guild_id = None
            member_id = None
            try:
                guild_id, member_id = await pending_queue.get()
                member_key = (guild_id, member_id)
                queued_members.discard(member_key)

                guild = bot.get_guild(guild_id)
                if guild is None:
                    pending_queue.task_done()
                    await asyncio.sleep(WORKER_DELAY_SECONDS)
                    continue

                member = guild.get_member(member_id)
                if member is None:
                    try:
                        member = await guild.fetch_member(member_id)
                    except Exception:
                        member = None

                if member is not None:
                    await _sync_member_role(member)
                    print(
                        f"[ESPOROS][WORKER-{worker_id}][CHECK] checado: "
                        f"{member} ({member.id}) | fila={pending_queue.qsize()}"
                    )

                pending_queue.task_done()
                await asyncio.sleep(WORKER_DELAY_SECONDS)
            except Exception as e:
                print(
                    f"[ESPOROS][WORKER-{worker_id}] erro no loop "
                    f"(guild={guild_id}, member={member_id}): {e}"
                )
                await asyncio.sleep(1)

    async def _startup_sync():
        await bot.wait_until_ready()
        total = 0
        for guild in bot.guilds:
            for member in guild.members:
                total += 1
                await _enqueue_member(member, source="startup")
        print(f"[ESPOROS] startup sync enfileirou {total} membros | fila={pending_queue.qsize()}")

    async def _periodic_resync():
        await bot.wait_until_ready()
        while not bot.is_closed():
            total = 0
            for guild in bot.guilds:
                for member in guild.members:
                    if member.status != discord.Status.offline:
                        total += 1
                        await _enqueue_member(member, source="periodic")
            print(f"[ESPOROS] resync periódico enfileirado: {total} membros online")
            await asyncio.sleep(RESYNC_INTERVAL_SECONDS)

    @bot.command()
    async def testesporos(ctx):
        """Testa o envio da mensagem dos Esporos"""
        try:
            await ctx.send(view=Components())
            await ctx.send("✅ Mensagem de teste enviada com sucesso!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao enviar mensagem: {e}")

    @bot.command(name="sync_esporos_me")
    async def sync_esporos_me(ctx):
        if isinstance(ctx.author, discord.Member):
            await _sync_member_role(ctx.author)
            await ctx.send("✅ Checagem de status executada para você.")
        else:
            await ctx.send("❌ Não consegui identificar seu membro no servidor.")
    
    async def esporos_task():
        await bot.wait_until_ready()
        
        async def send_esporos(channel_id: int, label: str):
            channel = bot.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await bot.fetch_channel(channel_id)
                except Exception as e:
                    print(f"Error fetching channel {label}: {e}")
                    return

            try:
                await channel.send(view=Components(), delete_after=AUTO_DELETE_SECONDS)
                print(f"Esporos message sent to channel {label}")
            except Exception as e:
                print(f"Error sending to channel {label}: {e}")

        await send_esporos(channel1, "1 (startup)")
        await send_esporos(channel2, "2 (startup)")

        while not bot.is_closed():
            await asyncio.sleep(3 * 60 * 60)
            await send_esporos(channel1, "1")
            await send_esporos(channel2, "2")

    @bot.listen("on_presence_update")
    async def esporos_on_presence_update(before: discord.Member, after: discord.Member):
        await _enqueue_member(after, source="presence_update")

    @bot.listen("on_member_join")
    async def esporos_on_member_join(member: discord.Member):
        await _enqueue_member(member, source="member_join")

    @bot.listen("on_message")
    async def esporos_on_message(message: discord.Message):
        if message.author.bot:
            return
        if isinstance(message.author, discord.Member):
            await _enqueue_member(message.author, source="message")
    
    bot.loop.create_task(esporos_task())
    for worker_id in range(1, WORKER_COUNT + 1):
        bot.loop.create_task(_role_worker(worker_id))
    bot.loop.create_task(_startup_sync())
    bot.loop.create_task(_periodic_resync())
