import time
import random
import os
from multiprocessing import Pool

file_size = 8 * 1024 * 1024 * 1024


class Profiler(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time - {}: {:.3f} sec".format(self.name, time.time() - self._startTime))


def worker(_):
    a = ''
    for _ in range(100_000):
        a += ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                      for _ in range(random.choice([3, 4, 5, 6]))] + ['/'])
    return a


if __name__ == '__main__':
    with Profiler('good') as p:
        with open('lr1.txt', 'a') as f:
            with Pool(processes=4) as pool:
                while True:
                    for result in pool.imap_unordered(worker, range(1_000)):
                        f.write(result)
                        if os.path.getsize('lr1.txt') >= file_size:
                            break
                    if os.path.getsize('lr1.txt') >= file_size:
                        break



