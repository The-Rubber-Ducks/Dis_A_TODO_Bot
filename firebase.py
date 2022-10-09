"""
create_list(list_name, author_id)

get_list_by_name(list_name)
    parameters: list_name -> str
    returns: dictionary representing list -> dictionary

get_user_lists(member_id)
    returns: list of dictionaries representing user's lists -> list[dictionary]

get_list_by_message_id(message_id)
    returns: dictionary representing list -> dictionary

is_user_member(list_name, user_id)
"""
import pyrebase


# TODO: move to new file
config = {
  "apiKey": "AIzaSyDbcs6CmlTSae_6wml5YMknjJVXSEU83_c",
  "databaseURL": "https://dis-a-todo-bot-default-rtdb.firebaseio.com/",
  "authDomain": "dis-a-todo-bot.firebaseapp.com",
  "projectId": "dis-a-todo-bot",
  "storageBucket": "dis-a-todo-bot.appspot.com",
  "messagingSenderId": "577063034746",
  "appId": "1:577063034746:web:1bbd16e93e62b020b840c3",
  "measurementId": "G-J61Y46XMBQ"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()


def create_list(list_name, server_id, author_id):

    data = {
        "serverID": server_id,
        "creator": author_id,
        "members": [author_id],
        "todoList": [],
        "completed": []
    }
    db.child("todoLists").child(list_name).set(data)
    db.child("members").child(author_id).child("todoLists").set(list_name)


def get_list_by_name(list_name):
    return db.child("todoLists").child(list_name).get().val()


def get_list_by_message_id(message_id):
    return db.child("todoLists").child()


def set_member_id(message_id):
    pass


# returns
def get_all_lists_names_by_user(author_id):
    return db.child("members").child(author_id).get().key()
        

create_list("homework", "server_id", "some_user_id")
print(get_all_lists_by_user("some_user_id"))