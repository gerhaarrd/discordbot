import discord


class ColorsView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)    
    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content="﹕🌈 𐔌・𝐂𝐎𝐑𝐄𝐒 𝐁𝐎𝐎𝐒𝐓𝐄𝐑・꒱\n˗ˏˋ ｡𖦹 **As cores daqui são especiais**, reservadas apenas aos que fortalecem o Soul com seu impulso. No 𝐑𝐞𝐢𝐧𝐨 𝐝𝐨𝐬 𝐕𝐞𝐧𝐭𝐨𝐬, esses viajantes ganham acesso a tons raros, feitos da mesma brisa que move as nuvens mais altas. Cada reação desbloqueia uma cor única, marcando seu nome com o brilho de quem sustenta a magia do lugar. 🍓 ｡˚꩜"),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1469429794818097172/Picsart_26-02-06_17-29-11-387.png?ex=6987a0a3&is=69864f23&hm=47346519a427180b092f40b6ce840429f0fd050d224c5e0d2cd3c8b2d696bd43&",
            ),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
        discord.ui.TextDisplay(content="###  ╰୭ ˚𝐂𝐎𝐑𝐄𝐒... ᵎᵎ\n── .✦ <@&1439110891659329536> ⭑.ᐟ\n── .✦ <@&1439111576090050760> ⭑.ᐟ\n── .✦ <@&1439113714002297014> ⭑.ᐟ\n── .✦ <@&1439114721360875530> ⭑.ᐟ\n── .✦ <@&1439115506048303124> ⭑.ᐟ\n── .✦ <@&1439301268429340894> ⭑.ᐟ\n── .✦ <@&1439301747364597925> ⭑.ᐟ\n── .✦ <@&1439302494109827284> ⭑.ᐟ"),
        discord.ui.ActionRow(
                discord.ui.Select(
                    custom_id="2a5a321f1e4e4d19d38516e4706b81a3",
                    options=[
                        discord.SelectOption(
                            label="˚⋆🍪｡𝐝𝐨𝐮𝐫𝐚𝐝𝐨ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="828e33616ea04bf8d9fb5fd31422561d",
                        ),
                        discord.SelectOption(
                            label="˚⋆💜｡𝐯𝐢𝐨𝐥𝐞𝐭𝐚ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="bc10cea34b4d4d43b896a981daba0ab4",
                        ),
                        discord.SelectOption(
                            label="˚⋆🌪｡𝐩𝐫𝐞𝐭𝐨ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="a8306ca7c7d84581bab0403a4d3b8db4",
                        ),
                        discord.SelectOption(
                            label="˚⋆🍙｡𝐛𝐫𝐚𝐧𝐜𝐨ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="c66eaffd958f45ea938a92b938500a07",
                        ),
                        discord.SelectOption(
                            label="˚⋆☘️｡𝐜𝐢𝐚𝐧𝐨ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="0daeb82366fe4056817da233d611ccca",
                        ),
                        discord.SelectOption(
                            label="˚⋆🍷｡𝐛𝐨𝐫𝐝𝐨ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="3685ca1593db4d8286b71cec7cdcab85",
                        ),
                        discord.SelectOption(
                            label="˚⋆🎀｡𝐦𝐚𝐠𝐞𝐭𝐚ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="98a99cb9e0ec4161c738971d410f7e0b",
                        ),
                        discord.SelectOption(
                            label="˚⋆🐳｡𝐚𝐳𝐮𝐥-𝐦𝐚𝐫𝐢𝐧𝐡𝐨ᵇᵒᵒˢᵗᵉʳ𖦹.ᡣ𐭩˚",
                            value="4edcfc2a198e44ddc88182e73c405a9d",
                        ),
                    ],
                ),
        ),
        accent_colour=discord.Colour(15742293),
    )