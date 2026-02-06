

from config import GUILD_ID
from views import Components


async def register(bot):
    @bot.event
    async def on_member_join(member):
        try:
            if GUILD_ID and member.guild.id != int(GUILD_ID):
                return


            await member.send(view=Components())
            print(f"Mensagem enviada para {member}")


        except Exception as e:
            print(f"Erro ao enviar DM para {member}:", e)