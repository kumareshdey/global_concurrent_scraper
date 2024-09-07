import csv
import os
import shutil
import time
import zipfile
from plombery import task, get_logger, Trigger, register_pipeline
import fastapi
import uuid

import redis
from celery_app import app
import pandas as pd
from celery.result import AsyncResult
from pydantic import BaseModel

class InputParams(BaseModel):
    url: str
    without_proxy: bool = False
    render_js: bool = True

def zip_and_store_folder(zip_name: str) -> str:
    folder_path = 'data'
    # Ensure the 'stored_data' directory exists
    stored_data_dir = 'stored_data'
    os.makedirs(stored_data_dir, exist_ok=True)
    
    # Create the zip file
    zip_path = os.path.join(stored_data_dir, f"{zip_name}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))

    # Remove the original folder
    shutil.rmtree(folder_path)
    
    return zip_path

def check_task_completed(main_task_id, log):
    while True:
        time.sleep(5)
        active_tasks = app.control.inspect().active() or {}
        scheduled_tasks = app.control.inspect().scheduled() or {}
        reserved_tasks = app.control.inspect().reserved() or {}

        active_task_ids = [task['id'] for worker in active_tasks.values() for task in worker]
        scheduled_task_ids = [task['id'] for worker in scheduled_tasks.values() for task in worker]
        reserved_task_ids = [task['id'] for worker in reserved_tasks.values() for task in worker]

        all_task_ids = active_task_ids + scheduled_task_ids + reserved_task_ids
        pending_tasks_count = sum(1 for task_id in all_task_ids if task_id.startswith(main_task_id))
        if pending_tasks_count==0:
            return True
        log.info(f'Task {main_task_id} is not complete. {pending_tasks_count} pending tasks left.')
        log.info(f"{get_row_count()} has been scraped so far.")
        time.sleep(5)

def get_row_count():
    if os.path.isfile('data/scraped_url.txt'):
        with open('data/scraped_url.txt', 'r', encoding='utf-8') as file:
            return len([row.strip() for row in file.readlines()])
    return 0

def write_results_to_excel(results, log):
    data_folder = 'data'
    os.makedirs(data_folder, exist_ok=True)
    df = pd.DataFrame(results)
    df.to_excel('data/scraped_data.xlsx', index=False)
    log.debug(f'Wrote {len(results)} results to data/scraped_data.xlsx')

def start_scraper(params):
    from scraper import scrape_website, log
    import uuid
    main_task_id = str(uuid.uuid4())
    log = get_logger()
    url = params.url
    log.info(f'Starting scraper for {url}')
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('stored_data'):
        os.mkdir('stored_data')
    scrape_website.s(url, main_url=url, main_task_id=main_task_id, render_js=params.render_js, without_proxy=params.without_proxy).apply_async(task_id=main_task_id, queue='scraping', routing_key='scraping')

    log.info(f'Sent scrape_website task for {url}')
    if check_task_completed(main_task_id, log):
        log.info(f'Finished scraping {url}')
        zip_and_store_folder(main_task_id)
        log.info(f"File is ready to download. Id is {main_task_id}")
    else:
        log.warning(f'Scraping of {url} is not completed yet.')
    return main_task_id


@task
def start_scraper_task(params):
    start_scraper(params)

register_pipeline(
    id="global_scraper",
    params=InputParams,
    description="Global scraper to scrape any website",
    tasks = [start_scraper_task],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("plombery:get_app", reload=True, factory=True, port=9877, host='0.0.0.0')
