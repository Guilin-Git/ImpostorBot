import discord
from discord.ext import commands
import random
import json
import os
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis do arquivo .env

# Configuração do bot com incase_sensitive para aceitar letras maiúsculas (!IMPOSTOR)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# Configurações globais e estado dos jogos
CONFIGURACOES = {
    "tempo_rodada": 30, # segundos
    "quantidade_turnos": 2 
}
# Guarda qual servidor tem um jogo rodando, e se ele foi cancelado
JOGOS_EM_ANDAMENTO = {}
JOGOS_CANCELADOS = {}

# Manipulação de Leaderboard (Salvo no disco)
def carregar_leaderboard():
    caminho = os.path.join(os.path.dirname(__file__), 'leaderboard.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_leaderboard(dados):
    caminho = os.path.join(os.path.dirname(__file__), 'leaderboard.json')
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

LEADERBOARD = carregar_leaderboard()

def registrar_vitorias(guild_id, membros_ganhadores):
    g_id = str(guild_id)
    if g_id not in LEADERBOARD:
        LEADERBOARD[g_id] = {}
        
    for membro in membros_ganhadores:
        u_id = str(membro.id)
        if u_id not in LEADERBOARD[g_id]:
            LEADERBOARD[g_id][u_id] = 0
        LEADERBOARD[g_id][u_id] += 1
        
    salvar_leaderboard(LEADERBOARD)

# Manipulação do Banco Clássico de Palavras
def carregar_palavras():
    caminho = os.path.join(os.path.dirname(__file__), 'palavras.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo palavras.json não foi encontrado em {caminho}!")
        return []

PALAVRAS_DO_JOGO = carregar_palavras()

# Função do OLLAMA API para injetar IA nas palavras
async def gerar_tema_ollama(tema: str):
    url = "http://127.0.0.1:11434/api/generate"
    prompt = f"""Você é o administrador de um jogo. 
                 O usuário enviará um TEMA.
                 Sua missão: 1. Buscar no seu conhecimento o elemento MAIS FAMOSO que pertence estritamente a esse TEMA (ex: se for um cantor, cite uma música real dele).
                 2. Criar uma DICA de 1 palavra que descreva uma característica ou ambiente dessa palavra escolhida.
                 Tema: {tema} Responda EXATAMENTE no formato abaixo, sem pontuação extra, sem asteriscos e sem diálogo: 
                 Palavra: [SUA PALAVRA] | Dica: [SUA DICA]"""
    payload = {
        "model": "qwen3:14b",
        "prompt": prompt,
        "stream": False
    }
    try:
        # Aumentado o timeout para 120s para dar tempo ao Ollama carregar o modelo pesado (cold-start) e responder
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=120) as response:
                if response.status == 200:
                    data = await response.json()
                    resposta = data.get("response", "").strip()
                    # Faz o parse da string bizarra e força separar. Ex: Palavra: Mustang | Dica: Veiculo
                    partes = resposta.split('|')
                    if len(partes) >= 2:
                        p_palavra = partes[0].replace('Palavra:', '').replace('**', '').strip()
                        p_dica = partes[1].replace('Dica:', '').replace('**', '').strip()
                        return {"palavra": p_palavra, "dica": p_dica}
    except Exception as e:
         print(f"Erro na conexão ao Ollama: {type(e).__name__} - {e}")
    return None


@bot.event
async def on_ready():
    print(f'🤖 Bot {bot.user.name} ({bot.user.id}) está online e pronto para jogar!')
    print('-----------------------------------------')

@bot.command(name='set_time', help='Define o tempo em segundos de cada turno.')
async def set_time(ctx, segundos: int):
    CONFIGURACOES["tempo_rodada"] = segundos
    await ctx.send(f"⏱️ O tempo que cada pessoa tem para digitar foi alterado para **{segundos} segundos**!")

@bot.command(name='set_turns', help='Define a quantidade total de rodadas no jogo.')
async def set_turns(ctx, turnos: int):
    CONFIGURACOES["quantidade_turnos"] = turnos
    await ctx.send(f"🔄 A quantidade de turnos totais foi alterada para **{turnos}**!")

@bot.command(name='stop_game', aliases=['forcar_parada', 'parar'], help='Cancela forçadamente um jogo em andamento.')
async def stop_game(ctx):
    guild_id = ctx.guild.id
    if JOGOS_EM_ANDAMENTO.get(guild_id, False):
        JOGOS_CANCELADOS[guild_id] = True
        await ctx.send("🚨 Recebido! Cancelando todos os processamentos e rodadas da partida ativa do sistema...")
    else:
        await ctx.send("Mas não tem nenhuma partida sendo jogada no momento! 🤔")

@bot.command(name='leaderboard', aliases=['ranking', 'placar'], help='Exibe o ranking de vitórias do servidor.')
async def mostrar_leaderboard(ctx):
    guild_id = str(ctx.guild.id)
    banco_servidor = LEADERBOARD.get(guild_id, {})
    
    if not banco_servidor:
         await ctx.send("Calma aí, apressado! Ninguém nesse servidor venceu uma partida ainda... Joguem com `!impostor` primeiro!")
         return
         
    # Ordena o dicionario do maior para o menor
    ranking_ordenado = sorted(banco_servidor.items(), key=lambda x: x[1], reverse=True)
    
    msg_leaderboard = "🏆 **PLACAR OFICIAL DOS SOBREVIVENTES** 🏆\n\n"
    # Pega apenas o top 10
    limit = min(len(ranking_ordenado), 10)
    
    for i in range(limit):
         user_id, vitorias = ranking_ordenado[i]
         emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔹"
         msg_leaderboard += f"{emoji} **{i+1}º** - <@{user_id}>: **{vitorias} vitórias**\n"
         
    await ctx.send(msg_leaderboard)

@bot.command(name='impostor', help='Inicia uma rodada do jogo do impostor. Passe um tema no final para fazer a Inteligência Artificial bolar a palavra.')
async def jogar_impostor(ctx, *, tema_personalizado: str = None):
    guild_id = ctx.guild.id
    
    if JOGOS_EM_ANDAMENTO.get(guild_id, False):
        await ctx.send("❌ Já existe um jogo rolando ou votação ativa. Aguarde terminar ou digite `!stop_game` para forçar.")
        return

    # Inicia e define variaveis de estado com a segurança que nenhum botão !stop foi pressionado ainda
    JOGOS_EM_ANDAMENTO[guild_id] = True
    JOGOS_CANCELADOS[guild_id] = False

    # Verifica se o autor da mensagem está em algum canal de voz
    if getattr(ctx.author.voice, "channel", None) is None:
        await ctx.send(f"{ctx.author.mention}, você precisa entrar em um canal de voz para que eu detecte os participantes e inicie o jogo!")
        JOGOS_EM_ANDAMENTO[guild_id] = False
        return

    canal_voz = ctx.author.voice.channel
    # Pega todos os membros do canal, ignorando os bots
    membros = [membro for membro in canal_voz.members if not membro.bot]

    # Verifica se há o mínimo de pessoas necessário
    if len(membros) < 3:
        await ctx.send("Vocês precisam de pelo menos 3 pessoas (não-bots) no canal de voz para jogar de forma justa!")
        JOGOS_EM_ANDAMENTO[guild_id] = False
        return

    # LÓGICA DE DICAS (IA vs BANCO FIXO)
    if tema_personalizado:
        await ctx.send(f"🧠 Consultando a inteligência artificial para bolar uma palavra no modelo **qwen3:14b** sobre o tema: `{tema_personalizado}`...")
        resultado_ia = await gerar_tema_ollama(tema_personalizado)
        if resultado_ia is None:
             await ctx.send("⚠️ Erro: Não consegui me conectar e receber formato válido do seu Ollama rodando localmente na tela do computador. Vou usar uma palavra do meu banco padrão (`palavras.json`).")
             if not PALAVRAS_DO_JOGO:
                  JOGOS_EM_ANDAMENTO[guild_id] = False
                  return
             tema = random.choice(PALAVRAS_DO_JOGO)
             palavra = tema["palavra"]
             dica = random.choice(tema["dicas"])
        else:
             palavra = resultado_ia["palavra"]
             dica = resultado_ia["dica"]
    else:
        if not PALAVRAS_DO_JOGO:
            await ctx.send("O banco de palavras não pôde ser carregado! Configure o arquivo `palavras.json`.")
            JOGOS_EM_ANDAMENTO[guild_id] = False
            return
        # Sorteia do JSON
        tema = random.choice(PALAVRAS_DO_JOGO)
        palavra = tema["palavra"]
        dica = random.choice(tema["dicas"])

    try:
        # Embaralha a ordem para não seguir lista óbvia
        random.shuffle(membros)
        impostor = random.choice(membros)

        await ctx.send(f"🎲 **O JOGO COMEÇOU!**\nSorteando impostor para os {len(membros)} participantes do canal **{canal_voz.name}**...\nChequem agora suas mensagens privadas (DM)!")

        # Envia as DMs
        for membro in membros:
            try:
                if membro == impostor:
                    await membro.send(f"🤫 **VOCÊ É O IMPOSTOR!**\nPara de ajudar as pessoas! Você tem que adivinhar a palavra.\nVocê recebeu a pista de que a palavra lida com a categoria: **{dica}**\nTente deduzir a palavra pelas dicas de outras pessoas!")
                else:
                    await membro.send(f"😇 Você é **Inocente**!\nA palavra do jogo é: **{palavra}**\nDê dicas inteligentes que mostrem para os outros inocentes que você sabe o que é, mas sem deixar tão óbvio para o impostor!")
            except discord.Forbidden:
                await ctx.send(f"⚠️ Atenção: Não consegui enviar DM para **{membro.name}**. Peça para ele habilitar as Mensagens Diretas do servidor!")

        await asyncio.sleep(4)
        
        # -------------------
        # SISTEMA DE TURNOS
        # -------------------
        turnos = CONFIGURACOES["quantidade_turnos"]
        tempo_rodada = CONFIGURACOES["tempo_rodada"]

        for rodada in range(turnos):
            if JOGOS_CANCELADOS.get(guild_id, False):
                 await ctx.send("🔴 **Parada Solicitada.** Descontinuando todos os turnos!")
                 JOGOS_EM_ANDAMENTO[guild_id] = False
                 return
                 
            await ctx.send(f"\n📢 **--- INICIANDO RODADA {rodada + 1} DE {turnos} ---**")
            await asyncio.sleep(2)
            
            for membro in membros:
                if JOGOS_CANCELADOS.get(guild_id, False):
                     await ctx.send("🔴 **Parada Solicitada.** Interrompendo rodada...")
                     JOGOS_EM_ANDAMENTO[guild_id] = False
                     return
            
                msg_vez = await ctx.send(f"🗣️ Sua vez, {membro.mention}! Você tem **{tempo_rodada} segundos** para enviar apenas **SUA DICA FIXA** aqui.")
                
                def check(m):
                    return m.author == membro and m.channel == ctx.channel

                try:
                    # Timeout assincrono cortado no timer
                    msg = await bot.wait_for('message', check=check, timeout=tempo_rodada)
                    
                    if JOGOS_CANCELADOS.get(guild_id, False):
                         JOGOS_EM_ANDAMENTO[guild_id] = False
                         return
                         
                    await ctx.send(f"✅ Anotado! O {membro.display_name} já deu sua dica.")
                except asyncio.TimeoutError:
                    if JOGOS_CANCELADOS.get(guild_id, False):
                         JOGOS_EM_ANDAMENTO[guild_id] = False
                         return
                    await ctx.send(f"⏰ O tempo esgotou e o silêncio ecoou... Passando a vez.")
                    
                await asyncio.sleep(1.5)
                
        # -------------------
        # SISTEMA DE VOTAÇÃO
        # -------------------
        if JOGOS_CANCELADOS.get(guild_id, False):
            JOGOS_EM_ANDAMENTO[guild_id] = False
            return
            
        await ctx.send("\n🚨 **--- HORA DA VOTAÇÃO ---** 🚨\nChegou a hora de apontarem o dedo! Reaja a esta mensagem no botão numérico de quem você acha que é o impostor!")
        
        emojis_votacao = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        limit_jogadores = min(len(membros), 10)
        
        texto_opcoes = "**Vote Clicando:**\n"
        for i in range(limit_jogadores):
            texto_opcoes += f"{emojis_votacao[i]} - {membros[i].mention}\n"
            
        voto_msg = await ctx.send(texto_opcoes)
        
        # Bot adiciona a reação base inicial pra facilitar mobile
        for i in range(limit_jogadores):
            await voto_msg.add_reaction(emojis_votacao[i])
            
        await ctx.send("Vocês têm **30 segundos** para escolher as reações firmemente agora!")
        
        # Faz uma espera quebravel com 5 hooks seguidos pra checar se foi cancelado
        for timer_stop in range(6): 
             if JOGOS_CANCELADOS.get(guild_id, False):
                  await ctx.send("🔴 **Votação Interrompida.**")
                  JOGOS_EM_ANDAMENTO[guild_id] = False
                  return
             await asyncio.sleep(5)
        
        # Resgata mensagem do servidor pra ter quantidade de likes/reações nela pós votação
        voto_msg = await ctx.channel.fetch_message(voto_msg.id)
        votos = []
        
        for reaction in voto_msg.reactions:
            if reaction.emoji in emojis_votacao:
                idx = emojis_votacao.index(reaction.emoji)
                if idx < limit_jogadores:
                    quant_real = max(0, reaction.count - 1)
                    votos.append((membros[idx], quant_real))
                    
        # Define os resultados baseados na contagem
        if votos:
            votos.sort(key=lambda x: x[1], reverse=True)
            quant_mais_votos = votos[0][1]
            
            if quant_mais_votos == 0:
                 await ctx.send(f"Nenhum de vocês teve coragem de votar... O impostor fugiu! E ele realmente era o {impostor.mention}!")
                 registrar_vitorias(ctx.guild.id, [impostor]) # Vence Impostor
            else:
                 # Empates?
                 lista_empatados = [v[0] for v in votos if v[1] == quant_mais_votos]
                 if len(lista_empatados) > 1:
                     await ctx.send(f"😱 **Empate nos votos!** Vocês não entraram em acordo e deixaram o impostor escapar. Ele na verdade era... {impostor.mention}!")
                     registrar_vitorias(ctx.guild.id, [impostor]) # Vence Impostor
                 else:
                     o_mais_votado = lista_empatados[0]
                     if o_mais_votado == impostor:
                         await ctx.send(f"🎉 **Parabéns, descobriram o impostor!** A eliminação foi certeira, era mesmo o {impostor.mention}!")
                         inocentes = [m for m in membros if m != impostor]
                         registrar_vitorias(ctx.guild.id, inocentes) # Vencem Inocentes coletivos
                     else:
                         await ctx.send(f"😭 **Os inocentes perderam!** Vocês atiraram cegamente e o mais votado foi {o_mais_votado.mention}... Mas o verdadeiro Impostor era o {impostor.mention}!")
                         registrar_vitorias(ctx.guild.id, [impostor]) # Vence Impostor
        else:
             await ctx.send(f"Algo não funcionou perfeitamente nos votos ou ninguém votou. Ponto nulo para todos. O impostor era {impostor.mention}!")

    except Exception as erro:
        await ctx.send(f"Algo explodiu e a rodada encerrou brutalmente. Erro no core: {erro}")
    finally:
        JOGOS_EM_ANDAMENTO[guild_id] = False
        JOGOS_CANCELADOS[guild_id] = False

# =========================================================
# INSIRA O SEU TOKEN AQUI NA LINHA DE BAIXO E SALVE O ARQUIVO
# =========================================================
TOKEN = os.getenv('TOKEN')

bot.run(TOKEN)
