import logging

def create_logger():
    logger = logging.getLogger('consumer_logger')
    logger.setLevel(logging.INFO)

    logger.setLevel(logging.INFO)

    consumer_file_handler = logging.FileHandler('./logs/consumer.log')
    consumer_file_handler.setLevel(logging.INFO)

    consumer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    consumer_file_handler.setFormatter(consumer_formatter)

    logger.addHandler(consumer_file_handler)

    logger.propagate = False

    logger.info("consumer logger initialized.")

    return logger
