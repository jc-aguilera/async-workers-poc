import asyncio
import random
from collections.abc import Callable, Coroutine

from async_workers_poc.logger import get_logger
from async_workers_poc.models import Job, Worker


_logger = get_logger(__name__)


def _random_seconds(max_seconds: int = 5):
    return random.random() * max_seconds


async def acknowledge_job(job: Job, pending_job_queue: asyncio.Queue[Job]):
    _logger.info(f'Job {job} has been acknowledged.')


async def mark_as_complete(job: Job,
                           completed_job_queue: asyncio.Queue[Job]):
    _logger.info(f'Job {job} is about to be marked as finished.')
    job.status = "finished"
    asyncio.create_task(completed_job_queue.put(job))
    _logger.info(f'Job {job} has been completed.')


async def worker_task(worker: Worker,
                      pending_job_queue: asyncio.Queue[Job],
                      completed_job_queue: asyncio.Queue[Job],
                      do_work_handler: Callable[[Job, Worker], Coroutine[bool]]
                      ):
    while True:
        job = await pending_job_queue.get()
        _logger.info(f"Worker {worker} is about to start working on job {job}")
        await do_work_handler(job, worker)
        pending_job_queue.task_done()
        asyncio.create_task(mark_as_complete(job, completed_job_queue))
