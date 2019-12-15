#!/usr/bin/python3

import random

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

    def get_random_word(self, whatever):
        return random.choices(self.words, self.weights)[0]

    def generateFile(self, filename, size=1):
        """
        Size given in megabytes
        """
        size_bytes = size * 1024 * 1024
        text = ''
        pool = Pool(2)
        while len(text) * 8 < size_bytes:
            text += ' '.join(pool.map(self.get_random_word, range(2048)))

        with open(filename, 'w', encoding='utf8') as wf:
            wf.write(text)


def main():
    generator = HugeFileGenerator()
    generator.generateFile('random.txt', 1024)


if __name__ == "__main__":
    main()
