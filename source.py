import csv
from bs4 import BeautifulSoup
import requests

# Make a request to the web page and create a BeautifulSoup object from the HTML content
html = requests.get('https://www.brainyquote.com/topics')
soup = BeautifulSoup(html.content, "html.parser")

# Find all the category links on the page
categories = soup.find_all("a", class_="topicIndexChicklet")

# Initialize empty lists for the titles, URLs, and quotes
titles = []
urls = []
quotes = []

# Loop through the category links and extract the title and URL
for category in categories:
    title = category.find("span", class_="topicContentName").text.strip()
    url = 'https://www.brainyquote.com' + category['href']
    titles.append(title)
    urls.append(url)

# Set the starting index to 1
index = 1

# Loop through each URL
for url in urls:
    try:
        # Make a request to the URL and create a BeautifulSoup object from the HTML content
        html = requests.get(url, timeout=10)
        # Handle timeout exception
    except requests.exceptions.Timeout:
        print('Request timed out ⏳')
        # Handle other exception
    except requests.exceptions.RequestException as e:
        print('Request failed ❌', e)
    soup = BeautifulSoup(html.content, "html.parser")
    quotes = soup.find_all("div", class_="clearfix")
    for quote in quotes:
        author = quote.find("a", class_="bq-aut")
        quote = quote.find("div", class_="")
        with open('test.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([quote.text.strip(), author.text.strip()])
    print(f'Scrapped {url} 😊')
    pagination_counter = 2
    while (1):
        pagination_url = url + '_' + str(pagination_counter)
        try:
            html = requests.get(pagination_url, timeout=10)
        except requests.exceptions.Timeout:
            print('Request timed out ⏳')
        except requests.exceptions.RequestException as e:
            print('Request failed ❌', e)
        # Break out of the loop if there are no more pagination pages
        if (html.url == url):
            pagination_counter = 2
            break
        soup = BeautifulSoup(html.content, "html.parser")
        # Find all the quotes on the pagination page
        quotes = soup.find_all("div", class_="clearfix")
        # Loop through each quote and extract the author and text
        for quote in quotes:
            author = quote.find("a", class_="bq-aut")
            quote = quote.find("div", class_="")
            # Write the quote and author to a CSV file
            with open('test.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([quote.text.strip(), author.text.strip()])
        print(f'Scrapped {pagination_url} 😊')
        pagination_counter += 1
    index += 1
    progress = index / len(urls) * 100
    # Print a message indicating that the pagination page has been scraped
    print(f'{progress:.2f}% completed 💪')
