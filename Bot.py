import discord
from discord.ext import commands


class Bot(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['h'])
    async def help(self, ctx):
        embed = discord.Embed(
            title=f'Help menu',
            description='> Page - 1/1',
            colour=discord.Colour.dark_grey()
        )
        embed.set_footer(
            text='[] - Required, <> - Optional, () - Command aliases')
        embed.add_field(name='List of Commands', value='''
        > This bot currently only accepts spotify playlists not individual songs.
        `help` ▹ displays this menu!
        `play [query]` ▹ plays a song from a query. Can be a song name or a youtube link.
        `track [query]` ▹ plays a spotify playlist. Must be a link to a spotify playlist.
        `queue (q)` ▹ displays the current queue for this server. 
        `pause` ▹ pauses the current song.
        `resume` ▹ resumes the current song.
        `disconnect (d)` ▹ disconnects the bot from the voice channel. 
        `skip (s)` ▹ skips the current song.
        ''', inline=False)
        await ctx.send(embed=embed)