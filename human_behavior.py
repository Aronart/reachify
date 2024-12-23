import time
import random


class HumanBehavior:
    @staticmethod
    def sleep(min_seconds=1, max_seconds=4):
        # Wait for a random duration between 2 and max_seconds
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)
        print(f"Slept for {sleep_time:.2f} seconds")
