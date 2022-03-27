import os
import discord
from discord.ext import commands
from Music import Music

intents  = discord.Intents.all()
client = commands.Bot(command_prefix = '-', intents=intents)
client.remove_command('help')

client.add_cog(Music(client))

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


client.run(os.getenv('TOKEN'))