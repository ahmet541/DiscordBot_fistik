from dis import disco
from operator import ne
from tracemalloc import start
from urllib import response

import discord
import os
import requests
import json
import random
from discord.ext import commands,tasks
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
# client = discord.Client()  # delete?
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


@client.command( alliases = ['p'], help = 'Play video using key word or url')
async def play(ctx, ulr: str):

    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to any voice channel.".format(ctx.message.author.name))
        return
    else:
        voiceChannel = ctx.message.author.voice.channel   
        voiceChannel.connect();      
    



    

@client.command(name = 'join', help = 'Tells bot to join voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to any voice channel.".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command(help = "Tells bot to leave from voice channel")
async def leave(ctx):
    bot = ctx.message.guild.voice_client
    if bot.is_connected():
        await bot.disconnected()
    else:
        await ctx.send('Bot is not in any voice channel.')

@client.command(help = "Pauses bot's action")
async def pause(ctx):
    bot = ctx.message.guild.voice_client
    if bot.is_playin():
        await bot.pause()
    else:
        await ctx.send("Bot is not playing anyting right now.")    

@client.command(help = "Resumes bot's action")
async def resume(ctx):
    bot = ctx.message.guild.voice_client
    if bot.is_paused():
        await bot.resume()
    else:
        await ctx.send("Bot should be paused before it to resume. Use '!play' command") 

@client.command(help="Stops the bot")
async def stop(ctx):
    bot = ctx.message.voice_client
    if bot.is_playing():
        await bot.stop()
    else:
        await ctx.send("Bot should be playing before it to stop. Use '!play' command")



client.run(TOKEN)





