import uvicorn 
from loguru import logger 
from apscheduler.triggers.cron import CronTrigger 
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler 

from create_charts import plot_all 
from scrape_data import scrape_all
from publish_github import publish

def build_dashboard(): 
    scrape_all()
    plot_all()
    publish()


### scheduler process 
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Start scheduler')
    scheduler.start()
    yield
    logger.info('stop scheduler')
    scheduler.shutdown()

### scheduling server 
app = FastAPI(lifespan=lifespan)
scheduler = BackgroundScheduler()

@app.get('/')
def index():
    return 'running'

trigger = CronTrigger(hour = 0, minute = 0)
scheduler.add_job(build_dashboard, trigger=trigger)

if __name__ == "__main__": 
    # build_dashboard()
    uvicorn.run(app, host = "0.0.0.0", port = 8200)
