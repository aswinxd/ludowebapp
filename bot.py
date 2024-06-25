from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
import logging
import asyncio
import os

TOKEN = '7057474043:AAEXL5Up5MpjTh1kyCVSS4WZpzwhGI5xRp4'

client = MongoClient('mongodb+srv://test:test@cluster0.q9llhnj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['ludo_game']
users_collection = db['users']
games_collection = db['games']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if not users_collection.find_one({'user_id': user_id}):
        users_collection.insert_one({'user_id': user_id, 'points': 0})
    await update.message.reply_text('Welcome to Ludo Bot! Type /join to join a game.')

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    game = games_collection.find_one({'status': 'waiting'})
    if not game:
        game_id = games_collection.insert_one({'players': [user_id], 'status': 'waiting', 'winner': None}).inserted_id
        await update.message.reply_text(f'You have created a new game with ID: {game_id}. Waiting for other players...')
    else:
        games_collection.update_one({'_id': game['_id']}, {'$push': {'players': user_id}})
        await update.message.reply_text(f'You have joined the game with ID: {game["_id"]}.')
        if len(game['players']) + 1 == 4:
            games_collection.update_one({'_id': game['_id']}, {'$set': {'status': 'ongoing'}})
            

async def win(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    game_id = context.args[0]
    games_collection.update_one({'_id': game_id}, {'$set': {'status': 'finished', 'winner': user_id}})
    users_collection.update_one({'user_id': user_id}, {'$inc': {'points': 10}})
    await update.message.reply_text(f'Congratulations! You won the game {game_id}. You earned 10 points.')

async def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("win", win))

    await application.initialize()
    await application.start()

if __name__ == '__main__':
    asyncio.run(main())
