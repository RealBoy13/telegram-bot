import os
import logging
import random
from datetime import datetime
from typing import Final
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging for debugging and error tracking
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
TOKEN: Final = os.getenv('TELEGRAM_BOT_TOKEN')  # Using environment variable for token
BOT_USERNAME: Final = '@TelegramTestBot'

# Initialize a dictionary to store user message counts (for /stats command)
user_message_counts = {}

# List of random jokes for the /joke command
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why do Java developers wear glasses? Because they can't C#.",
    "What’s a programmer’s favorite hangout place? Foo Bar!"
]

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    keyboard = [['/help', '/datetime', '/joke', '/stats']]  # Custom keyboard
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Hello! I'm TelegramTest bot. Use the buttons or commands to interact with me!",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    commands = [
        "/start - Start interaction with the bot",
        "/help - List available commands",
        "/datetime - Show the current date and time",
        "/joke - Get a random programming joke",
        "/stats - Get statistics about your message activity"
    ]
    help_text = "Here are the available commands:\n" + "\n".join(commands)
    await update.message.reply_text(help_text)

async def datetime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the current date and time to the user."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    await update.message.reply_text(f"The current date and time is: {now}")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random programming joke."""
    joke = random.choice(JOKES)
    await update.message.reply_text(joke)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send statistics about the user's message activity."""
    user_id = update.message.from_user.id
    message_count = user_message_counts.get(user_id, 0)
    await update.message.reply_text(f"You have sent {message_count} messages to this bot.")

# Helper function to process and respond to text messages
def handle_response(text: str) -> str:
    """Generate bot's response based on the user's input."""
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I\'m good! How about you?'

    return 'I don\'t understand'

# Handle incoming text messages and track user activity
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general text messages."""
    user_id = update.message.from_user.id
    text: str = update.message.text

    # Track how many messages a user has sent
    user_message_counts[user_id] = user_message_counts.get(user_id, 0) + 1

    logger.info(f'User ({user_id}) sent message: "{text}"')

    response: str = handle_response(text)
    logger.info(f'Bot response: {response}')
    await update.message.reply_text(response)

# Handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log any errors."""
    logger.error(f'Update {update} caused error {context.error}')

# Main function to start the bot
if __name__ == '__main__':
    logger.info('Starting bot...')

    # Create the Application
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('datetime', datetime_command))
    app.add_handler(CommandHandler('joke', joke_command))
    app.add_handler(CommandHandler('stats', stats_command))

    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Add error handler
    app.add_error_handler(error)

    # Start polling the bot
    logger.info('Polling...')
    app.run_polling(poll_interval=3)
