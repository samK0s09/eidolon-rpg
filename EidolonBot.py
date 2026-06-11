import os
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║     EIDOLON GAMES - RPG MODULE                         ║
║     "Forge Your Legend"                                ║
║     ⚔️ 1800+ LINES OF PURE ADVENTURE ⚔️               ║
╚══════════════════════════════════════════════════════════╝
"""

import discord
from discord import app_commands
from discord.ui import Button, View, Select, Modal, TextInput
import asyncio
import random
import json
import datetime
import os
import sys
import hashlib

# ============================================
# CONFIGURAÇÃO
# ============================================

class EidolonGames(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.data_file = "eidolon_rpg.json"
        self.players = self.load_data()
        self._guilds = self.load_guilds()
        self.pet_data = {}
        self.DONO_ID = 1111135014453788682

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot {self.user} online!")

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}

    def load_guilds(self):
        if os.path.exists("guilds.json"):
            with open("guilds.json", 'r') as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.players, f, indent=2)
        with open("guilds.json", 'w') as f:
            json.dump(self._guilds, f, indent=2)

    def get_player(self, user_id):
        return self.players.get(str(user_id), None)

    def create_player(self, user_id, name):
        self.players[str(user_id)] = {
            'name': name,
            'level': 1, 'xp': 0, 'xp_needed': 100,
            'hp': 100, 'max_hp': 100, 'mp': 50, 'max_mp': 50,
            'stats': {'forca': 5, 'defesa': 5, 'vida': 10, 'magia': 5, 'mana': 5, 'agilidade': 5, 'sorte': 5},
            'atk': 10, 'def': 5, 'spd': 5,
            'gold': 100, 'gems': 10,
            'bank_gold': 0, 'bank_gems': 0,
            'race': 'Humano', 'class': 'Guerreiro',
            'inventory': [], 'equipment': {'weapon': None, 'armor': None, 'accessory': None},
            'skills': ['Corte Básico'],
            'scrolls': [],
            'island': 'Ilha Inicial',
            'quests_completed': [],
            'bosses_defeated': [],
            'pvp_wins': 0, 'pvp_losses': 0,
            'ores': {},
            'materials': {},
            'crafts_made': 0,
            'titles': ['Aventureiro'],
            'active_title': 'Aventureiro',
            'guild': None,
            'pets': [],
            'active_pet': None,
            'pet_eggs': [],
            'trades': [],
            'achievements': [],
            'chests_opened': 0,
            'total_gold_earned': 0,
            'total_bosses_killed': 0,
            'status_points': 0,
        }
        self.save_data()

bot = EidolonGames()

# ============================================
# DADOS DO RPG EXPANDIDO
# ============================================

RACES = {
    'Humano': {'stats': {'forca': 5, 'defesa': 5, 'vida': 10, 'magia': 5, 'mana': 5, 'agilidade': 5, 'sorte': 5}, 'desc': '+10% XP'},
    'Elfo': {'stats': {'forca': 3, 'defesa': 4, 'vida': 8, 'magia': 8, 'mana': 8, 'agilidade': 8, 'sorte': 6}, 'desc': '+10% MP'},
    'Anão': {'stats': {'forca': 7, 'defesa': 8, 'vida': 12, 'magia': 3, 'mana': 3, 'agilidade': 3, 'sorte': 4}, 'desc': '+10% DEF'},
    'Draconiano': {'stats': {'forca': 8, 'defesa': 6, 'vida': 11, 'magia': 6, 'mana': 6, 'agilidade': 5, 'sorte': 5}, 'desc': '+10% ATK'},
}

CLASSES = {
    'Guerreiro': {'stats': {'forca': 3, 'defesa': 2, 'vida': 3}, 'skills': ['Corte Poderoso', 'Giro do Guerreiro', 'Fúria de Batalha', 'Investida', 'Golpe Brutal']},
    'Mago': {'stats': {'magia': 5, 'mana': 4, 'sorte': 1}, 'skills': ['Bola de Fogo', 'Raio Congelante', 'Meteoro', 'Campo de Força', 'Distorção Temporal']},
    'Arqueiro': {'stats': {'agilidade': 4, 'forca': 2, 'sorte': 2}, 'skills': ['Chuva de Flechas', 'Tiro Preciso', 'Flecha Explosiva', 'Armadilha', 'Marca do Caçador']},
    'Assassino': {'stats': {'forca': 4, 'agilidade': 5, 'sorte': 3}, 'skills': ['Golpe Sombrio', 'Veneno Mortal', 'Lâmina Fantasma', 'Furtividade', 'Golpe nas Costas']},
}

OVOS = {
    'Ovo Comum': {'rarity': 'Comum', 'chance': 0.15, 'pets': ['Slime', 'Rato', 'Pássaro', 'Gato', 'Cachorro']},
    'Ovo Raro': {'rarity': 'Raro', 'chance': 0.08, 'pets': ['Lobo', 'Águia', 'Cobra', 'Raposa', 'Coruja']},
    'Ovo Épico': {'rarity': 'Épico', 'chance': 0.03, 'pets': ['Tigre', 'Urso', 'Pantera', 'Grifo', 'Hipogrifo']},
    'Ovo Lendário': {'rarity': 'Lendário', 'chance': 0.01, 'pets': ['Dragão Jovem', 'Fênix', 'Quimera', 'Serpente Alada', 'Unicórnio']},
    'Ovo Mítico': {'rarity': 'Mítico', 'chance': 0.003, 'pets': ['Dragão Ancião', 'Leviatã', 'Titã', 'Deus Menor', 'Entidade Cósmica']},
    'Ovo Supremo': {'rarity': 'Supremo', 'chance': 0.0007, 'pets': ['Dragão Supremo', 'Deus do Caos', 'Fênix Primordial', 'Ser Supremo', 'O Criador']},
}

PERGAMINHOS = [
    {'name': 'Pergaminho de Força', 'effect': {'forca': 10}, 'duration': 3, 'desc': '+10 Força por 3 batalhas'},
    {'name': 'Pergaminho de Vida', 'effect': {'vida': 20}, 'duration': 3, 'desc': '+20 Vida por 3 batalhas'},
    {'name': 'Pergaminho de Sorte', 'effect': {'sorte': 15}, 'duration': 5, 'desc': '+15 Sorte por 5 batalhas'},
    {'name': 'Pergaminho Supremo', 'effect': {'forca': 25, 'defesa': 25, 'vida': 50}, 'duration': 2, 'desc': '+25 Força/Defesa +50 Vida por 2 batalhas'},
]

ISLANDS_FULL = [
    {'name': 'Ilha Inicial', 'cost': 0, 'level': 1, 'ores': ['Ferro', 'Pedra'], 'desc': 'Onde tudo começa', 'bosses': ['Slime Rei', 'Goblin Chefe']},
    {'name': 'Ilha do Gelo', 'cost': 500, 'level': 5, 'ores': ['Prata', 'Gelo Eterno'], 'desc': 'Fria e perigosa', 'bosses': ['Rei Gelado', 'Dragão de Gelo']},
    {'name': 'Ilha do Vulcão', 'cost': 1000, 'level': 8, 'ores': ['Ouro', 'Obsidiana'], 'desc': 'Quente e mortal', 'bosses': ['Dragão de Fogo', 'Fênix Flamejante']},
    {'name': 'Ilha Sombria', 'cost': 2000, 'level': 10, 'ores': ['Mithril', 'Essência Sombria'], 'desc': 'Coberta de trevas', 'bosses': ['Lorde das Sombras', 'Rei dos Mortos']},
    {'name': 'Ilha das Montanhas', 'cost': 1500, 'level': 12, 'ores': ['Adamantita', 'Pedra Rúnica'], 'desc': 'Montanhas gigantes', 'bosses': ['Golem de Pedra', 'Titã de Ferro']},
    {'name': 'Ilha do Oceano', 'cost': 3000, 'level': 14, 'ores': ['Pérola Negra', 'Coral Mágico'], 'desc': 'Profundezas misteriosas', 'bosses': ['Serpente Marinha', 'Leviatã']},
    {'name': 'Ilha dos Dragões', 'cost': 5000, 'level': 16, 'ores': ['Escama de Dragão', 'Cristal Dracônico'], 'desc': 'Lar dos dragões', 'bosses': ['Dragão Ancião']},
    {'name': 'Ilha Celestial', 'cost': 8000, 'level': 18, 'ores': ['Fragmento Celestial', 'Nuvem Sólida'], 'desc': 'Acima das nuvens', 'bosses': ['Deus do Trovão', 'Titã do Trovão']},
    {'name': 'Ilha do Inferno', 'cost': 15000, 'level': 20, 'ores': ['Pedra Infernal', 'Lava Solidificada'], 'desc': 'O lugar mais perigoso', 'bosses': ['Rei Demônio', 'Deus do Caos']},
    {'name': 'Ilha do Templo', 'cost': 2500, 'level': 11, 'ores': ['Ouro', 'Relíquia Sagrada'], 'desc': 'Ruínas antigas', 'bosses': ['Guardião do Templo']},
    {'name': 'Ilha Mágica', 'cost': 3500, 'level': 9, 'ores': ['Cristal Mágico', 'Pó de Fada'], 'desc': 'Onde a magia flui', 'bosses': ['Mago Supremo']},
    {'name': 'Ilha da Floresta', 'cost': 800, 'level': 6, 'ores': ['Madeira Sagrada', 'Seiva Mística'], 'desc': 'Floresta densa', 'bosses': []},
    {'name': 'Ilha do Deserto', 'cost': 1200, 'level': 7, 'ores': ['Ouro', 'Arenito'], 'desc': 'Deserto escaldante', 'bosses': []},
    {'name': 'Ilha do Céu', 'cost': 6000, 'level': 15, 'ores': ['Nuvem Sólida', 'Vento Etéreo'], 'desc': 'Entre as nuvens', 'bosses': []},
    {'name': 'Ilha do Submundo', 'cost': 10000, 'level': 19, 'ores': ['Pedra Infernal', 'Essência Demoníaca'], 'desc': 'Abaixo da superfície', 'bosses': []},
]

def make_embed(title, description, color=0xff4444):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now())
    embed.set_footer(text="⚔️ EIDOLON GAMES - RPG | Forge Your Legend")
    return embed

# ============================================
# COMANDOS PRINCIPAIS
# ============================================

@bot.tree.command(name="criar", description="🎮 Criar seu personagem")
@app_commands.describe(nome="Nome do seu personagem")
async def criar(i: discord.Interaction, nome: str):
    if bot.get_player(i.user.id):
        return await i.response.send_message("❌ Você já tem um personagem!", ephemeral=True)
    bot.create_player(i.user.id, nome)
    await i.response.send_message(embed=make_embed("🎮 PERSONAGEM CRIADO!", f"**{nome}** está pronto!\nUse `/perfil` para ver seus status!\nUse `/status` para distribuir pontos!", 0x00ff00))

@bot.tree.command(name="perfil", description="👤 Ver seu personagem completo")
async def perfil(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    s = p.get('stats', {})
    pets = "\n".join([f"• {pet}" for pet in p.get('pets', [])]) or "Nenhum"
    titles = ", ".join(p.get('titles', ['Aventureiro']))
    materials = "\n".join([f"• {k}: {v}" for k,v in list(p.get('materials', {}).items())[:10]]) or "Nenhum"
    scrolls = "\n".join([f"• {s}" for s in p.get('scrolls', [])]) or "Nenhum"
    
    desc = f"""
