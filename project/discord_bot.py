import discord
from dotenv import load_dotenv
from discord.ext import commands
import os

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!",intents=intents)

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @bot.command()
    async def ping(ctx):
        await ctx.message.author.send("Salut l'artiste :^)")



    load_dotenv('/'.join(os.getcwd().split('\\')[:-1])+"/.env")
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    run()
