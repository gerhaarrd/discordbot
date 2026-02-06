import discord


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
            content="\n🔮 Torne-se Booster e tenha acesso a uma ampla customização única!"
        ),


        discord.ui.MediaGallery(
            discord.MediaGalleryItem(
                media="https://cdn.discordapp.com/attachments/1445955005659222078/1466782521109909690/Picsart_26-01-30_00-11-45-266.jpg"
            )
        ),


        discord.ui.ActionRow(
            discord.ui.Button(
                label="TikTok",
                url="https://www.tiktok.com/@gg_soulll"
            )
        ),


        accent_colour=discord.Colour(16112295),
    )