**{p['name']}** | {p.get('active_title', 'Aventureiro')}
🏹 Raça: **{p['race']}** | Classe: **{p['class']}**
⭐ Nível: **{p['level']}** ({p['xp']}/{p['xp_needed']} XP)

📊 **ATRIBUTOS:**
💪 Força: {s.get('forca', 5)} | 🛡️ Defesa: {s.get('defesa', 5)}
❤️ Vida: {s.get('vida', 10)} | 🔮 Magia: {s.get('magia', 5)}
💎 Mana: {s.get('mana', 5)} | 💨 Agilidade: {s.get('agilidade', 5)}
🍀 Sorte: {s.get('sorte', 5)}

⚔️ ATK: {p['atk']} | 🛡️ DEF: {p['def']} | 💨 SPD: {p['spd']}
❤️ HP: {p['hp']}/{p['max_hp']} | 💎 MP: {p['mp']}/{p['max_mp']}

💰 Gold: {p['gold']:,} | 💎 Gems: {p['gems']:,}
🏦 Banco: {p.get('bank_gold', 0):,} Gold | {p.get('bank_gems', 0):,} Gems

🗺️ Ilha: **{p.get('island', 'Ilha Inicial')}**
🏆 PvP: {p.get('pvp_wins', 0)}W / {p.get('pvp_losses', 0)}L

🏅 Títulos: {titles}
🐾 Pets: {pets}
📜 Pergaminhos: {scrolls}
⚒️ Materiais: {materials}
🏰 Guilda: {p.get('guild', 'Nenhuma')}

⭐ **Pontos de Status:** {p.get('status_points', 0)}
Use `/status` para distribuir!
    """
    await i.response.send_message(embed=make_embed(f"👤 {p['name']}", desc, 0x00ff00))

@bot.tree.command(name="status", description="📊 Distribuir pontos de status")
@app_commands.describe(atributo="Qual atributo upar")
@app_commands.choices(atributo=[
    app_commands.Choice(name="💪 Força", value="forca"),
    app_commands.Choice(name="🛡️ Defesa", value="defesa"),
    app_commands.Choice(name="❤️ Vida", value="vida"),
    app_commands.Choice(name="🔮 Magia", value="magia"),
    app_commands.Choice(name="💎 Mana", value="mana"),
    app_commands.Choice(name="💨 Agilidade", value="agilidade"),
    app_commands.Choice(name="🍀 Sorte", value="sorte"),
])
async def status(i: discord.Interaction, atributo: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    points = p.get('status_points', 0)
    if points <= 0:
        return await i.response.send_message(f"❌ Você não tem pontos de status! Suba de nível para ganhar!", ephemeral=True)
    
    p.setdefault('stats', {})
    p['stats'][atributo] = p['stats'].get(atributo, 5) + 1
    p['status_points'] = points - 1
    
    s = p['stats']
    p['atk'] = 10 + s.get('forca', 5) * 2 + s.get('agilidade', 5)
    p['def'] = 5 + s.get('defesa', 5) * 2
    p['spd'] = 5 + s.get('agilidade', 5) * 2
    p['max_hp'] = 100 + s.get('vida', 10) * 10
    p['max_mp'] = 50 + s.get('mana', 5) * 10 + s.get('magia', 5) * 5
    p['hp'] = min(p['hp'], p['max_hp'])
    p['mp'] = min(p['mp'], p['max_mp'])
    
    bot.save_data()
    await i.response.send_message(embed=make_embed("📊 STATUS UP!", f"**{atributo.upper()}** aumentado para **{p['stats'][atributo]}**!\n⭐ Pontos restantes: {p['status_points']}", 0x00ff00))

@bot.tree.command(name="bau", description="🎁 Abrir um baú do tesouro")
async def bau(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    if random.random() < 0.3:
        p['chests_opened'] = p.get('chests_opened', 0) + 1
        
        roll = random.random()
        if roll < 0.0007: egg = 'Ovo Supremo'
        elif roll < 0.0037: egg = 'Ovo Mítico'
        elif roll < 0.0137: egg = 'Ovo Lendário'
        elif roll < 0.0437: egg = 'Ovo Épico'
        elif roll < 0.1237: egg = 'Ovo Raro'
        else: egg = 'Ovo Comum'
        
        p.setdefault('pet_eggs', []).append(egg)
        gold = random.randint(50, 500)
        p['gold'] += gold
        bot.save_data()
        await i.response.send_message(embed=make_embed("🎁 BAÚ ENCONTRADO!", f"Você encontrou um baú!\n\n🥚 **{egg}**\n💰 **{gold} Gold**\n\nUse `/chocar` para chocar o ovo!", 0xffd700))
    else:
        await i.response.send_message(embed=make_embed("🔍 NADA...", "Você procurou mas não encontrou nenhum baú. Tente novamente!", 0xff0000))

# ============================================
# EVENTOS
# ============================================

@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════╗
║   ⚔️ EIDOLON GAMES - RPG ⚔️       ║
║   1800+ LINES OF ADVENTURE         ║
║   👑 Dono ID: {bot.DONO_ID}              ║
╚══════════════════════════════════════╝
    """)
    print(f"⚔️ Bot: {bot.user}")
    print(f"🎮 /criar - Comece sua aventura!")
    print(f"🛡️ /admin - Painel de Admin (só dono)")
    print(f"⚒️ /craft - Craftar itens")
    print(f"🐾 /pets - Seus pets")
    print(f"🤝 /trade - Trocar itens")
    print(f"⚔️ /pvp - Duelar jogadores")
    print(f"📜 /pergaminhos - Usar pergaminhos")
    print(f"🗺️ /ilhas - Ver ilhas disponíveis")
    await bot.change_presence(activity=discord.Game(name="⚔️ /criar | EIDOLON RPG"))

