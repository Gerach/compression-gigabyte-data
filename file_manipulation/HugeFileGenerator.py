#!/usr/bin/python3

import random
import time

from multiprocessing import Pool


class HugeFileGenerator:
    def __init__(self):
        self.words = []
        self.weights = []

        with open('words.csv', 'r', encoding='utf8') as rf:
            lines = rf.readlines()

        total_freq = 0
        for line in lines:
            word, freq = line.split(',')
            total_freq += int(freq)

        for line in lines:
            word, freq = line.split(',')
            self.words.append(str.strip(word, '"'))
            self.weights.append(int(freq) / total_freq)

    def get_random_word(self, _):
        random_separator = random.randint(1, 1000)
        if random_separator < 5:
            return random.choices(self.words, self.weights)[0] + '.\n'\
                   + random.choices(self.words, self.weights)[0].capitalize()
        elif random_separator < 100:
            return random.choices(self.words, self.weights)[0] + '. '\
                   + random.choices(self.words, self.weights)[0].capitalize()
        else:
            return random.choices(self.words, self.weights)[0] + ' '

    def generate_file(self, filename, size=1.0):
        """
        Size given in megabytes
        """
        size_bytes = size * 1024 * 1024
        text = ''
        pool = Pool(2)
        start_time = time.time()
        while len(text) < size_bytes:
            text += ''.join(pool.map(self.get_random_word, range(2048)))

        with open(filename, 'w', encoding='utf8') as wf:
            wf.write(text)

        print(time.time() - start_time)


def main():
    generator = HugeFileGenerator()
    file_name = input('Input file name: ')
    if not file_name:
        raise Exception('File name not given')
    file_size = float(input('Input file size in megabytes: '))
    generator.generate_file(file_name, file_size)


if __name__ == "__main__":
    main()
