import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f'logs/{name}.log', 'w')

    logging_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(logging_formatter)
    file_handler.setFormatter(logging_formatter)
    logger.addHandler(stream_handler)
    # logger.addHandler(file_handler)
    return logger