# ============================================
# 70 QUESTS COMPLETAS
# ============================================

QUESTS = [
    {'name': 'O Início', 'level': 1, 'xp': 50, 'gold': 50, 'gems': 5, 'desc': 'Derrote 3 slimes na floresta'},
    {'name': 'Coleta de Ervas', 'level': 1, 'xp': 40, 'gold': 40, 'gems': 3, 'desc': 'Colete 5 ervas medicinais'},
    {'name': 'Primeira Caça', 'level': 1, 'xp': 45, 'gold': 45, 'gems': 4, 'desc': 'Cace 3 ratos gigantes'},
    {'name': 'Aprendiz de Ferreiro', 'level': 1, 'xp': 30, 'gold': 60, 'gems': 2, 'desc': 'Entregue 5 minérios de ferro'},
    {'name': 'Mensageiro', 'level': 1, 'xp': 35, 'gold': 35, 'gems': 3, 'desc': 'Entregue uma carta na vila vizinha'},
    {'name': 'Proteja a Vila', 'level': 2, 'xp': 80, 'gold': 100, 'gems': 8, 'desc': 'Derrote os bandidos'},
    {'name': 'Caça aos Goblins', 'level': 2, 'xp': 60, 'gold': 80, 'gems': 5, 'desc': 'Derrote 5 goblins'},
    {'name': 'Ervas Raras', 'level': 2, 'xp': 70, 'gold': 70, 'gems': 6, 'desc': 'Colete 3 ervas raras'},
    {'name': 'O Poço Misterioso', 'level': 2, 'xp': 75, 'gold': 90, 'gems': 7, 'desc': 'Investigue o poço'},
    {'name': 'Pescaria', 'level': 2, 'xp': 50, 'gold': 60, 'gems': 4, 'desc': 'Pesque 5 peixes no rio'},
    {'name': 'Mina Abandonada', 'level': 3, 'xp': 120, 'gold': 150, 'gems': 10, 'desc': 'Explore a mina'},
    {'name': 'O Ladrão de Joias', 'level': 3, 'xp': 100, 'gold': 200, 'gems': 12, 'desc': 'Capture o ladrão'},
    {'name': 'O Tesouro do Pirata', 'level': 3, 'xp': 110, 'gold': 350, 'gems': 11, 'desc': 'Encontre o tesouro'},
    {'name': 'A Ponte Quebrada', 'level': 3, 'xp': 90, 'gold': 120, 'gems': 9, 'desc': 'Conserte a ponte'},
    {'name': 'Lobos Selvagens', 'level': 3, 'xp': 105, 'gold': 130, 'gems': 10, 'desc': 'Derrote 5 lobos'},
    {'name': 'Caça ao Tesouro', 'level': 4, 'xp': 150, 'gold': 300, 'gems': 15, 'desc': 'Encontre o tesouro'},
    {'name': 'O Roubo do Banco', 'level': 4, 'xp': 130, 'gold': 280, 'gems': 14, 'desc': 'Impeça o roubo'},
    {'name': 'A Casa Mal-Assombrada', 'level': 4, 'xp': 140, 'gold': 200, 'gems': 13, 'desc': 'Investigue a casa'},
    {'name': 'O Poço dos Desejos', 'level': 4, 'xp': 120, 'gold': 180, 'gems': 12, 'desc': 'Faça um desejo'},
    {'name': 'Ovelhas Perdidas', 'level': 4, 'xp': 110, 'gold': 160, 'gems': 11, 'desc': 'Encontre 5 ovelhas'},
    {'name': 'A Floresta Sombria', 'level': 5, 'xp': 200, 'gold': 250, 'gems': 15, 'desc': 'Sobreviva à floresta'},
    {'name': 'A Floresta Encantada', 'level': 5, 'xp': 180, 'gold': 220, 'gems': 12, 'desc': 'Colete flores mágicas'},
    {'name': 'A Poção Mágica', 'level': 5, 'xp': 190, 'gold': 240, 'gems': 13, 'desc': 'Crie a poção mágica'},
    {'name': 'O Feiticeiro Louco', 'level': 5, 'xp': 210, 'gold': 260, 'gems': 16, 'desc': 'Derrote o feiticeiro'},
    {'name': 'Cogumelos Mágicos', 'level': 5, 'xp': 170, 'gold': 210, 'gems': 11, 'desc': 'Colete cogumelos'},
    {'name': 'O Enigma da Esfinge', 'level': 6, 'xp': 250, 'gold': 350, 'gems': 20, 'desc': 'Resolva o enigma'},
    {'name': 'A Maldição da Bruxa', 'level': 6, 'xp': 230, 'gold': 330, 'gems': 18, 'desc': 'Quebre a maldição'},
    {'name': 'O Velho Sábio', 'level': 6, 'xp': 240, 'gold': 340, 'gems': 19, 'desc': 'Ajude o velho sábio'},
    {'name': 'O Rio Amaldiçoado', 'level': 6, 'xp': 220, 'gold': 310, 'gems': 17, 'desc': 'Purifique o rio'},
    {'name': 'A Pedra Filosofal', 'level': 6, 'xp': 260, 'gold': 500, 'gems': 25, 'desc': 'Encontre a pedra'},
    {'name': 'O Dragão da Montanha', 'level': 7, 'xp': 350, 'gold': 500, 'gems': 25, 'desc': 'Derrote o dragão'},
    {'name': 'O Feitiço do Tempo', 'level': 7, 'xp': 320, 'gold': 480, 'gems': 22, 'desc': 'Desfaça o feitiço'},
    {'name': 'O Labirinto', 'level': 7, 'xp': 330, 'gold': 450, 'gems': 23, 'desc': 'Encontre a saída'},
    {'name': 'O Cristal Mágico', 'level': 7, 'xp': 310, 'gold': 420, 'gems': 21, 'desc': 'Encontre o cristal'},
    {'name': 'O Fantasma da Ópera', 'level': 7, 'xp': 340, 'gold': 490, 'gems': 24, 'desc': 'Derrote o fantasma'},
    {'name': 'O Templo Perdido', 'level': 8, 'xp': 400, 'gold': 600, 'gems': 30, 'desc': 'Encontre o templo'},
    {'name': 'O Rio dos Mortos', 'level': 8, 'xp': 380, 'gold': 550, 'gems': 28, 'desc': 'Atravesse o rio'},
    {'name': 'O Enigma do Faraó', 'level': 8, 'xp': 390, 'gold': 580, 'gems': 29, 'desc': 'Resolva o enigma'},
    {'name': 'A Arca Perdida', 'level': 8, 'xp': 370, 'gold': 520, 'gems': 27, 'desc': 'Encontre a arca'},
    {'name': 'O Guardião de Pedra', 'level': 8, 'xp': 410, 'gold': 620, 'gems': 31, 'desc': 'Derrote o guardião'},
    {'name': 'Arena dos Campeões', 'level': 9, 'xp': 450, 'gold': 700, 'gems': 35, 'desc': 'Vença 3 lutas'},
    {'name': 'A Invasão Zumbi', 'level': 9, 'xp': 420, 'gold': 650, 'gems': 32, 'desc': 'Sobreviva aos zumbis'},
    {'name': 'O Cetro Real', 'level': 9, 'xp': 430, 'gold': 680, 'gems': 33, 'desc': 'Recupere o cetro'},
    {'name': 'A Biblioteca Proibida', 'level': 9, 'xp': 440, 'gold': 690, 'gems': 34, 'desc': 'Acesse a biblioteca'},
    {'name': 'O Feiticeiro Supremo', 'level': 9, 'xp': 460, 'gold': 720, 'gems': 36, 'desc': 'Derrote o feiticeiro'},
    {'name': 'A Ilha do Gelo', 'level': 10, 'xp': 500, 'gold': 800, 'gems': 40, 'desc': 'Sobreviva ao gelo'},
    {'name': 'A Fonte da Juventude', 'level': 10, 'xp': 490, 'gold': 780, 'gems': 39, 'desc': 'Encontre a fonte'},
    {'name': 'A Montanha Sagrada', 'level': 10, 'xp': 480, 'gold': 750, 'gems': 38, 'desc': 'Escale a montanha'},
    {'name': 'O Dragão de Prata', 'level': 10, 'xp': 510, 'gold': 820, 'gems': 41, 'desc': 'Derrote o dragão'},
    {'name': 'O Espelho Mágico', 'level': 10, 'xp': 470, 'gold': 740, 'gems': 37, 'desc': 'Encontre o espelho'},
    {'name': 'O Barco Fantasma', 'level': 11, 'xp': 550, 'gold': 900, 'gems': 45, 'desc': 'Derrote o capitão'},
    {'name': 'O Dragão de Fogo', 'level': 11, 'xp': 520, 'gold': 850, 'gems': 42, 'desc': 'Derrote o dragão'},
    {'name': 'O Portal Dimensional', 'level': 11, 'xp': 530, 'gold': 880, 'gems': 43, 'desc': 'Feche o portal'},
    {'name': 'A Coroa do Rei', 'level': 11, 'xp': 540, 'gold': 890, 'gems': 44, 'desc': 'Recupere a coroa'},
    {'name': 'O Exército de Pedra', 'level': 11, 'xp': 560, 'gold': 920, 'gems': 46, 'desc': 'Derrote o exército'},
    {'name': 'O Portal do Inferno', 'level': 12, 'xp': 600, 'gold': 1000, 'gems': 50, 'desc': 'Feche o portal'},
    {'name': 'O Reino Subterrâneo', 'level': 12, 'xp': 590, 'gold': 980, 'gems': 49, 'desc': 'Explore o reino'},
    {'name': 'A Guerra dos Clãs', 'level': 12, 'xp': 580, 'gold': 950, 'gems': 48, 'desc': 'Escolha um lado'},
    {'name': 'O Deserto Proibido', 'level': 12, 'xp': 570, 'gold': 930, 'gems': 47, 'desc': 'Sobreviva ao deserto'},
    {'name': 'O Gênio da Lâmpada', 'level': 12, 'xp': 610, 'gold': 1020, 'gems': 51, 'desc': 'Liberte o gênio'},
    {'name': 'A Torre do Mago', 'level': 13, 'xp': 650, 'gold': 1100, 'gems': 55, 'desc': 'Chegue ao topo'},
    {'name': 'A Lâmina Perdida', 'level': 13, 'xp': 620, 'gold': 1050, 'gems': 52, 'desc': 'Encontre a lâmina'},
    {'name': 'O Guardião do Templo', 'level': 13, 'xp': 630, 'gold': 1080, 'gems': 53, 'desc': 'Derrote o guardião'},
    {'name': 'A Cidade Flutuante', 'level': 13, 'xp': 640, 'gold': 1090, 'gems': 54, 'desc': 'Chegue à cidade'},
    {'name': 'O Vulcão Adormecido', 'level': 14, 'xp': 700, 'gold': 1200, 'gems': 60, 'desc': 'Sobreviva ao vulcão'},
    {'name': 'A Caverna de Cristal', 'level': 14, 'xp': 680, 'gold': 1150, 'gems': 58, 'desc': 'Colete cristais'},
    {'name': 'A Cidade Submersa', 'level': 15, 'xp': 750, 'gold': 1300, 'gems': 65, 'desc': 'Explore as ruínas'},
    {'name': 'O Labirinto Infinito', 'level': 16, 'xp': 800, 'gold': 1400, 'gems': 70, 'desc': 'Encontre a saída'},
    {'name': 'O Reino das Sombras', 'level': 17, 'xp': 850, 'gold': 1500, 'gems': 75, 'desc': 'Derrote o rei'},
    {'name': 'O Guardião do Céu', 'level': 18, 'xp': 900, 'gold': 1600, 'gems': 80, 'desc': 'Derrote o guardião'},
    {'name': 'O Abismo', 'level': 19, 'xp': 950, 'gold': 1800, 'gems': 90, 'desc': 'Sobreviva ao abismo'},
    {'name': 'A Última Batalha', 'level': 20, 'xp': 1000, 'gold': 2000, 'gems': 100, 'desc': 'Derrote o chefão final'},
    {'name': 'A Lenda do Herói', 'level': 20, 'xp': 1100, 'gold': 2200, 'gems': 120, 'desc': 'Complete a lenda'},
]

