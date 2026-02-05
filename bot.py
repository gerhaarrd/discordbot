import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from pathlib import Path
import os
import time

load_dotenv(Path(__file__).parent / ".env")
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user} (ID {bot.user.id})")
    try:
        # Debug: listar comandos atualmente registrados na árvore local
        local_cmds = list(bot.tree.get_commands())
        print(f"Comandos locais registrados: {len(local_cmds)}")
        for c in local_cmds:
            try:
                print(f" - {c.name} (guild_only={getattr(c, 'guild_only', False)})")
            except Exception:
                print(f" - {c}")

        if GUILD_ID:
            guild_obj = discord.Object(id=int(GUILD_ID))
            synced = await bot.tree.sync(guild=guild_obj)
            print(f"Sincronizados {len(synced)} comandos no servidor de teste {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"Sincronizados {len(synced)} comandos (globais)")
    except Exception as e:
        print("Erro ao sincronizar comandos:", e)



@bot.event
async def on_member_join(member: discord.Member):
    # Envia um embed por DM quando um usuário entra no servidor
    try:
        description = """### ˚₊‧꒰ 𝐛𝐨𝐚𝐬-𝐯𝐢𝐧𝐝𝐚𝐬 𝐚 𝐒𝐨𝐮𝐥! 🍄🌿

    ⋆˙ Comeu um cogumelo e agora está meio perdido(a)? Calma, você caiu na comunidade certa! Boas-vindas a Soul™ o melhor servidor temático único para criar novas amizades que nunca para de crescer! 🎋

    🔮 Torne-se Booster e tenha acesso a uma ampla customização única que só você como booster pode ter! ₊˚⊹ 
    ── .✦ Cores em degrade. 🌈
    ── .✦ Mídia em bate-papo 🎨
    ── .✦ 5x XP. 🎀
    ── .✦ Emblema de Booster. 🎏
    E muito mais...

    Acesse nosso TikTok no botão abaixo!  🎯 ˖⋆࿐໋"""
        embed = discord.Embed(description=description, color=15191462)
        embed.set_footer(text="𝗦𝗼𝘂𝗹™ — seus sonhos estão guardados aqui!  ⋆˚࿔")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1445955005659222078/1466782521109909690/Picsart_26-01-30_00-11-45-266.jpg?ex=6985e82c&is=698496ac&hm=f8d2c81578dca88bc5c881c20d5c9a4410e6b96b637f5acfab02024728e791a4&")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1439299374302630011/1466847919079428400/10_Sem_Titulo_20260130142941.png?ex=69862514&is=6984d394&hm=c1f51f50275007a904a12b1358280f4dab0842b33755a60171a5d143de537d1a&")
        await member.send(embed=embed)
        print(f"Embed de boas-vindas enviado para {member} ({member.id})")
    except Exception as e:
        # Usuário pode ter DMs desabilitadas; logamos e seguimos
        print(f"Não foi possível enviar DM para {member} ({member.id}):", e)


@bot.tree.command(name="ping", description="Responde com pong")
async def ping(interaction: discord.Interaction):
    start = time.perf_counter()
    await interaction.response.send_message("Pinging...")
    elapsed = (time.perf_counter() - start) * 1000
    try:
        msg = await interaction.original_response()
        await msg.edit(content=f"{elapsed:.0f}ms (RTT) — ws {bot.latency*1000:.0f}ms")
    except Exception:
        # Fallback: send followup if editing failed
        await interaction.followup.send(f"{elapsed:.0f}ms (RTT) — ws {bot.latency*1000:.0f}ms")


@bot.tree.command(name="echo", description="Repete sua mensagem")
@app_commands.describe(message="Mensagem a repetir")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name="math", description="Soma dois números")
@app_commands.describe(a="Primeiro número", b="Segundo número")
async def math_add(interaction: discord.Interaction, a: int, b: int):
    await interaction.response.send_message(f"{a} + {b} = {a + b}")


if __name__ == "__main__":
    if not TOKEN:
        print("TOKEN não definido. Crie um arquivo .env com TOKEN=seu_token")
    else:
        bot.run(TOKEN)
