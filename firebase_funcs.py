import pyrebase
import os
from dotenv import load_dotenv
import json

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


firebase = pyrebase.initialize_app(config)
db = firebase.database()

def create_list(list_name, server_id, author_id):
    lists = db.child("todoLists").get().val()
    if list_name in 
    data = {
        "todoListName": list_name,
        "serverID": server_id,
        "creator": author_id,
        "members": [author_id],
        "todoList": [],
        "completed": [],
        "message_id": ""
    }
    db.child("todoLists").child(list_name).set(data)
    db.child("members").child(author_id).child("todoLists").set(list_name)


def get_list_by_name(list_name):
    # With list name AND by user
    # db.child("users").order_by_child("score").equal_to(10).get()
    print(db.child("todoLists").order_by_child("todoListName").equal_to(list_name).get())
    return db.child("todoLists").order_by_child("todoListName").equal_to(list_name).get().val()


def get_list_by_message_id(message_id):
    lists = db.child("todoLists").get().val()
    for key, val in lists.items():
        if val["message_id"] == message_id:
            return val
    return None


def set_member_id(list_name, message_id):
    db.child("todoLists").child(list_name).update({"message_id": message_id})


import json 
def get_all_list_names_by_user(author_id):
    return db.child("members").child(author_id).get().key()

def update_list(author_id, list_name, the_list):
    lsts = db.child("todoLists").get().val()


    # "order_by("todoListName").equal_to(list_name)
    # obj = db.child("todoLists").order_by_child("todoListName").equal_to(author_id).order_by_child("creator").equal_to(list_name)
    print(lsts)
    # print(dir(lsts))
    # return obj
    #````

    """
    GOOD: https://dis-a-todo-bot-default-rtdb.firebaseio.com/todoLists.json?orderBy="child"

    https://dis-a-todo-bot-default-rtdb.firebaseio.com/todoLists.json?orderBy=%2522%2522child%2522%2522
    https://dis-a-todo-bot-default-rtdb.firebaseio.com/todoLists.json?orderBy=%22creator%22&equalTo=%22666%22
    https://dis-a-todo-bot-default-rtdb.firebaseio.com/todoLists.json?orderBy=%22creator%22&equalTo=%22666%22
    """
    
create_list("groceries", "server777", "djgdgfgfd")

lst = get_list_by_name("groceries")
print(lst)
#lst["message_id"] = "000"


#update_list(lst["creator"], "groceries", lst)
# print(lst)