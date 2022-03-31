import os
import discord
from discord.ext import commands
from Music import Music
from Bot import Bot

intents  = discord.Intents.all()
client = commands.Bot(command_prefix = '-', intents=intents)
client.remove_command('help')

client.add_cog(Music(client))
client.add_cog(Bot(client))

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game("use -help for a list of commands!")
    )


client.run(os.getenv('TOKEN'))