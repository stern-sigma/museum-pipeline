"""Wrapper for running kafka pipeline from lms stream"""
from datetime import time

from museum_pipeline.kafka_pipeline import run_pipeline

START_TIME = time(hour=10, minute=45)
END_TIME = time(hour=16, minute=15)
MUSEUM = "lms"
if __name__ == "__main__":
    run_pipeline(MUSEUM, START_TIME, END_TIME)
