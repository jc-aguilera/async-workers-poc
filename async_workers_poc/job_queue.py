import asyncio
from collections.abc import Callable, Coroutine

from async_workers_poc.logger import get_logger
from async_workers_poc.models import Job


_logger = get_logger(__name__)


async def pending_job_running_task(pending_job_queue: asyncio.Queue[Job],
                                   job_retriever: Callable[[], Coroutine[Job]],
                                   job_acknowledgement_handler: Callable[[Job, asyncio.Queue[Job]], Coroutine]
                                   ):
    while True:
        pending_job = await job_retriever()
        await pending_job_queue.put(pending_job)
        _logger.info(f'Job {pending_job} has been put into the pending queue.')
        asyncio.create_task(job_acknowledgement_handler(pending_job, pending_job_queue))


async def completed_job_running_task(completed_job_queue: asyncio.Queue[Job],
                                     completed_job_handler: Callable[[Job], Coroutine]
                                     ):
    while True:
        completed_job = await completed_job_queue.get()
        _logger.info(f'Running post-completion tasks on job {completed_job}')
        await completed_job_handler(completed_job)
        completed_job_queue.task_done()