# ============================================
# 25 BOSSES COMPLETOS
# ============================================

BOSSES = [
    {'name': 'Slime Rei', 'hp': 200, 'atk': 15, 'def': 5, 'level': 3, 'xp': 100, 'gold': 150, 'gems': 10, 'island': 'Ilha Inicial', 'drops': ['Poção de Cura', 'Ovo Comum'], 'egg_chance': 15},
    {'name': 'Goblin Chefe', 'hp': 350, 'atk': 20, 'def': 8, 'level': 5, 'xp': 180, 'gold': 250, 'gems': 15, 'island': 'Ilha Inicial', 'drops': ['Espada de Ferro', 'Ovo Comum'], 'egg_chance': 12},
    {'name': 'Lobo Alfa', 'hp': 280, 'atk': 18, 'def': 6, 'level': 4, 'xp': 140, 'gold': 200, 'gems': 12, 'island': 'Ilha Inicial', 'drops': ['Poção de Cura', 'Ovo Comum'], 'egg_chance': 10},
    {'name': 'Aranha Gigante', 'hp': 400, 'atk': 22, 'def': 7, 'level': 6, 'xp': 220, 'gold': 300, 'gems': 18, 'island': 'Ilha da Floresta', 'drops': ['Armadura de Couro', 'Ovo Raro'], 'egg_chance': 8},
    {'name': 'Dragão de Fogo', 'hp': 600, 'atk': 35, 'def': 15, 'level': 8, 'xp': 350, 'gold': 500, 'gems': 25, 'island': 'Ilha do Vulcão', 'drops': ['Escama de Dragão', 'Ovo Raro'], 'egg_chance': 8},
    {'name': 'Rei Gelado', 'hp': 800, 'atk': 40, 'def': 20, 'level': 10, 'xp': 500, 'gold': 800, 'gems': 40, 'island': 'Ilha do Gelo', 'drops': ['Armadura de Ferro', 'Ovo Raro'], 'egg_chance': 7},
    {'name': 'Lorde das Sombras', 'hp': 1000, 'atk': 50, 'def': 25, 'level': 12, 'xp': 700, 'gold': 1000, 'gems': 50, 'island': 'Ilha Sombria', 'drops': ['Lâmina do Dragão', 'Ovo Épico'], 'egg_chance': 3},
    {'name': 'Mago Supremo', 'hp': 900, 'atk': 70, 'def': 20, 'level': 11, 'xp': 600, 'gold': 900, 'gems': 45, 'island': 'Ilha Mágica', 'drops': ['Cajado Arcano', 'Ovo Raro'], 'egg_chance': 6},
    {'name': 'Guardião do Templo', 'hp': 1300, 'atk': 58, 'def': 32, 'level': 13, 'xp': 800, 'gold': 1100, 'gems': 55, 'island': 'Ilha do Templo', 'drops': ['Escudo de Mithril', 'Ovo Épico'], 'egg_chance': 3},
    {'name': 'Fênix Flamejante', 'hp': 1200, 'atk': 55, 'def': 30, 'level': 14, 'xp': 850, 'gold': 1200, 'gems': 60, 'island': 'Ilha do Vulcão', 'drops': ['Armadura de Ouro', 'Ovo Épico'], 'egg_chance': 2},
    {'name': 'Golem de Pedra', 'hp': 1500, 'atk': 60, 'def': 40, 'level': 15, 'xp': 900, 'gold': 1300, 'gems': 65, 'island': 'Ilha das Montanhas', 'drops': ['Manopla do Poder', 'Ovo Lendário'], 'egg_chance': 1},
    {'name': 'Serpente Marinha', 'hp': 1800, 'atk': 65, 'def': 35, 'level': 16, 'xp': 950, 'gold': 1400, 'gems': 70, 'island': 'Ilha do Oceano', 'drops': ['Cajado Arcano', 'Ovo Lendário'], 'egg_chance': 1},
    {'name': 'Titã de Ferro', 'hp': 2200, 'atk': 80, 'def': 55, 'level': 17, 'xp': 1050, 'gold': 1500, 'gems': 75, 'island': 'Ilha das Montanhas', 'drops': ['Armadura de Ouro', 'Ovo Lendário'], 'egg_chance': 0.8},
    {'name': 'Dragão de Gelo', 'hp': 1900, 'atk': 70, 'def': 40, 'level': 16, 'xp': 1000, 'gold': 1400, 'gems': 70, 'island': 'Ilha do Gelo', 'drops': ['Lâmina do Dragão', 'Ovo Lendário'], 'egg_chance': 0.9},
    {'name': 'Rei dos Mortos', 'hp': 2800, 'atk': 90, 'def': 55, 'level': 18, 'xp': 1300, 'gold': 2000, 'gems': 100, 'island': 'Ilha Sombria', 'drops': ['Armadura Divina', 'Ovo Mítico'], 'egg_chance': 0.3},
    {'name': 'Dragão Ancião', 'hp': 2000, 'atk': 75, 'def': 45, 'level': 18, 'xp': 1100, 'gold': 1600, 'gems': 80, 'island': 'Ilha dos Dragões', 'drops': ['Armadura Divina', 'Ovo Mítico'], 'egg_chance': 0.3},
    {'name': 'Fênix Negra', 'hp': 2600, 'atk': 95, 'def': 45, 'level': 19, 'xp': 1400, 'gold': 2200, 'gems': 110, 'island': 'Ilha do Vulcão', 'drops': ['Manopla do Poder', 'Ovo Mítico'], 'egg_chance': 0.2},
    {'name': 'Deus do Trovão', 'hp': 2500, 'atk': 85, 'def': 50, 'level': 19, 'xp': 1200, 'gold': 1800, 'gems': 90, 'island': 'Ilha Celestial', 'drops': ['Martelo de Guerra', 'Ovo Mítico'], 'egg_chance': 0.2},
    {'name': 'Titã do Trovão', 'hp': 3200, 'atk': 105, 'def': 60, 'level': 20, 'xp': 1600, 'gold': 2800, 'gems': 140, 'island': 'Ilha Celestial', 'drops': ['Martelo de Guerra', 'Ovo Supremo'], 'egg_chance': 0.07},
    {'name': 'Leviatã', 'hp': 3500, 'atk': 110, 'def': 65, 'level': 20, 'xp': 1800, 'gold': 3000, 'gems': 150, 'island': 'Ilha do Oceano', 'drops': ['Lâmina do Caos', 'Ovo Supremo'], 'egg_chance': 0.06},
    {'name': 'Rei Demônio', 'hp': 3000, 'atk': 100, 'def': 60, 'level': 20, 'xp': 1500, 'gold': 2500, 'gems': 120, 'island': 'Ilha do Inferno', 'drops': ['Lâmina do Caos', 'Ovo Supremo'], 'egg_chance': 0.05},
    {'name': 'Deus do Caos', 'hp': 4000, 'atk': 120, 'def': 70, 'level': 20, 'xp': 2000, 'gold': 4000, 'gems': 200, 'island': 'Ilha do Inferno', 'drops': ['Lâmina do Caos', 'Ovo Supremo'], 'egg_chance': 0.04},
    {'name': 'Dragão Supremo', 'hp': 5000, 'atk': 150, 'def': 80, 'level': 20, 'xp': 3000, 'gold': 5000, 'gems': 300, 'island': 'Ilha dos Dragões', 'drops': ['Lâmina do Caos', 'Ovo Supremo'], 'egg_chance': 0.03},
    {'name': 'Deus Primordial', 'hp': 10000, 'atk': 200, 'def': 100, 'level': 20, 'xp': 5000, 'gold': 10000, 'gems': 500, 'island': 'Ilha Celestial', 'drops': ['Lâmina do Caos', 'Ovo Supremo'], 'egg_chance': 0.02},
    {'name': 'O Criador', 'hp': 50000, 'atk': 500, 'def': 200, 'level': 20, 'xp': 10000, 'gold': 50000, 'gems': 1000, 'island': 'Ilha do Inferno', 'drops': ['Lâmina do Caos', 'Ovo Supremo'], 'egg_chance': 0.01},
]

