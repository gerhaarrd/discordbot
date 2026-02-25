 

import discord

class BumpComponents(discord.ui.LayoutView):    
    def __init__(self):
        super().__init__(timeout=None)
        self.container1 = discord.ui.Container(
            discord.ui.TextDisplay(content="## 𐔌 ♻️. É HORA DO BUMP.ᐟ ֹ ₊ ꒱\n➦ Já se passaram 2 horas. É hora de utilizar o comando /bump novamente para divulgar a comunidade! .𖥔 ݁ ˖\n"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
            discord.ui.TextDisplay(content="Adquire cargo <@&1405007024701308949> em **Canais & Cargos** no topo da lista de chats.  ݁ ˖Ი𐑼⋆"),
            accent_colour=discord.Colour(3066993),
        )
        self.add_item(self.container1)