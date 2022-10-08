import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from todo_list import *

# Setup Stuff
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

test_data = Todo_List("Test_List", "Me")
test_data.load_JSON(open("./test_data.json"))
emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']


# -----Helper functions-----

def make_output_list(the_list, list_title, extra=""):
    output = [f"__**{list_title}{extra}**__"]
    for index, item in enumerate(the_list):
        output.append(f"**{index + 1}.** {item}")
    return output


async def add_emojis(the_message, the_list):
    for index, items in enumerate(the_list):
        await the_message.add_reaction(emojis[index])


# -----Commands-----

# Create new list
@bot.command(name="makelist")
async def make_new_list(ctx: discord.ext.commands.Context, *, list_name):
    global test_data
    test_data = Todo_List(list_name, ctx.author)
    await ctx.message.add_reaction('✅')


# Show List Command
@bot.command(name="showlist")
async def show_list(ctx: discord.ext.commands.Context):
    output = make_output_list(test_data.get_todo_list(), test_data.get_todo_list_name())
    the_message = await ctx.send("\n".join(output))
    await add_emojis(the_message, test_data.get_todo_list())


# Show list of Completed Items
@bot.command(name="showcomplete")
async def show_complete(ctx: discord.ext.commands.Context):
    output = make_output_list(test_data.get_completed(), test_data.get_todo_list_name(), "--Completed")
    await ctx.send("\n".join(output))


# Add item Command
@bot.command(name="add", help="Testing")
async def add_item(ctx: discord.ext.commands.Context, *, new_item):
    test_data.add_item(new_item)
    await ctx.message.add_reaction('✅')


# ----Events-----

# Listens for emoji reactions
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    if user.id == bot.user.id:
        return
    item_index = emojis.index(reaction.emoji)
    test_data.complete_item(test_data.get_todo_list()[item_index])
    output = make_output_list(test_data.get_todo_list(), test_data.get_todo_list_name())
    await reaction.message.edit(content="\n".join(output))
    await reaction.message.clear_reactions()
    await add_emojis(reaction.message, test_data.get_todo_list())


# Start Bot
bot.run(DISCORD_TOKEN)
