import time
from multiprocessing import Pool
from collections import Counter

CHUNK_SIZE = 1024
CHUNK_MIN_SIZE = 1024 - 7


class Profiler(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time - {}: {:.3f} sec".format(self.name, time.time() - self._startTime))


class Chunk:
    @classmethod
    def split(cls, file_name):
        with open(file_name, 'rb') as f:
            chunk_end = f.tell()
            delta = 0
            while True:
                chunk_start = chunk_end
                delta = cls._EOC(f, delta)
                chunk_end = f.tell() - delta
                yield chunk_start, chunk_end
                if delta > 6:
                    break

    @staticmethod
    def _EOC(f, delta):
        f.read(CHUNK_MIN_SIZE - delta)
        chunk_tail = f.read(7)
        return 6 - chunk_tail.rfind(b'/')  # число символов лишнего считывания

    @staticmethod
    def read(a, d, g):
        g.seek(a)
        return g.read(d-a)

    @staticmethod
    def parse(chunk_string):
        d = dict(Counter(chunk_string.split('/')))
        d.pop('', None)
        return d


def gen_default_dict():
    d = {}
    for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        d[i] = {}
        for j in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            d[i][j] = {}
            for k in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                d[i][j][k] = {}
    return d


def worker_map(args):
    with open('lr1.txt', 'r') as g:
        return Chunk.parse(Chunk.read(*args, g))


if __name__ == '__main__':
    with Profiler('lr1') as p:
        with Pool(processes=4) as pool:
            workers = []
            d = gen_default_dict()
            for d2 in pool.imap_unordered(worker_map, Chunk.split('lr1.txt')):
                for key, value in d2.items():
                    if d[key[0]][key[1]][key[2]].get(key):
                        d[key[0]][key[1]][key[2]][key] += value
                    else:
                        d[key[0]][key[1]][key[2]][key] = value
            with open('lr1_result.txt', 'w') as q:
                q.write(str(d))
