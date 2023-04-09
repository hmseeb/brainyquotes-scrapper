from os import path
import pandas as pd
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import time

webpage = requests.get('https://www.brainyquote.com/topics')
soup = BeautifulSoup(webpage.content, "html.parser")

category_links = soup.find_all("a", class_="topicIndexChicklet")

titles_list = []
urls_list = []
quotes_list = []
choice = input('Press y if you want separate csv\'s for each category: ')
start_time = time.time()
for category_link in category_links:
    title = category_link.find("span", class_="topicContentName").text.strip()
    url = 'https://www.brainyquote.com' + category_link['href']
    titles_list.append(title)
    urls_list.append(url)


def scrape_url(url):
    scraped_authors = []
    scraped_quotes = []
    scraped_categories = []
    session = requests.Session()
    try:
        webpage = session.get(url, timeout=10)
    except requests.exceptions.Timeout:
        print('Request timed out ⏳')
    except requests.exceptions.RequestException as e:
        print('Request failed ❌', e)
    soup = BeautifulSoup(webpage.content, "html.parser")
    quotes = soup.find_all("div", class_="clearfix")
    for quote in quotes:
        author = quote.find("a", class_="bq-aut")
        quote_text = quote.find("div", class_="")
        scraped_authors.append(author.text.strip())
        scraped_quotes.append(quote_text.text.strip())
    print(f'Scraped {url}')
    pagination_counter = 2
    while (1):
        pagination_url = url + '_' + str(pagination_counter)
        try:
            webpage = session.get(pagination_url, timeout=10)
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

            scraped_authors.append(author.text.strip())
            scraped_quotes.append(quote_text.text.strip())
        print(f'Scraped {pagination_url}')
        pagination_counter += 1

    scraped_categories = titles_list[urls_list.index(url)]
    data = {
        'quotes': scraped_quotes,
        'authors': scraped_authors,
        'categories': scraped_categories,
    }

    df = pd.DataFrame(data)

    if choice == 'y':
        if path.isfile('scraped/categories/' + scraped_categories + '.csv'):
            df.to_csv('scraped/categories/' +
                      scraped_categories + '.csv', header=False, index=False)
        else:
            df.to_csv('scraped/categories/' +
                      scraped_categories + '.csv', index=False)
    else:
        if path.isfile('scraped/brainyquotes.csv'):
            df.to_csv('scraped/brainyquotes.csv',
                      mode='a', header=False, index=False)
        else:
            df.to_csv('scraped/brainyquotes.csv', mode='a', index=False)
    session.close()


with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(scrape_url, urls_list)

print(f'Elapsed time: {int(time.time() - start_time)} seconds')
