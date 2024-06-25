from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from pymongo import MongoClient

TOKEN = 'YOUR_BOT_TOKEN'

client = MongoClient('mongodb://localhost:27017/')
db = client['ludo_game']
users_collection = db['users']
games_collection = db['games']

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not users_collection.find_one({'user_id': user_id}):
        users_collection.insert_one({'user_id': user_id, 'points': 0})
    update.message.reply_text('Welcome to Ludo Bot! Type /join to join a game.')

def join(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    game = games_collection.find_one({'status': 'waiting'})
    if not game:
        game_id = games_collection.insert_one({'players': [user_id], 'status': 'waiting', 'winner': None}).inserted_id
        update.message.reply_text(f'You have created a new game with ID: {game_id}. Waiting for other players...')
    else:
        games_collection.update_one({'_id': game['_id']}, {'$push': {'players': user_id}})
        update.message.reply_text(f'You have joined the game with ID: {game["_id"]}.')
        if len(game['players']) + 1 == 4:
            games_collection.update_one({'_id': game['_id']}, {'$set': {'status': 'ongoing'}})
           

def win(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    game_id = context.args[0]
    games_collection.update_one({'_id': game_id}, {'$set': {'status': 'finished', 'winner': user_id}})
    users_collection.update_one({'user_id': user_id}, {'$inc': {'points': 10}})
    update.message.reply_text(f'Congratulations! You won the game {game_id}. You earned 10 points.')

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("join", join))
updater.dispatcher.add_handler(CommandHandler("win", win))

updater.start_polling()
updater.idle()
