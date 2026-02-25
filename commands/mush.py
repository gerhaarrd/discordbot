import discord
import json
import os
from discord.ext import commands
from discord import app_commands

ADMIN_ROLE_ID = [1404088289610301441, 1459225578304569532]
MUSHROOM_ROLES = [
    1475153859776221194, 
    1475154995778420849, 
    1475156042022125729, 
    1475156211409358984, 
    1475156474136367286
]
 
USAGE_FILE = "mushadd_usage.json"

def load_usage():
    """Carrega os dados de uso do arquivo JSON."""
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                usage = {int(k): v for k, v in data.items()}
                return usage, {}
        except Exception as e:
            print(f"Erro ao carregar arquivo de uso: {e}")
            return {}, {}
    return {}, {}

def save_usage(usage_data, relations_data):
    """Salva os dados de uso no arquivo JSON."""
    try:
        optimized_data = {str(k): v for k, v in usage_data.items()}
        with open(USAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, separators=(',', ':'))
    except Exception as e:
        print(f"Erro ao salvar arquivo de uso: {e}")

mushadd_usage, mushadd_relations = load_usage()

async def register(bot):
    @bot.tree.command(name="mushadd", description="Adiciona um usuário a um cargo de cogumelos", guild=discord.Object(id=1389947780683796701))
    @app_commands.describe(
        usuario="Usuário que receberá o cargo",
        cargo="Cargo específico para adicionar"
    )
    async def mushadd(interaction: discord.Interaction, usuario: discord.Member, cargo: discord.Role):
        admin_role = any(interaction.guild.get_role(role_id) in interaction.user.roles for role_id in ADMIN_ROLE_ID)
        if not admin_role:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ Você não pode adicionar cargo a si mesmo!", ephemeral=True)
            return
        
        for role_id in MUSHROOM_ROLES:
            role = interaction.guild.get_role(role_id)
            if role and role in usuario.roles:
                await interaction.response.send_message(f"❌ {usuario.mention} já tem um sticker! Cada pessoa só pode ter um.", ephemeral=True)
                return
        
        if cargo.id not in MUSHROOM_ROLES:
            await interaction.response.send_message("❌ Este cargo não está na lista de stickers!", ephemeral=True)
            return
        
        try:
            await usuario.add_roles(cargo)
            
            mushadd_usage[usuario.id] = True 
            
            save_usage(mushadd_usage, mushadd_relations)
            
            await interaction.response.send_message(f"✅ Sticker {cargo.mention} adicionado para {usuario.mention}!", ephemeral=True)
                
        except discord.Forbidden:
            print("Erro: Sem permissão para adicionar sticker")
            await interaction.response.send_message("❌ Não tenho permissão para adicionar este sticker!", ephemeral=True)
        except Exception as e:
            print(f"Erro ao adicionar sticker: {e}")
            await interaction.response.send_message(f"❌ Erro ao adicionar sticker: {e}", ephemeral=True)

    @bot.tree.command(name="mushremove", description="Remove todos os stickers de um usuário", guild=discord.Object(id=1389947780683796701))
    @app_commands.describe(
        usuario="Usuário que terá os stickers removidos"
    )
    async def mushremove(interaction: discord.Interaction, usuario: discord.Member):
        admin_role = any(interaction.guild.get_role(role_id) in interaction.user.roles for role_id in ADMIN_ROLE_ID)
        if not admin_role:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
            return
        
        roles_to_remove = []
        for role_id in MUSHROOM_ROLES:
            role = interaction.guild.get_role(role_id)
            if role and role in usuario.roles:
                roles_to_remove.append(role)
        
        if not roles_to_remove:
            await interaction.response.send_message(f"❌ {usuario.mention} não tem nenhum sticker para remover!", ephemeral=True)
            return
        
        try:
            await usuario.remove_roles(*roles_to_remove)
            
            if usuario.id in mushadd_usage:
                del mushadd_usage[usuario.id]
            
            save_usage(mushadd_usage, mushadd_relations)
            
            await interaction.response.send_message(f"✅ Todos os stickers removidos de {usuario.mention}!", ephemeral=True)
            
        except Exception as e:
            print(f"Erro ao remover stickers: {e}")
            await interaction.response.send_message(f"❌ Erro ao remover stickers: {e}", ephemeral=True)