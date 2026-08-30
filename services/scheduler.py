# -*- coding: utf-8 -*-
"""Local scheduler: run the whole pipeline nightly and serve a liveness probe.

    python scheduler.py

Was `main.py`. Note that this has to stay running on one PC, which is why the
workspace TASKS.md carries the question of moving it to a GitHub Actions cron --
the manual data drops are what make that hard.
"""

import uvicorn 
from loguru import logger 
from apscheduler.triggers.cron import CronTrigger 
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler 

from pipeline import main as build_charts
from scrape import scrape_all
from publish import publish

def build_dashboard(): 
    try:
        logger.info("Starting dashboard build...")
        scrape_all()
        # pipeline.main, not pipeline.build: build() only registers charts.
        # Writing the manifest and pruning stale data files happen around it,
        # and without them the frontend reads a manifest that predates the run.
        build_charts()
        publish()
        logger.info("Dashboard build completed.")
    except Exception as e:
        logger.exception("Dashboard build failed!")


### scheduler process 
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler(timezone="Europe/Vienna")
    
    trigger = CronTrigger(hour=0, minute=1, timezone="Europe/Vienna")
    scheduler.add_job(
        build_dashboard,
        trigger=trigger,
        misfire_grace_time=3600,   # allow 1 hour delay
        coalesce=True,
        max_instances=1
    )

    scheduler.start()
    logger.info("Scheduler started")

    try:
        yield
    finally:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

### scheduling server 
app = FastAPI(lifespan=lifespan)

@app.get('/')
def index():
    return 'running'

if __name__ == "__main__": 
    build_dashboard()
    logger.info("Started automatic build process.")
    uvicorn.run(app, host = "0.0.0.0", port = 8200)
