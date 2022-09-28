import asyncio
import os

import aiomysql

from async_workers_poc.logger import get_logger
from async_workers_poc.models import Job


_logger = get_logger(__name__)


async def get_db_conn():
    return await aiomysql.connect(host=os.getenv('DB_HOST', 'localhost'),
                                  port=int(os.getenv('DB_PORT', '3306')),
                                  user=os.getenv('DB_USER', 'root'),
                                  password=os.getenv('DB_PASSWORD', ''),
                                  db=os.getenv('DB_NAME', 'test_db'),
                                  autocommit=True
                                  )


async def retrieve_single_job_from_db(conn, time_between_checks: int = 3) -> Job:
    cursor = await conn.cursor(aiomysql.cursors.DictCursor)

    job = None
    while job is None:
        _logger.info(f'Sleeping for {time_between_checks} seconds...')
        await asyncio.sleep(time_between_checks)

        get_job_query = "SELECT * FROM jobs WHERE status = 10 ORDER BY created_at LIMIT 1;"
        _logger.info('DB query: ' + get_job_query)
        await cursor.execute(get_job_query)

        db_job = await cursor.fetchone()
        if db_job is not None:
            _logger.info(f"Job found! Job id: {db_job['id']}")
            job = Job(id=db_job['id'], type=db_job['request_info'], status=db_job['status'])
            update_statement_query = f"UPDATE jobs SET status = 11 WHERE id = {db_job['id']};"
            _logger.info('DB query: ' + update_statement_query)
            await cursor.execute(update_statement_query)
        else:
            _logger.info('No job found')

    return job


async def update_completed_job_on_db(job: Job, conn):
    cursor = await conn.cursor(aiomysql.cursors.DictCursor)
    query = f"UPDATE jobs SET status = 1000 WHERE id = {job.id};"
    _logger.info('DB query: ' + query)
    await cursor.execute(query)
