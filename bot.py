import asyncio
import os
import time

import discord
from discord.ext import commands
import random
import youtube_dl

from bot_services import get_random_title, get_random_GIF

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # your bot token

AVAILABLE_URL = {
    'anime': 'https://tenor.com/search/anime-gifs',
    'animals': 'https://tenor.com/search/animals-gifs',
    'morning': 'https://tenor.com/search/good-morning-gifs',
    'sad': 'https://tenor.com/search/sad-gifs',
    'fun': 'https://tenor.com/search/fun-gifs'
}

QUEUE_MUSIC = []  # список воспроизводимых аудио
MUSIC_QUEUE_LIST = []  # список названий видео

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('\n----------------------')
    print(f'Logged in as {client.user.name}')
    print(f'ID: {client.user.id}')
    print('----------------------\n')
    game = discord.Game("!help")
    await client.change_presence(status=discord.Status.online, activity=game)


client.remove_command('help')


@client.command(pass_context=True)
async def help(ctx):
    """Предоставляет список всех доступных команд."""
    author = ctx.message.author.mention

    embed = discord.Embed(
        colour=discord.Color.magenta(),
        title=':robot: Abyss bot',
        description=f'Below you can see all the commands I know.\n Have a nice day {author}!'
    )

    embed.add_field(name=':musical_note:  **MUSIC**',
                    value='`!join`, `!play [url]`, `!skip`, `!stop`, `!leave`',
                    inline=False)
    embed.add_field(name=':crossed_flags:  **ANIME**',
                    value='`!anime`, `!gif [anime]`',
                    inline=False)
    embed.add_field(name=':dividers:  **GIFs**',
                    value='`!gif [anime | animals | morning | sad | fun]`',
                    inline=False)
    embed.add_field(name=':tools:  **SERVER COMMANDS**',
                    value='`!clear [ value ]` deletes as many messages that you specify (default=100)',
                    inline=False)
    embed.add_field(name=':black_joker:  **FUN**',
                    value='`!echo` duplicate your message.\n `!roll` random value from 1 to 100.',
                    inline=False)

    embed.set_image(url='https://edgyanimeteenblog.files.wordpress.com/2019/01/87e.gif?w=500')

    await ctx.send(embed=embed)


@client.command()
async def echo(message, *args):
    """Дублирует сообщение отправителя."""
    echo_message = f'{" ".join([word for word in args])}'
    await message.send(echo_message)


@client.command()
async def anime(message):
    """Возвращает случайный тайтл с yummyanime.club"""
    anime_title = get_random_title()
    await message.send(anime_title)


@client.command()
async def gif(message, *args):
    """
    Возвращает случайную гифку из переданной категории.
    Если переданной клиентом категории нет в списке доступных категорий, то возвращает соответствующую ошибку.
    """
    if str(*args) in AVAILABLE_URL:
        random_gif = get_random_GIF(AVAILABLE_URL[str(*args)])
        await message.send(random_gif)
    else:
        await message.send(":no_entry_sign: Invalid values!\n"
                           ":white_check_mark: Available values for the command `!gif`: **anime, animals, morning, sad, fun.**")


@client.command()
async def roll(message):
    """Случайное число от 1 до 100."""
    random_number = random.randint(1, 100)
    await message.send(random_number)


@client.command()
async def clear(message, amount=100):
    """Удаляет указанное кол-во сообщений с канала. Если аргумент не был передан, то удаляет 100 сообщений."""
    await message.channel.purge(limit=amount + 1)
    await message.send(':wastebasket: Messages deleted!')


@client.command(pass_context=True)
async def join(ctx):
    """Если пользователь находится на голосовом канале, то подключается к нему."""
    try:
        author = ctx.message.author
        voice_channel = author.voice.channel
        await voice_channel.connect()
    except AttributeError:
        await ctx.send(":no_entry_sign: You are currently not in a channel! Please join a voice channel.")


@client.command(pass_context=True)
async def leave(ctx):
    """Если бот находится на голосовом канале, то отключается от него."""
    try:
        server = ctx.message.guild.voice_client
        await server.disconnect()
    except AttributeError:
        await ctx.send(":no_entry_sign: I am currently not in a channel!")


ffmpeg_options = {
    'options': '-vn'
}


def _play_audio(ctx):
    """
    Если QUEUE_MUSIC не пуст, то воспроизводит 1-ый в этом списке файл, а также удаляет его из QUEUE_MUSIC
    и MUSIC_QUEUE_LIST.
    """
    if QUEUE_MUSIC:
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable="C:/Users/maksi/ffmpeg/bin/ffmpeg.exe",  # путь к ffmpeg.exe
                                                     source=f'music/{QUEUE_MUSIC[0]}'),
                              after=lambda e: _play_audio(ctx))
        QUEUE_MUSIC.pop(0)
        MUSIC_QUEUE_LIST.pop(0)


@client.command()
async def play(ctx, url: str = None):
    """
    1) Подключается к голосовому каналу.
    2) Если небыл передан url или переданного url-а не существует, то возвращает соответствующую ошибку.
    3) Загружает с корректного url-a видео и конвертирует его в формат m4a.
    4) После чего добавляет имя файла и название видео в списки QUEUE_MUSIC, MUSIC_QUEUE_LIST соответственно.
    5) Запускает функцию _play_audio для воспроизведения аудио.
    """
    if not url:
        await ctx.send(":no_entry_sign: Try adding a URL. e.g. !play https://youtube.com/watch?v=XXXXXXXXX")
    else:
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        elif ctx.author.voice and ctx.author.voice.channel:

            await channel.connect()

        if ctx.voice_client is not None:
            result_str = str(time.time())
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'/music/{result_str}.m4a',  # имя и формат создаваемого аудиофайла
                'noplaylist': True,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                if not os.path.isfile(f'music/{result_str}.m4a'):
                    try:
                        info_dict = ydl.extract_info(url, download=False)
                        MUSIC_QUEUE_LIST.append(info_dict["title"])
                        ydl.download([url])
                        QUEUE_MUSIC.append(f'{result_str}.m4a')
                        await ctx.send(
                            f":notes: Right now in queue the next songs: {', '.join(list(map(lambda s: f'**`{s}`**', MUSIC_QUEUE_LIST)))}")
                    except youtube_dl.utils.DownloadError:
                        await ctx.send(f":no_entry_sign: **{url}** is not a valid URL.")

            if not ctx.voice_client.is_playing():
                _play_audio(ctx)


@client.command()
async def stop(ctx):
    """Останавливает воспроизведение аудио."""
    vc = ctx.voice_client
    vc.stop()


@client.command()
async def skip(ctx):
    """Пропускает воспроизводимую композицию."""
    vc = ctx.voice_client
    vc.stop()
    _play_audio(ctx)

if __name__ == '__main__':
    client.run(DISCORD_TOKEN)
