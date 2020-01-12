#!/usr/bin/python3

import textract


class ExtractFromPdf:
    def __init__(self, path_to_file):
        lt_iso_code = 'iso-8859-4'
        encoded_text = textract.process(path_to_file, lt_iso_code)
        self.text = encoded_text.decode(lt_iso_code)

    def get_words(self) -> str:
        return self.text

    def get_letters(self) -> list:
        return list(self.text)

    def get_length(self) -> int:
        return len(self.text)


def main():
    extractor = ExtractFromPdf('Neris.pdf')
    with open('extracted.txt', 'w') as wf:
        wf.write(extractor.get_words())


if __name__ == "__main__":
    main()
