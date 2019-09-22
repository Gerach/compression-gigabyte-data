#!/usr/bin/python3

import os
import operator
import math


def calculate_entropy(probabilities):
    h = 0
    probability_freq = {}

    for letter in probabilities:
        probability = probabilities[letter]

        if probability in probability_freq:
            probability_freq[probability] += 1
        else:
            probability_freq[probability] = 1

    for probability in probability_freq:
        frequency = probability_freq[probability]
        logarithm = math.log(1 / probability, 2)
        partial_h = frequency * probability * logarithm
        h += partial_h

    return h


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

        return probabilities

    def get_probabilities_sorted(self):
        probabilities = self.get_probabilities()

        return sorted(probabilities.items(), key=operator.itemgetter(1))


def main():
    entropy = Entropy()
    entropy.fill_frequencies()
    probabilities = entropy.get_probabilities()
    print('Entropy without probability distribution: {}'.format(calculate_entropy(probabilities)))
    print('Entropy with probability distribution: {}'.format(math.log(len(entropy.alphabet), 2)))


if __name__ == "__main__":
    main()
