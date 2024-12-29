import logging
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import pandas as pd
import json
import sqlite3


def send_request(url):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log', mode='a')  # Save logs to a file
        ]
    )

    soup = None
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Language': 'en-US, en;q=0.9',
        'Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        logging.info(f"Sending request to URL: {url}")
        session = HTMLSession()
        res = session.get(url, headers=headers)
        res.html.render(timeout=15)
        # Check response status
        if res.status_code == 200:
            logging.info(f"Success! Received 200 OK for URL: {url}")
            soup = BeautifulSoup(res.html.html, 'lxml')
        else:
            logging.warning(f"Initial request returned status {res.status_code}. Retrying...")

            retry_url = url.replace('news/', '')
            logging.info(f"Retrying with modified URL: {retry_url}")
            session = HTMLSession()
            res = session.get(retry_url, headers=headers)
            res.html.render(timeout=15)
            if res.status_code == 200:
                logging.info(f"Retry successful! Received 200 OK for URL: {retry_url}")
                soup = BeautifulSoup(res.html.html, 'lxml')
                logging.info(f"Scraped {retry_url}.")
            else:
                logging.error(f"Retry failed. Received status {res.status_code}. Saving response.")
                # Save the failed response for analysis
                with open('responsenot200.html', 'w', encoding='utf-8') as file:
                    file.write(res.html.html)
                logging.info("Failed response saved to 'responsenot200.html'.")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while sending the request: {e}")
    if soup:
        logging.info(f"Scraped {url}.")
    else:
        logging.info("Scraping failed. Check logs for details.")

    return soup


def get_articles_links(soup):
    urls = []
    main_ = soup.find('main', {'id': 'main-content'})
    article_class = main_.find('article')
    if article_class:
        logging.info('Articles Found')
        links = soup.find_all('a', class_='sc-2e6baa30-0 gILusN')
        for link in links:
            url = link['href']
            if not url.startswith('ht'):
                url = 'https://www.bbc.com' + link['href']
                if 'news' not in url:
                    url = 'https://www.bbc.com/news' + link['href']
            if 'articles' in url or 'article' in url:
                # logging.info('Successfully fetched links for articles.')
                urls.append(url)
            if not url:
                logging.warning('Link not found for article')
    return urls


def get_data(soup):
    dat = []
    descriptions = []
    try:
        title = soup.find('h1', class_='sc-518485e5-0 bWszMR').text.strip()
    except AttributeError:
        try:
            title = soup.find('h1', {'id': 'main-heading'}).find('span').text.strip()
        except AttributeError:
            title = ''
    try:
        when = soup.find('div', class_='sc-2b5e3b35-1 jTEdni').find('time', class_='sc-2b5e3b35-2 fkLXLN').text.strip()
    except AttributeError:
        try:
            when = soup.find('span', {'class': 'ssrcss-1if1g9v-MetadataText e4wm5bw1'}).find('time').text.strip()
        except AttributeError:
            when = ''

    # try:
    #     image = soup.find('image', class_='sc-a34861b-0 efFcac')['src']
    # except AttributeError:
    #     image = ''

    try:
        publisher = soup.find('span', class_='sc-2b5e3b35-7 bZCrck').text.strip()
    except AttributeError:
        try:
            publisher = soup.find('div', class_='ssrcss-68pt20-Text-TextContributorName e8mq1e98').text.strip()
        except AttributeError:
            publisher = 'BBC News'

    try:
        pub_add = soup.find('div', class_='sc-2b5e3b35-8 gxaSLA').find('span').text.strip()
    except AttributeError:
        try:
            pub_add = soup.find('div', class_='ssrcss-84ltp5-Text e8mq1e912').text.strip()
        except AttributeError:
            pub_add = 'Member of BBC News. Name not available'
    try:
        description_blocks = soup.find('article').find_all('div', {'data-component': 'text-block'})
        descriptions = [block.text.strip() for block in description_blocks]
    except AttributeError:
        descriptions = []

    article_data = {
        'Title': title,
        'Time': when,  # Add logic to fetch time if needed
        'Publisher': publisher,
        'Role': pub_add,
        'Descriptions': descriptions,  # Combine all descriptions into a list
    }

    return article_data


def main():
    main_data = []
    ul = 'https://www.bbc.com/news'
    try:
        so = send_request(url=ul)
    except Exception as e:
        logging.error(f"Failed to fetch the main page: {e}")
        return
    urls = get_articles_links(soup=so)
    if not urls:
        logging.warning("No URLs found!")
        return
    for url in urls:
        try:
            s = send_request(url)
            article_data = get_data(s)
            main_data.append(article_data)
        except Exception as e:
            logging.error(f"Error processing URL {url}: {e}")

    if not main_data:
        logging.warning("No data collected!")
        return
    try:
        df = pd.DataFrame(main_data)
        df.to_excel('articles.xlsx', index=False)
        df.to_csv('articles.csv', index=False)
        df = df.applymap(lambda x: str(x) if isinstance(x, (dict, list)) else x)
    except ValueError as e:
        logging.error(f"Error creating DataFrame: {e}")
        return
    try:
        with open('articles.json', 'w', encoding='utf-8') as json_file:
            json.dump(main_data, json_file, ensure_ascii=False, indent=4)
    except TypeError as e:
        logging.error(f"Failed to write JSON: {e}")
    try:
        conn = sqlite3.connect('articles.db')
        df.to_sql('articles', conn, if_exists='replace', index=False)
        conn.close()
    except Exception as e:
        logging.error(f"Failed to write to SQLite: {e}")

    logging.info("Data exported successfully to SQLite.")

def info():
    print('This scraper is designed by github.com/Abdullah-Shaheer')
    print("[+] Scrapes Latest Headlines")
    print("[+] Reusable")
    print("[+] CSV, Json, Excel, SQlite3 Output")


if __name__ == '__main__':
    info()
    main()
