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

def create_list(db, list_name, server_id, author_id):

    data = {
        "serverID": server_id,
        "creator": author_id,
        "members": [author_id],
        "todoList": [],
        "completed": [],
        "message_id": ""
    }
    db.child("todoLists").child(list_name).set(data)
    db.child("members").child(author_id).child("todoLists").set(list_name)


def get_list_by_name(db, list_name):
    return db.child("todoLists").child(list_name).get().val()


def get_list_by_message_id(db, message_id):
    lists = db.child("todoLists").get()
    pass


def set_member_id(db, list_name, message_id):
    db.child("todoLists").child(list_name).update({"message_id": message_id})



def get_all_list_names_by_user(db, author_id):
    return db.child("members").child(author_id).get().key()
        

create_list("homework", "server_id", "some_user_id")
print(get_all_list_names_by_user("some_user_id"))