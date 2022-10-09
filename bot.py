import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import pyrebase

# Setup Stuff
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

bot = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

number_emojis = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')
yes_no_emojis = ('❌','✅')

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

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def is_unique_list(list_name, server_id):
    if not db.child().get().val():
        return True
    elif str(server_id) not in list(db.child().get().val()):
        # Fix by adding server table on bot entry to server
        return True

    return list_name not in list(db.child(server_id).get().val().keys())


def create_list(list_name, author_id, server_id, is_for_all=False):
    server_object = db.child(server_id).get().val()

    data = {
        "creator": author_id,
        "members": [author_id],
        "message_id": "",
        "for_all": is_for_all
    }
    if server_object is None:
        db.child(server_id).child(list_name).set(data)
        return db.child(server_id).child(list_name).get().val()

    db.child(server_id).child(list_name).set(data)
    return db.child(server_id).child(list_name).get().val()


def get_list_by_name(list_name, server_id):
    ret = db.child(server_id).child(list_name).get()
    return ret.key(), ret.val()


def get_list_by_message_id(message_id, server_id):
    lists = db.child(server_id).get().val()
    for key, val in lists.items():
        if val["message_id"] == message_id:
            return key, val
    return None


def get_all_list_names_by_user(author_id, server_id):
    output = []


    if str(server_id) not in list(db.child().get().val()):
        return output

    all_lists = db.child(server_id).get().val()
    for lst in all_lists:
        if author_id in all_lists[lst]["members"]:
            output.append(lst)
    return output

def update_list(list_name, server_id, the_list):
    return db.child(server_id).child(list_name).update(the_list)


def remove_list(list_name, server_id):
    return db.child(server_id).child(list_name).remove()

def add_new_user_to_public_lists(user_id, server_id):
    all_lists = db.child(server_id).get()
    for lst in all_lists.each():
        if lst.val()["for_all"] and user_id not in lst.val()["members"]:
            lst.val()["members"].append(user_id)
            update_list(lst.key(), server_id, lst.val())


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
        await the_message.add_reaction(number_emojis[index])


async def add_yes_no_emojis(the_message):
    await the_message.add_reaction(yes_no_emojis[1])
    await the_message.add_reaction(yes_no_emojis[0])


# -----Commands-----

# Create new list
@bot.command(name="makelist", help="Make a new ToDo list")
async def make_new_list(ctx: discord.ext.commands.Context, permission, *, list_name=None):

    if list_name is None:
        list_name = permission
        if not is_unique_list(list_name, ctx.guild.id):
            await ctx.send("List name already in use")
            return
        new_list = create_list(list_name, ctx.author.id, ctx.guild.id)

    elif permission == "all":
        if not is_unique_list(list_name, ctx.guild.id):
            await ctx.send("List name already in use")
            return
        new_list = create_list(list_name, ctx.author.id, ctx.guild.id, True)
        
        # Add all members since permission all
        for member in ctx.guild.members:
            new_list["members"].append(member.id)
        
    else:
        await ctx.send("""
            ⚠Invalid command used to make list.⚠
            ```!makelist all NAME``` For a server-wide todo list
            ```!makelist NAME``` For a personal to do list
            """)
        return

    update_list(list_name, ctx.guild.id, new_list)
    await ctx.message.add_reaction('✅')


@bot.command(name="removelist", help="Removes list by name")
async def remove_list_by_name(ctx: discord.ext.commands.Context, *, list_name=None):
    if list_name is None:
        await ctx.send("""
            ⚠Invalid command used to remove list.⚠
            ```!removelist NAME``` To remove your list
            """)
        return

    user_id = ctx.author.id
    _list_name, the_list = get_list_by_name(list_name, ctx.guild.id)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if user_id in the_list["members"]:
        new_message = await ctx.send(f"Are you sure you want to delete this list? ```{list_name}``` ✅=YES ❌=NO")
        await add_yes_no_emojis(new_message)
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Show users lists
@bot.command(name="mylists", help="Display ToDo lists for specific user")
async def show_my_lists(ctx: discord.ext.commands.Context):
    user_lists_names = get_all_list_names_by_user(ctx.author.id, ctx.guild.id)
    if len(user_lists_names) > 0:
        await ctx.send("**Here are your lists:**")
        await ctx.send("\n".join(user_lists_names))
    else:
        await ctx.send("You have no lists!")