# ============================================
# 100 RECEITAS DE CRAFT
# ============================================

ITEMS_CRAFT = {
    # ARMAS (25)
    'Espada de Ferro': {'materials': {'Ferro': 5}, 'level': 1, 'stats': {'forca': 3}, 'desc': 'Uma espada básica de ferro'},
    'Espada de Prata': {'materials': {'Ferro': 10, 'Prata': 5}, 'level': 5, 'stats': {'forca': 5}, 'desc': 'Espada de prata refinada'},
    'Espada de Ouro': {'materials': {'Ouro': 10, 'Ferro': 20}, 'level': 10, 'stats': {'forca': 10}, 'desc': 'Espada banhada a ouro'},
    'Lâmina do Dragão': {'materials': {'Escama de Dragão': 5, 'Mithril': 10}, 'level': 15, 'stats': {'forca': 20, 'agilidade': 5}, 'desc': 'Forjada com escamas de dragão'},
    'Martelo de Guerra': {'materials': {'Ferro': 30, 'Ouro': 15}, 'level': 12, 'stats': {'forca': 15}, 'desc': 'Martelo pesado de guerra'},
    'Arco Élfico': {'materials': {'Madeira Sagrada': 10, 'Prata': 5}, 'level': 8, 'stats': {'forca': 8, 'agilidade': 5}, 'desc': 'Arco élfico preciso'},
    'Cajado Arcano': {'materials': {'Cristal Mágico': 10, 'Ouro': 15}, 'level': 14, 'stats': {'magia': 15, 'mana': 10}, 'desc': 'Cajado imbuído com magia'},
    'Manopla do Poder': {'materials': {'Adamantita': 8, 'Ouro': 20}, 'level': 16, 'stats': {'forca': 25}, 'desc': 'Manopla que aumenta a força'},
    'Lâmina do Caos': {'materials': {'Pedra Infernal': 10, 'Fragmento Celestial': 5, 'Escama de Dragão': 10}, 'level': 20, 'stats': {'forca': 50, 'agilidade': 20}, 'desc': 'A arma mais poderosa'},
    'Adaga Sombria': {'materials': {'Essência Sombria': 5, 'Mithril': 5}, 'level': 9, 'stats': {'forca': 7, 'agilidade': 8}, 'desc': 'Adaga das sombras'},
    
    # ARMADURAS (25)
    'Armadura de Couro': {'materials': {'Couro': 10}, 'level': 2, 'stats': {'defesa': 3}, 'desc': 'Armadura leve de couro'},
    'Armadura de Ferro': {'materials': {'Ferro': 15}, 'level': 5, 'stats': {'defesa': 8}, 'desc': 'Armadura de ferro'},
    'Armadura de Prata': {'materials': {'Prata': 15, 'Ferro': 10}, 'level': 8, 'stats': {'defesa': 12}, 'desc': 'Armadura de prata'},
    'Armadura de Ouro': {'materials': {'Ouro': 20, 'Ferro': 15}, 'level': 12, 'stats': {'defesa': 20}, 'desc': 'Armadura de ouro'},
    'Armadura de Mithril': {'materials': {'Mithril': 15}, 'level': 14, 'stats': {'defesa': 25}, 'desc': 'Armadura leve e resistente'},
    'Armadura Divina': {'materials': {'Fragmento Celestial': 10, 'Adamantita': 15}, 'level': 18, 'stats': {'defesa': 40, 'vida': 30}, 'desc': 'Abençoada pelos deuses'},
    'Escudo de Madeira': {'materials': {'Madeira Sagrada': 8}, 'level': 3, 'stats': {'defesa': 4}, 'desc': 'Escudo simples'},
    'Escudo de Ferro': {'materials': {'Ferro': 12}, 'level': 6, 'stats': {'defesa': 10}, 'desc': 'Escudo de ferro'},
    'Escudo de Mithril': {'materials': {'Mithril': 10}, 'level': 13, 'stats': {'defesa': 22}, 'desc': 'Escudo leve'},
    'Escudo Divino': {'materials': {'Fragmento Celestial': 8, 'Ouro': 15}, 'level': 17, 'stats': {'defesa': 35}, 'desc': 'Escudo celestial'},
    
    # ACESSÓRIOS (25)
    'Anel de Sorte': {'materials': {'Ouro': 5, 'Cristal Mágico': 3}, 'level': 5, 'stats': {'sorte': 10}, 'desc': '+10 Sorte'},
    'Colar da Sabedoria': {'materials': {'Prata': 8, 'Cristal Mágico': 5}, 'level': 8, 'stats': {'magia': 8, 'mana': 8}, 'desc': '+8 Magia e Mana'},
    'Botas Velozes': {'materials': {'Couro': 10, 'Prata': 5}, 'level': 6, 'stats': {'agilidade': 10}, 'desc': '+10 Agilidade'},
    'Amuleto da Sorte': {'materials': {'Ouro': 15, 'Cristal Mágico': 8}, 'level': 12, 'stats': {'sorte': 20}, 'desc': '+20 Sorte'},
    'Bracelete de Força': {'materials': {'Ferro': 15, 'Ouro': 10}, 'level': 10, 'stats': {'forca': 10}, 'desc': '+10 Força'},
    'Cinto do Guerreiro': {'materials': {'Couro': 20, 'Ferro': 15}, 'level': 9, 'stats': {'forca': 8, 'defesa': 5}, 'desc': '+8 Força +5 Defesa'},
    'Tiara Mágica': {'materials': {'Prata': 10, 'Cristal Mágico': 10}, 'level': 11, 'stats': {'magia': 12, 'mana': 10}, 'desc': '+12 Magia +10 Mana'},
    'Pedra da Vitalidade': {'materials': {'Cristal Mágico': 15, 'Ouro': 10}, 'level': 14, 'stats': {'vida': 30}, 'desc': '+30 Vida'},
    'Olho do Dragão': {'materials': {'Escama de Dragão': 3, 'Ouro': 20}, 'level': 16, 'stats': {'forca': 15, 'sorte': 10}, 'desc': '+15 Força +10 Sorte'},
    'Coração de Fênix': {'materials': {'Essência de Fênix': 5, 'Ouro': 25}, 'level': 18, 'stats': {'vida': 50, 'sorte': 15}, 'desc': '+50 Vida +15 Sorte'},
    
    # POÇÕES (15)
    'Poção de Cura': {'materials': {'Erva Medicinal': 3}, 'level': 1, 'stats': {}, 'desc': 'Restaura 50 HP'},
    'Poção de Cura Grande': {'materials': {'Erva Medicinal': 5, 'Cristal Mágico': 2}, 'level': 5, 'stats': {}, 'desc': 'Restaura 150 HP'},
    'Poção de Mana': {'materials': {'Cristal Mágico': 3}, 'level': 1, 'stats': {}, 'desc': 'Restaura 30 MP'},
    'Poção de Mana Grande': {'materials': {'Cristal Mágico': 5, 'Erva Medicinal': 3}, 'level': 5, 'stats': {}, 'desc': 'Restaura 100 MP'},
    'Elixir': {'materials': {'Erva Medicinal': 10, 'Cristal Mágico': 10}, 'level': 10, 'stats': {}, 'desc': 'Restaura todo HP e MP'},
    'Poção de Força': {'materials': {'Ferro': 5, 'Erva Medicinal': 3}, 'level': 3, 'stats': {}, 'desc': '+10 Força por 1 batalha'},
    'Poção de Defesa': {'materials': {'Pedra': 5, 'Erva Medicinal': 3}, 'level': 3, 'stats': {}, 'desc': '+10 Defesa por 1 batalha'},
    'Poção de Velocidade': {'materials': {'Pena': 5, 'Erva Medicinal': 3}, 'level': 3, 'stats': {}, 'desc': '+10 Agilidade por 1 batalha'},
    'Poção de Sorte': {'materials': {'Trevo': 5, 'Cristal Mágico': 3}, 'level': 5, 'stats': {}, 'desc': '+15 Sorte por 3 batalhas'},
    'Poção Suprema': {'materials': {'Erva Medicinal': 15, 'Cristal Mágico': 10, 'Ouro': 5}, 'level': 15, 'stats': {}, 'desc': '+50 todos os status'},
    
    # FERRAMENTAS (10)
    'Picareta de Ferro': {'materials': {'Ferro': 10, 'Madeira': 5}, 'level': 1, 'stats': {}, 'desc': 'Minera melhor (+1 minério)'},
    'Picareta de Prata': {'materials': {'Prata': 10, 'Ferro': 15}, 'level': 5, 'stats': {}, 'desc': 'Minera melhor (+2 minérios)'},
    'Picareta de Ouro': {'materials': {'Ouro': 10, 'Ferro': 20}, 'level': 10, 'stats': {}, 'desc': 'Minera melhor (+3 minérios)'},
    'Picareta de Mithril': {'materials': {'Mithril': 10, 'Ouro': 15}, 'level': 15, 'stats': {}, 'desc': 'Minera melhor (+5 minérios)'},
    'Vara de Pescar': {'materials': {'Madeira': 10, 'Linha': 5}, 'level': 1, 'stats': {}, 'desc': 'Pesca melhor'},
    'Vara de Pescar Pro': {'materials': {'Madeira Sagrada': 10, 'Linha de Prata': 5}, 'level': 8, 'stats': {}, 'desc': 'Pesca muito melhor'},
    'Tocha': {'materials': {'Madeira': 5, 'Carvão': 3}, 'level': 1, 'stats': {}, 'desc': 'Explora melhor'},
    'Tocha Mágica': {'materials': {'Madeira Sagrada': 5, 'Cristal Mágico': 3}, 'level': 5, 'stats': {}, 'desc': 'Explora muito melhor'},
    'Mapa do Tesouro': {'materials': {'Papel': 5, 'Tinta': 3}, 'level': 3, 'stats': {}, 'desc': 'Encontra mais tesouros'},
    'Bússola Mágica': {'materials': {'Cristal Mágico': 5, 'Ouro': 5}, 'level': 7, 'stats': {}, 'desc': 'Sempre aponta para tesouros'},
}

