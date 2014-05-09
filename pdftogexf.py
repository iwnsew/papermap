#-*- coding: utf-8 -*-
import argparse
import os
import re
import shlex
import subprocess
from gensim import corpora, models, similarities

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-t",
    "--threshold",
    default=0.07,
    type=float,
    help="Add an edge if the similarity between two papers exceeds this value. Default value is 0.07."
  )
  parser.add_argument(
    "-s",
    "--short",
    default=3,
    type=int,
    help="Discard short words less than this value. Default value is 3."
  )
  parser.add_argument(
    "-r",
    "--rare",
    default=3,
    type=int,
    help="Discard rare words less than this value. Default value is 3."
  )
  args = parser.parse_args()
  THRESHOLD_SIM = args.threshold
  THRESHOLD_SHORT_WORD = args.short
  THRESHOLD_RARE_WORD = args.rare

  # Conpile regex pattern
  rechar = re.compile("[a-zA-Z ]")
  regtitle = re.compile("(.*?)\n(.*?)\n")

  # Load stopword
  stopwords = set([])
  for line in open("stopword.txt"):
    stopwords.add(line.rstrip())

  # Run on all papers to extract texts
  id2paper = {}
  texts = []
  dirname = os.path.abspath(os.path.dirname(__file__)) + "/paper/"
  papers = os.listdir(dirname)
  for paper in papers:
    if paper == ".gitkeep":
      continue
    #print paper, ":",
    command = shlex.split("pdftotext -raw -enc UTF-8 " + dirname + paper + " -")
    rawtext = subprocess.check_output(command)
    text = ""
    title = ""
    mt = regtitle.match(rawtext)
    title = mt.group(1) + " " + mt.group(2)
    #print title
    id2paper[len(id2paper)] = title
    for c in rawtext:
      m = rechar.search(c)
      if m:
        text += c
      elif c == "\n":
        text += " "
    texts.append(text)
    #if len(texts) > 19:
      #break

  #Convert text into tfidf-weighted gensim-corpus
  wordlists = [[word for word in text.lower().split() if word not in stopwords and len(word) >= THRESHOLD_SHORT_WORD] for text in texts]
  alltokens = sum(wordlists, [])
  raretokens = set(word for word in set(alltokens) if alltokens.count(word) < THRESHOLD_RARE_WORD)
  wordlists = [[word for word in wordlist if word not in raretokens] for wordlist in wordlists]
  dictionary = corpora.Dictionary(wordlists)
  corpus = [dictionary.doc2bow(wordlist) for wordlist in wordlists]
  for k, v in dictionary.token2id.items():
    dictionary.id2token[v] = k
  tfidf = models.TfidfModel(corpus)
  wcorpus = []
  print '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
  print '<graph mode="static" defaultedgetype="undirected">'
  print '<nodes>'
  for i in range(len(corpus)):
    wcorpus.append(tfidf[corpus[i]])
    print '<node id="'+str(i)+'" label="'+str(id2paper[i])+'" />'
  print '</nodes>'

  # Compute similarity for each pair
  print '<edges>'
  eid = 0
  index = similarities.MatrixSimilarity(wcorpus)
  for i in range(len(wcorpus)-1):
    for j in range(i+1, len(index[wcorpus[i]])):
      if index[wcorpus[i]][j] > THRESHOLD_SIM:
        print '<edge id="'+str(eid)+'" source="'+str(i)+'" target="'+str(j)+'" weight="'+str(index[wcorpus[i]][j])+'" />'
        eid += 1
  print '</edges>'
  print '</graph>'
  print '</gexf>'

if __name__ == "__main__":
  main()
