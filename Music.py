import asyncio
import os
import discord
from discord.ext import commands
from discord.errors import ClientException
from discord.utils import get
import youtube_dl
import validators
import requests
import base64
from pprint import pprint



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.nowPlaying = None
    
    async def check_queue(self, ctx):
        if self.queue[ctx.guild.id] != []:
            voice = ctx.guild.voice_client
            user = self.queue[ctx.guild.id][0][1]
            image = self.queue[ctx.guild.id][0][2]
            await self.play_song(ctx, voice, self.queue[ctx.guild.id].pop(0)[0], user, image)


    async def play_song(self, ctx, voice, query, user, image = None):
        hasImage = True
        if (image == None):
            hasImage = False
        valid = validators.url(query)
        if (valid):
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        else:
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'default_search':'ytsearch'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        if (valid):
            URL = info['formats'][0]['url']
        else:
            URL = info['entries'][0]['formats'][0]['url']
        if valid:
            self.nowPlaying = [info['title'], user, image]
        else:
            self.nowPlaying = [info['entries'][0]['title'], user, image]
        try:
            voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda x = None: asyncio.run_coroutine_threadsafe(self.check_queue(ctx), self.bot.loop))
            if (valid):
                # await ctx.send(f'Now playing: {info["title"]}')
                embed = discord.Embed(
                title = f"Now playing: {info['title']}",
                description = f"Requested by: {user}",
                color = discord.Color.dark_blue()
                )
                if (hasImage):
                    embed.set_thumbnail(url = image)
                await ctx.send(embed = embed)
            else:
                # await ctx.send(f'Now playing: {info["entries"][0]["title"]}')
                embed = discord.Embed(
                title = f"Now playing: {info['entries'][0]['title']}",
                description = f"Requested by: {user}",
                color = discord.Color.dark_blue()
                )
                if (hasImage):
                    embed.set_thumbnail(url = image)
                await ctx.send(embed = embed)
        except ClientException:
            await ctx.send("You are sending commands too fast!")
        


    @commands.command()
    async def song(self, ctx):
        embed = discord.Embed(
        title = f"Now playing: {self.nowPlaying[0]}",
        description = f"Requested by: {self.nowPlaying[1]}",
        color = discord.Color.dark_blue()
        )
        if (self.nowPlaying[2] != None):
            embed.set_thumbnail(url = self.nowPlaying[2])
        await ctx.send(embed = embed)
        
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
            await self.play_song(ctx, voice, query, ctx.author.name)
        else:
            await ctx.send(f"Added your song to the queue.")
            if (not ctx.guild.id in self.queue):
                self.queue[ctx.guild.id] = []

            self.queue[ctx.guild.id].append([query, ctx.author.name, None])
            return
        
    
    @commands.command(aliases = ["d"])
    async def disconnect(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            if not ctx.guild.id in self.queue:
                await voice.disconnect()
                await ctx.send("Disconnected")
            self.queue[ctx.guild.id] = []
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
            self.queue[ctx.guild.id] = []
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
        if (not ctx.guild.id in self.queue):
            self.queue[ctx.guild.id] = []
        for i in range(len(data['tracks']['items'])):
            #if add new things, add them to the end of the sublist
            author = data['tracks']['items'][i]['track']['artists'][0]['name']
            songname = data['tracks']['items'][i]['track']['name']
            url = data['tracks']['items'][i]['track']['album']['images'][0]['url']
            self.queue[ctx.guild.id].append([songname + " - " + author, ctx.author.name, url])
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
            song = self.queue[ctx.guild.id].pop(0)[0]
            name = ctx.author.name
            url = data['tracks']['items'][0]['track']['album']['images'][0]['url']
            await self.play_song(ctx, voice, song, name, url) # add new params here if needed in the future
        else:
            await ctx.send("Added to queue!")

    
    @commands.command(aliases = ['q'])
    async def queue(self, ctx, pageNum = None):
        try:
            if (self.queue[ctx.guild.id] == []):
                await ctx.send("There is nothing in the queue.")
                return
            str = ""
            pageCount = len(self.queue[ctx.guild.id]) // 10 + 1
            if pageCount == 1:
                for i in self.queue[ctx.guild.id]:
                    str += "**" + i[0] + "**" + " requested by: " + i[1] + "\n"
                pageNum = 1
            else:
                if (pageNum == None):
                    pageNum = 1
                else:
                    pageNum = int(pageNum)
                if (pageNum > pageCount or pageNum < 1):
                    await ctx.send("Invalid page number.")
                    return
                for i in range(10 * (pageNum - 1), 10 * pageNum):
                    if (i >= len(self.queue[ctx.guild.id])):
                        break
                    str += "**" + self.queue[ctx.guild.id][i][0] + "**" + " requested by: " + self.queue[ctx.guild.id][i][1] + "\n"
            embed = discord.Embed(title = f"Queue for {ctx.guild.name}", description = f"Now playing: **{self.nowPlaying[0]}** Requested by: {self.nowPlaying[1]}", color = discord.Color.dark_blue())
            embed.add_field(name = f"Songs in queue:", value = str)
            embed.set_footer(text = f"Page {pageNum}/{pageCount}")
            await ctx.send(embed = embed)
        except KeyError:
            await ctx.send("There is nothing in the queue.")
        

            
        