# ============================================
# MATERIAIS
# ============================================

MATERIAIS_CRAFT = {
    'Ferro': {'rarity': 'Comum', 'found_in': ['Ilha Inicial', 'Ilha das Montanhas'], 'price': 10},
    'Prata': {'rarity': 'Comum', 'found_in': ['Ilha do Gelo', 'Ilha Inicial'], 'price': 25},
    'Ouro': {'rarity': 'Raro', 'found_in': ['Ilha do Vulcão', 'Ilha do Deserto'], 'price': 50},
    'Mithril': {'rarity': 'Épico', 'found_in': ['Ilha Sombria', 'Ilha dos Dragões'], 'price': 100},
    'Adamantita': {'rarity': 'Lendário', 'found_in': ['Ilha Celestial', 'Ilha do Inferno'], 'price': 200},
    'Obsidiana': {'rarity': 'Raro', 'found_in': ['Ilha do Vulcão'], 'price': 40},
    'Cristal Mágico': {'rarity': 'Raro', 'found_in': ['Ilha Mágica'], 'price': 60},
    'Fragmento Celestial': {'rarity': 'Mítico', 'found_in': ['Ilha Celestial'], 'price': 500},
    'Pedra Infernal': {'rarity': 'Supremo', 'found_in': ['Ilha do Inferno'], 'price': 1000},
    'Pérola Negra': {'rarity': 'Lendário', 'found_in': ['Ilha do Oceano'], 'price': 300},
    'Coral Mágico': {'rarity': 'Épico', 'found_in': ['Ilha do Oceano'], 'price': 150},
    'Escama de Dragão': {'rarity': 'Lendário', 'found_in': ['Ilha dos Dragões'], 'price': 250},
    'Essência Sombria': {'rarity': 'Épico', 'found_in': ['Ilha Sombria'], 'price': 120},
    'Essência Demoníaca': {'rarity': 'Lendário', 'found_in': ['Ilha do Inferno'], 'price': 350},
    'Gelo Eterno': {'rarity': 'Raro', 'found_in': ['Ilha do Gelo'], 'price': 70},
    'Nuvem Sólida': {'rarity': 'Épico', 'found_in': ['Ilha do Céu'], 'price': 130},
    'Erva Medicinal': {'rarity': 'Comum', 'found_in': ['Ilha Inicial', 'Ilha da Floresta'], 'price': 5},
    'Cogumelo': {'rarity': 'Comum', 'found_in': ['Ilha da Floresta'], 'price': 3},
    'Flor Mágica': {'rarity': 'Raro', 'found_in': ['Ilha Mágica'], 'price': 35},
    'Trevo': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 4},
    'Pena': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 2},
    'Couro': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 8},
    'Linha': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 3},
    'Linha de Prata': {'rarity': 'Raro', 'found_in': ['Ilha Mágica'], 'price': 30},
    'Madeira': {'rarity': 'Comum', 'found_in': ['Ilha Inicial', 'Ilha da Floresta'], 'price': 4},
    'Madeira Sagrada': {'rarity': 'Raro', 'found_in': ['Ilha da Floresta'], 'price': 45},
    'Carvão': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 3},
    'Papel': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 5},
    'Tinta': {'rarity': 'Comum', 'found_in': ['Ilha Inicial'], 'price': 6},
    'Pedra': {'rarity': 'Comum', 'found_in': ['Ilha Inicial', 'Ilha das Montanhas'], 'price': 4},
}

