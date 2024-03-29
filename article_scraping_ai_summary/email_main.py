import base64
from email.mime.text import MIMEText
import os
import pickle
import requests
from bs4 import BeautifulSoup
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

def fetch_article_summary(article_url):
    try:
        response = requests.get(article_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_container = soup.find('div', id='articleContainer')
            if article_container:
                paragraphs = article_container.find_all('p')[:3]
                summary = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
                return summary
            else:
                return "Article summary not found."
        else:
            return "Failed to fetch article."
    except requests.RequestException as e:
        return f"Request error: {e}"

def create_message(sender, to, subject, message_html):
    message = MIMEText(message_html, 'html')  # Specify the MIME type as 'html'
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
    except HttpError as error:
        print(f'An error occurred: {error}')

def send_email(subject, body):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = create_message('tibbitts.chris@gmail.com', 'chris3-93@hotmail.com', subject, body)
        send_message(service, "me", message)
    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    articles_info = []
    url = "https://www.ksl.com/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_containers = soup.find_all('div', class_='queue', limit=10)

            for article in article_containers:
                headline_tag = article.find('h2')
                if headline_tag:
                    a_tag = headline_tag.find('a')
                    if a_tag and a_tag.has_attr('href'):
                        href = a_tag['href']
                        full_url = href if href.startswith('http') else f"https://www.ksl.com{href}"
                        headline = a_tag.get_text(strip=True)
                        summary = fetch_article_summary(full_url)
                        # Format the article info as HTML, making the title bold
                        articles_info.append(f"<strong>Title: {headline}</strong><br>Link: <a href='{full_url}'>{full_url}</a><br><p>Summary:<br>{summary.replace('\n', '<br>')}</p><hr>")
            
            email_body = "".join(articles_info)
            send_email("Daily Article Summaries", email_body)
        else:
            print("Failed to fetch the main page.")
    except requests.RequestException as e:
        print(f"Failed to fetch the main page: {e}")

if __name__ == '__main__':
    main()
