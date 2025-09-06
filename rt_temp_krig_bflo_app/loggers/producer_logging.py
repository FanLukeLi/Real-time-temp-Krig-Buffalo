import logging

def create_logger():
    logger = logging.getLogger('producer_logger')
    logger.setLevel(logging.INFO)

    logger.setLevel(logging.INFO)

    producer_file_handler = logging.FileHandler('./logs/producer.log')
    producer_file_handler.setLevel(logging.INFO)

    producer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    producer_file_handler.setFormatter(producer_formatter)

    logger.addHandler(producer_file_handler)

    logger.propagate = False

    logger.info("Producer logger initialized.")

    return logger
