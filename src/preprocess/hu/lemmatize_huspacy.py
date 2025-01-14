#!/usr/bin/python3

import os
import huspacy
from tqdm import tqdm
import src.common_functions as cf

# Source: https://github.com/huspacy/huspacy
# To download the latest model, use this: huspacy.download()
# Or download the latest model directly: pip install https://huggingface.co/huspacy/hu_core_news_lg/resolve/main/hu_core_news_lg-any-py3-none-any.whl

# List of POS tags: https://spacy.io/api/annotation#pos-tagging.
ALLOWED_POSTAGS = ['ADJ', 'ADV', 'NOUN', 'NUM', 'PROPN', 'VERB']


def lemmatize_and_filter(text):
    """
    Lemmatize text and filter tokens based on allowed POS tag list.
    :param text: text to be lemmatized
    :return: list of lemmatized tokens
    """
    token_list = []
    document = nlp(text.strip())
    for token in document:
        if token.tag_ in ALLOWED_POSTAGS:
            token_list.append(str(token.lemma_).lower())
    return token_list


if __name__ == '__main__':

    # Load data
    in_path = 'data/interim/txt_accented_urlextract_nospecial'
    out_path = 'data/interim/txt_accented_urlextract_nospecial_lemmatized'
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    data_dict = cf.load_folder_to_dict(path=in_path)

    # Initialize nlp model
    nlp = huspacy.load()

    # Lemmatize, filter and save results
    for filename, content in tqdm(data_dict.items()):
        lemmatized = ' '.join(lemmatize_and_filter(content))
        with open(f'{out_path}/{filename}', mode='w', encoding='utf-8') as outfile:
            outfile.write(lemmatized.strip(' '))
