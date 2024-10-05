import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import telebot
from threading import Thread
import time
import schedule

conn = sqlite3.connect('notices.db', check_same_thread=False) # Ensure multi-threading support
cursor = conn.cursor()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

notice_url = "https://cit.ac.in/pages-notices-all"

def purple(a):
    return "\33[35m"+a+"\33[0m"

def insert_notice(data_tuple):
    cursor.execute('''
            INSERT INTO notices (date, title, link)
            VALUES (?,?,?)
        ''',data_tuple)
    conn.commit()

# checks if a notice already exists in the database
def check_if_exists(data_tuple):
    cursor.execute('''
            SELECT * FROM notices WHERE date = ? AND title = ? AND link = ?
        ''', data_tuple)
    result = cursor.fetchone()
    return result

def scrape_data(NOTICE_URL):
    """
        Scrapes the notice page and returns relevant notice information.
    
        Args:
            NOTICE_URL (str): The URL of the notice page to scrape.
    
        Returns:
            tuple: A tuple containing:
                - notice_date (str): The date of the notice.
                - notice_name (str): The title of the notice.
                - notice_attachment_link (str): The link to the attachment.
    """
    page = requests.get(NOTICE_URL)
    
    # Parse the HTML content of the page 
    soup = BeautifulSoup(page.content, "html.parser")

    # Find the table containing the notices (there's only one table on the page)
    table = soup.find('table', class_='table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    """
    Each row contains two anchor(<a>) tags:
    - first one contains the actual title of the notice and
    - second one contains the link to the attachment.
    """
    anchor_tags = rows[0].find_all('a')
        
    notice_date = rows[0].find('span').text
    notice_name = anchor_tags[0].text.strip()
    notice_attachment_link = anchor_tags[1]['href']
    return notice_date, notice_name, notice_attachment_link


def insert_subscriber(chat_id):
    cursor.execute('''
        INSERT OR IGNORE INTO subscribers (chat_id) VALUES (?)
        ''', (chat_id,)) # pls don't remove the comma after chat_id, without the comma, its just a grouped expression, not a tuple
    conn.commit()

def remove_subscriber(chat_id):
    cursor.execute('''
        DELETE FROM subscribers  WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()

def get_subscribers():
    cursor.execute('SELECT chat_id FROM subscribers')
    return [row[0] for row in cursor.fetchall()]

def check_and_notify():
    """
        First scrapes data from the page and then checks if it already exists in the database,
        if not inserts it and then prints the notice.
    """
    scraped_data = scrape_data(notice_url)
    if not check_if_exists(scraped_data):
        insert_notice(scraped_data)
        
        message = f"New Notice!\nDate: {scraped_data[0]}\nTitle: {scraped_data[1]}\nLink: {scraped_data[2]}"
        
        subscribers = get_subscribers()
        for chat_id in subscribers:
            bot.send_message(chat_id, message)
        print(purple("New notice found and notified."))
    else:
        print(purple("No new notice found"))

# --------------
# BOT Commands
# --------------
@bot.message_handler(commands=['start'])
def start(message):
    start_text = open("start_text.txt", "r")
    bot.reply_to(message, start_text.read(), parse_mode='Markdown')
    start_text.close() 

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    chat_id = str(message.chat.id)
    insert_subscriber(chat_id)
    bot.reply_to(message,"You have subscribed to notifications!")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    chat_id = str(message.chat.id)
    remove_subscriber(chat_id)
    bot.reply_to(message, "You have unsubcribed to notificaitons!")

@bot.message_handler(commands=['help'])
def help(message):
    help_text = open("help_text.txt", "r")
    #help_text_fr = help_text.read()
    bot.reply_to(message, help_text.read())
    help_text.close()    

# Schedule the check_and_notify function to run every 15 minutes
schedule.every(1).minutes.do(check_and_notify)
print("Bot started. Waiting for new notices...")

# Function to handle bot polling in a separate thread
def start_polling():
    print("Starting bot polling...")
    bot.infinity_polling()
    
try:
    # Start the bot polling in a separate thread
    polling_thread = Thread(target=start_polling)
    polling_thread.start()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
finally:
    conn.close()

#print(scrape_data("https://cit.ac.in/pages-notices-all"))
