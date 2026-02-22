import discord
import json
import os
from discord.ext import commands
from discord import app_commands

ADMIN_ROLE_ID = 1459225578304569532
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
                usage = {}
                relations = {}
                
                for key, value in data.items():
                    if key.startswith("_rel_"):
                        receiver_id = int(key[5:])
                        relations[receiver_id] = int(value)
                    else:
                        usage[int(key)] = value
                
                return usage, relations
        except Exception as e:
            print(f"Erro ao carregar arquivo de uso: {e}")
            return {}, {}
    return {}, {}

def save_usage(usage_data, relations_data):
    """Salva os dados de uso e relações no arquivo JSON."""
    try:
        combined_data = {}
        
        for k, v in usage_data.items():
            combined_data[str(k)] = v
        
        for receiver_id, giver_id in relations_data.items():
            combined_data[f"_rel_{receiver_id}"] = giver_id
        
        with open(USAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, separators=(',', ':'))
    except Exception as e:
        print(f"Erro ao salvar arquivo de uso: {e}")

mushadd_usage, mushadd_relations = load_usage()

async def register(bot):
    @bot.tree.command(name="mushadd", description="Adiciona um usuário a um cargo de cogumelos")
    @app_commands.describe(
        usuario="Usuário que receberá o cargo",
        cargo="Cargo específico para adicionar"
    )
    async def mushadd(interaction: discord.Interaction, usuario: discord.Member, cargo: discord.Role):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
            return
        
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ Você não pode adicionar cargo a si mesmo!", ephemeral=True)
            return
        
        user_id = interaction.user.id
        if user_id in mushadd_usage:
            receiver_id = None
            for rid, gid in mushadd_relations.items():
                if gid == user_id:
                    receiver_id = rid
                    break
            
            if receiver_id:
                receiver_member = interaction.guild.get_member(receiver_id)
                if receiver_member:
                    await interaction.response.send_message(f"❌ {receiver_member.mention} já recebeu o cargo {cargo.mention} de você! Não pode usar novamente.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Você já usou este comando! Não pode usar novamente.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Você já usou este comando! Não pode usar novamente.", ephemeral=True)
            return
        
        if cargo.id not in MUSHROOM_ROLES:
            await interaction.response.send_message("❌ Este cargo não está na lista de cargos de cogumelos!", ephemeral=True)
            return
        
        if cargo in usuario.roles:
            await interaction.response.send_message(f"❌ {usuario.mention} já tem o cargo {cargo.mention}!", ephemeral=True)
            return
        
        try:
            print(f"Tentando adicionar cargo {cargo.id} ({cargo.name}) para usuário {usuario.id} ({usuario.name})")
            await usuario.add_roles(cargo)
            print(f"Cargo adicionado com sucesso")
            
            mushadd_usage[user_id] = True
            
            mushadd_relations[usuario.id] = user_id
            
            save_usage(mushadd_usage, mushadd_relations)
            
            await interaction.response.send_message(f"✅ Cargo {cargo.mention} adicionado para {usuario.mention}!", ephemeral=True)
                
        except discord.Forbidden:
            print("Erro: Sem permissão para adicionar cargo")
            await interaction.response.send_message("❌ Não tenho permissão para adicionar este cargo!", ephemeral=True)
        except Exception as e:
            print(f"Erro ao adicionar cargo: {e}")
            await interaction.response.send_message(f"❌ Erro ao adicionar cargo: {e}", ephemeral=True)

    @bot.tree.command(name="mushremove", description="Remove todos os cargos de cogumelos de um usuário")
    @app_commands.describe(
        usuario="Usuário que terá os cargos removidos"
    )
    async def mushremove(interaction: discord.Interaction, usuario: discord.Member):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
            return
        
        roles_to_remove = []
        for role_id in MUSHROOM_ROLES:
            role = interaction.guild.get_role(role_id)
            if role and role in usuario.roles:
                roles_to_remove.append(role)
        
        if not roles_to_remove:
            await interaction.response.send_message(f"❌ {usuario.mention} não tem nenhum cargo de cogumelos para remover!", ephemeral=True)
            return
        
        try:
            await usuario.remove_roles(*roles_to_remove)
            
            if usuario.id in mushadd_relations:
                giver_id = mushadd_relations[usuario.id]
                if giver_id in mushadd_usage:
                    del mushadd_usage[giver_id]
            
            if usuario.id in mushadd_relations:
                del mushadd_relations[usuario.id]
            
            save_usage(mushadd_usage, mushadd_relations)
            
            await interaction.response.send_message(f"✅ Cargos de cogumelos removidos de {usuario.mention}! Quem deu o cargo pode usar novamente.", ephemeral=True)
            
        except Exception as e:
            print(f"Erro ao remover cargos: {e}")
            await interaction.response.send_message(f"❌ Erro ao remover cargos: {e}", ephemeral=True)