# Show List Command
@bot.command(name="showlist", help="Display a ToDo list in chat")
async def show_list(ctx: discord.ext.commands.Context, *, list_name=None):
    if list_name is None:
        await ctx.send("""
            ⚠Invalid command used to show list.⚠
            ```!showlist NAME``` To show your list
            """)
        return

    user_id = ctx.author.id
    _list_name, the_list = get_list_by_name(list_name, ctx.guild.id)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if user_id in the_list["members"]:  # if user_id in get_list_by_name("list_name")["members"]

        if "todoList" not in the_list:
            await ctx.send("Add some tasks!")
            return

        todo_output = make_output_list(the_list["todoList"], list_name)
        if "completed" not in the_list:
            the_list["completed"] = []
        completed_output = make_completed_list(the_list["completed"])
        output = todo_output + completed_output
        the_message = await ctx.send("\n".join(output))
        the_list["message_id"] = the_message.id
        update_list(list_name, ctx.guild.id, the_list)
        await add_emojis(the_message, the_list["todoList"])
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Add item Command
@bot.command(name="add", help="Add new item to list. Need quotes around list name")
async def add_item(ctx: discord.ext.commands.Context, list_name, *, new_item):
    _list_name, the_list = get_list_by_name(list_name, ctx.guild.id)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if "todoList" not in the_list:
        the_list["todoList"] = [new_item]
    else:
        the_list["todoList"].append(new_item)
    update_list(list_name, ctx.guild.id, the_list)
    await ctx.message.add_reaction('✅')


# ----Events-----
@bot.event
async def on_member_join(new_member):
    add_new_user_to_public_lists(new_member.id, new_member.guild.id)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)
    await ctx.send("Check available commands below:")
    await ctx.send_help()


# Listens for emoji reactions
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    if user.id == bot.user.id:
        return
    # Emoji Number reaction 
    if reaction.emoji in number_emojis:
        list_name, the_list = get_list_by_message_id(reaction.message.id, reaction.message.guild.id)
        if user.id not in the_list["members"]:
            await reaction.message.remove_reaction(reaction.emoji, user)
            return

        if "todoList" not in the_list:
            return

        item_index = number_emojis.index(reaction.emoji)

        if item_index >= len(the_list["todoList"]):
            return
        item_to_move = the_list["todoList"][item_index]
        the_list["todoList"].remove(item_to_move)

        if "completed" not in the_list:
            the_list["completed"] = [item_to_move]
        else:
            the_list["completed"].append(item_to_move)

        update_list(list_name, reaction.message.guild.id, the_list)

        todo_output = make_output_list(the_list["todoList"], list_name)
        completed_output = make_completed_list(the_list["completed"])
        output = todo_output + completed_output
        await reaction.message.edit(content="\n".join(output))
        await reaction.message.clear_reactions()
        await add_emojis(reaction.message, the_list["todoList"])
    
    # YES NO reaction
    elif reaction.emoji in yes_no_emojis:
        list_name = reaction.message.content.split("```")[1]
        _list_name, the_list = get_list_by_name(list_name, reaction.message.guild.id)
        if user.id not in the_list["members"]:
            await reaction.message.remove_reaction(reaction.emoji, user)
            return
        if reaction.emoji ==  yes_no_emojis[1]:
            remove_list(list_name, reaction.message.guild.id)
        elif reaction.emoji == yes_no_emojis[0]:
            await reaction.message.delete()


# Start Bot
bot.run(TOKEN)
