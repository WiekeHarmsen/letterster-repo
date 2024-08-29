"""
This is a script to convert pdf exports of spelling tests from the Letterster software to xlsx/csv/tsv files.

Run:
python3 convert-pdf-to-csv.py --data_dir /vol/bigdata3/datasets3/dutch_child_audio/letterster/spelling/letterster_dictations

INPUT
--data_dir is a directory containing one folder: 01_pdf (this folder contains the pdfs that have to be converted)

OUTPUT
02_dictations
03_error_categories
task-level-results.[tsv/csv/xlsx]

"""

import pandas as pd
import glob
import os
from datetime import datetime
import numpy as np
from PyPDF2 import PdfReader
import argparse

def parseDictationString(item):
    target = item.split(' ', 1)[0]
    correct = item.split(' ', -1)[-1]
    realized = item[len(target):len(item)-len(correct)]
    return [x.strip() for x in [target, realized, correct]]

def parseErrorCategoryString(item):
    error_cat_rank = item.split(' ')[0]
    error_cat_nr = item.split(' ')[1]
    error_cat_description = item.split(' ', 2)[-1]
    return [x.strip() for x in [error_cat_rank, error_cat_nr, error_cat_description]]

def parseTxt(data):

    # Meta data
    date_exported = data[0]
    link = data[1].replace(' 1/2Letterster toetsresultaten', '')
    day_administration = data[2].split(', ')[0].replace(' ', '-')
    time_administration = data[2].split(', ')[1]
    attempts = data[3].replace('Aantal hervattingen: ', '')
    duration = data[4].replace('Verstreken tijd: ', '')

    # Dictation data
    pages = [parseDictationString(data[idx]) for idx in np.arange(6, 59, 1)]
    dictationDF = pd.DataFrame(pages, columns = ['target', 'realized', 'correct'])
    
    # Error categories
    errorCategoryDF = pd.DataFrame([parseErrorCategoryString(data[idx]) for idx in np.arange(61, 61+12, 1)], columns = ['error_rank', 'error_cat_nr', 'error_cat_description'])

    # Metadata
    metadata = [date_exported, link, day_administration, time_administration, attempts, duration, len(dictationDF), len(dictationDF[dictationDF['correct'] == 'Goed']), len(dictationDF[dictationDF['correct'] == 'Fout'])]

    return dictationDF, errorCategoryDF, metadata, day_administration

def convert_pdf_to_txt(pdfFile):

    reader = PdfReader(pdfFile)

    page1 = reader.pages[0]
    txt_file_page1 = page1.extract_text().split('\n')

    page2 = reader.pages[1]
    txt_file_page2 = page2.extract_text().split('\n')[1:]
    txt_file_page2[0] = txt_file_page2[0].replace('https://app.lexipoort.nl/nl/#/products/letterster/students 2/2', '')

    return txt_file_page1 + txt_file_page2

def create_output_directories(dictation_dir, error_cat_dir):
    if not os.path.isdir(dictation_dir):
        os.makedirs(dictation_dir)

    if not os.path.isdir(error_cat_dir):
        os.makedirs(error_cat_dir)

def write_output_files(df, output_dir, filename):
    df.to_csv(os.path.join(output_dir, filename + '.tsv'), sep= '\t')
    df.to_csv(os.path.join(output_dir, filename + '.csv'))
    df.to_excel(os.path.join(output_dir, filename + '.xlsx'))

def run(args):

    # 1. Assign the inputs to variables
    dataDir = args.data_dir

    # 2. Get input pdfs and subdirectories from dataDir
    pdfDir = os.path.join(dataDir, '01_pdf')
    assert os.path.exists(pdfDir), 'Folder 01_pdf is not present in ' + dataDir

    # 3. PDF operations

    # 3a. List pdf files
    pdf_file_list = glob.glob(os.path.join(pdfDir, '*.pdf'))

    # 3b. Get basenames of pdf files
    basename_list = [os.path.basename(pdfFileName).replace('.pdf', '') for pdfFileName in pdf_file_list]

    # 3c. Convert the pdf files to txt files
    txt_file_list = [convert_pdf_to_txt(pdfFile) for pdfFile in pdf_file_list]

    # 4. Create output directories
    dictation_dir = os.path.join(dataDir, '02_dictations')
    error_cat_dir = os.path.join(dataDir, '03_error_categories')
    create_output_directories(dictation_dir, error_cat_dir)

    # 5. Parse each txt file and export the information
    metadataList = []
    for idx, txt_file in enumerate(txt_file_list):

        # Get author and testID from basename_list
        testID = basename_list[idx].split('-')[0]
        author = basename_list[idx].split('-')[1]

        dictationDF, errorCategoryDF, metadata, day_administration = parseTxt(txt_file)
        
        filename = author + '_' + testID + '_' + day_administration
        metadataList.append([filename, author, testID] + metadata)

        write_output_files(dictationDF, dictation_dir, filename)
        write_output_files(errorCategoryDF, error_cat_dir, filename)
    
    # Export the overarching information, providing an overview of all tests
    metadataDF = pd.DataFrame(metadataList, columns = ['filename', 'author', 'testID', 'date_exported(dd-mm-yy)', 'link', 'day_administration', 'time_administration(hh:mm)', 'attempts', 'duration(hh:mm:ss)', 'length_dication(nr_words)', 'correct(nr_words)', 'incorrect(nr_words)'])
    write_output_files(metadataDF, dataDir, 'task-level-results')

def main():
    parser = argparse.ArgumentParser("Message")
    parser.add_argument("--data_dir", type=str, help = "Data directory that contains at least one folder called 01_pdf with pdf files.")
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
