"""Wrapper for running the kafka_pipeline from lmnh data stream"""
from datetime import time

from museum_pipeline.kafka_pipeline import run_pipeline

MUSEUM = "lmnh"
START_TIME = time(hour=8, minute=45)
END_TIME = time(hour=18, minute=15)

if __name__ == "__main__":
    run_pipeline(MUSEUM, START_TIME, END_TIME)
