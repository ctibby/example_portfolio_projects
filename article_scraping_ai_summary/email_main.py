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
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_container = soup.find('div', id='articleContainer')
    paragraphs = article_container.find_all('p')[:3]
    summary = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
    return summary

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
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
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
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
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_containers = soup.find_all('div', class_='queue', limit=10)

    for article in article_containers:
        headline_tag = article.find('h2')
        if headline_tag:
            a_tag = headline_tag.find('a')
            if a_tag and a_tag.has_attr('href'):
                full_url = f"https://www.ksl.com{a_tag['href']}"
                headline = a_tag.get_text(strip=True)
                summary = fetch_article_summary(full_url)
                articles_info.append(f"Title: {headline}\nLink: {full_url}\nSummary: {summary}\n\n---\n")
    
    email_body = "\n".join(articles_info)
    send_email("Daily Article Summaries", email_body)

if __name__ == '__main__':
    main()
