import json
import datetime


class Todo_List:
    def __init__(self, list_name, creator):
        self.creator = creator
        self.creation_date = datetime.datetime.now()
        self.members = []
        self.completed = []
        self.todolist = []
        self.todoListName = list_name

    def load_JSON(self, json_data):
        raw_data = json.load(json_data)
        self.creator = raw_data["creator"]
        self.creation_date = raw_data["creation_date"]
        self.members = raw_data['members']
        self.completed = raw_data['completed']
        self.todolist = raw_data['todoList']
        self.todoListName = raw_data['todoListName']

    def get_todo_list(self):
        return self.todolist

    def get_todo_list_name(self):
        return self.todoListName

    def get_completed(self):
        return self.completed

    def add_item(self, new_item):
        self.todolist.append(new_item)

    def complete_item(self, the_item):
        self.todolist.remove(the_item)
        self.completed.append(the_item)
