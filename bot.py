import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import pyrebase
import firebase_funcs

# Discordpy setup
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

bot = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

# Pyrebase setup
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

# constants
number_emojis = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')
yes_no_emojis = ('❌','✅')


# helper functions
def make_output_list(the_list, list_title):
    """Creates a numbered list of ToDo items with a title

    Args:
        the_list(List): The list of items in TodoList
        list_title(String): Title of the list

    Returns:
        List: formated List of items
    """
    if len(the_list) > 0:
        output = [f"__**{list_title}**__"]
        for index, item in enumerate(the_list):
            output.append(f"**{index + 1}.** {item}")
        return output
    return ["All done!"]


def make_completed_list(the_list) -> list:
    """Creates a list of completed items

    Args:
        the_list(List): The list of items in a completed list

    Returns:
        list: formated List of items
    """
    if len(the_list) > 0:
        output = [f"__**Completed**__"]
        for index, item in enumerate(the_list):
            output.append(f"~~{item}~~")
        return output
    return []

async def add_emojis(the_message, the_list):
    """Adds numbered emojis reactions to a message based on a ToDo list

    Args:
        the_message(discord.Message): The message to add reactions to
        the_list(List): The list of items in TodoList
    """
    for index, items in enumerate(the_list):
        await the_message.add_reaction(number_emojis[index])


async def add_yes_no_emojis(the_message):
    """Adds yes/no emojis reactions to a message

    Args:
        the_message(discord.Message): The message to add reactions to

    Returns:
        None
    """
    await the_message.add_reaction(yes_no_emojis[1])
    await the_message.add_reaction(yes_no_emojis[0])

# -----Commands-----

# Create new list
@bot.command(name="makelist", help="Make a new ToDo list")
async def make_new_list(ctx: discord.ext.commands.Context, permission, *, list_name=None):
    """Bot command that creates a new ToDo list and adds it to the database

    Args:
        ctx(discord.ext.commands.Context): The context of the command from Discord
        permission(String): The permission of the new list. 'all' = public
        list_name(String): The name of the new list
    """
    if list_name is None:
        list_name = permission
        if not firebase_funcs.is_unique_list(db, list_name, ctx.guild.id):
            await ctx.send("List name already in use")
            return
        new_list = firebase_funcs.create_list(db, list_name, ctx.author.id, ctx.guild.id)

    elif permission == "all":
        if not firebase_funcs.is_unique_list(db, list_name, ctx.guild.id):
            await ctx.send("List name already in use")
            return
        new_list = firebase_funcs.create_list(db, list_name, ctx.author.id, ctx.guild.id, True)
        
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

    firebase_funcs.update_list(db, list_name, ctx.guild.id, new_list)
    await ctx.message.add_reaction('✅')


@bot.command(name="removelist", help="Removes list by name")
async def remove_list_by_name(ctx: discord.ext.commands.Context, *, list_name=None):
    """Bot command that removes a list from the database by name

    Args:
        ctx(discord.ext.commands.Context): The context of the command from Discord
        list_name(String): Title of the list that is to be deleted
    """
    if list_name is None:
        await ctx.send("""
            ⚠Invalid command used to remove list.⚠
            ```!removelist NAME``` To remove your list
            """)
        return

    user_id = ctx.author.id
    _list_name, the_list = firebase_funcs.get_list_by_name(db, list_name, ctx.guild.id)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if user_id in the_list["members"]:
        new_message = await ctx.send(f"Are you sure you want to delete this list? ```{list_name}```")
        await add_yes_no_emojis(new_message)
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Show users lists
@bot.command(name="mylists", help="Display ToDo lists for specific user")
async def show_my_lists(ctx: discord.ext.commands.Context):
    """Bot command that shows all avaiable list names that are avaiable to the user

    Args:
        ctx(discord.ext.commands.Context): The context of the command from Discord
    """
    user_lists_names = firebase_funcs.get_all_list_names_by_user(db, ctx.author.id, ctx.guild.id)
    if len(user_lists_names) > 0:
        await ctx.send("**Here are your lists:**")
        await ctx.send("\n".join(user_lists_names))
    else:
        await ctx.send("You have no lists!")


