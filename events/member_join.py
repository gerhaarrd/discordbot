from config import GUILD_ID
from views import WelcomeComponents

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
                    await bot.get_channel(channel1).send(mensagem)
                    print("enviado no canal 1")
                except Exception as e:
                    print(f"Erro ao enviar no canal 1:", e)

            if channel2:
                try:
                    await bot.get_channel(channel2).send(mensagem2)
                    print("enviado no canal 2")
                except Exception as e:
                    print(f"Erro ao enviar no canal 2:", e)

        except Exception as e:
            print("Erro geral no on_member_join:", e)