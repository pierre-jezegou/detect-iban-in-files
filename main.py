import re
import os
import PyPDF2
from PIL import Image
import pytesseract

IBAN_REGEX = r'([A-Z]{2}\s?\d{2}\s?(?:\d{4}\s?){5}\d{1,4})'
IBAN_CLEANED_REGEX = r'([A-Z]{2}\d{2}(?:\d{4}){5}\d{1,4})'
TARGET_IBAN = 'FR7616706050875394140728132'


# EXTRACT TEXT FROM FILES

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


def get_file_type(file_name: str) -> str:
    '''Return file extension'''
    _, extension = os.path.splitext(file_name)
    return extension.lower()



# IBAN RELATED FUNCTIONS

def format_iban(iban_str: str, expected_format_regex: str) -> str:
    '''Format IBAN'''
    cleaned_iban = re.sub(r'\s+', '', iban_str)
    if re.match(expected_format_regex, cleaned_iban):
        return cleaned_iban.upper()
    raise AssertionError('Iban bad format')


def detect_target_iban(text: str,
                       target_iban: str,
                       iban_raw_regex: str = IBAN_REGEX,
                       iban_cleaned_regex: str = IBAN_CLEANED_REGEX
                       )-> dict:
    '''Detect IBAN in a given text'''
    target_iban_present = False

    matches = search_regex(text, iban_raw_regex)
    formatted_matches = set()

    if matches == []:
        return False

    for match in matches:
        formatted_match = format_iban(match, iban_cleaned_regex)
        formatted_matches.add(formatted_match)
    if target_iban in formatted_matches:
        target_iban_present = True

    return target_iban_present



# DATE EXTRACTION

def detect_date(text: str) -> list[str] | None:
    '''Detect date in a given text'''
    regex = r'\d{1,2}\/\d{1,2}\/\d{2,4}'
    scraped_dates = set()
    matches = search_regex(text, regex)

    # TODO Cas où matches = None ?

    for match in matches:
        formatted_match = format_date(match)
        scraped_dates.add(formatted_match)

    return list(scraped_dates)

def format_date(date_str: str) -> str:
    '''Format date'''
    return date_str


# AMOUNT EXTRACTION

def detect_amount(text: str) -> list[float] | None:
    '''Detect date in a given text'''
    regex = r'\d{1,3}(?:\s?\d{3})*(?:,\d{1,2})?\s?€'
    scraped_values = set()
    matches = search_regex(text, regex)

    # TODO : traiter les cas où 8 EUR et €8

    # TODO Cas où matches = None ?

    for match in matches:
        formatted_match = format_amount(match)
        scraped_values.add(formatted_match)

    return list(scraped_values)

def format_amount(amount_str: str) -> float:
    '''Extract float value of currency amount given in argument'''
    extraction_regex = r'(\d+(?:\s?\d{3})*(?:,\d{1,2})?)'
    value_extraction = search_regex(amount_str, extraction_regex)

    if value_extraction == []:
        raise AssertionError('Impossible to extract amount')

    amount_without_currency_symbol = value_extraction[0].replace(",", ".")

    amount = float(amount_without_currency_symbol)

    return amount



# MAIN FUNCTION

def extract_gather_information(filename: str,
                               iban_target: str,
                               date_needed: bool = True,
                               amount_needed: bool= True
                               ) -> dict:
    '''MAIN FUNCTION :
        Detect informations from a file
        Accepted extensions :
            - `pdf`
            - images : `png`, `jpg`, `jpeg`
    '''

    returned_dict = {}
    extension = get_file_type(filename)

    # Extract informations from documents
    if extension == '.pdf':
        text = extract_text_pdf(filename)
    elif extension in ['.png', '.jpg', '.jpeg']:
        text = extract_text_image(filename)
    else:
        raise TypeError('Unknown file format')

    # Get target IBAN presence in extracted text
    target_present = detect_target_iban(text, iban_target)
    returned_dict.update({"target_iban_present": target_present})

    if date_needed:
        extracted_dates = detect_date(text)
        returned_dict.update({"detected_dates": extracted_dates})

    if amount_needed:
        extracted_amounts = detect_amount(text)
        returned_dict.update({"detected_amounts": extracted_amounts})

    return returned_dict


FILENAMES = [
                'files/fichier1.pdf',
                'files/fichier2.jpeg',
                'files/fichier3.pdf',
                'files/fichier4.jpg',
                'files/fichier5.png',
                'files/fichier6.png',
                'files/test.jpeg'
            ]

if __name__=="__main__":
    for file in FILENAMES:
        print(extract_gather_information(file, TARGET_IBAN))
