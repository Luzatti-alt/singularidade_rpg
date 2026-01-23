#base de dados
#from char_db import Base, Player, Personagem, Atributos, Itens, Equipamentos
from dotenv import load_dotenv
import os
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
#bot
bot = commands.Bot(command_prefix='!',intents=intents)#!comando -> intent
@bot.event
#sempre que for on_ready é quando esta online
async def on_ready():
    print(f"bot {bot.user.name} esta online")

@bot.event
async def on_member_join(member):
    #manda no pv deste jeito member.send()
    canal_geral = discord.utils.get(member.guild.text_channels, name="geral")
    await canal_geral.send(f"Bem vindo {member.name} ao servidor singularidade rpg! vamos criar sua ficha digite !ficha para começar")

@bot.event
#moderar mensagens
async def on_message(msg):#somente 1 parametro senão nn funciona
    member = msg.author#tem que definir manualmente
    #evitar auto reply
    if msg.author == bot.user:
        return
    if "não vou participar da sessão" in msg.content.lower():
        try:
            await member.send("vai sim")
            await msg.delete()
            await msg.channel.send(f"{member.mention} confirmou que vai participar da sessão")
        except:
            print("algum erro")
    await bot.process_commands(msg)#lidar com todas as outras mensagens
#comando(ctx) contexto -> !comando
@bot.command()
async def ficha(ctx):
    member = ctx.author
    role= discord.utils.get(ctx.guild.roles, name="Player")
    await ctx.send(f"{member.mention} iniciando criação de ficha")
        
#rodar bot
bot.run(token,log_handler=log,log_level=logging.DEBUG)