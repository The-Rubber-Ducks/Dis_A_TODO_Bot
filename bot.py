import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
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


# Setup Stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']


# -----Helper functions-----

def make_output_list(the_list, list_title):
    if len(the_list) > 0:
        output = [f"__**{list_title}**__"]
        for index, item in enumerate(the_list):
            output.append(f"**{index + 1}.** {item}")
        return output
    return ["All done!"]


def make_completed_list(the_list):
    if len(the_list) > 0:
        output = [f"__**Completed**__"]
        for index, item in enumerate(the_list):
            output.append(f"~~{item}~~")
        return output
    return []


async def add_emojis(the_message, the_list):
    for index, items in enumerate(the_list):
        await the_message.add_reaction(emojis[index])


# -----Commands-----

# Create new list
@bot.command(name="makelist", help="Make a new ToDo list")
async def make_new_list(ctx: discord.ext.commands.Context, permission, *, list_name):
    if not is_unique_list(list_name):
        await ctx.send("List name already in use`")
        return

    new_list = create_list(list_name, ctx.author.id)
    if permission == "all":
        for member in ctx.guild.members:
            new_list["members"].append(member.id)
        update_list(list_name, new_list)
    await ctx.message.add_reaction('✅')


@bot.command(name="removelist", help="Removes list by name")
async def remove_list(ctx: discord.ext.commands.Context, *, list_name):
    user_id = ctx.author.id
    _list_name, the_list = get_list_by_name(list_name)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if user_id in the_list["members"]:
        await ctx.send("Add function to delete this list!")
        await ctx.message.add_reaction('✅')
    #     Add function stuff here
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Show users lists
@bot.command(name="mylists", help="Display ToDo lists for specific user")
async def show_my_lists(ctx: discord.ext.commands.Context):
    user_lists_names = get_all_list_names_by_user(ctx.author.id)
    print(user_lists_names)
    if len(user_lists_names) > 0:
        await ctx.send("\n".join(user_lists_names))
    else:
        await ctx.send("You have no lists!")


# Show List Command
@bot.command(name="showlist", help="Display a ToDo list in chat")
async def show_list(ctx: discord.ext.commands.Context, *, list_name):
    user_id = ctx.author.id
    _list_name, the_list = get_list_by_name(list_name)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if user_id in the_list["members"]:  # if user_id in get_list_by_name("list_name")["members"]
        if "todoList" not in the_list:
            await ctx.send("Add some shit")
            return

        todo_output = make_output_list(the_list["todoList"], list_name)
        if "completed" not in the_list:
            the_list["completed"] = []
        completed_output = make_completed_list(the_list["completed"])
        output = todo_output + completed_output
        the_message = await ctx.send("\n".join(output))
        the_list["message_id"] = the_message.id
        update_list(list_name, the_list)
        await add_emojis(the_message, the_list["todoList"])
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Show list of Completed Items
@bot.command(name="showcomplete", help="Display all completed items ")
async def show_complete(ctx: discord.ext.commands.Context, list_name):
    _list_name, the_list = get_list_by_name(list_name)

    if "completed" not in the_list:
        await ctx.send("You haven't done shit")
        return

    output = make_output_list(the_list["completed"], list_name)
    await ctx.send("\n".join(output))


# Add item Command
@bot.command(name="add", help="Add new item to list. Need quotes around list name")
async def add_item(ctx: discord.ext.commands.Context, list_name, *, new_item):
    _list_name, the_list = get_list_by_name(list_name)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if "todoList" not in the_list:
        the_list["todoList"] = [new_item]
    else:
        the_list["todoList"].append(new_item)
    update_list(list_name, the_list)
    await ctx.message.add_reaction('✅')


# ----Events-----

# Listens for emoji reactions
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    if user.id == bot.user.id:
        return
    if reaction.emoji not in emojis:
        return
    list_name, the_list = get_list_by_message_id(reaction.message.id)
    if user.id not in the_list["members"]:
        await reaction.message.remove_reaction(reaction.emoji, user)
        return

    if "todoList" not in the_list:
        return

    item_index = emojis.index(reaction.emoji)

    if item_index >= len(the_list["todoList"]):
        return
    item_to_move = the_list["todoList"][item_index]
    the_list["todoList"].remove(item_to_move)

    if "completed" not in the_list:
        the_list["completed"] = [item_to_move]
    else:
        the_list["completed"].append(item_to_move)

    update_list(list_name, the_list)

    todo_output = make_output_list(the_list["todoList"], list_name)
    completed_output = make_completed_list(the_list["completed"])
    output = todo_output + completed_output
    await reaction.message.edit(content="\n".join(output))
    await reaction.message.clear_reactions()
    await add_emojis(reaction.message, the_list["todoList"])


# Start Bot
bot.run(TOKEN)
