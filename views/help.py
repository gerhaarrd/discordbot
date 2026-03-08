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
                media="https://media.discordapp.net/attachments/1450869346304786594/1480025378880884827/help.png?ex=69ae2c8b&is=69acdb0b&hm=69ebbe6899c3dfa7c662ba52a58e2576bb819f50aa1798f881d209b4d0f0a180&=&format=webp&quality=lossless&width=700&height=1050"
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

        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),

        discord.ui.TextDisplay(
            content="## 🎙️ **Comandos de Call e Moedas**\n\n"
                    "**/voicestats** - Mostra suas estatísticas de tempo em call.\n\n"
                    "**/moedas** - Mostra seu saldo de moedas de call.\n\n"
                    "── .✦ Fique em call, ganhe moedas e personalize seu perfil! ˎˊ˗"
        ),

        accent_colour=discord.Colour(15742293),
    )
