import requests
from bs4 import BeautifulSoup

def purple(a):
    return "\33[35m"+a+"\33[0m"

NOTICE_URL = "https://cit.ac.in/pages-notices-all"
page = requests.get(NOTICE_URL)

# Parse the HTML content of the page using 
soup = BeautifulSoup(page.content, "html.parser")

# Find the table containing the notices (there's only one table on the page)
table = soup.find('table', class_='table')
table_body = table.find('tbody')

rows = table_body.find_all('tr')

# Each row represents a single notice
for row in reversed(rows[0:9]):
    '''
    Each row contains two anchor(<a>) tags:
    - first one contains the actual title of the notice and
    - second one contains the link to the attachment.
    '''
    anchor_tags = row.find_all('a')
    
    notice_date = row.find('span').text
    notice_name = anchor_tags[0].text.strip()
    notice_attachment_link = anchor_tags[1]['href']
    
    #print(f'{notice_date} - {notice_name} : {notice_attachment_link}')
    print(purple(notice_date)+"-"+notice_name+"\n"+notice_attachment_link+"\n")
