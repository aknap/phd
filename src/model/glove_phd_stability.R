# Title     : Stability testing of GloVe models
# Objective : Testing the stability of GloVe models with various parameters
# Created by: knapa
# Created on: 2022.06.02.

library(text2vec)
library(dplyr)
library(rio)
library(readr)

setwd(dir = 'e:/PyCharm/14_Trianon_and_Holocaust/data/phd/glove/data')
out_dir <- 'f:/phd/'


# Create list of focus words
focus_words <- c("trianon", "holokauszt")

# Create list of context words
context_words <- c("zsidó", "kormány", "nemzet", "magyarság", "jobbik", "haza", "áldozat", "család", "erő", "erdély", "szövetséges", "kárpátalja", "megszállás", 
                   "kormányzó", "trauma", "magyarellenes", "állítólagos", "hovatartozás", "összeesküvés", "befogadó", "önkényes", "színmagyar", "újvidék", 
                   "békerendszer", "történelemhamisító", "kivégzett", "wehrmacht", "ágyútűz", "gonosztett", "elborult")

# Create 1440 random numbers to be used as seed values
seed_values <- sample(1000:9999, 1440, FALSE)


# Start from model number 1
model_no <- 1


## Iterate corpora
for (corpus_name in list('pgmt', 'ngmt', 'farr')) {

  # Load corpus
  corpus <- read_csv2(file = paste0(c(corpus_name, '.csv'), collapse = ""), col_names = FALSE)
  corpus_text <- corpus$X1

  cat(corpus_name, "corpus loaded containing", length(corpus_text), "documents.")

  # Create iterator over tokens
  tokens <- space_tokenizer(corpus_text)

  # Create vocabulary. Terms will be unigrams (simple words)
  it <- itoken(tokens, progressbar = FALSE)

  vocab <- create_vocabulary(it)

  # Filter out nonfrequent words
  vocab <- prune_vocabulary(vocab, term_count_min = 5L)

  # Use our filtered vocabulary
  vectorizer <- vocab_vectorizer(vocab)


  ## Iterate window sizes
  for (window in c(5L, 10L)) {

    # Create TCM
    tcm <- create_tcm(it, vectorizer, skip_grams_window = window)

    ## Iterate over iteration values
    for (iteration in c(5, 10, 15, 20)) {

      ## Iterate over dimensions
      for (dimension in c(100, 200, 300)) {

        ## Iterate over run numbers
        for (run in seq(1, 20, 1)) {

          # Set seed value for the current run
          set.seed(seed_values[model_no])

          # Print model info
          cat(c("\nCorpus: \t", corpus_name, "\n",
                "Window: \t", window, "\n",
                "Iterations: \t", iteration, "\n",
                "Dimensions: \t", dimension, "\n",
                "Version: \t", run, "\n",
                "Seed: \t\t", seed_values[model_no], "\n",
                "Model#: \t", model_no, "\n"
          ), sep="")

          # Set basic filename
          filename <- paste0(c(sprintf("%04d", model_no), "_", toupper(corpus_name), "_d", dimension, "_w", window, "_i", iteration, "_s", seed_values[model_no], "_v", sprintf("%02d", run)), collapse = "")

          # Train GloVe model
          glove <- GlobalVectors$new(rank = dimension, x_max = 10, learning_rate = 0.1)
          word_vectors_main <- glove$fit_transform(tcm, n_iter = window, n_threads = 7)
          word_vectors_context <- t(glove$components)
          word_vectors <- word_vectors_main + word_vectors_context

          # Get distance of focus and context words
          focus_vec <- word_vectors[focus_words,,drop = FALSE]
          context_vec <- word_vectors[context_words,,drop = FALSE]
          focus_context_distance <- sim2(x = context_vec, y = focus_vec, method = "cosine", norm = "l2")
          results <- as.data.frame(focus_context_distance, )
          
          # Export results for stability checking
          result_filename <- paste0(c(out_dir, filename, ".csv"), collapse = "")
          write.csv(results, file=result_filename)

          # Save word vectors
          vectors_filename <- paste0(c(out_dir, filename, ".Rdata"), collapse = "")
          save(word_vectors, file = vectors_filename)

          # Bump model number
          model_no <- model_no+1

        }
      }
    }
  }
}
