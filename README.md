# Global Scraper Concurrent

This project is a scalable, concurrent web scraping framework designed for large-scale data extraction from arbitrary websites. It leverages Celery for distributed task execution, Redis/RabbitMQ as a message broker, and supports both API and pipeline-based orchestration (Plombery, FastAPI). The system is containerized with Docker and orchestrated using Docker Compose for easy deployment.

## Features

- **Concurrent Scraping:** Uses Celery workers to scrape multiple websites or pages in parallel.  
  The system breaks down the scraping process into independent tasks, each responsible for fetching and processing a single web page or resource. These tasks are distributed to a pool of Celery worker processes, which can run on one or many machines. As new links are discovered during scraping (e.g., from `<a>` tags), additional tasks are dynamically created and queued. This allows the scraper to efficiently traverse and extract data from large websites or multiple domains at the same time, maximizing throughput and minimizing idle time. The concurrency level (number of parallel workers) can be configured in the Docker Compose file or Celery settings, enabling the system to scale horizontally as needed.

- **Proxy Support:** Integrates with ScrapeOps proxy for reliable and anonymous scraping.
- **JavaScript Rendering:** Optional JS rendering for dynamic websites.
- **Data Deduplication:** Avoids scraping the same URL multiple times.
- **Automatic File Management:** Scraped data is stored in CSV/Excel and zipped for download.
- **API & Pipeline:** Exposes scraping as a REST API (FastAPI) and as a Plombery pipeline for workflow automation.
- **Dockerized:** Ready for deployment with Docker and Docker Compose.
- **Logging:** Centralized logging for debugging and monitoring.

## Folder Structure

- `api.py` - Plombery pipeline API for orchestrating scraping jobs.
- `fast_api.py` - FastAPI server for RESTful scraping endpoints.
- `scraper.py` - Core scraping logic and Celery tasks.
- `services.py` - Utility functions for file management, deduplication, and API helpers.
- `setup.py` - Logging and proxy configuration.
- `celery_app.py` - Celery application setup.
- `credential.py` - API keys and proxy credentials (excluded from version control).
- `requirements.txt` - Python dependencies.
- `init.sh` - Entrypoint script for container startup.
- `Dockerfile` - Docker image definition.
- `docker-compose.yaml` - Multi-service orchestration (Celery, FastAPI, RabbitMQ).
- `.gitignore` - Ignore logs, data, and credentials.

## Quick Start

### 1. Clone the Repository

```bash
git clone <repo-url>
cd global_scraper_concurrent
```

### 2. Configure Credentials

- Create a `credential.py` file with your `SCRAPEOPS` and `API_KEY` values.
- Example:
  ```python
  SCRAPEOPS = "your_scrapeops_api_key"
  API_KEY = "your_custom_api_key"
  ```

### 3. Build and Start with Docker Compose

```bash
docker-compose up --build
```

- This will start RabbitMQ, Celery workers, and the FastAPI server on port 8000.

### 4. Usage

- **FastAPI:**  
  Access the API at [http://localhost:8000](http://localhost:8000)
- **Plombery Pipeline:**  
  The Plombery pipeline runs on port 9877 (if enabled).

- To trigger a scrape, POST to the API or use the Plombery UI.

### 5. Download Results

- Scraped data is stored in the `stored_data/` directory as zipped files.
- Download links are provided by the API after scraping is complete.

## Environment Variables

- `EXECUTION_TYPE`: Set to `celery`, `fast_api`, or `plombery` to control the container's startup mode.
- `CELERY_BROKER_URL`: Message broker URL (default set for RabbitMQ in docker-compose).

## Notes

- Make sure to set up your credentials in `credential.py`.
- The `data/` and `stored_data/` folders are managed automatically and ignored by git.
- For large-scale scraping, adjust concurrency in `docker-compose.yaml` and Celery settings.

## License

This project is for demonstration and internal use only.
