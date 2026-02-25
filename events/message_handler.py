async def handle_bump_detection(bot, message):
    channel = 1389979510975500349
    disboard_id = 302050872383242240
    
    if message.channel.id != channel:
        return
        
    if message.author.id != disboard_id:
        return
        
    if not message.embeds:
        return
        
    embed = message.embeds[0]
    if not (embed.description and "bump done" in embed.description.lower()):
        return
        
    print("Bump done detected")
    
    await message.channel.send(f"✅ Bump detectado! Vou lembrar em 2 horas para dar o próximo bump! ⏰")
    
    from events.bump import bump_reminder
    import asyncio
    
    if hasattr(bot, '_bump_task') and bot._bump_task and not bot._bump_task.done():
        bot._bump_task.cancel()
        print("Cancelled existing bump task")
        
    bot._bump_task = asyncio.create_task(bump_reminder(message.channel))
    print("Created new bump task in 2 hours")


async def handle_message_filter(message):
    CHANNEL_ID = 1446156978702389492
    CHANNEL_ID2 = 1465827743978750246

    if getattr(message.channel, "id", None) not in (CHANNEL_ID, CHANNEL_ID2):
        return

    has_media = False
    for att in message.attachments:
        ct = att.content_type
        if ct and (ct.startswith("image") or ct.startswith("video")):
            has_media = True
            break

    if not has_media:
        try:
            await message.delete()
        except Exception as e:
            print("Erro ao deletar mensagem:", e)


async def register(bot):
    @bot.event
    async def on_message(message):
        await bot.process_commands(message)

        await handle_bump_detection(bot, message)

        await handle_message_filter(message)
