#!/usr/bin/python3

import os
import src.common_functions as cf
from tqdm import tqdm
from spacy.lang.hu.stop_words import STOP_WORDS


if __name__ == '__main__':

    # Add all articles that need to be processed to a dictionary
    in_path = 'data/interim/txt_accented_urlextract_nospecial_lemmatized_ner_trigram_bigram_replace'
    out_path = 'data/interim/txt_accented_urlextract_nospecial_lemmatized_ner_trigram_bigram_replace_stop'

    data_dict = cf.load_folder_to_dict(path=in_path, minimal_length=1)

    # Load custom stopwords
    stopword_list = list(STOP_WORDS)  # Spacy builtin stopwords list.
    with open(os.path.join('data', 'common', 'github_stopwords_hu_v01.txt'), 'r', encoding='utf-8') as stopwords_file:
        custom_stopwords = [line.rstrip('\n') for line in stopwords_file]
    stopword_list.extend(custom_stopwords)
    stopword_set = set(stopword_list)

    # Remove stopwords and save result
    for filename, text in tqdm(data_dict.items(), desc='Removing stopwords and writing files'):
        words = text.split()
        article_clean = []
        for word in words:
            if word not in stopword_set:
                article_clean.append(word)
        with open(os.path.join(out_path, filename), 'w', encoding='utf-8') as outfile:
            outfile.write(' '.join(article_clean))

