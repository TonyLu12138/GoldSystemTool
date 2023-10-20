#! /usr/bin/env python3
from tqdm import tqdm

class ProgressBar:
    def __init__(self, max):
        self.total_steps = max
        self.progress_bar = tqdm(total=max, dynamic_ncols=True)

    def update(self, step=1):
        self.progress_bar.update(step)

    def close(self):
        self.progress_bar.close()