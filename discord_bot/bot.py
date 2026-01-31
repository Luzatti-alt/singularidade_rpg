#base de dados
from dotenv import load_dotenv
import os
from char import Char
#bot
import logging
import discord
from discord.ext import commands

#secrets
load_dotenv()
token =os.getenv('DISCORD_BOT_TOKEN')

#configurando bot
log = logging.FileHandler(filename='bot.log',encoding='utf-8',mode='w')
#intents(todas as permissoes via intents, temos que habilitar manualmente)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

#cargos
player = "Player"
GM = "GM"
#bot
bot = commands.Bot(command_prefix='!',intents=intents,case_insensitive=True)#!comando -> intent
@bot.event
#sempre que for on_ready é quando esta online
async def on_ready():
    print(f"bot {bot.user.name} esta online")

@bot.event
async def on_member_join(member):
    #manda no pv deste jeito member.send()
    canal_geral = discord.utils.get(member.guild.text_channels, name="geral")
    await canal_geral.send(f"""Bem vindo {member.name} ao servidor singularidade rpg!
                           qualquer dúvida digite !comandos para a lista de comandos
                           vamos criar sua ficha digite !ficha para começar""")

@bot.event
#moderar mensagens
async def on_message(msg):#somente 1 parametro senão nn funciona
    member = msg.author#tem que definir manualmente
    #evitar auto reply
    if msg.author == bot.user:
        return
    #piada
    if "não vou participar da sessão" in msg.content.lower():
        try:
            await member.send("vai sim")
            await msg.delete()
            await msg.channel.send(f"{member.mention} confirmou que vai participar da sessão")
        except:
            print("algum erro")
    await bot.process_commands(msg)#lidar com todas as outras mensagens
        
#comando(ctx) ctx=contexto -> !comando

#criação de ficha(DM)
@bot.command()
async def ficha(ctx):#para mandar a dm e ver o que foi mandado dps
    member = ctx.author
    cargo= discord.utils.get(ctx.guild.roles, name=player)
    #add cargo
    if cargo:
        await member.add_roles(cargo)
    await ctx.send(f"{member.mention} criação de ficha no privado olhe sua dm")
    await member.send(f"{member.mention} iniciando criação de ficha")
    Char.criar_char_user(member.name)
    await criar_ficha(member)
async def criar_ficha(member):
    await member.send(f"""Para criar sua ficha vai ser passada algumas informações
info basica do rpg
A ordem da criação é nome, origem(classe principal), especialização(classe secundaria) e distribuição de atributos
digite !nome + para definir o nome do personagem
digite !origem + origem para escolher a origem
digite !especialização + origem para escolher a especialização
se especialização for reestringido ele ja colocara automaticamente
digite !atributo + forca:valor, destreza:valor, constituicao:valor, inteligencia:valor, sabedoria:valor, essencia:valor, essencia_negativa:valor, stamina:valor, fama:valor
            
Regras de pontos:
Você tem 10 pontos de atributo para gastar livremente(15 se reestringido e não pode gastar na essencia)
- nivel mínimo de stats: 8(se restringido essencia sera sempre 8)
- nivel máximo de stats: 25
- Você tem 10 pontos para gastar
- Reduzir abaixo de 10 gera pontos extras
- Movimento será calculado automaticamente
- a cada lv do personagem se ganha 3 pontos """)
    await member.send("""Tabela de custo de atributos:\nNivel de stats | Pontos\n8 -> +2  (ganha pontos)\n9  -> +1 \n10 ->  0\n11 -> -1\n12 -> -2\n13 -> -3\n14 -> -4\n15 -> -4\n16 -> -6\n17 -> -6\n18 -> -8\n19 -> -8\n20 -> -10\n21 -> -10\n22 -> -10\n23 -> -11\n24 -> -11\n25 -> -12""")

