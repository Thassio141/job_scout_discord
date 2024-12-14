import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from commands import setup_commands
from schedule import scheduled_search
load_dotenv()

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    # Inicia o agendamento da busca programada
    scheduled_search()


setup_commands(bot)

bot.run(TOKEN)
