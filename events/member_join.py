from config import GUILD_ID
from views import WelcomeComponents

import asyncio
import discord

AUTO_DELETE_SECONDS = 8 * 60


async def _get_channel(bot, channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel is not None:
        return channel

    try:
        fetched = await bot.fetch_channel(channel_id)
    except Exception as e:
        print(f"Erro ao buscar canal {channel_id}:", e)
        return None

    return fetched if isinstance(fetched, discord.abc.Messageable) else None


async def _delete_later(message: discord.Message, delay: int):
    await asyncio.sleep(delay)

    try:
        await message.delete()
        print(f"Mensagem de boas-vindas deletada (id={message.id})")
    except Exception as e:
        print(f"Erro ao deletar mensagem de boas-vindas (id={message.id}):", e)


async def _send_welcome_with_auto_delete(bot, channel_id: int, content: str):
    channel = await _get_channel(bot, channel_id)
    if channel is None:
        print(f"Canal {channel_id} indisponível para envio.")
        return

    message = await channel.send(content)
    print(f"Mensagem enviada no canal {channel_id} (id={message.id})")

    bot.loop.create_task(_delete_later(message, AUTO_DELETE_SECONDS))


async def register(bot):
    @bot.event
    async def on_member_join(member):
        try:
            if GUILD_ID and member.guild.id != int(GUILD_ID):
                return

            try:
                await member.send(view=WelcomeComponents())
                print(f"Mensagem enviada para {member}")
            except Exception as e:
                print(f"Erro ao enviar DM para {member}:", e)

            channel1 = 1389947781778772132
            channel2 = 1476989026274902198

            mensagem = f"⊹ ࣪ ˖ {member.mention} | <@&1405007119329005719>\n︶ ͡ ۫ ˓꒰ Um novo dreamer chegou ao Reino dos Ventos — deem suas boas-vindas! Obrigado por se juntar. 𐔌՞. .՞𐦯 🍄"
            mensagem2 = f"⊹ ࣪ ˖ {member.mention}|\n︶ ͡ ۫ ˓꒰ Um novo dreamer chegou ao Reino dos Ventos — deem suas boas-vindas! Obrigado por se juntar. 𐔌՞. .՞𐦯 🍄"

            if channel1:
                try:
                    await _send_welcome_with_auto_delete(bot, channel1, mensagem)
                except Exception as e:
                    print("Erro ao enviar no canal 1:", e)

            if channel2:
                try:
                    await _send_welcome_with_auto_delete(bot, channel2, mensagem2)
                except Exception as e:
                    print("Erro ao enviar no canal 2:", e)

        except Exception as e:
            print("Erro geral no on_member_join:", e)
