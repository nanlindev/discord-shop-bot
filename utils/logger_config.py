import sys
import os
from loguru import logger
os.makedirs('logs', exist_ok = True)
logger.remove()
logger.add(sys.stderr, level = 'DEBUG', colorize = True)
logger.add(
    'logs/app_{time:YYYY-MM-DD}.log',
    rotation = '00:00',
    retention =  '7 days',
    level = 'DEBUG',
    encoding = 'utf-8',
    enqueue = True
)