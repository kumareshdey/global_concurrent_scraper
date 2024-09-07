import os
import re
import openpyxl
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from setup import proxied_request, log
from celery_app import app
import uuid
from celery.result import AsyncResult
import csv

csv.field_size_limit(2**31 - 1) 
def append_to_csv(data, filename='data/scraped_data.csv'):
    try:
        file_exists = os.path.isfile(filename)
        
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['url', 'website_text']#, 'html']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        
        log.info(f'Wrote {data["url"]} to {filename}')
    except Exception as e:
        log.error(f'Failed to append data to {filename}: {str(e)}')

def append_to_txt(url, filename='data/scraped_url.txt'):
    with open(filename, mode='a', encoding='utf-8') as file:
            file.write(f'{url}\n')


def filter_not_existing_links(links):
    scraped_urls = set()
    try:
        if os.path.isfile('data/scraped_url.txt'):
            with open('data/scraped_url.txt', 'r', encoding='utf-8') as file:
                scraped_urls = set(row.strip() for row in file.readlines())
    except Exception as e:
        log.error(f'Error reading scraped URLs file: {str(e)}')
    
    new_urls = [link for link in links if link not in scraped_urls]
    log.info(f"Out of {len(links)} links, {len(new_urls)} are new.")
    return new_urls


@app.task(queue='scraping', routing_key='scraping', max_retries=3)
def download_document(url, main_task_id, without_proxy=False):
    log.info(f'Downloading {url}')
    response = proxied_request(url, without_proxy=without_proxy)
    file_name = url.split('/')[-1]
    data_folder = 'data'
    os.makedirs(data_folder, exist_ok=True)
    with open(os.path.join(data_folder, file_name), 'wb') as f:
        f.write(response.content)
    log.info(f"Downloaded {file_name}")
    return

@app.task(queue='scraping', routing_key='scraping', max_retries=3)
def scrape_website(url, main_url, main_task_id, without_proxy=False, render_js=False):
    log.info(f'Scraping {url}')
    if not filter_not_existing_links([url]):
        log.info(f'Already scraped {url}')
        return
    response = proxied_request(url, render_js=render_js, without_proxy=without_proxy)
    append_to_txt(url)
    if not response:
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    website_text = soup.get_text("\n", strip=True)
    append_to_csv({
        'url': url,
        'website_text': website_text,
        # "html": soup.prettify(),
    })
    excluded_extensions = ['.mp4', '.mp3', '.jpg', '.jpeg', '.png', '.gif', '.ppt', '.pptx', '.zip', '.rar', '.7z', '.tar', '.gz', '.js', '.jsx']

    excluded_extensions_regex = re.compile(r'|'.join([re.escape(ext) + r'$' for ext in excluded_extensions]))
    links = [link['href'] for link in soup.find_all('a', href=True) 
            if (main_url in link['href'] or link['href'].endswith('.pdf') or link['href'].endswith('.docs')) 
            and not excluded_extensions_regex.search(link['href'])]
    links = filter_not_existing_links(links)
    log.info(f"Found {len(links)} new links on {url}")
    for link in links:
        task_id = main_task_id+link
        if link.endswith('.pdf') or link.endswith('.docs'):
            download_document.s(link, main_task_id=main_task_id, without_proxy=without_proxy).apply_async(queue='scraping', routing_key='scraping', task_id=task_id)
        else:
            scrape_website.s(link, main_url=main_url, main_task_id=main_task_id, without_proxy=without_proxy, render_js=render_js).apply_async(queue='scraping', routing_key='scraping', task_id=task_id)

