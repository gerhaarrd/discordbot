async def register(bot):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return


        CHANNEL_ID = 1446156978702389492
        CHANNEL_ID2 = 1465827743978750246


        if getattr(message.channel, "id", None) not in (CHANNEL_ID, CHANNEL_ID2):
            await bot.process_commands(message)
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


        await bot.process_commands(message)