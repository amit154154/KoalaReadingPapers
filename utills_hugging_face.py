import requests
from bs4 import BeautifulSoup
import string
from tqdm import tqdm

def find_articles(url):
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Create a BeautifulSoup object with the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the elements that contain the articles
        article_elements = soup.find_all('article')

    papers_list = []
    for article in article_elements:
        title_element = article.find('h3')
        title = title_element.text.strip() if title_element else 'N/A'

        link_element = article.find('a', href=True)
        link = link_element['href'] if link_element else 'N/A'
        arxiv_num = link.split('/')[-1]
        papers_list.append((title,arxiv_num))
        print(f"Title: {title}")
        print(f"Link to paper page: {arxiv_num}")
        print("=" * 30)
    return papers_list

def get_valid_filename(title):
    # Remove any invalid characters from the title
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in title if c in valid_chars)

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    return filename

from datetime import datetime, timedelta

def generate_dates_between(start_date_str, end_date_str):
    dates_list = []

    # Convert input strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Generate dates between start_date and end_date (inclusive)
    current_date = start_date
    while current_date <= end_date:
        dates_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return dates_list

def download_papers(papers_list,dir_output):
    for name,arxiv_id in tqdm(papers_list):
        paper_url = f'https://arxiv.org/pdf/{arxiv_id}".pdf'
        response = requests.get(paper_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Check if the response contains PDF content
            if response.headers['Content-Type'] == 'application/pdf':
                # Save the PDF content to a local file
                with open(f'{dir_output}/{get_valid_filename(name)}_{arxiv_id}.pdf', 'wb') as file:
                    file.write(response.content)
            else:
                print("The provided URL does not point to a PDF file.")
        else:
            print(name)
            print(f"Failed to fetch the PDF. Status code: {response.status_code}")

def download_papers_between_dates(to_path,from_date,to_date):
    dates_urls = generate_dates_between(from_date,to_date)
    print(dates_urls)
    dates_urls = [f'https://huggingface.co/papers?date={k}' for k in dates_urls]
    print(dates_urls)
    all_articals = [find_articles(i) for i in dates_urls]
    for day_articals in all_articals:
        download_papers(day_articals,to_path)
