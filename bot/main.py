import os, time
from dotenv import load_dotenv
from backstage_scraper import browse_ai
from db import _db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue, Updater
import pprint, re

# Replace 'YOUR_TOKEN' with your actual Bot Token provided by BotFather
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_ADDRESS = os.getenv("BOT_ADDRESS")
job = None

def escape_markdown_v2(text):
    # Define the characters to be escaped
    escape_chars = r'`_*[]()~>#+-=|{}.!'
    # Use regular expression to escape each character with a preceding backslash
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


def poll_backstage_for_casting_calls():
    # Implement this function to poll BrowseAI for new casting calls
    print("Polling Backstage for new casting calls...")
    run_info = browse_ai.run_robot()
    pprint.pprint(run_info["result"]["status"])
    run_info = browse_ai.retrieve_task(run_info["result"]["robotId"], run_info["result"]["id"])
    while run_info["result"]["status"] != "successful":
        run_info = browse_ai.retrieve_task(run_info["result"]["robotId"], run_info["result"]["id"])
        time.sleep(15)
        pprint.pprint(run_info["result"]["status"])
    pprint.pprint(run_info["result"]["status"])
    # grab the list of Casting Calls from result -> status -> capturedLists -> Casting Calls
    castingCalls = run_info["result"]["capturedLists"]["Casting Calls"]
    # create a list of all the Detail Link
    detailLinks = [castingCall["Detail Link"] for castingCall in castingCalls]
    # filter the list of casting calls to only include the ones that are not already in the database
    filtered_list_of_links = _db.filter_all_notifications_already_in_db_from_current_list("Atlanata", "Backstage Notifications", detailLinks)
    # filter the castingCalls list to only include the ones that are in the filtered_list_of_links
    filtered_casting_calls = [castingCall for castingCall in castingCalls if castingCall["Detail Link"] in filtered_list_of_links]
    # update the database with the new casting calls
    _db.update_casting_call_notification_list("Atlanta", "Backstage Notifications", detailLinks)
    # return the filtered_casting_calls
    return filtered_casting_calls

async def send_message_to_all_users(filtered_casting_calls: list):
    print("Sending messages to all users...\nNumber of casting calls: ", len(filtered_casting_calls))
    for castingCall in filtered_casting_calls:
        # send a message to all users with the casting call information
        if castingCall["Title"] == None:
            continue
        await send_to_telegram(castingCall)
        time.sleep(3)

async def run_polling_and_send_messages(context: ContextTypes.DEFAULT_TYPE = None):
    # Implement this function to run the polling and sending messages
    filtered_casting_calls = poll_backstage_for_casting_calls()
    await send_message_to_all_users(filtered_casting_calls)

async def send_to_telegram(casting_call_info, chat_id=BOT_ADDRESS):
    """
    Send the casting call information to the telegram channel
    """
    bot = Bot(token=TOKEN)
    text = f"🎬 New Casting Call 🎬\n\n"
    text += f"Title: {casting_call_info['Title']}\n"
    text += f"Category: {casting_call_info['Category']}\n"
    text += f"Type: {casting_call_info['Type']}\n"
    text += f"Location: {casting_call_info['Location']}\n"
    text += f"Description: {casting_call_info['Description']}\n"
    text += f"Dates & Locations: {casting_call_info['Dates & Locations']}\n\n"
    text += f"Detail Link: [{casting_call_info['Detail Link']}]({casting_call_info['Detail Link']})\n"
    try:
        await bot.send_message(chat_id=chat_id, text=escape_markdown_v2(text), parse_mode="MarkdownV2")
        return True
    except Exception as e:
        print(f"Error sending message to telegram: {e}")
        return False
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Start Polling", callback_data='start_polling')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # print chat_id
    print(update.message.chat_id)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)

async def stop_pooling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Stop the job
    if job:
        job.schedule_removal()
        job = None
        await update.message.reply_text('Polling stopped!')
    else:
        await update.message.reply_text('No job to stop!')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "start_polling":
        # Start the job
        await run_polling_and_send_messages(context)
        job = context.job_queue.run_repeating(run_polling_and_send_messages, interval=300)
        await query.edit_message_text(text="Polling started!")

async def main():
    await run_polling_and_send_messages()




if __name__ == '__main__':
    # run main async function
    import asyncio
    asyncio.run(main())