#base de dados
from char_db import Base, Player, Personagem, Atributos, Itens, Equipamentos
from dotenv import load_dotenv
import os
#bot
import logging
import discord
from discord.ext import commands

#env
load_dotenv()
token =os.getenv('DISCORD_BOT_TOKEN')