import os
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Make a request to the web page and create a BeautifulSoup object from the HTML content
webpage = requests.get('https://www.brainyquote.com/topics')
soup = BeautifulSoup(webpage.content, "html.parser")

# Find all the category links on the page
category_links = soup.find_all("a", class_="topicIndexChicklet")

# Initialize empty lists for the titles, URLs, and quotes
titles_list = []
urls_list = []
quotes_list = []

# Loop through the category links and extract the title and URL
for category_link in category_links:
    title = category_link.find("span", class_="topicContentName").text.strip()
    url = 'https://www.brainyquote.com' + category_link['href']
    titles_list.append(title)
    urls_list.append(url)

# Set the starting index to 1
progress = 1

# Loop through each URL
for url in urls_list:
    scrapped_authors = []
    scrapped_quotes = []
    scrapped_categories = []
    try:
        # Make a request to the URL and create a BeautifulSoup object from the HTML content
        webpage = requests.get(url, timeout=10)
        # Handle timeout exception
    except requests.exceptions.Timeout:
        print('Request timed out ⏳')
        # Handle other exception
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
        # Break out of the loop if there are no more pagination pages
        if (webpage.url == url):
            pagination_counter = 2
            break
        soup = BeautifulSoup(webpage.content, "html.parser")
        # Find all the quotes on the pagination page
        quotes = soup.find_all("div", class_="clearfix")
        # Loop through each quote and extract the author and text
        for quote in quotes:
            author = quote.find("a", class_="bq-aut")
            quote_text = quote.find("div", class_="")
            # Write the quote and author to a CSV file
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
    if os.path.isfile('test.csv'):
        df.to_csv('test.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('test.csv', index=False)
    progress += 1
    calculated_progress = progress / len(urls_list) * 100
    # Print a message indicating that the pagination page has been scraped
    print(f'{calculated_progress:.2f}% completed 💪')
