import discord
from discord.ext import commands
from config import TOKEN


import events.ready as ready_event
import events.member_join as join_event
import events.message_filter as message_event
import commands.misc as misc_commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_modules():
    await ready_event.register(bot)
    await join_event.register(bot)
    await message_event.register(bot)
    await misc_commands.register(bot)




@bot.event
async def setup_hook():
    await load_modules()

if __name__ == "__main__":
    if not TOKEN:
        print("TOKEN não definido")
    else:
        bot.run(TOKEN)