import asyncio

from async_workers_poc.logger import get_logger
from async_workers_poc.models import Job, Worker
from async_workers_poc.workers import _random_seconds


_logger = get_logger(__name__)


async def complete_while_sleeping(job: Job, worker: Worker) -> bool:
    job.status = "working"  # This status is mostly for internal use, e.g.: tracebacks

    _logger.info(f"Worker {worker} is now working on job {job}...")

    # The actual work is done here.
    # Since this is just an example, we're sleeping for a random amount of seconds, simulating work
    await asyncio.sleep(_random_seconds())
    job.status = "just completed"

    _logger.info(f"Worker {worker} has just completed job {job}.")
    return True
