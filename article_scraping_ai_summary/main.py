from bs4 import BeautifulSoup
import requests
from datetime import datetime

def fetch_article_summary(article_url):
    try:
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        article_container = soup.find('div', id='articleContainer')
        paragraphs = article_container.find_all('p')[:3]
        
        summary = "\n\n".join(paragraph.get_text() for paragraph in paragraphs)
        return summary
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "Summary could not be retrieved."

def scrape_ksl_articles_to_file():
    url = "https://www.ksl.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    article_containers = soup.find_all('div', class_='queue', limit=10)

    # Extract the date from the most recent article for the filename
    date_span = article_containers[0].find('span', class_='short')
    most_recent_date = date_span.get_text(strip=True) if date_span else None
    if most_recent_date:
        # Convert the date to m/d/y format. This assumes the date is in "Month DD - HH:MM a.m./p.m." format
        try:
            most_recent_date_obj = datetime.strptime(most_recent_date, "%B %d - %I:%M %p")
            date_for_filename = most_recent_date_obj.strftime("%m_%d_%Y")
        except ValueError:
            # Fallback in case parsing fails
            date_for_filename = "date_unknown"
    else:
        date_for_filename = "date_unknown"

    filename = f'article_summaries_{date_for_filename}.txt'

    with open(filename, 'w', encoding='utf-8') as file:
        for article in article_containers:
            headline_tag = article.find('h2')
            if headline_tag:
                a_tag = headline_tag.find('a')
                if a_tag and a_tag.has_attr('href'):
                    full_url = f"https://www.ksl.com{a_tag['href']}"
                    headline = a_tag.get_text(strip=True)
                    date_time = date_span.get_text(strip=True) if date_span else "Date not found"
                    
                    summary = fetch_article_summary(full_url)
                    
                    file.write(f"Headline: {headline}\nURL: {full_url}\nDate and Time: {date_time}\nSummary: {summary}\n\n---\n\n")

    print(f"Article summaries have been saved to {filename}.")

scrape_ksl_articles_to_file()