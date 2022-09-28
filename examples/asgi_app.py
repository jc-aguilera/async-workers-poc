import asyncio
import functools

import aiomysql
import uvicorn
from fastapi import FastAPI

from async_workers_poc.job_queue import pending_job_running_task, completed_job_running_task
from async_workers_poc.db_ops import retrieve_single_job_from_db, update_completed_job_on_db
from async_workers_poc.logger import get_logger
from async_workers_poc.models import Worker
from async_workers_poc.workers import worker_task, acknowledge_job
from async_workers_poc.do_work_callback_examples import complete_while_sleeping

_logger = get_logger(__name__)


def create_app():
    worker_tasks: list[asyncio.Task] = []
    pending_job_queue = asyncio.Queue()
    completed_job_queue = asyncio.Queue()
    queue_tasks: list[asyncio.Task] = []

    # For now, keep the db connection inside the ASGI app,
    # in case we need to reestablish it while the app is running,
    # possibly via health checks
    conn = None

    async def startup_handler():
        # Start workers
        worker_count = 1
        _logger.info(f'Starting {worker_count} workers')
        workers = [Worker(id=i+1) for i in range(worker_count)]
        for worker in workers:
            worker_tasks.append(asyncio.create_task(
                worker_task(worker,
                            pending_job_queue,
                            completed_job_queue,
                            complete_while_sleeping)))

        try:
            nonlocal conn
            conn = await aiomysql.connect(host='localhost',
                                          port=3306,
                                          user='root',
                                          password='',
                                          db='workers_test',
                                          autocommit=True
                                          )
        except aiomysql.OperationalError as e:
            _logger.error(f'Could not connect to database: {e}')
            raise e
        # Start pending queue
        _logger.info('Initializing pending queue task...')
        job_retriever = functools.partial(retrieve_single_job_from_db, conn=conn)
        queue_tasks.append(asyncio.create_task(
            pending_job_running_task(pending_job_queue,
                                     job_retriever,
                                     acknowledge_job
                                     )))

        # Start completed queue
        _logger.info('Initializing completed queue task...')
        completed_job_handler = functools.partial(update_completed_job_on_db, conn=conn)
        queue_tasks.append(asyncio.create_task(
            completed_job_running_task(completed_job_queue,
                                       completed_job_handler)))

    async def shutdown_handler():
        _logger.info(f'Shutting down {len(worker_tasks)} workers...')
        for t in worker_tasks:
            t.cancel()

        _logger.info('Shutting down queue tasks...')
        for q in queue_tasks:
            q.cancel()

        await asyncio.gather(*worker_tasks, *queue_tasks, return_exceptions=True)

    return FastAPI(on_startup=[startup_handler], on_shutdown=[shutdown_handler])


app = create_app()


@app.get("/health")
async def app_health():
    return {"status": "ok"}


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("examples.asgi_app:app", host="0.0.0.0", port=8050, reload=True)
