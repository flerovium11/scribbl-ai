import os
from enum import Enum, auto
import logging

EXTERNAL_DIR = os.path.dirname(os.path.abspath(__file__))

def create_logger(log_file:str, log_dir:str='log', formatter_str:str='%(asctime)s - %(levelname)s - %(message)s')->logging.Logger:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file), encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(formatter_str)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

class LobbyState(Enum):
    WAITING = auto()
    READY = auto()
    CHOOSE_WORD = auto()
    GAME = auto()
    RESULTS = auto()
    STOPPED = auto()
    DISCONNECTED = auto()

class PlayerRole(Enum):
    GUESSER = auto()
    DRAWER = auto()