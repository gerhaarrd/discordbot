import discord
from discord.ext import commands
from discord import app_commands, ui
from dotenv import load_dotenv
from pathlib import Path
import os
import time
import logging
from logging.handlers import RotatingFileHandler

load_dotenv(Path(__file__).parent / ".env")
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- VIEW ----------------

class Components(discord.ui.LayoutView):

    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(
                content="### ˚₊‧꒰ 𝐛𝐨𝐚𝐬-𝐯𝐢𝐧𝐝𝐚𝐬 𝐚 𝐒𝐨𝐮𝐥! 🍄🌿\n\n"
                        "⋆˙ Comeu um cogumelo e agora está meio perdido(a)? "
                        "Calma, você caiu na comunidade certa! Boas-vindas a **Soul™** "
                        "o melhor servidor temático único para criar novas amizades "
                        "que nunca para de crescer! 🎋"
            ),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1469146027922817271/10_Sem_Titulo_20260130142941.png"
            ),
        ),

        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),

        discord.ui.TextDisplay(
            content="\n🔮 Torne-se Booster e tenha acesso a uma ampla customização única que só você como booster pode ter! ₊˚⊹\n"
                    "── .✦ Cores em degrade. 🌈\n"
                    "── .✦ Mídia em bate-papo 🎨\n"
                    "── .✦ 5x XP. 🎀\n"
                    "── .✦ Emblema de Booster. 🎏\n"
                    "**E muito mais...**\n\n"
                    "Acesse nosso **TikTok** no botão abaixo! 🎯 ˖⋆࿐໋"
        ),

        discord.ui.MediaGallery(
            discord.MediaGalleryItem(
                media="https://cdn.discordapp.com/attachments/1445955005659222078/1466782521109909690/Picsart_26-01-30_00-11-45-266.jpg"
            )
        ),

        discord.ui.ActionRow(
            discord.ui.Button(
                label="TikTok",
                url="https://www.tiktok.com/@gg_soulll?_r=1&_t=ZS-93g7EKTUQ53"
            )
        ),

        accent_colour=discord.Colour(16112295),
    )


# ---------------- EVENTOS ----------------

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    try:
        if GUILD_ID:
            guild_obj = discord.Object(id=int(GUILD_ID))
            synced = await bot.tree.sync(guild=guild_obj)
            print(f"Sincronizados {len(synced)} comandos no servidor {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"Sincronizados {len(synced)} comandos globais")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")


@bot.event
async def on_member_join(member: discord.Member):

    #try:
        if GUILD_ID and member.guild.id != int(GUILD_ID):
            return

        view = Components()

        await member.send(view=view)

        #print(f"Mensagem de boas-vindas enviada para {member}")

    #except Exception as e:
        #print(f"Erro ao enviar DM para {member}: {e}")


@bot.command()
async def send_components(ctx):
    await ctx.send(view=Components())

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    CHANNEL_ID = 1446156978702389492 #facereveal
    CHANNEL_ID2 = 1465827743978750246 #skinreveal

    #print(f"Recebida mensagem {getattr(message, 'id', None)} de {message.author} no canal {getattr(message.channel,'id',None)}")

    if getattr(message.channel, "id", None) not in (CHANNEL_ID, CHANNEL_ID2):
        #print("Canal não é alvo — processando comandos normalmente")
        await bot.process_commands(message)
        return

    has_media = False

    for att in message.attachments:
        ct = att.content_type
        if ct:
            if ct.startswith("image") or ct.startswith("video"):
                has_media = True
                break
        fn = att.filename.lower()
        if fn.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".mp4", ".mov", ".mkv", ".webm", ".avi", ".flv")):
            has_media = True
            break

    if not has_media:
        for emb in message.embeds:
            if getattr(emb, "image", None) and getattr(emb.image, "url", None):
                has_media = True
                break
            if getattr(emb, "video", None) and getattr(emb.video, "url", None):
                has_media = True
                break

    if not has_media:
        #try:
            await message.delete()
            #print(f"Deletada mensagem {getattr(message,'id',None)} de {message.author} no canal {message.channel} — sem mídia")
        #except Exception as e:
            #print(f"Erro ao deletar mensagem {getattr(message,'id',None)} em {message.channel}: {e}")
        #return

    #print(f"Mensagem {getattr(message,'id',None)} preservada (tem mídia) no canal {message.channel}")
    await bot.process_commands(message)


# ---------------- SLASH COMMANDS ----------------

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    start = time.perf_counter()
    await interaction.response.send_message("Pinging...")
    elapsed = (time.perf_counter() - start) * 1000

    msg = await interaction.original_response()
    await msg.edit(content=f"{elapsed:.0f}ms — ws {bot.latency*1000:.0f}ms")


# ---------------- RUN ----------------

if __name__ == "__main__":
    if not TOKEN:
        print("TOKEN não definido no .env")
    else:
        bot.run(TOKEN)
