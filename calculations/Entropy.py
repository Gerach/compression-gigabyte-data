#!/usr/bin/python3

import os
import operator


class Entropy:

    alphabet = ['a', 'ą', 'b', 'c', 'č', 'd', 'e', 'ę', 'ė', 'f', 'g', 'h', 'i', 'į', 'y', 'j', 'k', 'l', 'm', 'n', 'o',
                'p', 'r', 's', 'š', 't', 'u', 'ų', 'ū', 'v', 'z', 'ž']

    def __init__(self):
        self.total_letters = 0
        self.frequencies = {}

        for letter in self.alphabet:
            self.frequencies[letter] = 0

        self_full_path = os.path.realpath(__file__)
        self_dir = os.path.dirname(self_full_path)
        words_path = self_dir + '/../words.csv'

        with open(words_path, 'r') as words_file:
            self.data = words_file.readlines()

    def calculate_word(self, word, frequency):
        for letter in word:
            if letter in self.frequencies:
                self.frequencies[letter] += frequency

    def fill_frequencies(self):
        for datum in self.data:
            word, frequency = datum.split(',')[0], datum.split(',')[1]
            word = word.strip('"')
            frequency = int(frequency.strip())

            self.total_letters += len(word) * frequency
            self.calculate_word(word, frequency)

    def get_probabilities(self):
        probabilities = {}

        for letter in self.alphabet:
            probabilities[letter] = round(self.frequencies[letter] / self.total_letters, 3)

        return sorted(probabilities.items(), key=operator.itemgetter(1))


def main():
    entropy = Entropy()
    entropy.fill_frequencies()
    print(entropy.get_probabilities())


if __name__ == "__main__":
    main()
