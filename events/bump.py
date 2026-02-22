import asyncio
import discord
from datetime import datetime

bump_role = 1405007024701308949
channel = 1389979510975500349
disboard_id = 302050872383242240

async def bump_reminder(channel):
    try:
        print("Starting bump reminder task...")
        await asyncio.sleep(2 * 60 * 60)

        guild = channel.guild
        role = guild.get_role(bump_role)
        
        embed = discord.Embed(
            title="𐔌 ♻️. É HORA DO BUMP.ᐟ ֹ ₊ ꒱",
            description="➦ Já se passaram 2 horas. É hora de utilizar o comando /bump novamente para divulgar a comunidade! .𖥔 ݁ ˖",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"{datetime.now().strftime('%H:%M')}")
        
        print(f"Sending reminder to channel {channel.id}, role {role.id if role else 'None'}")
        
        if role:
            await channel.send(content=f"{role.mention}", embed=embed)
        else:
            await channel.send(embed=embed)
        
        print("Reminder sent successfully!")

    except asyncio.CancelledError:
        print("Bump reminder task was cancelled")
    except Exception as e:
        print(f"Error in bump reminder: {e}")
