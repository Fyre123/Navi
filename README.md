[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python: 3.8](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/) [![Database: SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/index.html)
# Navi

Reminder / Helper for EPIC RPG. This reminder supports the latest slash commands.

# Setup
• Install python 3.8 or higher.  
• Install the third party libraries mentioned in `requirements.txt`.  
• Create a Discord application with a bot user and generate a bot token.  
• Rename `default.env` to `.env` and add your token.  
• Rename `database/default_db.db` to `database/navi_db.db`.  
• Change all custom emojis in `resources/emojis.py` to something the bot can see in your servers.  
• Run `bot.py`.  

# Required intents
• guilds  
• members  
• message_content  
• messages  

# Required permissions
• Send Messages  
• Embed Links  
• Add Reactions  
• Use External Emoji  
• Read Message History  

Note that this bot will transition to slash commands soon, so make sure you give it the `applications.commands` scope.  

# Commands
• Default prefix is `navi `.  
• Use `navi help` for an overview.  

# Dev commands
 The dev commands are not listed in `help`. Use `navi dev` to get a list.   
 These can be used to set event reductions, change default cooldowns, load cogs, shutdown the bot, etc.  
 Ignore `navi dev test`, I use this to, well, test.
