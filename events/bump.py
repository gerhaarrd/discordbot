import asyncio

bump_role = 1405007024701308949
channel = 1389979510975500349
disboard_id = 302050872383242240

async def bump_reminder(channel):
    try:
        print("Starting bump reminder task...")
        await asyncio.sleep(2 * 60 * 60)

        guild = channel.guild
        role = guild.get_role(bump_role)
        
        from views.bumpview import BumpComponents
        
        if role:
            await channel.send(view=BumpComponents())
        else:
            await channel.send(view=BumpComponents())
            
        print("Reminder sent successfully!")
    except asyncio.CancelledError:
        print("Bump reminder task was cancelled")
    except Exception as e:
        print(f"Error in bump reminder: {e}")
