#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════╗
# ║     EIDOLON GAMES - RPG COMPLETO v2.0                  ║
# ║     "Forge Your Legend"                                ║
# ║     2500+ LINES OF PURE ADVENTURE                      ║
# ╚══════════════════════════════════════════════════════════╝

import discord, os, sys, json, hashlib, random, string, re, socket, asyncio
import requests, datetime, subprocess, time
from discord import app_commands
from discord.ui import Button, View, Select
from urllib.parse import quote

# ============================================
# CORES E ESTILO
# ============================================
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'; C = '\033[96m'; W = '\033[97m'; BOLD = '\033[1m'; END = '\033[0m'

# ============================================
# CLASSE PRINCIPAL
# ============================================
class EidolonRPG(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.data_file = "eidolon_rpg.json"
        self.players = self.load_data()
        self._guilds = self.load_guilds()
        self.auctions = {}
        self.dungeons = {}
        self.DONO_ID = 1111135014453788682

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot {self.user} online!")

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f: return json.load(f)
        return {}

    def load_guilds(self):
        if os.path.exists("guilds.json"):
            with open("guilds.json", 'r') as f: return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_file, 'w') as f: json.dump(self.players, f, indent=2)
        with open("guilds.json", 'w') as f: json.dump(self._guilds, f, indent=2)

    def get_player(self, uid): return self.players.get(str(uid), None)

bot = EidolonRPG()

def make_embed(title, description, color=0xff4444):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now())
    embed.set_footer(text="⚔️ EIDOLON RPG | Forge Your Legend")
    return embed

# ============================================
# RAÇAS (4 INICIAIS + 9 DESBLOQUEÁVEIS)
# ============================================

RACES_INICIAIS = {
    'Humano': {'stats': {'forca': 5, 'defesa': 5, 'vida': 10, 'magia': 5, 'mana': 5, 'agilidade': 5, 'sorte': 5}, 'desc': '+10% XP'},
    'Elfo': {'stats': {'forca': 3, 'defesa': 4, 'vida': 8, 'magia': 8, 'mana': 8, 'agilidade': 8, 'sorte': 6}, 'desc': '+10% MP'},
    'Anão': {'stats': {'forca': 7, 'defesa': 8, 'vida': 12, 'magia': 3, 'mana': 3, 'agilidade': 3, 'sorte': 4}, 'desc': '+10% DEF'},
    'Draconiano': {'stats': {'forca': 8, 'defesa': 6, 'vida': 11, 'magia': 6, 'mana': 6, 'agilidade': 5, 'sorte': 5}, 'desc': '+10% ATK'},
}

RACES_DESBLOQUEAVEIS = {
    'Darkin': {'boss': 'Lorde das Sombras', 'stats': {'forca': 9, 'defesa': 4, 'vida': 9, 'magia': 7, 'mana': 7, 'agilidade': 7, 'sorte': 5}, 'desc': '+10% Dano Sombrio'},
    'Celestial': {'boss': 'Deus do Trovão', 'stats': {'forca': 5, 'defesa': 5, 'vida': 8, 'magia': 9, 'mana': 9, 'agilidade': 6, 'sorte': 7}, 'desc': '+10% Cura'},
    'Fênix': {'boss': 'Fênix Flamejante', 'stats': {'forca': 7, 'defesa': 5, 'vida': 9, 'magia': 8, 'mana': 8, 'agilidade': 7, 'sorte': 6}, 'desc': 'Revive 1x por batalha'},
    'Demônio': {'boss': 'Rei Demônio', 'stats': {'forca': 12, 'defesa': 4, 'vida': 10, 'magia': 7, 'mana': 7, 'agilidade': 6, 'sorte': 4}, 'desc': '+15% dano crítico'},
    'Golem': {'boss': 'Golem de Pedra', 'stats': {'forca': 13, 'defesa': 12, 'vida': 15, 'magia': 1, 'mana': 1, 'agilidade': 1, 'sorte': 3}, 'desc': '+10% DEF'},
    'Vampiro': {'boss': 'Rei dos Mortos', 'stats': {'forca': 10, 'defesa': 5, 'vida': 9, 'magia': 6, 'mana': 6, 'agilidade': 8, 'sorte': 5}, 'desc': 'Drena 5% do dano'},
    'Titã': {'boss': 'Titã de Ferro', 'stats': {'forca': 16, 'defesa': 10, 'vida': 16, 'magia': 1, 'mana': 1, 'agilidade': 1, 'sorte': 2}, 'desc': '+20% HP'},
    'Dragão': {'boss': 'Dragão Supremo', 'stats': {'forca': 15, 'defesa': 12, 'vida': 14, 'magia': 8, 'mana': 8, 'agilidade': 5, 'sorte': 5}, 'desc': '+15% todos'},
    'Deus': {'boss': 'O Criador', 'stats': {'forca': 20, 'defesa': 20, 'vida': 20, 'magia': 20, 'mana': 20, 'agilidade': 15, 'sorte': 15}, 'desc': '+20% todos'},
}

# ============================================
# CLASSES (4 DISPONÍVEIS)
# ============================================

CLASSES = {
    'Guerreiro': {'stats': {'forca': 3, 'defesa': 2, 'vida': 3}, 'skills': ['Corte Poderoso', 'Giro do Guerreiro', 'Fúria de Batalha']},
    'Mago': {'stats': {'magia': 5, 'mana': 4, 'sorte': 1}, 'skills': ['Bola de Fogo', 'Raio Congelante', 'Meteoro']},
    'Arqueiro': {'stats': {'agilidade': 4, 'forca': 2, 'sorte': 2}, 'skills': ['Chuva de Flechas', 'Tiro Preciso', 'Flecha Explosiva']},
    'Assassino': {'stats': {'forca': 4, 'agilidade': 5, 'sorte': 3}, 'skills': ['Golpe Sombrio', 'Veneno Mortal', 'Lâmina Fantasma']},
}

# ============================================
# TÍTULOS COM BÔNUS
# ============================================

TITLES = {
    'Aventureiro': {'bonus': {}, 'desc': 'Título inicial'},
    'Dragon Slayer': {'bonus': {'forca': 15, 'defesa': 10}, 'desc': 'Derrote um Dragão'},
    'Goblin Exterminador': {'bonus': {'forca': 5, 'agilidade': 5}, 'desc': 'Derrote um Goblin Chefe'},
    'Senhor do Gelo': {'bonus': {'defesa': 10, 'mana': 5}, 'desc': 'Derrote o Rei Gelado'},
    'Mestre das Sombras': {'bonus': {'agilidade': 15, 'sorte': 5}, 'desc': 'Derrote o Lorde das Sombras'},
    'Caçador de Fênix': {'bonus': {'vida': 20, 'sorte': 10}, 'desc': 'Derrote uma Fênix'},
    'Deus da Guerra': {'bonus': {'forca': 20, 'defesa': 15, 'agilidade': -5}, 'desc': 'Vença 50 PvPs'},
    'Milionário': {'bonus': {'sorte': 20}, 'desc': 'Acumule 100.000 Gold'},
    'Supremo': {'bonus': {'forca': 25, 'defesa': 25, 'vida': 50, 'sorte': 15}, 'desc': 'Alcance o nível 375'},
    'Brutamonte': {'bonus': {'forca': 15, 'defesa': 10, 'agilidade': -5}, 'desc': 'Cause 10.000 de dano'},
    'O Criador': {'bonus': {'forca': 50, 'defesa': 50, 'vida': 100, 'magia': 50, 'mana': 50, 'agilidade': 25, 'sorte': 25}, 'desc': 'Derrote O Criador'},
}

# ============================================
# MONTARIAS
# ============================================

MOUNTS = {
    'Cavalo': {'price': 500, 'bonus': {'spd': 5}, 'desc': 'Um cavalo comum'},
    'Lobo': {'price': 1500, 'bonus': {'spd': 10, 'atk': 5}, 'desc': 'Um lobo feroz'},
    'Dragão Jovem': {'price': 5000, 'bonus': {'spd': 20, 'atk': 15, 'def': 10}, 'desc': 'Um dragão jovem'},
    'Fênix': {'price': 10000, 'bonus': {'spd': 30, 'magia': 20}, 'desc': 'Uma fênix majestosa'},
    'Dragão Ancião': {'price': 50000, 'bonus': {'spd': 50, 'atk': 40, 'def': 30, 'vida': 100}, 'desc': 'O mais poderoso dos dragões'},
}

# ============================================
# OVOS DE PETS
# ============================================

OVOS = {
    'Ovo Comum': {'rarity': 'Comum', 'chance': 0.15, 'pets': ['Slime', 'Rato', 'Pássaro', 'Gato', 'Cachorro']},
    'Ovo Raro': {'rarity': 'Raro', 'chance': 0.08, 'pets': ['Lobo', 'Águia', 'Cobra', 'Raposa', 'Coruja']},
    'Ovo Épico': {'rarity': 'Épico', 'chance': 0.03, 'pets': ['Tigre', 'Urso', 'Pantera', 'Grifo', 'Hipogrifo']},
    'Ovo Lendário': {'rarity': 'Lendário', 'chance': 0.01, 'pets': ['Dragão Jovem', 'Fênix', 'Quimera', 'Serpente Alada', 'Unicórnio']},
    'Ovo Mítico': {'rarity': 'Mítico', 'chance': 0.003, 'pets': ['Dragão Ancião', 'Leviatã', 'Titã', 'Deus Menor', 'Entidade Cósmica']},
    'Ovo Supremo': {'rarity': 'Supremo', 'chance': 0.0007, 'pets': ['Dragão Supremo', 'Deus do Caos', 'Fênix Primordial', 'Ser Supremo', 'O Criador']},
}

# ============================================
# COMANDOS PRINCIPAIS
# ============================================

@bot.tree.command(name="criar", description="🎮 Criar seu personagem")
@app_commands.describe(nome="Nome do seu personagem")
@app_commands.choices(raca=[
    app_commands.Choice(name="🧑 Humano (+10% XP)", value="Humano"),
    app_commands.Choice(name="🧝 Elfo (+10% MP)", value="Elfo"),
    app_commands.Choice(name="⛏️ Anão (+10% DEF)", value="Anão"),
    app_commands.Choice(name="🐉 Draconiano (+10% ATK)", value="Draconiano"),
])
@app_commands.choices(classe=[
    app_commands.Choice(name="⚔️ Guerreiro", value="Guerreiro"),
    app_commands.Choice(name="🔮 Mago", value="Mago"),
    app_commands.Choice(name="🏹 Arqueiro", value="Arqueiro"),
    app_commands.Choice(name="🗡️ Assassino", value="Assassino"),
])
async def criar(i: discord.Interaction, nome: str, raca: str = "Humano", classe: str = "Guerreiro"):
    if bot.get_player(i.user.id):
        return await i.response.send_message("❌ Você já tem um personagem!", ephemeral=True)
    
    race_data = RACES_INICIAIS[raca]
    class_data = CLASSES[classe]
    stats = race_data['stats'].copy()
    for stat, bonus in class_data['stats'].items():
        stats[stat] = stats.get(stat, 5) + bonus
    
    bot.players[str(i.user.id)] = {
        'name': nome, 'level': 1, 'xp': 0, 'xp_needed': 100,
        'hp': 100, 'max_hp': 100, 'mp': 50, 'max_mp': 50,
        'stats': stats,
        'atk': 10 + stats.get('forca', 5), 'def': 5 + stats.get('defesa', 5),
        'spd': 5 + stats.get('agilidade', 5),
        'gold': 100, 'gems': 10, 'bank_gold': 0, 'bank_gems': 0,
        'race': raca, 'class': classe,
        'unlocked_races': ['Humano', 'Elfo', 'Anão', 'Draconiano'],
        'inventory': [], 'equipment': {'weapon': None, 'armor': None, 'accessory': None},
        'skills': class_data['skills'].copy(),
        'scrolls': [], 'island': 'Ilha Inicial',
        'quests_completed': [], 'bosses_defeated': [],
        'pvp_wins': 0, 'pvp_losses': 0,
        'ores': {}, 'materials': {}, 'crafts_made': 0,
        'titles': ['Aventureiro'], 'active_title': 'Aventureiro',
        'guild': None, 'pets': [], 'active_pet': None, 'pet_eggs': [],
        'trades': [], 'achievements': [], 'chests_opened': 0,
        'total_gold_earned': 0, 'total_bosses_killed': 0,
        'status_points': 0, 'mount': None, 'mounts': [],
        'daily_streak': 0, 'last_daily': None,
    }
    bot.save_data()
    await i.response.send_message(embed=make_embed("🎮 PERSONAGEM CRIADO!", 
        f"**{nome}** está pronto!\n\n🏹 Raça: **{raca}**\n⚔️ Classe: **{classe}**\n\n🔓 Raças desbloqueadas: 4\nDerrote bosses para desbloquear novas raças!\nUse `/racas` para ver todas!", 0x00ff00))

@bot.tree.command(name="perfil", description="👤 Ver seu personagem completo")
async def perfil(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    s = p.get('stats', {})
    active_title = p.get('active_title', 'Aventureiro')
    title_bonus = TITLES.get(active_title, {}).get('bonus', {})
    
    desc = f"""
**{p['name']}** | 🏅 {active_title}
🏹 Raça: **{p['race']}** | ⚔️ Classe: **{p['class']}**
⭐ Nível: **{p['level']}** ({p['xp']}/{p['xp_needed']} XP)
🗺️ Ilha: **{p.get('island', 'Ilha Inicial')}**

📊 **ATRIBUTOS:** {'(com bônus do título)' if title_bonus else ''}
💪 Força: {s.get('forca', 5)} {f'(+{title_bonus.get("forca", 0)})' if title_bonus.get('forca') else ''}
🛡️ Defesa: {s.get('defesa', 5)} {f'(+{title_bonus.get("defesa", 0)})' if title_bonus.get('defesa') else ''}
❤️ Vida: {s.get('vida', 10)} {f'(+{title_bonus.get("vida", 0)})' if title_bonus.get('vida') else ''}
🔮 Magia: {s.get('magia', 5)} {f'(+{title_bonus.get("magia", 0)})' if title_bonus.get('magia') else ''}
💎 Mana: {s.get('mana', 5)} {f'(+{title_bonus.get("mana", 0)})' if title_bonus.get('mana') else ''}
💨 Agilidade: {s.get('agilidade', 5)} {f'({title_bonus.get("agilidade", 0)})' if title_bonus.get('agilidade') else ''}
🍀 Sorte: {s.get('sorte', 5)} {f'(+{title_bonus.get("sorte", 0)})' if title_bonus.get('sorte') else ''}

⚔️ ATK: {p['atk']} | 🛡️ DEF: {p['def']} | 💨 SPD: {p['spd']}
❤️ HP: {p['hp']}/{p['max_hp']} | 💎 MP: {p['mp']}/{p['max_mp']}

💰 Carteira: {p['gold']:,} Gold | 💎 {p['gems']:,} Gems
🏦 Banco: {p.get('bank_gold', 0):,} Gold | {p.get('bank_gems', 0):,} Gems

🐾 Pets: {len(p.get('pets', []))} | 🥚 Ovos: {len(p.get('pet_eggs', []))}
🐉 Montaria: {p.get('mount', 'Nenhuma')}
🏰 Guilda: {p.get('guild', 'Nenhuma')}
🏆 PvP: {p.get('pvp_wins', 0)}W / {p.get('pvp_losses', 0)}L

⭐ **Pontos de Status:** {p.get('status_points', 0)}
Use `/status` para distribuir!
    """
    await i.response.send_message(embed=make_embed(f"👤 {p['name']}", desc, 0x00ff00))

@bot.tree.command(name="daily", description="🎁 Resgatar bônus diário")
async def daily(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if p.get('last_daily') == today:
        return await i.response.send_message("❌ Você já resgatou hoje! Volte amanhã!", ephemeral=True)
    
    p['last_daily'] = today
    p['daily_streak'] = p.get('daily_streak', 0) + 1
    streak = p['daily_streak']
    
    bonus_gold = 100 + (streak * 10)
    bonus_xp = 50 + (streak * 5)
    
    p['gold'] += bonus_gold
    p['xp'] += bonus_xp
    
    while p['xp'] >= p['xp_needed']:
        p['level'] += 1
        p['xp'] -= p['xp_needed']
        p['xp_needed'] = int(p['xp_needed'] * 1.5)
        p['status_points'] = p.get('status_points', 0) + 2
    
    bot.save_data()
    await i.response.send_message(embed=make_embed("🎁 DAILY", f"Streak: **{streak} dias** 🔥\n💰 +{bonus_gold} Gold\n⭐ +{bonus_xp} XP\n\nVolte amanhã para manter sua streak!", 0x00ff00))

@bot.tree.command(name="racas", description="🏹 Ver raças disponíveis e desbloqueadas")
async def racas(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    unlocked = p.get('unlocked_races', ['Humano', 'Elfo', 'Anão', 'Draconiano'])
    
    desc = "**🔓 RAÇAS DESBLOQUEADAS:**\n"
    for r in unlocked:
        if r in RACES_INICIAIS:
            desc += f"✅ **{r}** - {RACES_INICIAIS[r]['desc']}\n"
        elif r in RACES_DESBLOQUEAVEIS:
            desc += f"✅ **{r}** - {RACES_DESBLOQUEAVEIS[r]['desc']}\n"
    
    desc += "\n**🔒 RAÇAS BLOQUEADAS:**\n"
    for r, data in RACES_DESBLOQUEAVEIS.items():
        if r not in unlocked:
            desc += f"🔒 **{r}** - Derrote: {data['boss']}\n"
    
    await i.response.send_message(embed=make_embed("🏹 RAÇAS", desc, 0x00ff00))

@bot.tree.command(name="mudar_raca", description="🔄 Mudar para uma raça desbloqueada")
@app_commands.describe(raca="Nome da raça")
async def mudar_raca(i: discord.Interaction, raca: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    unlocked = p.get('unlocked_races', [])
    if raca not in unlocked:
        return await i.response.send_message(f"❌ Você não desbloqueou a raça **{raca}** ainda!\nUse `/racas` para ver como desbloquear.", ephemeral=True)
    
    if raca in RACES_INICIAIS:
        race_stats = RACES_INICIAIS[raca]['stats']
    else:
        race_stats = RACES_DESBLOQUEAVEIS[raca]['stats']
    
    p['race'] = raca
    p['stats'] = race_stats.copy()
    p['atk'] = 10 + race_stats.get('forca', 5) * 2
    p['def'] = 5 + race_stats.get('defesa', 5) * 2
    p['spd'] = 5 + race_stats.get('agilidade', 5) * 2
    p['max_hp'] = 100 + race_stats.get('vida', 10) * 10
    p['max_mp'] = 50 + race_stats.get('mana', 5) * 10
    
    bot.save_data()
    await i.response.send_message(embed=make_embed("🔄 RAÇA ALTERADA!", f"Você agora é um(a) **{raca}**!\nSeus status foram atualizados!", 0x00ff00))

@bot.tree.command(name="montarias", description="🐉 Ver montarias disponíveis")
async def montarias(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    desc = "**Suas montarias:**\n" + ("\n".join([f"• {m}" for m in p.get('mounts', [])]) or "Nenhuma") + "\n\n**Loja de Montarias:**\n"
    for name, data in MOUNTS.items():
        owned = "✅" if name in p.get('mounts', []) else f"💰 {data['price']} Gold"
        desc += f"{owned} **{name}** - {data['desc']}\n"
    
    await i.response.send_message(embed=make_embed("🐉 MONTARIAS", desc, 0xff00ff))

@bot.tree.command(name="comprar_montaria", description="🐉 Comprar uma montaria")
@app_commands.describe(nome="Nome da montaria")
async def comprar_montaria(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    
    mount = MOUNTS.get(nome)
    if not mount: return await i.response.send_message("❌ Montaria não encontrada!", ephemeral=True)
    if nome in p.get('mounts', []): return await i.response.send_message("❌ Você já tem essa montaria!", ephemeral=True)
    if p['gold'] < mount['price']: return await i.response.send_message(f"❌ {mount['price']} Gold necessário!", ephemeral=True)
    
    p['gold'] -= mount['price']
    p.setdefault('mounts', []).append(nome)
    if not p.get('mount'): p['mount'] = nome
    bot.save_data()
    await i.response.send_message(embed=make_embed("🐉 MONTARIA COMPRADA!", f"Você adquiriu **{nome}**!\n📝 {mount['desc']}", 0x00ff00))

@bot.tree.command(name="sync", description="🔄 Sincronizar comandos (DONO)")
async def sync(i: discord.Interaction):
    if i.user.id != bot.DONO_ID:
        return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    await bot.tree.sync()
    await i.response.send_message("✅ Todos os comandos foram sincronizados!", ephemeral=True)

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
    {'name': 'O Poço Misterioso', 'level': 2, 'xp': 75, 'gold': 90, 'gems': 7, 'desc': 'Investigue o poço abandonado'},
    {'name': 'Pescaria', 'level': 2, 'xp': 50, 'gold': 60, 'gems': 4, 'desc': 'Pesque 5 peixes no rio'},
    {'name': 'Mina Abandonada', 'level': 3, 'xp': 120, 'gold': 150, 'gems': 10, 'desc': 'Explore a mina'},
    {'name': 'O Ladrão de Joias', 'level': 3, 'xp': 100, 'gold': 200, 'gems': 12, 'desc': 'Capture o ladrão'},
    {'name': 'O Tesouro do Pirata', 'level': 3, 'xp': 110, 'gold': 350, 'gems': 11, 'desc': 'Encontre o tesouro'},
    {'name': 'A Ponte Quebrada', 'level': 3, 'xp': 90, 'gold': 120, 'gems': 9, 'desc': 'Conserte a ponte'},
    {'name': 'Lobos Selvagens', 'level': 3, 'xp': 105, 'gold': 130, 'gems': 10, 'desc': 'Derrote 5 lobos'},
    {'name': 'Caça ao Tesouro', 'level': 4, 'xp': 150, 'gold': 300, 'gems': 15, 'desc': 'Encontre o tesouro escondido'},
    {'name': 'O Roubo do Banco', 'level': 4, 'xp': 130, 'gold': 280, 'gems': 14, 'desc': 'Impeça o roubo'},
    {'name': 'A Casa Mal-Assombrada', 'level': 4, 'xp': 140, 'gold': 200, 'gems': 13, 'desc': 'Investigue a casa'},
    {'name': 'O Poço dos Desejos', 'level': 4, 'xp': 120, 'gold': 180, 'gems': 12, 'desc': 'Faça um desejo'},
    {'name': 'Ovelhas Perdidas', 'level': 4, 'xp': 110, 'gold': 160, 'gems': 11, 'desc': 'Encontre 5 ovelhas'},
    {'name': 'A Floresta Sombria', 'level': 5, 'xp': 200, 'gold': 250, 'gems': 15, 'desc': 'Sobreviva à floresta'},
    {'name': 'A Floresta Encantada', 'level': 5, 'xp': 180, 'gold': 220, 'gems': 12, 'desc': 'Colete flores mágicas'},
    {'name': 'A Poção Mágica', 'level': 5, 'xp': 190, 'gold': 240, 'gems': 13, 'desc': 'Crie a poção'},
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
# 25 BOSSES (CADA UM NA SUA ILHA)
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
# 15 ILHAS
# ============================================

ISLANDS = [
    {'name': 'Ilha Inicial', 'cost': 0, 'level': 1, 'ores': ['Ferro', 'Pedra', 'Cobre'], 'bosses': ['Slime Rei', 'Goblin Chefe', 'Lobo Alfa'], 'desc': 'Onde tudo começa'},
    {'name': 'Ilha da Floresta', 'cost': 500, 'level': 5, 'ores': ['Madeira Sagrada', 'Seiva Mística'], 'bosses': ['Aranha Gigante'], 'desc': 'Floresta densa e misteriosa'},
    {'name': 'Ilha do Gelo', 'cost': 2000, 'level': 10, 'ores': ['Prata', 'Gelo Eterno'], 'bosses': ['Rei Gelado', 'Dragão de Gelo'], 'desc': 'Fria e perigosa'},
    {'name': 'Ilha do Vulcão', 'cost': 5000, 'level': 15, 'ores': ['Ouro', 'Obsidiana'], 'bosses': ['Dragão de Fogo', 'Fênix Flamejante', 'Fênix Negra'], 'desc': 'Quente e mortal'},
    {'name': 'Ilha Sombria', 'cost': 8000, 'level': 20, 'ores': ['Mithril', 'Essência Sombria'], 'bosses': ['Lorde das Sombras', 'Rei dos Mortos'], 'desc': 'Coberta de trevas'},
    {'name': 'Ilha das Montanhas', 'cost': 12000, 'level': 25, 'ores': ['Adamantita', 'Pedra Rúnica'], 'bosses': ['Golem de Pedra', 'Titã de Ferro'], 'desc': 'Montanhas gigantes'},
    {'name': 'Ilha do Oceano', 'cost': 20000, 'level': 30, 'ores': ['Pérola Negra', 'Coral Mágico'], 'bosses': ['Serpente Marinha', 'Leviatã'], 'desc': 'Profundezas misteriosas'},
    {'name': 'Ilha dos Dragões', 'cost': 50000, 'level': 50, 'ores': ['Escama de Dragão', 'Cristal Dracônico'], 'bosses': ['Dragão Ancião', 'Dragão Supremo'], 'desc': 'Lar dos dragões'},
    {'name': 'Ilha Celestial', 'cost': 100000, 'level': 100, 'ores': ['Fragmento Celestial', 'Nuvem Sólida'], 'bosses': ['Deus do Trovão', 'Titã do Trovão', 'Deus Primordial'], 'desc': 'Acima das nuvens'},
    {'name': 'Ilha do Inferno', 'cost': 500000, 'level': 200, 'ores': ['Pedra Infernal', 'Lava Solidificada'], 'bosses': ['Rei Demônio', 'Deus do Caos', 'O Criador'], 'desc': 'O lugar mais perigoso'},
    {'name': 'Ilha do Templo', 'cost': 3000, 'level': 12, 'ores': ['Ouro', 'Relíquia Sagrada'], 'bosses': ['Guardião do Templo'], 'desc': 'Ruínas antigas'},
    {'name': 'Ilha Mágica', 'cost': 1500, 'level': 8, 'ores': ['Cristal Mágico', 'Pó de Fada'], 'bosses': ['Mago Supremo'], 'desc': 'Onde a magia flui'},
    {'name': 'Ilha do Deserto', 'cost': 1000, 'level': 7, 'ores': ['Ouro', 'Arenito', 'Marfim'], 'bosses': [], 'desc': 'Deserto escaldante'},
    {'name': 'Ilha do Céu', 'cost': 30000, 'level': 35, 'ores': ['Nuvem Sólida', 'Vento Etéreo'], 'bosses': [], 'desc': 'Entre as nuvens'},
    {'name': 'Ilha do Submundo', 'cost': 200000, 'level': 150, 'ores': ['Pedra Infernal', 'Essência Demoníaca'], 'bosses': [], 'desc': 'Abaixo da superfície'},
]

# ============================================
# COMANDOS DE MISSÃO, BOSS, ILHAS
# ============================================

@bot.tree.command(name="missoes", description="📋 Ver missões disponíveis")
async def missoes(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    available = [q for q in QUESTS if p['level'] >= q['level'] and q['name'] not in p.get('quests_completed', [])]
    desc = "\n".join([f"**{q['name']}** (Nv.{q['level']})\n{q['desc']}\n💰 {q['gold']} Gold | ⭐ {q['xp']} XP\n" for q in available[:10]])
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
        p['xp'] += quest['xp']; p['gold'] += quest['gold']; p['gems'] += quest['gems']
        p.setdefault('quests_completed', []).append(quest['name'])
        while p['xp'] >= p['xp_needed']:
            p['level'] += 1; p['xp'] -= p['xp_needed']
            p['xp_needed'] = int(p['xp_needed'] * 1.5)
            p['max_hp'] += 20; p['hp'] = p['max_hp']
            p['max_mp'] += 10; p['mp'] = p['max_mp']
            p['atk'] += 3; p['def'] += 2; p['spd'] += 1
            p['status_points'] = p.get('status_points', 0) + 2
        bot.save_data()
        await i.response.send_message(embed=make_embed("✅ MISSÃO COMPLETA!", f"**{quest['name']}** concluída!\n💰 +{quest['gold']} Gold | ⭐ +{quest['xp']} XP", 0x00ff00))
    else:
        p['hp'] = max(1, p['hp'] - 20); bot.save_data()
        await i.response.send_message(embed=make_embed("❌ MISSÃO FALHOU!", "Você falhou e perdeu 20 HP!", 0xff0000))

@bot.tree.command(name="bosses", description="👹 Ver bosses na sua ilha atual")
async def bosses(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    current = p.get('island', 'Ilha Inicial')
    desc = f"**📍 Você está em: {current}**\n\n"
    for b in BOSSES:
        if b['island'] == current:
            available = "✅" if p['level'] >= b['level'] else "🔒"
            desc += f"{available} **{b['name']}** (Nv.{b['level']})\n❤️ {b['hp']} HP | ⚔️ {b['atk']} ATK | 💰 {b['gold']} Gold\n\n"
    await i.response.send_message(embed=make_embed(f"👹 BOSSES EM {current.upper()}", desc or "Nenhum boss nesta ilha", 0xff0000))

@bot.tree.command(name="boss", description="⚔️ Enfrentar um Boss")
@app_commands.describe(nome="Nome do Boss")
async def boss(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    boss_data = next((b for b in BOSSES if b['name'].lower() == nome.lower()), None)
    if not boss_data: return await i.response.send_message("❌ Boss não encontrado!", ephemeral=True)
    current_island = p.get('island', 'Ilha Inicial')
    if boss_data['island'] != current_island:
        return await i.response.send_message(f"❌ Você precisa estar na **{boss_data['island']}**!\nUse `/viajar {boss_data['island']}` primeiro.", ephemeral=True)
    if p['level'] < boss_data['level']: return await i.response.send_message(f"❌ Nível {boss_data['level']} necessário!", ephemeral=True)
    
    boss_hp = boss_data['hp']; player_hp = p['hp']; log = []; turn = 1
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
        p['xp'] += boss_data['xp']; p['gold'] += boss_data['gold']; p['gems'] += boss_data['gems']
        p['hp'] = player_hp
        p.setdefault('bosses_defeated', []).append(boss_data['name'])
        p['total_bosses_killed'] = p.get('total_bosses_killed', 0) + 1
        if random.random() < boss_data['egg_chance'] / 100:
            egg = boss_data['drops'][-1]
            p.setdefault('pet_eggs', []).append(egg)
            log.append(f"🥚 Drop: **{egg}**!")
        
        # Verifica raças desbloqueáveis
        for race_name, race_data in RACES_DESBLOQUEAVEIS.items():
            if race_data['boss'] == boss_data['name'] and race_name not in p.get('unlocked_races', []):
                p.setdefault('unlocked_races', []).append(race_name)
                log.append(f"🔓 Nova raça: **{race_name}**!")
        
        # Verifica títulos
        for title_name, title_data in TITLES.items():
            if title_name not in p.get('titles', []):
                if 'Dragão' in boss_data['name'] and 'Dragon' in title_name:
                    p.setdefault('titles', []).append(title_name)
                    log.append(f"🏅 Novo título: **{title_name}**!")
        
        bot.save_data()
        result = f"✅ **VITÓRIA!**\n💰 +{boss_data['gold']} Gold | 💎 +{boss_data['gems']} Gems | ⭐ +{boss_data['xp']} XP"
    else:
        p['hp'] = max(1, p['max_hp'] // 2); bot.save_data()
        result = "❌ **DERROTA!** Perdeu metade do HP!"
    
    await i.response.send_message(embed=make_embed(f"⚔️ VS {boss_data['name']} ({current_island})", "\n".join(log[-10:]) + f"\n\n{result}", 0x00ff00 if player_hp > 0 else 0xff0000))

@bot.tree.command(name="ilhas", description="🗺️ Ver todas as ilhas")
async def ilhas(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    desc = ""
    for ilha in ISLANDS:
        available = "✅" if p['level'] >= ilha['level'] and p['gold'] >= ilha['cost'] else "🔒"
        desc += f"{available} **{ilha['name']}** (Nv.{ilha['level']})\n💰 {ilha['cost']} Gold\n👹 Bosses: {', '.join(ilha['bosses']) or 'Nenhum'}\n⛏️ Minérios: {', '.join(ilha['ores'][:2])}\n\n"
    await i.response.send_message(embed=make_embed("🗺️ ILHAS", desc, 0x00ff00))

@bot.tree.command(name="viajar", description="🗺️ Viajar para uma ilha")
@app_commands.describe(nome="Nome da ilha")
async def viajar(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    ilha = next((il for il in ISLANDS if il['name'].lower() == nome.lower()), None)
    if not ilha: return await i.response.send_message("❌ Ilha não encontrada!", ephemeral=True)
    if p['level'] < ilha['level']: return await i.response.send_message(f"❌ Nível {ilha['level']} necessário!", ephemeral=True)
    if p['gold'] < ilha['cost']: return await i.response.send_message(f"❌ {ilha['cost']} Gold necessário!", ephemeral=True)
    p['gold'] -= ilha['cost']; p['island'] = ilha['name']; bot.save_data()
    await i.response.send_message(embed=make_embed("🗺️ VIAGEM", f"Você viajou para **{ilha['name']}**!\n💰 Custo: {ilha['cost']} Gold\n👹 Bosses: {', '.join(ilha['bosses']) or 'Nenhum'}\n⛏️ Minérios: {', '.join(ilha['ores'])}", 0x00ff00))

@bot.tree.command(name="minerar", description="⛏️ Minerar na ilha atual")
async def minerar(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    ilha = next((il for il in ISLANDS if il['name'] == p.get('island', 'Ilha Inicial')), None)
    if not ilha: return await i.response.send_message("❌ Ilha não encontrada!", ephemeral=True)
    ore = random.choice(ilha['ores']); amount = random.randint(1, 5)
    p.setdefault('materials', {})
    p['materials'][ore] = p['materials'].get(ore, 0) + amount
    bot.save_data()
    await i.response.send_message(embed=make_embed("⛏️ MINERAR", f"Você minerou **{amount}x {ore}** na **{ilha['name']}**!", 0xffaa00))

# ============================================
# PETS
# ============================================

@bot.tree.command(name="pets", description="🐾 Ver seus pets")
async def pets(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    pets_list = p.get('pets', []); eggs = p.get('pet_eggs', []); active = p.get('active_pet', 'Nenhum')
    desc = f"🐾 **Pet Ativo:** {active}\n\n**Pets:**\n" + ("\n".join([f"• {pet}" for pet in pets_list]) or "Nenhum") + "\n\n**Ovos:**\n" + ("\n".join([f"• {egg}" for egg in eggs]) or "Nenhum")
    await i.response.send_message(embed=make_embed("🐾 PETS", desc, 0xff00ff))

@bot.tree.command(name="chocar", description="🥚 Chocar um ovo de pet")
async def chocar(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    eggs = p.get('pet_eggs', [])
    if not eggs: return await i.response.send_message("❌ Você não tem ovos!", ephemeral=True)
    egg_priority = ['Ovo Supremo', 'Ovo Mítico', 'Ovo Lendário', 'Ovo Épico', 'Ovo Raro', 'Ovo Comum']
    chosen_egg = None
    for priority in egg_priority:
        if priority in eggs: chosen_egg = priority; break
    if not chosen_egg: return await i.response.send_message("❌ Erro ao chocar ovo!", ephemeral=True)
    egg_data = OVOS[chosen_egg]
    if random.random() < egg_data['chance']:
        pet = random.choice(egg_data['pets'])
        p['pet_eggs'].remove(chosen_egg)
        p.setdefault('pets', []).append(pet)
        if not p.get('active_pet'): p['active_pet'] = pet
        bot.save_data()
        await i.response.send_message(embed=make_embed("🥚 OVO CHOCOU!", f"🎉 Você conseguiu um **{pet}** ({egg_data['rarity']})!", 0x00ff00))
    else:
        p['pet_eggs'].remove(chosen_egg); bot.save_data()
        await i.response.send_message(embed=make_embed("💔 OVO QUEBROU!", f"Infelizmente o {chosen_egg} não vingou...", 0xff0000))

# ============================================
# LEILÃO
# ============================================

@bot.tree.command(name="leilao_criar", description="🏪 Criar um leilão")
@app_commands.describe(item="Item para leiloar", preco_minimo="Preço mínimo", duracao="Duração em horas")
async def leilao_criar(i: discord.Interaction, item: str, preco_minimo: int, duracao: int = 24):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    if item not in p.get('inventory', []): return await i.response.send_message("❌ Você não tem esse item!", ephemeral=True)
    if preco_minimo <= 0: return await i.response.send_message("❌ Preço inválido!", ephemeral=True)
    auction_id = hashlib.md5(f"{i.user.id}{datetime.datetime.now()}".encode()).hexdigest()[:8]
    bot.auctions[auction_id] = {'seller': i.user.id, 'item': item, 'min_price': preco_minimo, 'current_bid': 0, 'highest_bidder': None, 'end_time': datetime.datetime.now() + datetime.timedelta(hours=duracao), 'active': True}
    p['inventory'].remove(item); bot.save_data()
    await i.response.send_message(embed=make_embed("🏪 LEILÃO CRIADO!", f"**{item}**\n💰 Preço mínimo: {preco_minimo:,} Gold\n⏰ Duração: {duracao}h\n🆔 ID: `{auction_id}`\n\nUse `/leilao_ver {auction_id}` para dar lances!", 0xffd700))

@bot.tree.command(name="leilao_ver", description="🏪 Ver leilões ativos")
async def leilao_ver(i: discord.Interaction):
    active = {k: v for k, v in bot.auctions.items() if v['active']}
    if not active: return await i.response.send_message("❌ Nenhum leilão ativo!", ephemeral=True)
    desc = ""
    for aid, data in list(active.items())[:10]:
        seller = await bot.fetch_user(data['seller'])
        time_left = data['end_time'] - datetime.datetime.now()
        hours_left = max(0, time_left.total_seconds() // 3600)
        desc += f"🆔 `{aid}` | 🏷️ **{data['item']}**\n👤 {seller.name}\n💰 Lance atual: {data['current_bid']:,} Gold\n⏰ {int(hours_left)}h restantes\n\n"
    await i.response.send_message(embed=make_embed("🏪 LEILÕES ATIVOS", desc, 0xffd700))

@bot.tree.command(name="leilao_lance", description="💰 Dar lance em um leilão")
@app_commands.describe(auction_id="ID do leilão", valor="Valor do lance")
async def leilao_lance(i: discord.Interaction, auction_id: str, valor: int):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    auction = bot.auctions.get(auction_id)
    if not auction or not auction['active']: return await i.response.send_message("❌ Leilão não encontrado!", ephemeral=True)
    if datetime.datetime.now() > auction['end_time']: auction['active'] = False; return await i.response.send_message("❌ Leilão encerrado!", ephemeral=True)
    if valor <= auction['current_bid']: return await i.response.send_message(f"❌ Lance mínimo: {auction['current_bid']+1:,} Gold!", ephemeral=True)
    if valor < auction['min_price']: return await i.response.send_message(f"❌ Preço mínimo: {auction['min_price']:,} Gold!", ephemeral=True)
    if p['gold'] < valor: return await i.response.send_message("❌ Gold insuficiente!", ephemeral=True)
    if auction['highest_bidder']:
        old_bidder = bot.get_player(auction['highest_bidder'])
        if old_bidder: old_bidder['gold'] += auction['current_bid']
    p['gold'] -= valor; auction['current_bid'] = valor; auction['highest_bidder'] = i.user.id; bot.save_data()
    await i.response.send_message(embed=make_embed("💰 LANCE!", f"Leilão `{auction_id}`\n🏷️ {auction['item']}\n💰 Seu lance: {valor:,} Gold", 0x00ff00))

# ============================================
# MASMORRAS
# ============================================

@bot.tree.command(name="masmorra_criar", description="🏰 Criar grupo de masmorra")
@app_commands.describe(nome="Nome do grupo", nivel_min="Nível mínimo")
async def masmorra_criar(i: discord.Interaction, nome: str, nivel_min: int = 1):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    dungeon_id = hashlib.md5(f"{i.user.id}{datetime.datetime.now()}".encode()).hexdigest()[:8]
    bot.dungeons[dungeon_id] = {'leader': i.user.id, 'name': nome, 'min_level': nivel_min, 'members': [i.user.id], 'status': 'recruiting', 'floor': 1, 'max_floor': 10}
    await i.response.send_message(embed=make_embed("🏰 MASMORRA CRIADA!", f"**{nome}**\n👑 Líder: {i.user.mention}\n⭐ Nível mínimo: {nivel_min}\n🚪 Andar: 1/10\n🆔 `{dungeon_id}`\n\nUse `/masmorra_entrar {dungeon_id}` para entrar!", 0x00ff00))

@bot.tree.command(name="masmorra_entrar", description="🏰 Entrar em uma masmorra")
@app_commands.describe(dungeon_id="ID da masmorra")
async def masmorra_entrar(i: discord.Interaction, dungeon_id: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    dungeon = bot.dungeons.get(dungeon_id)
    if not dungeon: return await i.response.send_message("❌ Masmorra não encontrada!", ephemeral=True)
    if dungeon['status'] != 'recruiting': return await i.response.send_message("❌ Masmorra já em andamento!", ephemeral=True)
    if p['level'] < dungeon['min_level']: return await i.response.send_message(f"❌ Nível {dungeon['min_level']} necessário!", ephemeral=True)
    if i.user.id in dungeon['members']: return await i.response.send_message("❌ Você já está no grupo!", ephemeral=True)
    dungeon['members'].append(i.user.id)
    await i.response.send_message(embed=make_embed("🏰 MASMORRA", f"{i.user.mention} entrou na masmorra **{dungeon['name']}**!\n👥 Membros: {len(dungeon['members'])}", 0x00ff00))

@bot.tree.command(name="masmorra_avancar", description="🏰 Avançar andar da masmorra")
@app_commands.describe(dungeon_id="ID da masmorra")
async def masmorra_avancar(i: discord.Interaction, dungeon_id: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    dungeon = bot.dungeons.get(dungeon_id)
    if not dungeon: return await i.response.send_message("❌ Masmorra não encontrada!", ephemeral=True)
    if i.user.id != dungeon['leader']: return await i.response.send_message("❌ Apenas o líder!", ephemeral=True)
    if dungeon['floor'] >= dungeon['max_floor']: return await i.response.send_message("❌ Último andar!", ephemeral=True)
    monster_hp = 500 * dungeon['floor']; monster_atk = 20 * dungeon['floor']
    total_player_hp = sum(bot.get_player(uid)['hp'] for uid in dungeon['members'] if bot.get_player(uid))
    if total_player_hp > monster_hp * 0.3:
        dungeon['floor'] += 1
        reward_gold = 100 * dungeon['floor']; reward_xp = 50 * dungeon['floor']
        for uid in dungeon['members']:
            member = bot.get_player(uid)
            if member: member['gold'] += reward_gold; member['xp'] += reward_xp
        bot.save_data()
        await i.response.send_message(embed=make_embed("🏰 ANDAR AVANÇADO!", f"**{dungeon['name']}**\n🚪 Andar: {dungeon['floor']}/{dungeon['max_floor']}\n💰 +{reward_gold} Gold\n⭐ +{reward_xp} XP", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("❌ DERROTA!", "O grupo não foi forte o suficiente!", 0xff0000))

# ============================================
# PVP
# ============================================

@bot.tree.command(name="pvp", description="⚔️ Duelar com outro jogador")
@app_commands.describe(adversario="Quem desafiar", aposta="Gold apostado")
async def pvp(i: discord.Interaction, adversario: discord.User, aposta: int = 0):
    p1 = bot.get_player(i.user.id); p2 = bot.get_player(adversario.id)
    if not p1 or not p2: return await i.response.send_message("❌ Ambos precisam ter personagem!", ephemeral=True)
    if aposta < 0: return await i.response.send_message("❌ Aposta inválida!", ephemeral=True)
    if aposta > 0:
        if p1['gold'] < aposta: return await i.response.send_message("❌ Gold insuficiente!", ephemeral=True)
        if p2['gold'] < aposta: return await i.response.send_message(f"❌ {adversario.name} não tem Gold!", ephemeral=True)
        p1['gold'] -= aposta; p2['gold'] -= aposta
    p1_power = p1['atk'] + p1['def'] + p1['spd'] + (20 if p1.get('active_pet') else 0)
    p2_power = p2['atk'] + p2['def'] + p2['spd'] + (20 if p2.get('active_pet') else 0)
    p1_roll = random.randint(1, p1_power); p2_roll = random.randint(1, p2_power)
    if p1_roll > p2_roll: winner, loser = p1, p2; winner_name = i.user.mention
    else: winner, loser = p2, p1; winner_name = adversario.mention
    if aposta > 0: winner['gold'] += aposta * 2
    p1['pvp_wins'] = p1.get('pvp_wins', 0) + (1 if winner == p1 else 0)
    p1['pvp_losses'] = p1.get('pvp_losses', 0) + (1 if loser == p1 else 0)
    p2['pvp_wins'] = p2.get('pvp_wins', 0) + (1 if winner == p2 else 0)
    p2['pvp_losses'] = p2.get('pvp_losses', 0) + (1 if loser == p2 else 0)
    for player in [p1, p2]:
        if player.get('pvp_wins', 0) >= 50 and 'Deus da Guerra' not in player.get('titles', []):
            player.setdefault('titles', []).append('Deus da Guerra')
    bot.save_data()
    await i.response.send_message(embed=make_embed("⚔️ PVP", f"{i.user.mention} ({p1_roll}) vs {adversario.mention} ({p2_roll})\n\n🏆 **{winner_name}** venceu!\n{'💰 Ganhou ' + str(aposta*2) + ' Gold!' if aposta > 0 else ''}", 0xffd700))

# ============================================
# TRADE
# ============================================

@bot.tree.command(name="trade", description="🤝 Trocar itens/pets")
@app_commands.describe(jogador="Jogador para trocar", seu_item="Seu item/pet", item_dele="Item/pet que você quer")
async def trade(i: discord.Interaction, jogador: discord.User, seu_item: str, item_dele: str):
    p1 = bot.get_player(i.user.id); p2 = bot.get_player(jogador.id)
    if not p1 or not p2: return await i.response.send_message("❌ Ambos precisam ter personagem!", ephemeral=True)
    if seu_item not in p1.get('inventory', []) and seu_item not in p1.get('pets', []) and seu_item not in p1.get('materials', {}):
        return await i.response.send_message(f"❌ Você não tem **{seu_item}**!", ephemeral=True)
    if item_dele not in p2.get('inventory', []) and item_dele not in p2.get('pets', []) and item_dele not in p2.get('materials', {}):
        return await i.response.send_message(f"❌ {jogador.name} não tem **{item_dele}**!", ephemeral=True)
    trade_id = hashlib.md5(f"{i.user.id}{jogador.id}{datetime.datetime.now()}".encode()).hexdigest()[:8]
    p1.setdefault('trades', []).append({'id': trade_id, 'with': jogador.id, 'give': seu_item, 'receive': item_dele, 'status': 'pending'})
    bot.save_data()
    await i.response.send_message(embed=make_embed("🤝 TRADE", f"Trade `{trade_id}` criado!\n\n{i.user.mention} oferece: **{seu_item}**\nQuer receber: **{item_dele}**\n\n{jogador.mention} use `/aceitar_trade {trade_id}` para aceitar!", 0xffd700))

@bot.tree.command(name="aceitar_trade", description="✅ Aceitar uma troca")
@app_commands.describe(trade_id="ID da troca")
async def aceitar_trade(i: discord.Interaction, trade_id: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    trade = None; other_uid = None
    for uid, data in bot.players.items():
        for t in data.get('trades', []):
            if t['id'] == trade_id and t['status'] == 'pending' and t['with'] == i.user.id:
                trade = t; other_uid = uid; break
    if not trade: return await i.response.send_message("❌ Trade não encontrado!", ephemeral=True)
    other_player = bot.get_player(int(other_uid))
    if not other_player: return await i.response.send_message("❌ Jogador não encontrado!", ephemeral=True)
    give_item = trade['give']; receive_item = trade['receive']
    if give_item in other_player.get('inventory', []): other_player['inventory'].remove(give_item)
    if give_item in other_player.get('pets', []): other_player['pets'].remove(give_item)
    if give_item in other_player.get('materials', {}): del other_player['materials'][give_item]
    if receive_item in p.get('inventory', []): p['inventory'].remove(receive_item)
    if receive_item in p.get('pets', []): p['pets'].remove(receive_item)
    if receive_item in p.get('materials', {}): del p['materials'][receive_item]
    if give_item not in ['']: p.setdefault('inventory', []).append(give_item)
    if receive_item not in ['']: other_player.setdefault('inventory', []).append(receive_item)
    trade['status'] = 'completed'; bot.save_data()
    await i.response.send_message(embed=make_embed("✅ TRADE COMPLETO!", f"Trade `{trade_id}` concluído!", 0x00ff00))

# ============================================
# BANCO
# ============================================

@bot.tree.command(name="banco", description="🏦 Depositar ou Sacar")
@app_commands.describe(acao="Depositar ou Sacar", quantidade="Quantidade", tipo="Gold ou Gems")
@app_commands.choices(acao=[app_commands.Choice(name="Depositar", value="dep"), app_commands.Choice(name="Sacar", value="sac")])
@app_commands.choices(tipo=[app_commands.Choice(name="Gold", value="gold"), app_commands.Choice(name="Gems", value="gems")])
async def banco(i: discord.Interaction, acao: str, quantidade: int, tipo: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    if quantidade <= 0: return await i.response.send_message("❌ Quantidade inválida!", ephemeral=True)
    bank_key = f"bank_{tipo}"; current_bank = p.get(bank_key, 0)
    if acao == "dep":
        if p[tipo] < quantidade: return await i.response.send_message(f"❌ {tipo} insuficiente!", ephemeral=True)
        p[tipo] -= quantidade; p[bank_key] = current_bank + quantidade
        bot.save_data()
        await i.response.send_message(embed=make_embed("🏦 DEPÓSITO", f"Depositado **{quantidade:,} {tipo}**!\n🏦 Banco: {p[bank_key]:,} {tipo}", 0x00ff00))
    else:
        if current_bank < quantidade: return await i.response.send_message(f"❌ Saldo no banco insuficiente!", ephemeral=True)
        p[bank_key] = current_bank - quantidade; p[tipo] += quantidade
        bot.save_data()
        await i.response.send_message(embed=make_embed("🏧 SAQUE", f"Sacado **{quantidade:,} {tipo}**!\n💰 Agora: {p[tipo]:,} {tipo}", 0x00ff00))

# ============================================
# GUILDAS
# ============================================

@bot.tree.command(name="guilda_criar", description="🏰 Criar uma guilda")
@app_commands.describe(nome="Nome da guilda")
async def guilda_criar(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    if p.get('guild'): return await i.response.send_message("❌ Você já está em uma guilda!", ephemeral=True)
    if p['gold'] < 1000: return await i.response.send_message("❌ 1.000 Gold necessário!", ephemeral=True)
    if nome in bot._guilds: return await i.response.send_message("❌ Nome já existe!", ephemeral=True)
    p['gold'] -= 1000
    bot._guilds[nome] = {'owner': i.user.id, 'members': [i.user.id], 'level': 1, 'gold': 0}
    p['guild'] = nome; bot.save_data()
    await i.response.send_message(embed=make_embed("🏰 GUILDA CRIADA!", f"**{nome}** foi fundada!\n👑 Líder: {i.user.mention}", 0xffd700))

@bot.tree.command(name="guilda_entrar", description="🏰 Entrar em uma guilda")
@app_commands.describe(nome="Nome da guilda")
async def guilda_entrar(i: discord.Interaction, nome: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    if p.get('guild'): return await i.response.send_message("❌ Você já está em uma guilda!", ephemeral=True)
    if nome not in bot._guilds: return await i.response.send_message("❌ Guilda não encontrada!", ephemeral=True)
    bot._guilds[nome]['members'].append(i.user.id); p['guild'] = nome; bot.save_data()
    await i.response.send_message(embed=make_embed("🏰 GUILDA", f"Você entrou na guilda **{nome}**!", 0x00ff00))

# ============================================
# ADMIN
# ============================================

@bot.tree.command(name="admin", description="🛡️ [ADMIN] Painel")
async def admin(i: discord.Interaction):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    await i.response.send_message(embed=make_embed("🛡️ ADMIN", "`/admin_give` `/admin_level` `/admin_gold` `/admin_material` `/admin_egg` `/admin_reset`", 0xff0000), ephemeral=True)

@bot.tree.command(name="admin_give", description="🛡️ [ADMIN] Dar item")
@app_commands.describe(usuario="Jogador", item="Nome do item", quantidade="Quantidade")
async def admin_give(i: discord.Interaction, usuario: discord.User, item: str, quantidade: int = 1):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    p = bot.get_player(usuario.id)
    if not p: return await i.response.send_message("❌ Jogador não tem personagem!", ephemeral=True)
    for _ in range(quantidade): p.setdefault('inventory', []).append(item)
    bot.save_data()
    await i.response.send_message(embed=make_embed("🛡️ ADMIN", f"✅ Dado **{quantidade}x {item}** para {usuario.mention}!", 0x00ff00), ephemeral=True)

@bot.tree.command(name="admin_level", description="🛡️ [ADMIN] Setar nível")
@app_commands.describe(usuario="Jogador", level="Novo nível")
async def admin_level(i: discord.Interaction, usuario: discord.User, level: int):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    p = bot.get_player(usuario.id)
    if not p: return await i.response.send_message("❌ Jogador não tem personagem!", ephemeral=True)
    level = max(1, min(375, level))
    p['level'] = level; p['status_points'] = level * 2
    p['max_hp'] = 100 + level * 10; p['max_mp'] = 50 + level * 5
    p['hp'] = p['max_hp']; p['mp'] = p['max_mp']
    bot.save_data()
    await i.response.send_message(embed=make_embed("🛡️ ADMIN", f"✅ {usuario.mention} setado para nível **{level}**!", 0x00ff00), ephemeral=True)

@bot.tree.command(name="admin_gold", description="🛡️ [ADMIN] Dar gold")
@app_commands.describe(usuario="Jogador", quantidade="Quantidade")
async def admin_gold(i: discord.Interaction, usuario: discord.User, quantidade: int):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    p = bot.get_player(usuario.id)
    if not p: return await i.response.send_message("❌ Jogador não tem personagem!", ephemeral=True)
    p['gold'] += quantidade; bot.save_data()
    await i.response.send_message(embed=make_embed("🛡️ ADMIN", f"✅ Dado **{quantidade:,} Gold** para {usuario.mention}!", 0x00ff00), ephemeral=True)

@bot.tree.command(name="admin_material", description="🛡️ [ADMIN] Dar material")
@app_commands.describe(usuario="Jogador", material="Nome do material", quantidade="Quantidade")
async def admin_material(i: discord.Interaction, usuario: discord.User, material: str, quantidade: int = 1):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    p = bot.get_player(usuario.id)
    if not p: return await i.response.send_message("❌ Jogador não tem personagem!", ephemeral=True)
    p.setdefault('materials', {})
    p['materials'][material] = p['materials'].get(material, 0) + quantidade
    bot.save_data()
    await i.response.send_message(embed=make_embed("🛡️ ADMIN", f"✅ Dado **{quantidade}x {material}** para {usuario.mention}!", 0x00ff00), ephemeral=True)

@bot.tree.command(name="admin_egg", description="🛡️ [ADMIN] Dar ovo de pet")
@app_commands.describe(usuario="Jogador", ovo="Tipo de ovo")
@app_commands.choices(ovo=[
    app_commands.Choice(name="🥚 Ovo Comum", value="Ovo Comum"),
    app_commands.Choice(name="🥚 Ovo Raro", value="Ovo Raro"),
    app_commands.Choice(name="🥚 Ovo Épico", value="Ovo Épico"),
    app_commands.Choice(name="🥚 Ovo Lendário", value="Ovo Lendário"),
    app_commands.Choice(name="🥚 Ovo Mítico", value="Ovo Mítico"),
    app_commands.Choice(name="🥚 Ovo Supremo", value="Ovo Supremo"),
])
async def admin_egg(i: discord.Interaction, usuario: discord.User, ovo: str):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    p = bot.get_player(usuario.id)
    if not p: return await i.response.send_message("❌ Jogador não tem personagem!", ephemeral=True)
    p.setdefault('pet_eggs', []).append(ovo)
    bot.save_data()
    await i.response.send_message(embed=make_embed("🛡️ ADMIN", f"✅ Dado **{ovo}** para {usuario.mention}!", 0x00ff00), ephemeral=True)

@bot.tree.command(name="admin_reset", description="🛡️ [ADMIN] Resetar um jogador")
@app_commands.describe(usuario="Jogador")
async def admin_reset(i: discord.Interaction, usuario: discord.User):
    if i.user.id != bot.DONO_ID: return await i.response.send_message("❌ Apenas o DONO!", ephemeral=True)
    if str(usuario.id) in bot.players:
        del bot.players[str(usuario.id)]
        bot.save_data()
        await i.response.send_message(embed=make_embed("🛡️ ADMIN", f"✅ {usuario.mention} foi resetado!", 0x00ff00), ephemeral=True)
    else:
        await i.response.send_message("❌ Jogador não encontrado!", ephemeral=True)

# ============================================
# STATUS, TÍTULOS, CRAFT, BAÚ, EVENTO
# ============================================

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
    if points <= 0: return await i.response.send_message("❌ Você não tem pontos de status!", ephemeral=True)
    p.setdefault('stats', {})
    p['stats'][atributo] = p['stats'].get(atributo, 5) + 1
    p['status_points'] = points - 1
    s = p['stats']
    p['atk'] = 10 + s.get('forca', 5) * 2 + s.get('agilidade', 5)
    p['def'] = 5 + s.get('defesa', 5) * 2
    p['spd'] = 5 + s.get('agilidade', 5) * 2
    p['max_hp'] = 100 + s.get('vida', 10) * 10
    p['max_mp'] = 50 + s.get('mana', 5) * 10 + s.get('magia', 5) * 5
    p['hp'] = min(p['hp'], p['max_hp']); p['mp'] = min(p['mp'], p['max_mp'])
    bot.save_data()
    await i.response.send_message(embed=make_embed("📊 STATUS UP!", f"**{atributo.upper()}** aumentado para **{p['stats'][atributo]}**!\n⭐ Pontos restantes: {p['status_points']}", 0x00ff00))

@bot.tree.command(name="titulos", description="🏅 Ver seus títulos e trocar título ativo")
async def titulos(i: discord.Interaction):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    titles = p.get('titles', ['Aventureiro']); active = p.get('active_title', 'Aventureiro')
    desc = f"🏅 **Título Ativo:** {active}\n\n"
    for t in titles:
        bonus = TITLES.get(t, {}).get('bonus', {})
        bonus_text = ", ".join([f"{'+' if v > 0 else ''}{v} {k}" for k, v in bonus.items()]) if bonus else "Sem bônus"
        desc += f"• **{t}** - {bonus_text}\n"
    
    class TitleSelect(Select):
        def __init__(self):
            options = [discord.SelectOption(label=t, value=t) for t in titles[:25]]
            super().__init__(placeholder="Escolha um título...", options=options)
        async def callback(self, interaction: discord.Interaction):
            p['active_title'] = self.values[0]; bot.save_data()
            await interaction.response.send_message(f"✅ Título alterado para **{self.values[0]}**!", ephemeral=True)
    
    view = View()
    if len(titles) <= 25: view.add_item(TitleSelect())
    await i.response.send_message(embed=make_embed("🏅 TÍTULOS", desc, 0xffd700), view=view)

@bot.tree.command(name="craft", description="⚒️ Craftar um item")
@app_commands.describe(item="Nome do item")
async def craft(i: discord.Interaction, item: str):
    p = bot.get_player(i.user.id)
    if not p: return await i.response.send_message("❌ Use `/criar` primeiro!", ephemeral=True)
    if p.get('crafts_made', 0) < 5:
        p['crafts_made'] = p.get('crafts_made', 0) + 1
        bot.save_data()
        await i.response.send_message(embed=make_embed("⚒️ CRAFT", f"Você craftou **{item}**!", 0x00ff00))
    else:
        await i.response.send_message("❌ Você já craftou muitos itens hoje!", ephemeral=True)

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
        gold = random.randint(50, 500); p['gold'] += gold
        bot.save_data()
        await i.response.send_message(embed=make_embed("🎁 BAÚ ENCONTRADO!", f"🥚 **{egg}**\n💰 **{gold} Gold**\nUse `/chocar` para chocar o ovo!", 0xffd700))
    else:
        await i.response.send_message(embed=make_embed("🔍 NADA...", "Você procurou mas não encontrou nenhum baú.", 0xff0000))

@bot.tree.command(name="evento_rpg", description="🎪 Ver evento aleatório atual")
async def evento_rpg(i: discord.Interaction):
    events = [("🌟 Bônus de XP", "Todos ganham +50% XP!"), ("💰 Chuva de Gold", "Todos ganham +100 Gold!"), ("🥚 Ovos Misteriosos", "Chance de achar ovos dobrada!"), ("⚔️ Arena Livre", "PvP sem custo!"), ("🔥 Double Drop", "Drops duplicados!")]
    event = random.choice(events)
    await i.response.send_message(embed=make_embed("🎪 EVENTO", f"**{event[0]}**\n📝 {event[1]}", 0xff00ff))

# ============================================
# EVENTOS FINAIS
# ============================================

@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════╗
║   ⚔️ EIDOLON RPG v2.0 ⚔️          ║
║   2500+ LINES OF ADVENTURE         ║
║   👑 Dono ID: {bot.DONO_ID}              ║
╚══════════════════════════════════════╝
    """)
    print(f"⚔️ Bot: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="⚔️ /criar | EIDOLON RPG v2.0"))

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    print("⚔️ Iniciando EIDOLON RPG v2.0...\n")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\n❌ TOKEN INVÁLIDO!")
    except KeyboardInterrupt:
        print("\n🛑 RPG DESLIGADO!")
