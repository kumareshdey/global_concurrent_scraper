from celery import Celery
from celery.utils.log import get_task_logger
from celery.exceptions import Retry
import os 

broker_url = os.getenv('CELERY_BROKER_URL', 'pyamqp://guest@localhost//')
app = Celery('scraper',
             broker=broker_url,
             include=['scraper'])

# Optional configuration settings
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

app.conf.task_retry_parameters = {'max_retries': 3}
