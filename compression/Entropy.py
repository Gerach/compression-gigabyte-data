#!/usr/bin/python3

import math
import operator


class Entropy:

    def __init__(self, data):
        self.total_letters = 0
        self.frequencies, self.alphabet = self.get_letter_dictionary(data)
        self.total_letters = 0

        for word in self.frequencies:
            self.total_letters += self.frequencies[word]

    def get_probabilities(self) -> dict:
        print('Getting letter probabilities')
        probabilities = {}

        for word in self.alphabet:
            probabilities[word] = self.frequencies[word] / self.total_letters

        return probabilities

    def get_probabilities_sorted(self) -> list:
        probabilities = self.get_probabilities()

        return sorted(probabilities.items(), key=operator.itemgetter(1))

    @staticmethod
    def get_letter_dictionary(data):
        letters = list(data)
        dictionary = {}

        while letters:
            letter = letters[0]
            letter_count = letters.count(letter)
            letters = list(filter(lambda x: x != letter, letters))
            dictionary[letter] = letter_count

        alphabet = list(dictionary.keys())

        return dictionary, alphabet

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
    with open('extracted.txt', 'r') as rf:
        text = rf.read()

    entropy = Entropy(text)
    probabilities = entropy.get_probabilities()
    sorted_probabilities = entropy.get_probabilities_sorted()
    for probability in sorted_probabilities:
        print('{}&{}'.format(probability[0], round(probability[1] * 100, 4)))
    print('Entropy with probability distribution: {}'.format(entropy.calculate_entropy(probabilities)))
    print('Entropy without probability distribution: {}'.format(math.log(len(entropy.alphabet), 2)))


if __name__ == "__main__":
    main()
