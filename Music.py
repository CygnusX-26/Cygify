import asyncio
import os
import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import validators
import requests
import base64
from pprint import pprint



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
    

    async def check_queue(self, ctx):
        if self.queue != []:
            voice = ctx.guild.voice_client
            await self.play_song(ctx, voice, self.queue.pop(0))


    async def play_song(self, ctx, voice, query):
        valid = validators.url(query)
        if (valid):
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        else:
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'default_search':'ytsearch'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
        if (valid):
            await ctx.send(f"Now playing: {info['title']}")
        else:
            await ctx.send(f"Now playing: {info['entries'][0]['title']}")
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        if (valid):
            URL = info['formats'][0]['url']
        else:
            URL = info['entries'][0]['formats'][0]['url']
        voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda x = None: asyncio.run_coroutine_threadsafe(self.check_queue(ctx), self.bot.loop))


    @commands.command()
    async def song(self, ctx):
        await ctx.send(f"Now playing: {ctx.guild.voice_client.source.title}")
        
    @commands.command(aliases = ["p", "connect"])
    async def play(self, ctx, * , query):
        try:
            vc = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("You must be in a voice channel to use this command.")
            return
        if (vc == None):
            await ctx.send("You are not in a voice channel")
            return
        if (ctx.guild.voice_client == None):
            voice = await vc.connect()
        else:
            voice = get(self.bot.voice_clients, guild=ctx.guild)
        
        if not voice.is_playing():
            await self.play_song(ctx, voice, query)
        else:
            await ctx.send(f"Added your song to the queue.")
            self.queue.append(query)
            return
        
    
    @commands.command(aliases = ["d"])
    async def disconnect(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.send("Disconnected")
        else:
            await ctx.send("I am not connected to a voice channel")
    
    @commands.command()
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
            await ctx.send("Paused the current track")
        else:
            await ctx.send("I am not playing anything")

    @commands.command()
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            voice.resume()
            await ctx.send("Resumed the current track")
        else:
            await ctx.send("I am not paused")
    
    @commands.command()
    async def stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            self.queue = []
            voice.stop()
            await ctx.send("Stopped the queue")
        else:
            await ctx.send("I am not playing anything")
    
    @commands.command()
    async def skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if (voice and voice.is_playing()):
            voice.stop()
            await ctx.send("Skipped the current track")
        else:
            await ctx.send("I am not playing anything")





    @commands.command()
    async def track(self, ctx, * , query):
        access = os.getenv('SP_ID') + ":" + os.getenv('SP_SECRET')
        response = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'client_credentials'}, headers = {'Authorization':'Basic ' + base64.b64encode(access.encode()).decode()}).json()
        id = query[34:]
        headers = {
        'Authorization': f'Bearer {response["access_token"]}',
        }
        data = requests.get(f"https://api.spotify.com/v1/playlists/{id}", headers=headers).json()
        for i in range(len(data['tracks']['items'])):
            self.queue.append(data['tracks']['items'][i]['track']['album']['name'])
        try:
            vc = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("You must be in a voice channel to use this command.")
            return
        if (vc == None):
            await ctx.send("You are not in a voice channel")
            return
        if (ctx.guild.voice_client == None):
            voice = await vc.connect()
        else:
            voice = get(self.bot.voice_clients, guild=ctx.guild)
        if (not voice.is_playing()):
            await self.play_song(ctx, voice, self.queue.pop(0))
    
    @commands.command()
    async def queue(self, ctx):
        for i in self.queue:
            await ctx.send(i)
            
        
