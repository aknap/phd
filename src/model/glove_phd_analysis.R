library(text2vec)
library(dplyr)
library(rio)
library(readr)

setwd(dir = 'f:/phd/analysis/')


# Vektorterek betöltése

load("0701_PGMT_d300_w10_i10_s5373_v01.Rdata")
pgmt <- word_vectors

load("1021_NGMT_d300_w10_i10_s6117_v01.Rdata")
ngmt <- word_vectors

load("1181_FARR_d300_w10_i10_s4418_v01.Rdata")
farr <- word_vectors

rm(word_vectors)


# Word similarity
for (current_word in c('trianon', 'holokauszt', 'haza')) {
  # Save pgmt
  s.word <- pgmt[current_word,,drop = FALSE]
  dist.s <- sim2(x = pgmt, y = s.word, method = "cosine", norm = "l2")
  dist.s[order(dist.s, decreasing=T),][1:200]
  
  res_pgmt <- as.data.frame(dist.s[order(dist.s, decreasing=T),])
  colnames(res_pgmt) <- "pgmt"
  res_pgmt <- as_data_frame(res_pgmt, rownames = "words")
  
  # Save ngmt
  s.word <- ngmt[current_word,,drop = FALSE]
  dist.s <- sim2(x = ngmt, y = s.word, method = "cosine", norm = "l2")
  dist.s[order(dist.s, decreasing=T),][1:200]
  
  res_ngmt <- as.data.frame(dist.s[order(dist.s, decreasing=T),])
  colnames(res_ngmt) <- "ngmt"
  res_ngmt <- as_data_frame(res_ngmt, rownames = "words")
  
  # Save farr
  s.word <- farr[current_word,,drop = FALSE]
  dist.s <- sim2(x = farr, y = s.word, method = "cosine", norm = "l2")
  dist.s[order(dist.s, decreasing=T),][1:200]
  
  res_farr <- as.data.frame(dist.s[order(dist.s, decreasing=T),])
  colnames(res_farr) <- "farr"
  res_farr <- as_data_frame(res_farr, rownames = "words")
  

  # Export results.
  result_p_n <- full_join(res_pgmt, res_ngmt, by = "words")
  result_p_n_f <- full_join(result_p_n, res_farr, by = "words")
  result_filename <- paste0(c("simple_distances/distances_", current_word, "_c02.xlsx"), collapse = "")
  export(result_p_n_f, file=result_filename)
}
