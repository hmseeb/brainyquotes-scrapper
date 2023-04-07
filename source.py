import os
import pandas as pd
from bs4 import BeautifulSoup
import requests

webpage = requests.get('https://www.brainyquote.com/topics')
soup = BeautifulSoup(webpage.content, "html.parser")

category_links = soup.find_all("a", class_="topicIndexChicklet")

titles_list = []
urls_list = []
quotes_list = []

for category_link in category_links:
    title = category_link.find("span", class_="topicContentName").text.strip()
    url = 'https://www.brainyquote.com' + category_link['href']
    titles_list.append(title)
    urls_list.append(url)

progress = 1

for url in urls_list:
    scrapped_authors = []
    scrapped_quotes = []
    scrapped_categories = []
    try:
        webpage = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        print('Request timed out ⏳')
    except requests.exceptions.RequestException as e:
        print('Request failed ❌', e)
    soup = BeautifulSoup(webpage.content, "html.parser")
    quotes = soup.find_all("div", class_="clearfix")
    for quote in quotes:
        author = quote.find("a", class_="bq-aut")
        quote_text = quote.find("div", class_="")
        scrapped_authors.append(author.text.strip())
        scrapped_quotes.append(quote_text.text.strip())
    print(f'Scrapped {url} 😊')
    pagination_counter = 2
    while (1):
        pagination_url = url + '_' + str(pagination_counter)
        try:
            webpage = requests.get(pagination_url, timeout=10)
        except requests.exceptions.Timeout:
            print('Request timed out ⏳')
        except requests.exceptions.RequestException as e:
            print('Request failed ❌', e)

        if (webpage.url == url):
            pagination_counter = 2
            break
        soup = BeautifulSoup(webpage.content, "html.parser")

        quotes = soup.find_all("div", class_="clearfix")

        for quote in quotes:
            author = quote.find("a", class_="bq-aut")
            quote_text = quote.find("div", class_="")

            scrapped_authors.append(author.text.strip())
            scrapped_quotes.append(quote_text.text.strip())
        print(f'Scrapped {pagination_url} 😊')
        pagination_counter += 1

    scrapped_categories = titles_list[progress-1]
    data = {
        'quotes': scrapped_quotes,
        'authors': scrapped_authors,
        'categories': scrapped_categories,
    }

    df = pd.DataFrame(data)
    if os.path.isfile('brainyquotes.csv'):
        df.to_csv('brainyquotes.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('brainyquotes.csv', index=False, quoting=None)
    progress += 1
    calculated_progress = progress / len(urls_list) * 100

    print(f'{calculated_progress:.2f}% completed 💪')