#na dm criando ficha -> alterar json e gerar arquivo ficha pronta-> html/pdf da ficha
@bot.command()
@commands.dm_only()
async def nome(ctx):
    quem = ctx.author
    msg = ctx.message
    origem_escolhida = msg.content[6:]
    Char.mudar_stats(quem,msg.content[:5],origem_escolhida)
@nome.error
async def erro_nome(ctx,error):
    pass
@bot.command()
@commands.dm_only()
async def origem(ctx):
    quem = ctx.author
    msg = ctx.message
    origem_escolhida = msg.content[8:]
    Char.mudar_stats(quem,msg.content[:7],origem_escolhida)
@origem.error
async def erro_origem(ctx,error):
    pass

@bot.command()
@commands.dm_only()
async def especialização(ctx):
    quem = ctx.author
    msg = ctx.message
    especialização_escolhida = msg.content[15:]
    Char.mudar_stats(quem,msg.content[:15],especialização_escolhida)
@especialização.error
async def erro_especialização(ctx,error):
    pass

@bot.command()
@commands.dm_only()
async def atributo(ctx):
    quem = ctx.author
    msg = ctx.message
    atributo_escolhido = msg.content[9:]
    Char.mudar_stats(quem,msg.content[:9],atributo_escolhido)
@atributo.error
async def erro_atributo(ctx,error):
    pass

#comandos GM
@bot.command()
@commands.has_role(GM)
async def dia(ctx,*,pergunta=None):#ja vai fazer a pegunta
    embed = discord.Embed(title="Dia da sessão",description=f"Qual dia será a sessão\n\n Sábado\n Domingo\n Não posso esse fim de semana\n feriado(se tiver)")
    votacao = await ctx.send(embed=embed)
    await votacao.add_reaction("🔥")
    await votacao.add_reaction("1️⃣")
    await votacao.add_reaction("2️⃣")
    await votacao.add_reaction("3️⃣")
    await votacao.add_reaction("4️⃣")
@dia.error
async def dia_erro(ctx,error):
    member = ctx.author
    #se nn tiver o cargo
    if isinstance(error,commands.MissingRole):
        await ctx.send(f"{member.mention} não é um GM comando exclusivo para GM")
        await ctx.add_reaction("✅")
        await ctx.add_reaction("❌")


async def aviso(guild,tipo):
    #manda no pv deste jeito member.send()
    canal_geral = discord.utils.get(guild.text_channels, name="geral")
    if tipo == "inicio":
        await canal_geral.send(f"""Sessão prestes a iniciar""")
    elif tipo == "fim":
        await canal_geral.send(f"""Sessão finalizada""")
    else:
        await canal_geral.send(f"""aaaaa""")


#comandos gerais
@bot.command()
async def comandos(ctx):
    member = ctx.author
    await ctx.send(f"""{member.mention} a lista de comandos do bot é:
                           !ficha ajuda na criação da ficha e se torne um jogador e ganhe o cargo
                           !sair remove cargo de player(vc ainda pode participar no chat)
                           !comandos esta mensagem
                           """)
@bot.command()
async def poll(ctx,*,pergunta):
    embed = discord.Embed(title="Dia da sessão",description=pergunta)
    votacao = await ctx.send(embed=embed)
    await ctx.add_reaction("✅")
    await ctx.add_reaction("❌")

#comandos player
@bot.command()
@commands.has_role(player)
async def sair(ctx):
    member = ctx.author
    cargo= discord.utils.get(ctx.guild.roles, name=player)
    #remover cargo
    if cargo:
        await member.remove_roles(cargo)
    await ctx.send(f"{member.mention} saindo da campanha seu cargo não é mais {player}")
@sair.error
async def sair_erro(ctx,error):
    member = ctx.author
    #se nn tiver o cargo
    if isinstance(error,comandos.MissingRole):
        await ctx.send(f"{member.mention} não é {player} então não pode sair da campanha")

#rodar bot
bot.run(token,log_handler=log,log_level=logging.DEBUG)