import os
from enum import Enum, auto
import logging

EXTERNAL_DIR = os.path.dirname(os.path.abspath(__file__))

def create_logger(log_file:str,
                  log_dir:str='log',
                  formatter_str:str='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                  logger_level:any=logging.DEBUG,
                  console_level:any=logging.DEBUG,
                  file_level:any=logging.DEBUG
                 )->logging.Logger:

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(__name__)
    logger.setLevel(logger_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file), encoding='utf-8')
    file_handler.setLevel(file_level)
    formatter = logging.Formatter(formatter_str)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def recvall(socket: any, max_msg_size: int = 4028) -> bytes:
    buffer = b''

    while True:
        part = socket.recv(max_msg_size)
        buffer += part

        if b'\r\n' in buffer or not part:
            break
    
    return buffer

def compress_grid(grid: list[float, float]) -> list[float, float]:
    compressed = []
    for row in grid:
        if not row:
            continue
        count = 1
        current_value = row[0]
        for value in row[1:]:
            if value == current_value:
                count += 1
            else:
                compressed.append((count, current_value))
                count = 1
                current_value = value
        compressed.append((count, current_value))
    return compressed

def decompress_grid(compressed: list[float, float], width: int) -> list[float, float]:
    decompressed = []
    row = []
    for count, value in compressed:
        row.extend([value] * count)
        while len(row) >= width:
            decompressed.append(row[:width])
            row = row[width:]
    return decompressed

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