# Show List Command
@bot.command(name="showlist", help="Display a ToDo list in chat")
async def show_list(ctx: discord.ext.commands.Context, *, list_name=None):
    """Bot command that shows the ToDo list items from a list name

    Args:
        ctx(discord.ext.commands.Context): The context of the command from Discord
        list_name(String): The name of the list to be shown
    """
    if list_name is None:
        await ctx.send("""
            ⚠Invalid command used to show list.⚠
            ```!showlist NAME``` To show your list
            """)
        return

    user_id = ctx.author.id
    _list_name, the_list = firebase_funcs.get_list_by_name(db, list_name, ctx.guild.id)
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return
    if user_id in the_list["members"]:  # if user_id in firebase_funcs.get_list_by_name(db, "list_name")["members"]

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
        firebase_funcs.update_list(db, list_name, ctx.guild.id, the_list)
        await add_emojis(the_message, the_list["todoList"])
    else:
        await ctx.send("⛔You are not a member of this list.⛔")


# Add item Command
@bot.command(name="add", help="Add new item to list. Need quotes around list name")
async def add_item(ctx: discord.ext.commands.Context, list_name, *, new_item):
    """Bot command that adds a ToDo item to a list

    Args:
        ctx(discord.ext.commands.Context): The context of the command from Discord
        list_name(String): The name of the list to be shown
        new_item(String): The new item that will be added to the list
    """
    _list_name, the_list = firebase_funcs.get_list_by_name(db, list_name, ctx.guild.id)

    if _list_name is None and the_list is None:
        return
    
    if the_list is None:
        await ctx.send("⚠No list by that name ⚠")
        return

    if "todoList" not in the_list:
        the_list["todoList"] = [new_item]
    elif len(the_list["todoList"]) >= 10:
        await ctx.send("Max items reached. 10/10 Be more productive.")
        return
    else:
        the_list["todoList"].append(new_item)
    firebase_funcs.update_list(db, list_name, ctx.guild.id, the_list)
    await ctx.message.add_reaction('✅')


# ----Events-----
@bot.event
async def on_member_join(new_member):
    """Event that listens for when a new member joins a server, and adds that user to any public listst

    Args:
        new_member(discord.Member): The new user that joined the guild.
    """
    firebase_funcs.add_new_user_to_public_lists(db, new_member.id, new_member.guild.id)

@bot.event
async def on_command_error(ctx, error):
    """Event that listens for when a command raises an error

    Args:
        ctx(discord.ext.commands.Context): The context of the command from Discord
        error(String): The error that got raised
    """
    await ctx.send(error)
    await ctx.send("Check available commands below:")
    await ctx.send_help()


# Listens for emoji reactions
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    """Event that listens for emoji reactions and responds.

    Args:
        reaction(discord.Reaction): The reaction object
        user(discord.Member): The memebr that did that reactions
    """
    if user.id == bot.user.id:
        return
    if reaction.emoji not in number_emojis and reaction.emoji not in yes_no_emojis:
        return
        
    # Emoji Number reaction 
    if reaction.emoji in number_emojis:
        list_name, the_list = firebase_funcs.get_list_by_message_id(db, reaction.message.id, reaction.message.guild.id)

        if list_name is None and the_list is None:
            return

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

        firebase_funcs.update_list(db, list_name, reaction.message.guild.id, the_list)

        todo_output = make_output_list(the_list["todoList"], list_name)
        completed_output = make_completed_list(the_list["completed"])
        output = todo_output + completed_output
        await reaction.message.edit(content="\n".join(output))
        await reaction.message.clear_reactions()
        await add_emojis(reaction.message, the_list["todoList"])
    
    # YES NO reaction
    elif reaction.emoji in yes_no_emojis:
        if "`" not in reaction.message.content:
            # Handle 'race' condition
            return

        list_name = reaction.message.content.split("```")[1]
        _list_name, the_list = firebase_funcs.get_list_by_name(db, list_name, reaction.message.guild.id)

        if the_list is None:
            # Handle 'race' condition
            return
            
        if user.id not in the_list["members"]:
            await reaction.message.remove_reaction(reaction.emoji, user)
            return
        if reaction.emoji ==  yes_no_emojis[1]:
            firebase_funcs.remove_list(db, list_name, reaction.message.guild.id)
            await reaction.message.edit(content=f"{list_name} has been deleted!")
            await reaction.message.clear_reactions()
        elif reaction.emoji == yes_no_emojis[0]:
            await reaction.message.delete()


# Start Bot
bot.run(TOKEN)
