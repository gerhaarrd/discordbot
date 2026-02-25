import discord

class HelpView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        
    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(
                content="### ˚₊‧꒰ 𝐂𝐞𝐧𝐭𝐫𝐚𝐥 𝐝𝐞 𝐂𝐨𝐦𝐚𝐧𝐝𝐨𝐬 📚\n\n"
                    "⋆˙ Aqui estão todos os comandos disponíveis "
                    "para você usar no nosso servidor! Escolha o que precisa "
                    "e tenha a melhor experiência com o bot! 🍄✨"
            ),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1469429794818097172/Picsart_26-02-06_17-29-11-387.png?ex=6987a0a3&is=69864f23&hm=47346519a427180b092f40b6ce840429f0fd050d224c5e0d2cd3c8b2d696bd43&"
            ),
        ),

        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),

        discord.ui.TextDisplay(
            content="## 🏓 **Comandos de Utilidade**\n\n"
                    "**/ping** - Mede o tempo de resposta do bot e mostra o ping da WebSocket.\n\n"
                    "**/help** - Mostra esta bela interface de ajuda.\n\n"
                    "── .✦ Use estes comandos para verificar o status e obter ajuda! ˎˊ˗"
        ),

        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),

        discord.ui.TextDisplay(
            content="## ⭐ **Comandos de Reputação**\n\n"
                    "**/rep <@user> [motivo]** - Dá +1 ponto de reputação a um usuário.\n"
                    "⏱ Cooldown de 3h global e 6h por par.\n"
                    "🚫 Não pode dar para si mesmo ou bots.\n\n"
                    "**/reppoints [@user]** - Mostra reputação total e posição no ranking.\n\n"
                    "**/reptop** - Exibe o Top 10 usuários com mais reputação.\n\n"
                    "**/rephistory [@user]** - Mostra histórico das últimas 5 reputações recebidas.\n\n"
                    "── .✦ Construa sua reputação e suba no ranking do servidor! ˎˊ˗"
        ),

        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),

        discord.ui.TextDisplay(
            content="## 🍄 **Comandos de Stickers**\n\n"
                    "**/mushadd <@user> <@role>** - Adiciona um sticker (cargo de cogumelo) a um usuário.\n"
                    "🔒 Apenas Mush Crystals podem usar.\n"
                    "⚠ Cada usuário só pode ter um sticker.\n\n"
                    "**/mushremove <@user>** - Remove todos os stickers de um usuário.\n"
                    "🔒 Apenas Mush Crystals podem usar.\n\n"
                    "── .✦ Sistema exclusivo de personalização com stickers especiais! ˎˊ˗"
        ),

        accent_colour=discord.Colour(15742293),
    )
