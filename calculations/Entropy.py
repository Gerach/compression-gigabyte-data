#!/usr/bin/python3

import math
import operator

from ExtractFromPdf import ExtractFromPdf


class Entropy:

    def __init__(self, frequencies, words):
        self.total_letters = 0
        self.frequencies = {}
        self.frequencies = frequencies
        self.words = words
        self.total_letters = 0

        for word in frequencies:
            self.total_letters += frequencies[word]

    def get_probabilities(self) -> dict:
        probabilities = {}

        for word in self.words:
            probabilities[word] = self.frequencies[word] / self.total_letters

        return probabilities

    def get_probabilities_sorted(self) -> list:
        probabilities = self.get_probabilities()

        return sorted(probabilities.items(), key=operator.itemgetter(1))

    @staticmethod
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


def main():
    extractor = ExtractFromPdf('Neris.pdf')
    dictionary = extractor.get_letter_dictionary()
    alphabet = extractor.get_alphabet()

    entropy = Entropy(dictionary, alphabet)
    probabilities = entropy.get_probabilities()
    # print(probabilities)
    print('Entropy with probability distribution: {}'.format(entropy.calculate_entropy(probabilities)))
    print('Entropy without probability distribution: {}'.format(math.log(len(alphabet), 2)))


if __name__ == "__main__":
    main()
