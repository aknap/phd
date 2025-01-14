#!/usr/bin/python3

import os
import nltk
import re
import src.common_functions as cf
from tqdm import tqdm
from hunlp import HuNlp

# NOTICE: This code is deprecated. Please use emtsv or HuSpacy instead.
# To install the hunlp package use: pip install https://github.com/oroszgy/hunlp/releases/download/0.2/hunlp-0.2.0.tar.gz

# Settings
MAX_LENGTH_OF_SENTENCES = 50
EXCLUDE_LIST = []  # List of words to be excluded from lemmatization.


def remove_special(text):
    """ Remove special characters """
    text = text.replace('•', '. ')
    text = text.replace('~', '')
    text = text.replace('→', '')
    text = text.replace('|', '')
    text = text.replace(' * ', ' . ')
    text = text.replace('\u2000', ' ')  # Replace NQSP (en quad).
    text = text.replace('\u2001', ' ')  # Replace MQSP (em quad).
    text = text.replace('\u2002', ' ')  # Replace ENSP (en space).
    text = text.replace('\u2003', ' ')  # Replace EMSP (em space).
    text = text.replace('\u2004', ' ')  # Replace 3/MSP (three-per-em space).
    text = text.replace('\u2005', ' ')  # Replace 4/MSP (four-per-em space).
    text = text.replace('\u2006', ' ')  # Replace 6/MSP (six-per-em space).
    text = text.replace('\u2007', ' ')  # Replace FSP (figure space).
    text = text.replace('\u2008', ' ')  # Replace PSP (punctuation space).
    text = text.replace('\u2009', ' ')  # Replace THSP (thin space).
    text = text.replace('\u200A', ' ')  # Replace HSP (hair space).
    text = text.replace('\u200B', ' ')  # Replace zero width space.
    text = text.replace('\u200C', ' ')  # Replace zero width non-joiner.
    text = text.replace('\u200D', '')  # Remove zero width joiner.
    text = text.replace('\u200E', '')  # Remove left-to-right mark.
    text = text.replace('\u200F', '')  # Remove right-to-left mark.
    text = text.replace('\u2028', '')  # Remove LSEP.
    text = text.replace('\u2029', '')  # Remove RSEP.
    return text


def make_sentences(text, max_length_words):
    """ Split long sentences """
    text = text.replace('\n', '. ')
    text = re.sub(r'(?<=[a-z])[.?!…](?=[A-Z])', '. ', text)  # Create sentences, if sentence is separated like "something.New sentence" (missing space).
    text = re.sub(r'(?<=[a-z])[.]{3}(?=[A-Z])', '. ', text)  # The same, with ellipses.
    sentences = nltk.sent_tokenize(text)
    result = []
    for sentence in sentences:
        # If sentence does not exceed max length: continue.
        if len(sentence.split(' ')) <= max_length_words:
            result.append(sentence)
        # If sentence exceeds max length: split the text to sentences every max_length_words.
        else:
            wlst = []
            nth = 0
            for word in sentence.split(' '):
                nth += 1
                if nth % max_length_words == 0:
                    wlst.append(word+'.')
                else:
                    wlst.append(word)
            result.append(' '.join(wlst))
    # Capitalize every first word in the sentence.
    final = []
    for sentence in nltk.sent_tokenize(' '.join(result)):
        first = True
        for word in sentence.split(' '):
            if first:
                final.append(word.capitalize())
                first = False
            else:
                final.append(word)
    return ' '.join(final)


def lemmatize_and_filter(text, keep_sentences=False):
    """ Function to lemmatize text using the hunlp java server """
    # POS tags: https://spacy.io/api/annotation#pos-tagging.
    # ADJ: melléknév, ADV: határozószó, NOUN: főnév, NUM: szám, PROPN: tulajdonnév, VERB: ige.
    allowed_pos = ['ADJ', 'ADV', 'NOUN', 'NUM', 'PROPN']
    sentences_list = []
    text = remove_special(text)
    text = make_sentences(text, max_length_words=MAX_LENGTH_OF_SENTENCES)
    document = nlp(text.strip())
    for sentence in document:
        sentence_tokens = []
        for token in sentence:
            if str(token.text).lower() not in EXCLUDE_LIST:
                if token.tag in allowed_pos:
                    sentence_tokens.append(token.lemma)
            else:
                sentence_tokens.append(str(token.text))
        if len(sentence_tokens) > 0:
            if keep_sentences:
                sentence_tokens[-1] = sentence_tokens[-1]+'.'
            sentences_list.append(sentence_tokens)
    token_list = []
    for sentence in sentences_list:
        for word in sentence:
            token_list.append(word)
    return token_list


if __name__ == '__main__':

    # Load data
    in_path = 'data/interim/txt_accented_urlextract_nospecial'
    out_path = 'data/interim/txt_accented_urlextract_nospecial_lemmatized'
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    data_dict = cf.load_folder_to_dict(path=in_path)

    # Make a set of all files already in the folder
    folder = [f for f in tqdm(os.listdir(out_path), desc='Creating list of processed files') if os.path.isfile(os.path.join(out_path, f))]
    folder_set = set(folder)

    # Initialize hunlp
    nlp = HuNlp()

    # Lemmatize, filter and save results
    for filename, doc in tqdm(data_dict.items()):
        if filename in folder_set or len(doc) == 0:
            continue
        try:
            sentences_tokens = lemmatize_and_filter(doc)
            lemmatized_text = ' '.join(sentences_tokens)
            with open(os.path.join(out_path, filename), 'w', encoding='utf-8') as outfile:
                outfile.write(lemmatized_text)
        except Exception as e:
            print(filename, e)
