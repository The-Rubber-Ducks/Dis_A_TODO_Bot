import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from todo_list import *

<<<<<<< Updated upstream
=======
import pyrebase

load_dotenv()

config = {
    "apiKey": os.getenv("FBASE_APIKEY"),
    "databaseURL": os.getenv("FBASE_DATABASEURL"),
    "authDomain": os.getenv("FBASE_AUTHDOMAIN"),
    "projectId": os.getenv("FBASE_PROJECTID"),
    "storageBucket": os.getenv("FBASE_STORAGEBUCKET"),
    "messagingSenderId": os.getenv("FBASE_MESSAGINGSENDERID"),
    "appId": os.getenv("FBASE_APPID"),
    "measurementId": os.getenv("FBASE_MEASUREMENTID")
}


def is_unique_list(list_name):
    print(list(db.child("todoLists").get().val().keys()))
    return list_name not in list(db.child("todoLists").get().val().keys())


firebase = pyrebase.initialize_app(config)
db = firebase.database()


def create_list(list_name, author_id):
    data = {
        "creator": author_id,
        "members": [author_id],
        "message_id": ""
    }
    db.child("todoLists").child(list_name).set(data)
    db.child("members").child(author_id).child("todoLists").set(list_name)
    return db.child("todoLists").child(list_name).get().val()


def get_list_by_name(list_name):
    ret = db.child("todoLists").child(list_name).get()
    return ret.key(), ret.val()


def get_list_by_message_id(message_id):
    lists = db.child("todoLists").get().val()
    for key, val in lists.items():
        if val["message_id"] == message_id:
            return key, val
    return None


def set_message_id(list_name, message_id):
    return db.child("todoLists").child(list_name).update({"message_id": message_id})


def get_all_list_names_by_user(author_id):
    return db.child("members").child(author_id).get().val()


def update_list(list_name, the_list):
    return db.child("todoLists").child(list_name).update(the_list)


>>>>>>> Stashed changes
# Setup Stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

all_lists = []

test_data = Todo_List("Test_List", "Me")
test_data.load_JSON(open("./test_data.json"))
all_lists.append(test_data)


# -----Helper functions-----

def make_output_list(the_list, list_title, extra=""):
    output = [f"__**{list_title}{extra}**__"]
    for index, item in enumerate(the_list):
        output.append(f"**{index + 1}.** {item}")
    return output


async def add_emojis(the_message, the_list):
    for index, items in enumerate(the_list):
        await the_message.add_reaction(emojis[index])


def get_list_by_name(list_name):
    for some_list in all_lists:
        if some_list.get_todo_list_name() == list_name:
            return some_list
    return None


def get_list_by_message_id(message_id):
    for some_list in all_lists:
        if some_list.get_message_id() == message_id:
            return some_list
    return None


def get_user_lists(member_id):
    output = []
    for some_list in all_lists:
        if some_list.is_user_member(member_id):
            output.append(some_list)
    return output


# -----Commands-----

# Create new list
@bot.command(name="makelist", help="Make a new ToDo list")
async def make_new_list(ctx: discord.ext.commands.Context, permission, *, list_name):
    new_list = Todo_List(list_name, ctx.author.id)
    if permission == all:
        for member in ctx.guild.members:
            new_list.add_member(member.id)
    all_lists.append(new_list)
    await ctx.message.add_reaction('✅')


# Show users lists
@bot.command(name="mylists", help="Display ToDo lists for specific user")
async def show_my_lists(ctx: discord.ext.commands.Context):
    the_user = ctx.author.id
    user_lists_names = [x.get_todo_list_name() for x in get_user_lists(the_user)]
    if len(user_lists_names) > 0:
        await ctx.send("\n".join(user_lists_names))
    else:
        await ctx.send("You have no lists!")


# Show List Command
@bot.command(name="showlist", help="Display a ToDo list in chat")
async def show_list(ctx: discord.ext.commands.Context, *, list_name):
    user_id = ctx.author.id
    the_list = get_list_by_name(list_name)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
<<<<<<< Updated upstream
    if the_list.is_user_member(user_id):
        output = make_output_list(the_list.get_todo_list(), the_list.get_todo_list_name())
=======
    if user_id in the_list["members"]:  # if user_id in get_list_by_name("list_name")["members"]
        if "todoList" not in the_list:
            await ctx.send("Add some shit")
            return

        output = make_output_list(the_list["todoList"], list_name)
>>>>>>> Stashed changes
        the_message = await ctx.send("\n".join(output))
        the_list.set_message_id(the_message.id)
        await add_emojis(the_message, the_list.get_todo_list())
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Show list of Completed Items
@bot.command(name="showcomplete", help="Display all completed items ")
<<<<<<< Updated upstream
async def show_complete(ctx: discord.ext.commands.Context):
    output = make_output_list(test_data.get_completed(), test_data.get_todo_list_name(), "--Completed")
=======
async def show_complete(ctx: discord.ext.commands.Context, list_name):
    _list_name, the_list = get_list_by_name(list_name)

    if "completed" not in the_list:
        await ctx.send("You haven't done shit")
        return

    output = make_output_list(the_list["completed"], list_name, "--Completed")
>>>>>>> Stashed changes
    await ctx.send("\n".join(output))


# Add item Command
@bot.command(name="add", help="Add new item to list. Need quotes around list name")
async def add_item(ctx: discord.ext.commands.Context, list_name, *, new_item):
    the_list = get_list_by_name(list_name)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    the_list.add_item(new_item)
    await ctx.message.add_reaction('✅')


# ----Events-----

# Listens for emoji reactions
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    if user.id == bot.user.id:
        return
    if reaction.emoji not in emojis:
        return
    the_list = get_list_by_message_id(reaction.message.id)
    if not the_list.is_user_member(user.id):
        return

    item_index = emojis.index(reaction.emoji)
    the_list.complete_item(the_list.get_todo_list()[item_index])
    output = make_output_list(the_list.get_todo_list(), the_list.get_todo_list_name())
    await reaction.message.edit(content="\n".join(output))
    await reaction.message.clear_reactions()
    await add_emojis(reaction.message, the_list.get_todo_list())


# Start Bot
bot.run(TOKEN)
