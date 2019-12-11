#!/usr/bin/python3

import textract
import re


class ExtractFromPdf:
    def __init__(self, path_to_file):
        lt_iso_code = 'iso-8859-4'
        encoded_text = textract
        self.text = encoded_text.decode(lt_iso_code)
        # self.text = self.text[:1000]
        self.alphabet = []
        # self.text = re.sub(r'\xad\s', '', self.text)
        # self.text = re.sub(r'\d', '', self.text)
        # self.text = self.text.strip()
        # self.text = self.text.lower()

    def get_words(self) -> str:
        return self.text

    def get_letters(self) -> list:
        return list(self.text)

    def get_length(self) -> int:
        return len(self.text)

    def get_word_dictionary(self, symbols=2) -> dict:
        words = self.get_words()
        dictionary = {}

        while words:
            word = words[0:symbols]
            word_count = words.count(word)
            words = words.replace(word, '')
            dictionary[word] = word_count

        self.alphabet = list(dictionary.keys())

        return dictionary

    def get_letter_dictionary(self) -> dict:
        letters = self.get_letters()
        dictionary = {}

        while letters:
            letter = letters[0]
            letter_count = letters.count(letter)
            letters = list(filter(lambda x: x != letter, letters))
            dictionary[letter] = letter_count

        self.alphabet = list(dictionary.keys())

        return dictionary

    def get_alphabet(self) -> list:
        return self.alphabet


def main():
    extractor = ExtractFromPdf('Neris.pdf')
    words = extractor.get_word_dictionary()
    # letters = extractor.get_letter_dictionary()
    # print(letters)
    print(words)


if __name__ == "__main__":
    main()
