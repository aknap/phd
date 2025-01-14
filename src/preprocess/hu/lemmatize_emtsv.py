#!/usr/bin/python3

import requests
import os
from tqdm import tqdm
import src.common_functions as cf


# A running 'emtsv' Docker container is required to run this code
# Get it here: https://hub.docker.com/r/mtaril/emtsv
EMAGYAR_ENDPOINT = 'http://127.0.0.1:5000/tok/morph/pos'

# Source of POS tags: https://e-magyar.hu/en/textmodules/emmorph_codelist
ALLOWED_POSTAGS = {'adjective': '[/Adj]', 'adjective_ext': '[/Adj|',
                   'adverb': '[/Adv]', 'adverb_ext': '[/Adv|',
                   'noun': '[/N]', 'noun_ext': '[/N|',
                   'num': '[/Num]', 'num_ext': '[/Num|',
                   'verb': '[/V]'}


def lemmatize_and_filter(txt: str) -> list:
    """
    Tokenize text and create sentences
    :param txt: text to be lemmatized
    :return:
        lemma_list: list, where an item is a lemmatized token from 'text'
    """
    r = requests.post(EMAGYAR_ENDPOINT, data={'text': txt})
    lemma_list = []
    for line in r.text.split('\n'):
        if line.startswith('form\twsafter'):
            continue  # Skip first row (header)
        tok = line.split('\t')
        if len(tok) > 1:  # Not empty string
            lemma = tok[3].lower()
            postags = tok[4]
            if postags.startswith(tuple(ALLOWED_POSTAGS.values())):
                lemma_list.append(lemma)

    return lemma_list


if __name__ == '__main__':

    # Load data
    in_path = 'data/raw/txt'
    out_path = 'data/interim/txt_accented'
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    data_dict = cf.load_folder_to_dict(path=in_path)

    # Lemmatize, filter and save results
    for filename, content in tqdm(data_dict.items()):
        lemmatized = ' '.join(lemmatize_and_filter(content))
        with open(f'{out_path}/{filename}', mode='w', encoding='utf-8') as out:
            out.write(lemmatized.strip(' '))
