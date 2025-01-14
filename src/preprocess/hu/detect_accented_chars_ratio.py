#!/usr/bin/python3

import os
from tqdm import tqdm
import src.common_functions as cf

# This code calculates the ratio of Hungarian accented characters for each article, and writes out those that meet a certain threshold

# Settings
MINIMUM_ACCENT_RATIO = 0.05
ACCENTED_CHARS = {'ö', 'ü', 'ó', 'ő', 'ú', 'é', 'á', 'ű', 'í', 'Ö', 'Ü', 'Ó', 'Ő', 'Ú', 'É', 'Á', 'Ű', 'Í'}


if __name__ == '__main__':

    # Load data
    in_path = 'data/raw/txt'
    out_path = 'data/interim/txt_accented'
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    data_dict = cf.load_folder_to_dict(path=in_path)

    # Calculate ratio and save files
    for filename, text in tqdm(data_dict.items()):
        words = text.split(' ')
        letters = []
        for word in words:
            for character in word:
                letters.append(character)
        number_of_accented_chars = 0
        for letter in letters:
            if letter in ACCENTED_CHARS:
                number_of_accented_chars += 1
        if number_of_accented_chars / len(letters) > MINIMUM_ACCENT_RATIO:
            with open(os.path.join(out_path, filename), 'w', encoding='utf-8') as outfile:
                outfile.write(text.strip())
