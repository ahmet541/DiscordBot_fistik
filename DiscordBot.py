from dis import disco
from operator import ne
from tracemalloc import start
from urllib import response

import discord
import os
import requests
import json
import random
import pandas as pd
import yt_dlp

from youtube_api import YouTubeDataAPI
from discord.ext import commands,tasks
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
YT_KEY = os.getenv('API_KEY')


yt = YouTubeDataAPI(YT_KEY)
client = commands.Bot(command_prefix="!")

words_relatedTo_Movies = ["Movie", "Movies", "movie", "movies"]
starter_recommendedMovies = ["Edge Of Tomorrow", "The Arq", "The Tomorrows War"]


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event 
async def on_message(message):
    await client.process_commands(message)

    msg = message.content

    if message.author == client.user:
        return
    
    if msg.startswith('hi'):
        await message.channel.send('Hello {}! Have fun!'.format(message.author))
        
    if msg.startswith("inspire me"):
        newQuote = get_quote()
        await message.channel.send(newQuote)

    if msg.startswith("$addMovie"):
        newMovie = msg.split("$addMovie ",1)[1]
        update_recommendedMovie(newMovie) 
        await message.channel.send("New recommended movie added!")
    elif msg.startswith("$delMovie"):
        index = int(msg.split("$delMovie ",1)[1])
        if len(starter_recommendedMovies) > index:
            delete_recommendedMovie(index)
        await message.channel.send(starter_recommendedMovies)
    elif msg.startswith("$listMovies"):
        await message.channel.send(starter_recommendedMovies)
    elif any(word in msg for word in words_relatedTo_Movies):
        await message.channel.send("Hey! Litte recommendation! You should consider to watch " + random.choice(starter_recommendedMovies))     


@client.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state is None:
        # Exiting if the bot it's not connected to a voice channel
        return

    if len(voice_state.channel.members) == 1:
        await voice_state.disconnect()

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = "```" + json_data [0]['q'] + "```" +  "\n -" + json_data[0]['a']
    return(quote)

def update_recommendedMovie(new_movie):
    if new_movie not in starter_recommendedMovies:
        starter_recommendedMovies.append(new_movie)

def delete_recommendedMovie(index):
    if index < len(starter_recommendedMovies):
        del starter_recommendedMovies[index]


@client.command( allias = ['p'], help = "Play Music")
async def play(ctx,url):

    if len(url) == 1:
        url = url[0]

    try:
        if os.path.exists("songs"):
            files = os.listdir("songs")
            if len(files) > 20:
                os.remove(files[0])
    except PermissionError:
        await ctx.send("Wait for the current playing \
            music to end or use the 'stop' command.")
        return

    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
    else:
        voice_chan = ctx.message.author.voice.channel

    try:
        await voice_chan.connect()
    except discord.ClientException:  # Already in channel
        pass

    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprovessors': [{
            'key': 'FFmpegExtractAudio',
            'prefferedcodec': 'mp3',
            'prefferedquality': '192'
        }],
        'outtmpl': 'songs/song.mp3'
    }

    if "www.youtube.com" not in url:  # Search on keywords
        searches = pd.DataFrame(yt.search( q=url, max_results=10, type='video', videoCategoryId='10'))
        url = "http://www.youtube.com/watch?v=" + searches.iloc[0].video_id

    i = url.find("v=") + 2  # Skip v=
    song_id = url[i:]
    file_path = "songs/{}.mp3".format(song_id)
    if not os.path.exists("songs"):
        os.mkdir("songs")

    if not os.path.exists(file_path):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            title = info.get("title", None)
            os.rename("songs/song.mp3", file_path)
            await ctx.send(f'Now playing {title}!')

    voice.play(discord.FFmpegPCMAudio(file_path))



# @client.command( alliases = ['p'], help = 'Play video using key word or url')
# async def play(ctx, ulr: str):
#     try:
#         voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
        
#         if not ctx.message.author.voice:
#             await ctx.send("{} is not connected to any voice channel.".format(ctx.message.author.name))
#             return
#         else:
#             try:
#                 channel = ctx.message.author.voice.channel
#                 await channel.connect()
#             except:
#                 await voice.disconnect()
#                 channel = ctx.message.author.voice.channel
#                 await channel.connect() 
                
#     except discord.ext.commands.errors.MissingRequiredArgument:
#         await ctx.send("ulr is a required argument that is missing.")
#         return


    

@client.command(name = 'join', help = 'Tells bot to join voice channel')
async def join(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to any voice channel.".format(ctx.message.author.name))
        return
    else:
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except:
            await voice.disconnect()
            channel = ctx.message.author.voice.channel
            await channel.connect()




@client.command(help = "Tells bot to leave from voice channel")
async def leave(ctx):
    bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if bot.is_connected():
            await bot.disconnect()
    else:
        await ctx.send('Bot is not in any voice channel.')

@client.command(help = "Pauses bot's action")
async def pause(ctx):
    bot = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if bot.is_playing():
            await bot.pause()
    else:
        await ctx.send("Bot is not playing anyting right now.")    

@client.command(help = "Resumes bot's action")
async def resume(ctx):
    bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
   
    if bot.is_paused():
            await bot.resume()
    else:
        await ctx.send("Bot should be paused before it to resume. Use '!play' command") 

@client.command(help="Stops the bot")
async def stop(ctx):
    bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    
    if bot.is_playing():
            await bot.stop()
    else:
        await ctx.send("Bot should be playing before it to stop. Use '!play' command")



client.run(TOKEN)





# @client.command( alliases = ['p'], help = 'Play video using key word or url')
# async def play(ctx, ulr: str):
#     try:
#         voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
        
#         if not ctx.message.author.voice:
#             await ctx.send("{} is not connected to any voice channel.".format(ctx.message.author.name))
#             return
#         else:
#             voiceChannel = discord.utils.get(ctx.guild.voice_channels, guild = ctx.guild)
#             await voiceChannel.connect();  
                
#     except discord.ext.commands.errors.MissingRequiredArgument:
#         await ctx.send("ulr is a required argument that is missing.")
#         return

