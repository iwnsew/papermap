papermap
========

A code for creating GEXF format file of paper map based on document similarity.

How to use
==========

1. Put all PDF files of papers under paper/ directory.

2. Run this to create graph file (may take few minutes).

`python pdftogexf.py > out.gexf`
    
3. Use visualization tools such as _gephi_ for displaying out.gexf.

Requirements
============

* python 2.7.x (I'm not sure if this code works on other version)

* gensim

* pdftotext (already installed in Ubuntu and CentOS)

