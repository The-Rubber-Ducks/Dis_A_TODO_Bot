import pyrebase
import os
from dotenv import load_dotenv
import json

def is_unique_list(db: object, list_name: str, server_id: int) -> bool:
    """ Checks if a list has a unique name in the database.

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        list_name (str): name of todo list
        server_id (int): id of Discord guild

    Returns:
        bool: True if list name is unique, if database is empty, or if server is not in database
              False otherwise
    """
 
    
    if not db.child().get().val():
        return True
    elif str(server_id) not in list(db.child().get().val()):
        # Fix by adding server table on bot entry to server
        return True

    return list_name not in list(db.child(server_id).get().val().keys())


def create_list(db: object, list_name: str, author_id: int, server_id: int, is_for_all:bool=False) -> dict:
    """ Creates new todo list in database for the server in which "!makelist" command was called

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        list_name (str): name of todo list
        author_id (int): id of Discord member calling the command
        server_id (int): id of Discord guild
        is_for_all (bool, optional): _description_. Defaults to False.

    Returns:
        dictionary: properties of todo list that was just created
    """
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


def get_list_by_name(db: object, list_name: str, server_id: int) -> tuple:
    """ Retrieves todo list dictionary from database given by its unique name

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        list_name (str): name of todo list
        server_id (int): id of Discord guild

    Returns:
        tuple: (name of todo list, dictionary containing properties of todo list)
    """
    ret = db.child(server_id).child(list_name).get()
    return ret.key(), ret.val()


def get_list_by_message_id(db: object, message_id: str, server_id: int) -> tuple:
    """ Retrieves todo list dictionary from database given by its unique name

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        message_id (int): id of Discord message
        server_id (int): id of Discord guild

    Returns:
        tuple: (name of todo list, dictionary containing properties of todo list)
    """
    lists = db.child(server_id).get().val()
    for key, val in lists.items():
        if val["message_id"] == message_id:
            return key, val
    return (None, None)


def get_all_list_names_by_user(db: object, author_id: int, server_id: int) -> list:
    """ Retrieves list of todo list dictionaries of a Discord user

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        author_id (int): id of Discord member calling the command
        server_id (int): id of Discord guild

    Returns:
        list[string]: list of todo list names 
    """
    output = []


    if str(server_id) not in list(db.child().get().val()):
        return output

    all_lists = db.child(server_id).get().val()
    for lst in all_lists:
        if author_id in all_lists[lst]["members"]:
            output.append(lst)
    return output

def update_list(db: object, list_name: str, server_id: int, the_list: dict) -> None:
    """ Updates todo list in database

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        list_name (str): name of todo list
        server_id (int): id of Discord guild
        the_list (dict): properties of a todo list in JSON format
    """
    db.child(server_id).child(list_name).update(the_list)

def remove_list(db: object, list_name: str, server_id: int) -> None:
    """ Deletes to do list from database

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        list_name (str): name of todo list
        server_id (int): id of Discord guild
    """
    db.child(server_id).child(list_name).remove()

def add_new_user_to_public_lists(db: object, user_id: int, server_id: int) -> None:
    """ Adds new guild member to all todo lists in the database

    Args:
        db (firebase.Database): object representing connection to Firebase DB
        user_id (int: _description_
        server_id (int): id of Discord guild
    """
    all_lists = db.child(server_id).get()
    for lst in all_lists.each():
        if lst.val()["for_all"] and user_id not in lst.val()["members"]:
            lst.val()["members"].append(user_id)
            update_list(lst.key(), server_id, lst.val())

