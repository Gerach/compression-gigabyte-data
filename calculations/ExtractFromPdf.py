#!/usr/bin/python3

import textract
import re


class ExtractFromPdf:
    def __init__(self, path_to_file):
        lt_iso_code = 'iso-8859-4'
        encoded_text = textract.process(path_to_file, lt_iso_code)
        self.text = encoded_text.decode(lt_iso_code)
        # self.text = re.sub(r'\xad\s', '', self.text)
        # self.text = re.sub(r'\d', '', self.text)
        # self.text = self.text.strip()
        # self.text = self.text.lower()

    def get_words(self) -> list:
        return self.text.split()

    def get_letters(self) -> list:
        return list(self.text)

    def get_word_dictionary(self) -> dict:
        words = self.get_words()
        dictionary = {}

        while words:
            word = words[0]
            word_count = words.count(word)
            words = list(filter(lambda x: x != word, words))
            dictionary[word] = word_count

        return dictionary

    def get_letter_dictionary(self) -> dict:
        letters = self.get_letters()
        dictionary = {}

        while letters:
            letter = letters[0]
            letter_count = letters.count(letter)
            letters = list(filter(lambda x: x != letter, letters))
            dictionary[letter] = letter_count

        return dictionary

    def get_alphabet(self) -> list:
        letters = self.get_letters()
        alphabet = []

        while letters:
            alphabet.append(letters[0])
            letters = list(filter(lambda x: x != letters[0], letters))

        return alphabet


def main():
    extractor = ExtractFromPdf('Neris.pdf')
    letters = extractor.get_letter_dictionary()
    print(letters)


if __name__ == "__main__":
    main()
