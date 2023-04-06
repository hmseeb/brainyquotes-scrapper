from bs4 import BeautifulSoup
import requests
html = requests.get('https://www.brainyquote.com/topics')

soup = BeautifulSoup(html.content, "html.parser")

categories = soup.find_all("a", class_="topicIndexChicklet")

titles = []
urls = []
for category in categories:
    title = category.find("span", class_="topicContentName").text.strip()
    url = 'https://www.brainyquote.com' + category['href']
    titles.append(title)
    urls.append(url)

authors = []
quotations = []
index = 1
for url in urls:
    try:
        html = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        print('Request timed out ⏳')
    except requests.exceptions.RequestException as e:
        print('Request failed ❌', e)
    soup = BeautifulSoup(html.content, "html.parser")
    quotes = soup.find_all("div", class_="clearfix")
    for quote in quotes:
        author = quote.find("a", class_="bq-aut")
        quote = quote.find("div", class_="")
        authors.append(author.text.strip())
        quotations.append(quote.text.strip())
    print(f'Scrapped {url} 😊')
    pagination_counter = 16
    while (1):
        pagination_url = url + '_' + str(pagination_counter)
        try:
            html = requests.get(pagination_url, timeout=10)
        except requests.exceptions.Timeout:
            print('Request timed out ⏳')
        except requests.exceptions.RequestException as e:
            print('Request failed ❌', e)
        if (html.url == url):
            break
        soup = BeautifulSoup(html.content, "html.parser")
        quotes = soup.find_all("div", class_="clearfix")
        for quote in quotes:
            author = quote.find("a", class_="bq-aut")
            quote = quote.find("div", class_="")
            authors.append(author.text.strip())
            quotations.append(quote.text.strip())
        print(f'Scrapped {pagination_url} 😊')
        print(quotations)
        print(authors)
        pagination_counter += 1
    index += 1
    progress = index / len(urls) * 100
    print(f'{progress:.2f}% completed 💪')
