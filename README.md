---
title: 'Project documentation template'
disqus: hackmd
---

Dis A ToDo Bot
===

## Table of Contents

[TOC]

## Installation Guide

To avoid abuse, please send us a message if you want to use this bot!

Once your bot is in the server, you will have the ability to create personal or server-wide
ToDo lists!

## Helpful Bot Commands
All commands should be prepended with an exclamation point, i.e. !help
```
Commands:
  add        Add new item to list. Need quotes around list name
  help       Shows this message
  makelist   Make a new ToDo list
  mylists    Display ToDo lists for specific user
  removelist Removes list by name
  showlist   Display a ToDo list in chat

Type !help command for more info on a command.
You can also type !help category for more info on a category.
```

User stories
---
### Feature: User wants to add a personal list
User types in command:

![](https://i.imgur.com/nMQ15fs.png)

Bot responds with checkbox emoji to verify new list is created:

![](https://i.imgur.com/rOHSBvW.png)

---

### Feature: User wants to add a server-wide list
User types in command:

![](https://i.imgur.com/jz0DTsz.png)

Bot responds with checkbox emoji to verify new list is created:

![](https://i.imgur.com/GE0wj2B.png)

---

### Feature: User wants to add an item to their ToDo list
User types in command:

![](https://i.imgur.com/H2gxv0e.png)

Bot responds with checkbox emoji to verify new ToDo item was added to list:

![](https://i.imgur.com/NUrZcP4.png)

---

### Feature: User wants to see items on their ToDo list
User types in command:

![](https://i.imgur.com/LSRXjst.png)

Bot responds with ToDo list if tasks available or already completed:

![](https://i.imgur.com/g4QZhZN.png)

Bot responds with following if the list is fresh  with no tasks completed or available:

![](https://i.imgur.com/ogXfnET.png)

---

### Feature: User wants to view all their lists
User types in command to show lists:

![](https://i.imgur.com/bLEanz2.png)

Bot responds with all lists if available, including both personal and server-wide lists:

![](https://i.imgur.com/WRakQFT.png)

Bot responds with following if no lists available:

![](https://i.imgur.com/wlyiQ50.png)

---

### Feature: User wants to delete a list
User types in command to remove list:

![](https://i.imgur.com/5OLUVfR.png)

Bot asks user to confirm if they want to delete list:

![](https://i.imgur.com/uSVs02U.png)

If user clicks checkbox emoji, list is deleted:

![](https://i.imgur.com/LopxZgR.png)

If user clicks X emoji, the bot's message is removed.






## Appendix and FAQ

:::info
**Find this document incomplete?** Leave a comment!
:::

###### tags: `Templates` `Documentation`
