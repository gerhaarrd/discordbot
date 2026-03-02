import discord

class RankingCallComponents(discord.ui.LayoutView):
    def __init__(self, ranking_data: list):
        """
        ranking_data deve ser uma lista de tuplas:
        [
            (member, "2h 35m"),
            (member, "1h 12m"),
            ...
        ]
        """

        super().__init__(timeout=None)

        ranking_text = self._build_ranking_text(ranking_data)

        self.container1 = discord.ui.Container(
            discord.ui.TextDisplay(
                content=ranking_text
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://media.discordapp.net/attachments/1450869346304786594/1477861255338397747/Picsart_26-02-27_17-15-10-782.png?ex=69a64d0c&is=69a4fb8c&hm=bce241cafde112177b0799d8bed8d3d728b3708b012cbd7dd6ec19be56258eab&=&format=webp&quality=lossless&width=964&height=321",
                ),
            ),
            discord.ui.TextDisplay(
                content="૮꒰ Sua dedicação em call define sua posição no ranking ࣭ :four_leaf_clover:꒷꒦"
            ),
            accent_colour=discord.Colour(8442915),
        )

        self.add_item(self.container1)

    def _build_ranking_text(self, ranking_data: list) -> str:
        medals = [
            ":first_place:",
            ":second_place:",
            ":third_place:",
            "🏅",
            "🏅"
        ]

        header = (
            "### ˖𑣲:herb:⋆ 𝐑𝐀𝐍𝐊𝐈𝐍𝐆 𝐂𝐀𝐋𝐋𝐒 ݁ ˖ ◝\n"
            "  ๋࣭ ⭑ Bem-vindo ao ranking oficial dos membros com mais **horas em call**.\n"
            "Aqui, dedicação e presença fazem você subir cada vez mais no topo! ᝰ.ᐟ \n\n"
        )

        body = ""

        # Garantir que sempre tenha 5 posições
        for index in range(3):
            if index < len(ranking_data):
                member, time_str = ranking_data[index]
                body += (
                    f"ᯓ★ {member.mention} 𖦹˙— **Top #{index+1}** {medals[index]}\n"
                    f"- {time_str}\n\n"
                )
            else:
                # Preencher com usuário vazio
                body += (
                    f"ᯓ★ @usuário 𖦹˙— **Top #{index+1}** {medals[index]}\n"
                    f"- 0h 0m\n\n"
                )

        return header + body