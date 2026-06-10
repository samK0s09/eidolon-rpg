#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║     EIDOLON CASINO - SISTEMA MONETÁRIO                 ║
║     Moeda: Eidocoins 🪙                                ║
╚══════════════════════════════════════════════════════════╝
"""

import discord
from discord import app_commands
from discord.ui import Button, View, Select
import asyncio
import random
import json
import datetime
import sys
import os

# ============================================
# CONFIGURAÇÃO
# ============================================

class EidolonCasino(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.data_file = "eidocoins.json"
        self.users = self.load_data()
        self.cooldowns = {}

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot {self.user} online!")

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def get_coins(self, user_id):
        return self.users.get(str(user_id), {}).get('coins', 100)

    def set_coins(self, user_id, amount):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {'coins': 100, 'level': 1, 'xp': 0}
        self.users[str(user_id)]['coins'] = max(0, amount)
        self.save_data()

    def add_coins(self, user_id, amount):
        current = self.get_coins(user_id)
        self.set_coins(user_id, current + amount)

    def remove_coins(self, user_id, amount):
        current = self.get_coins(user_id)
        if current >= amount:
            self.set_coins(user_id, current - amount)
            return True
        return False

    def check_cooldown(self, user_id, cmd, seconds):
        key = f"{user_id}_{cmd}"
        if key in self.cooldowns:
            if (datetime.datetime.now() - self.cooldowns[key]).seconds < seconds:
                return False
        self.cooldowns[key] = datetime.datetime.now()
        return True

bot = EidolonCasino()

# ============================================
# EMBED BONITO
# ============================================

def make_embed(title, description, color=0xff4444):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now())
    embed.set_footer(text="🎰 EIDOLON CASINO | Eidocoins 🪙")
    return embed

# ============================================
# 🏦 COMANDOS BANCÁRIOS (8)
# ============================================

@bot.tree.command(name="carteira", description="🪙 Ver seu saldo de Eidocoins")
async def carteira(i: discord.Interaction):
    coins = bot.get_coins(i.user.id)
    await i.response.send_message(
        embed=make_embed("🪙 CARTEIRA", f"{i.user.mention}\n\n💰 Saldo: **{coins:,} Eidocoins**", 0x00ff00)
    )

@bot.tree.command(name="daily", description="🎁 Resgatar bônus diário (200 Eidocoins)")
async def daily(i: discord.Interaction):
    if bot.check_cooldown(i.user.id, "daily", 86400):
        bot.add_coins(i.user.id, 200)
        await i.response.send_message(embed=make_embed("🎁 DAILY", "Você resgatou **200 Eidocoins**! Volte em 24h!", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("⏰ DAILY", "Você já resgatou hoje! Volte amanhã!", 0xff0000))

@bot.tree.command(name="pagar", description="💸 Pagar Eidocoins para alguém")
@app_commands.describe(usuario="Quem vai receber", quantidade="Quantidade")
async def pagar(i: discord.Interaction, usuario: discord.User, quantidade: int):
    if quantidade <= 0:
        return await i.response.send_message("❌ Quantidade inválida!")
    if bot.remove_coins(i.user.id, quantidade):
        bot.add_coins(usuario.id, quantidade)
        await i.response.send_message(embed=make_embed("💸 PAGO", f"{i.user.mention} pagou **{quantidade:,} Eidocoins** para {usuario.mention}", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("❌ SALDO", "Saldo insuficiente!", 0xff0000))

@bot.tree.command(name="top", description="🏆 Ranking dos mais ricos")
async def top(i: discord.Interaction):
    sorted_users = sorted(bot.users.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    desc = ""
    for pos, (uid, data) in enumerate(sorted_users, 1):
        user = await bot.fetch_user(int(uid))
        desc += f"{'🥇🥈🥉'[pos-1] if pos <= 3 else f'{pos}º'} {user.name}: **{data.get('coins', 0):,}** 🪙\n"
    await i.response.send_message(embed=make_embed("🏆 TOP 10 RICOS", desc, 0xffd700))

@bot.tree.command(name="work", description="💼 Trabalhar para ganhar Eidocoins")
async def work(i: discord.Interaction):
    if bot.check_cooldown(i.user.id, "work", 3600):
        jobs = [
            ("Programador", 150), ("Hacker", 200), ("Minerador", 180),
            ("Designer", 120), ("Chef", 100), ("Motorista", 80),
            ("Streamer", 250), ("Investidor", random.randint(0, 500)),
        ]
        job, amount = random.choice(jobs)
        bot.add_coins(i.user.id, amount)
        await i.response.send_message(embed=make_embed("💼 TRABALHO", f"Você trabalhou como **{job}** e ganhou **{amount:,} Eidocoins**!", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("⏰ TRABALHO", "Você já trabalhou! Espere 1 hora!", 0xff0000))

@bot.tree.command(name="roubar", description="🥷 Tentar roubar Eidocoins de alguém")
@app_commands.describe(usuario="Alvo do roubo")
async def roubar(i: discord.Interaction, usuario: discord.User):
    if bot.check_cooldown(i.user.id, "roubar", 7200):
        if random.random() < 0.4:
            amount = random.randint(10, 100)
            if bot.remove_coins(usuario.id, amount):
                bot.add_coins(i.user.id, amount)
                await i.response.send_message(embed=make_embed("🥷 ROUBO", f"{i.user.mention} roubou **{amount:,} Eidocoins** de {usuario.mention}!", 0x00ff00))
            else:
                await i.response.send_message(embed=make_embed("❌ ROUBO", "Alvo sem saldo!", 0xff0000))
        else:
            fine = random.randint(50, 150)
            bot.remove_coins(i.user.id, fine)
            await i.response.send_message(embed=make_embed("🚔 ROUBO FALHOU", f"Você foi pego e pagou **{fine:,} Eidocoins** de multa!", 0xff0000))
    else:
        await i.response.send_message(embed=make_embed("⏰ ROUBO", "Espere 2 horas para roubar novamente!", 0xff0000))

@bot.tree.command(name="depositar", description="🏦 Guardar dinheiro (proteção contra roubo)")
@app_commands.describe(quantidade="Quanto guardar")
async def depositar(i: discord.Interaction, quantidade: int):
    if quantidade <= 0: return await i.response.send_message("❌ Quantidade inválida!")
    if bot.remove_coins(i.user.id, quantidade):
        bot.users[str(i.user.id)]['bank'] = bot.users[str(i.user.id)].get('bank', 0) + quantidade
        bot.save_data()
        await i.response.send_message(embed=make_embed("🏦 DEPÓSITO", f"**{quantidade:,} Eidocoins** guardados no banco! 🔒", 0x00ff00))
    else:
        await i.response.send_message("❌ Saldo insuficiente!")

@bot.tree.command(name="sacar", description="🏧 Sacar dinheiro do banco")
@app_commands.describe(quantidade="Quanto sacar")
async def sacar(i: discord.Interaction, quantidade: int):
    bank = bot.users.get(str(i.user.id), {}).get('bank', 0)
    if quantidade <= bank:
        bot.users[str(i.user.id)]['bank'] -= quantidade
        bot.add_coins(i.user.id, quantidade)
        await i.response.send_message(embed=make_embed("🏧 SAQUE", f"**{quantidade:,} Eidocoins** sacados!", 0x00ff00))
    else:
        await i.response.send_message("❌ Saldo no banco insuficiente!")

# ============================================
# 🎰 JOGOS DE CASSINO (12)
# ============================================

@bot.tree.command(name="coinflip", description="🪙 Cara ou Coroa (50%)")
@app_commands.describe(aposta="Valor da aposta", lado="cara ou coroa")
@app_commands.choices(lado=[app_commands.Choice(name="Cara", value="cara"), app_commands.Choice(name="Coroa", value="coroa")])
async def coinflip(i: discord.Interaction, aposta: int, lado: str):
    if aposta <= 0: return await i.response.send_message("❌ Valor inválido!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    result = random.choice(["cara", "coroa"])
    if result == lado:
        win = aposta * 2
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("🪙 COINFLIP", f"Resultado: **{result.upper()}**\nVocê GANHOU **{win:,} Eidocoins**! 🎉", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("🪙 COINFLIP", f"Resultado: **{result.upper()}**\nVocê PERDEU **{aposta:,} Eidocoins**! 💀", 0xff0000))

@bot.tree.command(name="dado", description="🎲 Apostar em um número (1-6)")
@app_commands.describe(aposta="Valor da aposta", numero="Número (1-6)")
async def dado(i: discord.Interaction, aposta: int, numero: int):
    if aposta <= 0 or numero < 1 or numero > 6: return await i.response.send_message("❌ Valores inválidos!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    result = random.randint(1, 6)
    if result == numero:
        win = aposta * 6
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("🎲 DADO", f"Resultado: **{result}**\nVocê acertou e GANHOU **{win:,} Eidocoins**! 🎉", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("🎲 DADO", f"Resultado: **{result}**\nVocê errou e PERDEU **{aposta:,} Eidocoins**! 💀", 0xff0000))

@bot.tree.command(name="roleta", description="🎡 Girar a roleta (cores)")
@app_commands.describe(aposta="Valor da aposta", cor="Vermelho ou Preto")
@app_commands.choices(cor=[app_commands.Choice(name="🔴 Vermelho", value="red"), app_commands.Choice(name="⚫ Preto", value="black")])
async def roleta(i: discord.Interaction, aposta: int, cor: str):
    if aposta <= 0: return await i.response.send_message("❌ Valor inválido!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    colors = ["red", "black", "red", "black", "red", "black", "red", "black", "red", "black", "red", "black", "green"]
    result = random.choice(colors)
    if result == cor:
        bot.add_coins(i.user.id, aposta * 2)
        await i.response.send_message(embed=make_embed("🎡 ROLETA", f"Resultado: **{'🔴' if result == 'red' else '⚫' if result == 'black' else '🟢'}**\nGANHOU **{aposta*2:,} Eidocoins**!", 0x00ff00))
    elif result == "green":
        await i.response.send_message(embed=make_embed("🎡 ROLETA", "🟢 ZERO! Você PERDEU!", 0xff0000))
    else:
        await i.response.send_message(embed=make_embed("🎡 ROLETA", f"Resultado: **{'🔴' if result == 'red' else '⚫'}**\nPERDEU **{aposta:,} Eidocoins**!", 0xff0000))

@bot.tree.command(name="blackjack", description="🃏 Jogar Blackjack (21)")
@app_commands.describe(aposta="Valor da aposta")
async def blackjack(i: discord.Interaction, aposta: int):
    if aposta <= 0 or not bot.remove_coins(i.user.id, aposta):
        return await i.response.send_message("❌ Saldo insuficiente!")
    
    def card():
        return random.randint(1, 11)
    
    player = [card(), card()]
    dealer = [card(), card()]
    
    player_score = sum(player)
    dealer_score = sum(dealer)
    
    msg = f"🃏 Suas cartas: {player} = **{player_score}**\n🃏 Dealer: [{dealer[0]}, ?]"
    
    if player_score == 21:
        bot.add_coins(i.user.id, aposta * 3)
        return await i.response.send_message(embed=make_embed("🃏 BLACKJACK!", f"{msg}\n\n**BLACKJACK!** Ganhou **{aposta*3:,} Eidocoins**! 🎉", 0x00ff00))
    elif player_score > 21:
        return await i.response.send_message(embed=make_embed("🃏 BLACKJACK", f"{msg}\n\n**ESTOUROU!** Perdeu **{aposta:,} Eidocoins**!", 0xff0000))
    elif dealer_score > 21 or player_score > dealer_score:
        bot.add_coins(i.user.id, aposta * 2)
        return await i.response.send_message(embed=make_embed("🃏 BLACKJACK", f"{msg}\n\nDealer: {dealer} = **{dealer_score}**\nGANHOU **{aposta*2:,} Eidocoins**!", 0x00ff00))
    elif player_score == dealer_score:
        bot.add_coins(i.user.id, aposta)
        return await i.response.send_message(embed=make_embed("🃏 BLACKJACK", f"{msg}\n\nDealer: {dealer} = **{dealer_score}**\nEMPATE! Aposta devolvida!", 0xffaa00))
    else:
        return await i.response.send_message(embed=make_embed("🃏 BLACKJACK", f"{msg}\n\nDealer: {dealer} = **{dealer_score}**\nPERDEU **{aposta:,} Eidocoins**!", 0xff0000))

@bot.tree.command(name="slot", description="🎰 Máquina caça-níqueis")
@app_commands.describe(aposta="Valor da aposta")
async def slot(i: discord.Interaction, aposta: int):
    if aposta <= 0 or not bot.remove_coins(i.user.id, aposta):
        return await i.response.send_message("❌ Saldo insuficiente!")
    
    emojis = ["🍒", "🍋", "🍊", "🍉", "⭐", "💎", "7️⃣"]
    result = [random.choice(emojis) for _ in range(3)]
    
    if result[0] == result[1] == result[2]:
        if result[0] == "7️⃣": multiplier = 10
        elif result[0] == "💎": multiplier = 7
        elif result[0] == "⭐": multiplier = 5
        else: multiplier = 3
        win = aposta * multiplier
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("🎰 SLOT", f"{' '.join(result)}\n\n**JACKPOT!** Ganhou **{win:,} Eidocoins**! 🎉", 0x00ff00))
    elif result[0] == result[1] or result[1] == result[2]:
        win = aposta * 2
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("🎰 SLOT", f"{' '.join(result)}\n\nQuase! Ganhou **{win:,} Eidocoins**!", 0xffaa00))
    else:
        await i.response.send_message(embed=make_embed("🎰 SLOT", f"{' '.join(result)}\n\nPerdeu **{aposta:,} Eidocoins**!", 0xff0000))

@bot.tree.command(name="corrida", description="🏇 Apostar em cavalos")
@app_commands.describe(aposta="Valor da aposta", cavalo="Número do cavalo (1-5)")
async def corrida(i: discord.Interaction, aposta: int, cavalo: int):
    if aposta <= 0 or cavalo < 1 or cavalo > 5: return await i.response.send_message("❌ Valores inválidos!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    
    winner = random.randint(1, 5)
    horses = {1: "🐴", 2: "🏇", 3: "🐎", 4: "🦄", 5: "🐴"}
    
    if cavalo == winner:
        win = aposta * 5
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("🏇 CORRIDA", f"Vencedor: Cavalo {winner} {horses[winner]}\nGANHOU **{win:,} Eidocoins**! 🎉", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("🏇 CORRIDA", f"Vencedor: Cavalo {winner} {horses[winner]}\nSeu cavalo {cavalo} PERDEU **{aposta:,} Eidocoins**!", 0xff0000))

@bot.tree.command(name="raspadinha", description="🎫 Comprar raspadinha")
@app_commands.describe(quantidade="Quantas comprar")
async def raspadinha(i: discord.Interaction, quantidade: int = 1):
    if quantidade <= 0 or quantidade > 10: return await i.response.send_message("❌ Máximo 10!")
    total = quantidade * 50
    if not bot.remove_coins(i.user.id, total): return await i.response.send_message("❌ Saldo insuficiente!")
    
    prizes = {1: 10, 2: 25, 3: 50, 4: 100, 5: 500, 6: 1000}
    win = 0
    for _ in range(quantidade):
        r = random.randint(1, 6)
        win += prizes.get(r, 0)
    
    bot.add_coins(i.user.id, win)
    await i.response.send_message(embed=make_embed("🎫 RASPADINHA", f"Comprou {quantidade}x (custo: {total})\nGanhou: **{win:,} Eidocoins**!", 0x00ff00 if win >= total else 0xff0000))

@bot.tree.command(name="loteria", description="🎟️ Comprar bilhete de loteria")
@app_commands.describe(quantidade="Quantos bilhetes")
async def loteria(i: discord.Interaction, quantidade: int = 1):
    if quantidade <= 0 or quantidade > 100: return await i.response.send_message("❌ Máximo 100!")
    total = quantidade * 10
    if not bot.remove_coins(i.user.id, total): return await i.response.send_message("❌ Saldo insuficiente!")
    
    win = 0
    for _ in range(quantidade):
        if random.random() < 0.01:
            win += random.randint(1000, 10000)
        elif random.random() < 0.1:
            win += random.randint(100, 500)
    
    bot.add_coins(i.user.id, win)
    await i.response.send_message(embed=make_embed("🎟️ LOTERIA", f"Bilhetes: {quantidade} (custo: {total})\nGanhou: **{win:,} Eidocoins**!", 0x00ff00 if win > 0 else 0xff0000))

@bot.tree.command(name="bicho", description="🐔 Jogo do Bicho")
@app_commands.describe(aposta="Valor", animal="Animal (1-25)")
async def bicho(i: discord.Interaction, aposta: int, animal: int):
    if aposta <= 0 or animal < 1 or animal > 25: return await i.response.send_message("❌ Valores inválidos!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    
    bichos = ["Avestruz","Águia","Burro","Borboleta","Cachorro","Cabra","Carneiro","Camelo","Cobra","Coelho","Cavalo","Elefante","Galo","Gato","Jacaré","Leão","Macaco","Porco","Pavão","Peru","Touro","Tigre","Urso","Veado","Vaca"]
    result = random.randint(1, 25)
    
    if animal == result:
        win = aposta * 18
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("🐔 JOGO DO BICHO", f"Resultado: **{bichos[result-1]}**\nGANHOU **{win:,} Eidocoins**! 🎉", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("🐔 JOGO DO BICHO", f"Resultado: **{bichos[result-1]}**\nPERDEU **{aposta:,} Eidocoins**!", 0xff0000))

@bot.tree.command(name="mines", description="💣 Campo Minado (1-5 bombas)")
@app_commands.describe(aposta="Valor", bombas="Quantas bombas (1-5)")
async def mines(i: discord.Interaction, aposta: int, bombas: int = 3):
    if aposta <= 0 or bombas < 1 or bombas > 5: return await i.response.send_message("❌ Valores inválidos!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    
    grid = ["💣" if random.random() < bombas/25 else "💎" for _ in range(25)]
    safe = grid.count("💎")
    if random.choice(grid) == "💎":
        win = aposta * (25 // max(safe, 1))
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("💣 MINES", f"Bombas: {bombas} | Seguro!\nGANHOU **{win:,} Eidocoins**!", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("💣 MINES", f"💥 EXPLODIU!\nPERDEU **{aposta:,} Eidocoins**!", 0xff0000))

@bot.tree.command(name="duel", description="⚔️ Duelar com outro jogador")
@app_commands.describe(adversario="Quem desafiar", aposta="Valor da aposta")
async def duel(i: discord.Interaction, adversario: discord.User, aposta: int):
    if aposta <= 0: return await i.response.send_message("❌ Valor inválido!")
    if not bot.remove_coins(i.user.id, aposta): return await i.response.send_message("❌ Saldo insuficiente!")
    if not bot.remove_coins(adversario.id, aposta): 
        bot.add_coins(i.user.id, aposta)
        return await i.response.send_message(f"❌ {adversario.mention} não tem saldo!")
    
    p1 = random.randint(1, 100)
    p2 = random.randint(1, 100)
    winner = i.user if p1 > p2 else adversario
    bot.add_coins(winner.id, aposta * 2)
    await i.response.send_message(embed=make_embed("⚔️ DUELO", f"{i.user.mention}: {p1} vs {adversario.mention}: {p2}\n🏆 {winner.mention} GANHOU **{aposta*2:,} Eidocoins**!", 0x00ff00))

@bot.tree.command(name="crash", description="📈 Apostar no Crash")
@app_commands.describe(aposta="Valor da aposta")
async def crash(i: discord.Interaction, aposta: int):
    if aposta <= 0 or not bot.remove_coins(i.user.id, aposta):
        return await i.response.send_message("❌ Saldo insuficiente!")
    
    crash_point = round(random.uniform(1.1, 10.0), 1)
    cashout = round(random.uniform(1.0, crash_point), 1)
    
    if cashout < crash_point:
        win = int(aposta * cashout)
        bot.add_coins(i.user.id, win)
        await i.response.send_message(embed=make_embed("📈 CRASH", f"Crash em: **{crash_point}x**\nVocê saiu em: **{cashout}x**\nGANHOU **{win:,} Eidocoins**!", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("📈 CRASH", f"Crash em: **{crash_point}x**\n💥 CRASHOU! PERDEU **{aposta:,} Eidocoins**!", 0xff0000))

# ============================================
# 📊 GRÁFICOS E INFO (5)
# ============================================

@bot.tree.command(name="grafico", description="📊 Ver gráfico de preços simulados")
async def grafico(i: discord.Interaction):
    coins = ["EIDO", "BTC", "ETH", "DOGE"]
    prices = {c: round(random.uniform(0.5, 5.0), 2) for c in coins}
    desc = "\n".join([f"**{c}**: {'█' * int(prices[c]*10)} {prices[c]:.2f} 🪙" for c in coins])
    await i.response.send_message(embed=make_embed("📊 GRÁFICO DE PREÇOS", desc, 0x00ff00))

@bot.tree.command(name="perfil", description="👤 Ver perfil de um jogador")
@app_commands.describe(usuario="Jogador")
async def perfil(i: discord.Interaction, usuario: discord.User = None):
    u = usuario or i.user
    data = bot.users.get(str(u.id), {})
    coins = data.get('coins', 100)
    bank = data.get('bank', 0)
    level = data.get('level', 1)
    xp = data.get('xp', 0)
    await i.response.send_message(embed=make_embed(f"👤 PERFIL: {u.name}", f"💰 Carteira: **{coins:,}** 🪙\n🏦 Banco: **{bank:,}** 🪙\n⭐ Level: **{level}**\n📊 XP: **{xp}**", 0x00ff00))

@bot.tree.command(name="rank", description="🏅 Ver seu rank global")
async def rank(i: discord.Interaction):
    sorted_users = sorted(bot.users.items(), key=lambda x: x[1].get('coins', 0), reverse=True)
    for pos, (uid, _) in enumerate(sorted_users, 1):
        if int(uid) == i.user.id:
            await i.response.send_message(embed=make_embed("🏅 RANK", f"Você está em **{pos}º lugar** de {len(sorted_users)} jogadores!", 0xffd700))
            return
    await i.response.send_message("❌ Perfil não encontrado!")

@bot.tree.command(name="missao", description="📋 Receber missão diária")
async def missao(i: discord.Interaction):
    if bot.check_cooldown(i.user.id, "missao", 86400):
        missions = ["Ganhe 1000 no cassino","Pague 500 para alguém","Roube 200 de alguém","Trabalhe 3 vezes","Jogue 5 slots"]
        mission = random.choice(missions)
        reward = random.randint(100, 500)
        bot.add_coins(i.user.id, reward)
        await i.response.send_message(embed=make_embed("📋 MISSÃO", f"Missão: **{mission}**\nRecompensa: **{reward:,} Eidocoins** 🪙", 0x00ff00))
    else:
        await i.response.send_message(embed=make_embed("⏰ MISSÃO", "Você já recebeu sua missão hoje!", 0xff0000))

@bot.tree.command(name="evento", description="🎉 Ver evento atual")
async def evento(i: discord.Interaction):
    events = ["🔥 Double XP!","🎰 Slots com 2x!","💰 Bônus de 50% no daily!","🎁 Raspadinha gratuita!","🏇 Corridas com prêmio extra!"]
    event = random.choice(events)
    await i.response.send_message(embed=make_embed("🎉 EVENTO ATUAL", f"**{event}**\nAproveite enquanto dura!", 0xffd700))

# ============================================
# 🛒 LOJA (3)
# ============================================

@bot.tree.command(name="loja", description="🛒 Ver itens da loja")
async def loja(i: discord.Interaction):
    items = [
        ("🎫 Raspadinha Grátis", 100),
        ("🛡️ Seguro contra Roubo (24h)", 500),
        ("⭐ XP Boost (2x)", 300),
        ("💎 VIP (1 dia)", 1000),
        ("🎰 Rodada Grátis", 200),
    ]
    desc = "\n".join([f"**{item}**: {price:,} 🪙" for item, price in items])
    await i.response.send_message(embed=make_embed("🛒 LOJA EIDOLON", desc, 0x00ff00))

@bot.tree.command(name="comprar", description="🛍️ Comprar item da loja")
@app_commands.describe(item="Qual item comprar")
@app_commands.choices(item=[app_commands.Choice(name="🎫 Raspadinha Grátis (100)", value="raspadinha")])
async def comprar(i: discord.Interaction, item: str):
    prices = {"raspadinha": 100}
    if item in prices:
        if bot.remove_coins(i.user.id, prices[item]):
            await i.response.send_message(embed=make_embed("🛍️ COMPRA", f"Você comprou **{item}** por **{prices[item]:,} Eidocoins**!", 0x00ff00))
        else:
            await i.response.send_message("❌ Saldo insuficiente!")

@bot.tree.command(name="presente", description="🎁 Enviar presente para alguém")
@app_commands.describe(usuario="Quem recebe", quantidade="Quantas Eidocoins")
async def presente(i: discord.Interaction, usuario: discord.User, quantidade: int):
    if quantidade <= 0: return await i.response.send_message("❌ Valor inválido!")
    if bot.remove_coins(i.user.id, quantidade):
        bot.add_coins(usuario.id, quantidade)
        await i.response.send_message(embed=make_embed("🎁 PRESENTE", f"{i.user.mention} enviou **{quantidade:,} Eidocoins** para {usuario.mention}!", 0x00ff00))
    else:
        await i.response.send_message("❌ Saldo insuficiente!")

# ============================================
# 🤝 SOCIAL (2)
# ============================================

@bot.tree.command(name="apostar", description="🤝 Criar aposta pública")
@app_commands.describe(valor="Valor da aposta", descricao="O que está apostando")
async def apostar(i: discord.Interaction, valor: int, descricao: str):
    if valor <= 0 or not bot.remove_coins(i.user.id, valor):
        return await i.response.send_message("❌ Saldo insuficiente!")
    await i.response.send_message(embed=make_embed("🤝 APOSTA", f"{i.user.mention} apostou **{valor:,} Eidocoins**\n📝 {descricao}\nReaja ✅ para aceitar!", 0xffd700))

@bot.tree.command(name="ranking", description="🏆 Ranking completo do servidor")
async def ranking(i: discord.Interaction):
    sorted_users = sorted(bot.users.items(), key=lambda x: x[1].get('coins', 0), reverse=True)
    desc = ""
    for pos, (uid, data) in enumerate(sorted_users, 1):
        user = await bot.fetch_user(int(uid))
        desc += f"**{pos}º** {user.name}: {data.get('coins', 0):,} 🪙\n"
    await i.response.send_message(embed=make_embed("🏆 RANKING COMPLETO", desc[:4000], 0xffd700))

# ============================================
# EVENTOS
# ============================================

@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════╗
║   🎰 EIDOLON CASINO 🎰            ║
║   Moeda: Eidocoins 🪙            ║
║   Comandos: 30+                   ║
╚══════════════════════════════════════╝
    """)
    print(f"🎰 Bot: {bot.user}")
    print(f"🪙 /carteira - Ver saldo")
    print(f"🎁 /daily - Bônus diário\n")
    await bot.change_presence(activity=discord.Game(name="🎰 /carteira | EIDOLON CASINO"))

if __name__ == "__main__":
    TOKEN = "MTUxMjk2MjE2MjMwMDAyNzAxMQ.GigkqR.jo7JVpjvhFVLNYbyDB6ej5VwtpS5bpNVGY7aQw"
    print("🎰 Iniciando EIDOLON CASINO...\n")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\n❌ TOKEN INVÁLIDO!")
    except KeyboardInterrupt:
        print("\n🛑 CASINO DESLIGADO!")
