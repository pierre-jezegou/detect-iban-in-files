import re
import os
import PyPDF2
from PIL import Image
import pytesseract

IBAN_REGEX = r'([A-Z]{2}\s?\d{2}\s?(?:\d{4}\s?){5}\d{1,4})'
IBAN_CLEANED_REGEX = r'([A-Z]{2}\d{2}(?:\d{4}){5}\d{1,4})'
TARGET_IBAN = 'FR7616706050875394140728132'


def get_file_type(file_name: str) -> str:
    '''Return file extension'''
    _, extension = os.path.splitext(file_name)
    return extension.lower()


def extract_text_pdf(pdf_path: str) -> str | None:
    '''Extract text from a pdf file'''
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            page_text = pdf_reader.getPage(page_num).extractText()
            text += page_text
        return text


def extract_text_image(image_path: str) -> str | None:
    '''Extract text from an image file'''
    text = pytesseract.image_to_string(Image.open(image_path))
    return text


def search_regex(text: str | None, regex_pattern: str) -> list[str] | None:
    '''Search regex_pattern in a given text'''
    if text is None:
        return None

    matches = re.findall(regex_pattern, text)
    return matches


def format_iban(iban_str: str, expected_format_regex: str) -> str:
    '''Format IBAN'''
    cleaned_iban = iban_str.replace(" ", "")
    if re.match(expected_format_regex, cleaned_iban):
        return cleaned_iban.upper()
    raise AssertionError('Iban bad format')


def detect_target_iban(filename: str,
                       target_iban: str,
                       iban_raw_regex: str = IBAN_REGEX,
                       iban_cleaned_regex: str = IBAN_CLEANED_REGEX
                       )-> dict:
    '''Main function : detect IBAN in filename file

        Accepted extensions :
            - `pdf`
            - images : `png`, `jpg`, `jpeg`
    '''
    returned_dic = {
        "iban_presence": False
    }

    formatted_matches = set()
    extension = get_file_type(filename)

    if extension == '.pdf':
        text = extract_text_pdf(filename)
    elif extension in ['.png', '.jpg', '.jpeg']:
        text = extract_text_image(filename)
    else:
        raise TypeError('Format non connu')

    matches = search_regex(text, iban_raw_regex)

    if matches is None:
        return returned_dic
    for match in matches:
        formatted_match = format_iban(match, iban_cleaned_regex)
        formatted_matches.add(formatted_match)
    if target_iban in formatted_matches:
        returned_dic["iban_presence"] = True
    return returned_dic

FILENAMES = [
                'files/fichier1.pdf',
                'files/fichier2.jpeg',
                'files/fichier3.pdf',
                'files/ecl.pdf'
            ]

if __name__=="__main__":
    for file in FILENAMES:
        print(detect_target_iban(file, TARGET_IBAN))
