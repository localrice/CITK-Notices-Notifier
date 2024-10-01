import requests
from bs4 import BeautifulSoup
import sqlite3

conn = sqlite3.connect('notices.db')
cursor = conn.cursor()

def purple(a):
    return "\33[35m"+a+"\33[0m"

def insert_data(date, title, link):
    cursor.execute('''
            INSERT INTO notices (date, title, link)
            VALUES (?,?,?)
        ''',(date, title, link))

# checks if a notice already exists in the database
def check_if_exists(date, title, link):
    cursor.execute('''
            SELECT * FROM notices WHERE date = ? AND title = ? AND link = ?
        ''', (date, title, link))
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

#print(scrape_data("https://cit.ac.in/pages-notices-all"))

conn.commit()
conn.close()