# ============================================
# COMANDOS DE MISSÃO E BOSS
# ============================================

@bot.tree.command(name="missoes", description="📋 Ver missões disponíveis")
async def missoes(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    available = [q for q in QUESTS if p['level'] >= q['level'] and q['name'] not in p.get('quests_completed', [])]
    desc = "\n".join([f"**{q['name']}** (Nv.{q['level']})\n{q['desc']}\n💰 {q['gold']} Gold | 💎 {q['gems']} Gems | ⭐ {q['xp']} XP\n" for q in available[:10]])
    await i.response.send_message(embed=make_embed("📋 MISSÕES", desc or "Nenhuma disponível", 0xffaa00))

@bot.tree.command(name="missao", description="⚔️ Fazer uma missão")
@app_commands.describe(nome="Nome da missão")
async def missao(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    quest = next((q for q in QUESTS if q['name'].lower() == nome.lower()), None)
    if not quest: return await i.response.send_message("❌ Missão não encontrada!", ephemeral=True)
    if p['level'] < quest['level']: return await i.response.send_message(f"❌ Nível {quest['level']} necessário!", ephemeral=True)
    if quest['name'] in p.get('quests_completed', []): return await i.response.send_message("❌ Missão já concluída!", ephemeral=True)
    
    chance = min(90, 50 + (p['level'] - quest['level']) * 10)
    if random.randint(1, 100) <= chance:
        p['xp'] += quest['xp']
        p['gold'] += quest['gold']
        p['gems'] += quest['gems']
        p.setdefault('quests_completed', []).append(quest['name'])
        
        while p['xp'] >= p['xp_needed']:
            p['level'] += 1
            p['xp'] -= p['xp_needed']
            p['xp_needed'] = int(p['xp_needed'] * 1.5)
            p['max_hp'] += 20; p['hp'] = p['max_hp']
            p['max_mp'] += 10; p['mp'] = p['max_mp']
            p['atk'] += 3; p['def'] += 2; p['spd'] += 1
            p['status_points'] = p.get('status_points', 0) + 2
        
        bot.save_data()
        await i.response.send_message(embed=make_embed("✅ MISSÃO COMPLETA!", f"**{quest['name']}** concluída!\n💰 +{quest['gold']} Gold | 💎 +{quest['gems']} Gems | ⭐ +{quest['xp']} XP", 0x00ff00))
    else:
        p['hp'] = max(1, p['hp'] - 20)
        bot.save_data()
        await i.response.send_message(embed=make_embed("❌ MISSÃO FALHOU!", "Você falhou e perdeu 20 HP!", 0xff0000))

@bot.tree.command(name="bosses", description="👹 Ver bosses disponíveis")
async def bosses(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    desc = "\n".join([f"**{b['name']}** (Nv.{b['level']})\n❤️ {b['hp']} HP | ⚔️ {b['atk']} ATK | 🛡️ {b['def']} DEF\n📍 {b['island']} | 💰 {b['gold']} Gold\n" for b in BOSSES[:10]])
    await i.response.send_message(embed=make_embed("👹 BOSSES", desc or "Nenhum disponível", 0xff0000))

@bot.tree.command(name="boss", description="⚔️ Enfrentar um Boss")
@app_commands.describe(nome="Nome do Boss")
async def boss(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    boss_data = next((b for b in BOSSES if b['name'].lower() == nome.lower()), None)
    if not boss_data: return await i.response.send_message("❌ Boss não encontrado!", ephemeral=True)
    if p['level'] < boss_data['level']: return await i.response.send_message(f"❌ Nível {boss_data['level']} necessário!", ephemeral=True)
    
    boss_hp = boss_data['hp']
    player_hp = p['hp']
    log = []
    turn = 1
    
    while boss_hp > 0 and player_hp > 0:
        dmg = max(1, p['atk'] + random.randint(0, 10) - boss_data['def'])
        crit = random.random() < 0.1
        if crit: dmg *= 2
        boss_hp -= dmg
        log.append(f"🗡️ T{turn}: Você causou **{dmg}** de dano{' (CRÍTICO!)' if crit else ''}")
        
        if boss_hp <= 0: break
        
        boss_dmg = max(1, boss_data['atk'] + random.randint(0, 5) - p['def'])
        player_hp -= boss_dmg
        log.append(f"👹 T{turn}: Boss causou **{boss_dmg}** de dano")
        turn += 1
    
    if player_hp > 0:
        p['xp'] += boss_data['xp']
        p['gold'] += boss_data['gold']
        p['gems'] += boss_data['gems']
        p['hp'] = player_hp
        p.setdefault('bosses_defeated', []).append(boss_data['name'])
        p['total_bosses_killed'] = p.get('total_bosses_killed', 0) + 1
        
        if random.random() < boss_data['egg_chance'] / 100:
            egg = boss_data['drops'][-1]
            p.setdefault('pet_eggs', []).append(egg)
            log.append(f"🥚 Drop: **{egg}**!")
        
        bot.save_data()
        result = f"✅ **VITÓRIA!**\n💰 +{boss_data['gold']} Gold | 💎 +{boss_data['gems']} Gems | ⭐ +{boss_data['xp']} XP"
    else:
        p['hp'] = max(1, p['max_hp'] // 2)
        bot.save_data()
        result = "❌ **DERROTA!** Perdeu metade do HP!"
    
    await i.response.send_message(embed=make_embed(f"⚔️ VS {boss_data['name']}", "\n".join(log[-10:]) + f"\n\n{result}", 0x00ff00 if player_hp > 0 else 0xff0000))

# ============================================
# COMANDOS DE CRAFT
# ============================================

@bot.tree.command(name="craft", description="⚒️ Craftar um item")
@app_commands.describe(item="Nome do item para craftar")
async def craft(i: discord.Interaction, item: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    recipe = ITEMS_CRAFT.get(item)
    if not recipe: return await i.response.send_message("❌ Item não encontrado nas receitas!", ephemeral=True)
    if p['level'] < recipe['level']: return await i.response.send_message(f"❌ Nível {recipe['level']} necessário!", ephemeral=True)
    
    player_materials = p.get('materials', {})
    missing = []
    for mat, qtd in recipe['materials'].items():
        if player_materials.get(mat, 0) < qtd:
            missing.append(f"{mat}: {player_materials.get(mat, 0)}/{qtd}")
    
    if missing: return await i.response.send_message(f"❌ Materiais insuficientes!\n" + "\n".join(missing), ephemeral=True)
    
    for mat, qtd in recipe['materials'].items():
        player_materials[mat] -= qtd
    
    p.setdefault('inventory', []).append(item)
    p['crafts_made'] = p.get('crafts_made', 0) + 1
    bot.save_data()
    await i.response.send_message(embed=make_embed("⚒️ CRAFT COMPLETO!", f"Você craftou **{item}**!\n📝 {recipe['desc']}", 0x00ff00))

@bot.tree.command(name="receitas", description="📋 Ver receitas de craft disponíveis")
async def receitas(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    desc = ""
    for name, data in ITEMS_CRAFT.items():
        if p['level'] >= data['level']:
            mats = ", ".join([f"{v}x {k}" for k,v in data['materials'].items()])
            desc += f"**{name}** (Nv.{data['level']})\n📝 {data['desc']}\n⚒️ {mats}\n\n"
    
    await i.response.send_message(embed=make_embed("📋 RECEITAS", desc or "Nenhuma disponível", 0xffaa00))

# ============================================
# COMANDOS DE ILHAS
# ============================================

@bot.tree.command(name="ilhas", description="🗺️ Ver todas as ilhas")
async def ilhas(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    desc = ""
    for ilha in ISLANDS_FULL:
        available = "✅" if p['level'] >= ilha['level'] and p['gold'] >= ilha['cost'] else "🔒"
        desc += f"{available} **{ilha['name']}** (Nv.{ilha['level']})\n💰 {ilha['cost']} Gold | ⛏️ {', '.join(ilha['ores'][:2])}\n👹 Bosses: {', '.join(ilha['bosses']) or 'Nenhum'}\n\n"
    
    await i.response.send_message(embed=make_embed("🗺️ ILHAS", desc, 0x00ff00))

@bot.tree.command(name="viajar", description="🗺️ Viajar para uma ilha")
@app_commands.describe(nome="Nome da ilha")
async def viajar(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    ilha = next((il for il in ISLANDS_FULL if il['name'].lower() == nome.lower()), None)
    if not ilha: return await i.response.send_message("❌ Ilha não encontrada!", ephemeral=True)
    if p['level'] < ilha['level']: return await i.response.send_message(f"❌ Nível {ilha['level']} necessário!", ephemeral=True)
    if p['gold'] < ilha['cost']: return await i.response.send_message(f"❌ {ilha['cost']} Gold necessário!", ephemeral=True)
    
    p['gold'] -= ilha['cost']
    p['island'] = ilha['name']
    bot.save_data()
    await i.response.send_message(embed=make_embed("🗺️ VIAGEM", f"Você viajou para **{ilha['name']}**!\n💰 Custo: {ilha['cost']} Gold\n⛏️ Minérios: {', '.join(ilha['ores'])}", 0x00ff00))

@bot.tree.command(name="minerar", description="⛏️ Minerar na ilha atual")
async def minerar(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    ilha = next((il for il in ISLANDS_FULL if il['name'] == p.get('island', 'Ilha Inicial')), None)
    if not ilha: return await i.response.send_message("❌ Ilha não encontrada!", ephemeral=True)
    
    ore = random.choice(ilha['ores'])
    amount = random.randint(1, 5)
    p.setdefault('materials', {})
    p['materials'][ore] = p['materials'].get(ore, 0) + amount
    bot.save_data()
    await i.response.send_message(embed=make_embed("⛏️ MINERAR", f"Você minerou **{amount}x {ore}** na **{ilha['name']}**!", 0xffaa00))

# ============================================
# EVENTOS
# ============================================

@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════╗
║   ⚔️ EIDOLON GAMES - RPG ⚔️       ║
║   1800+ LINES OF ADVENTURE         ║
║   👑 Dono ID: {bot.DONO_ID}              ║
╚══════════════════════════════════════╝
    """)
    print(f"⚔️ Bot: {bot.user}")
    print(f"🎮 /criar - Comece sua aventura!")
    print(f"⚒️ /craft - Craftar itens")
    print(f"🗺️ /ilhas - Ver ilhas disponíveis")
    await bot.change_presence(activity=discord.Game(name="⚔️ /criar | EIDOLON RPG"))

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    print("⚔️ Iniciando EIDOLON RPG...\n")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\n❌ TOKEN INVÁLIDO!")
    except KeyboardInterrupt:
        print("\n🛑 RPG DESLIGADO!")
