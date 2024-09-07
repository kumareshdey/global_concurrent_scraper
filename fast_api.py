import os
from typing import Optional
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel

from services import create_zip, start_scraper, log, verify_api_key

app = FastAPI()

class InputParams(BaseModel):
    url: str
    without_proxy: bool = False
    render_js: bool = True


@app.get("/scrape", dependencies=[Depends(verify_api_key)])
async def scrape(
    url: str = Query(..., description="The URL to scrape"),
    without_proxy: Optional[bool] = Query(False, description="Whether to use a proxy"),
    render_js: Optional[bool] = Query(False, description="Whether to render JavaScript")
):
    params = InputParams(url=url, without_proxy=without_proxy, render_js=render_js)
    main_task_id = start_scraper(params)
    if main_task_id is None:
        return {"message": "Scraping process is not completed yet. Please try again later."}
    file_path = os.path.join('stored_data', f"{main_task_id}.zip")
    return await create_zip(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
