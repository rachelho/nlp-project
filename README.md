# NLP QA Project by Tory Leavitt and Rachel Ho #
## Instructions for running ##
* To set up the venv, from the CADE machine navigate to terminal and type in the following: 
``` 
source home/u0958645/tlrh-env/bin/activate.csh
 ```
* Once connected to the venv navigate to our project folder and run the command: 
```
python3 qa.py [inputFile]
```
* Each story should take about *** x seconds ***
* In case of any issues, this venv was set up in CADE machine 1-9
## External libraries, data, software and tools: ##
* Spacy for NER with the en_core_web_trf model
    * https://spacy.io/
    * https://github.com/explosion/spacy-models/releases/tag/en_core_web_trf-3.4.1 
* NLTK corpus for stopwords
    * https://www.nltk.org/api/nltk.corpus.html 
    * https://www.nltk.org/nltk_data/ (#73)
* NLTK tokenize with sent_tokenize and word_tokenize
    * https://www.nltk.org/api/nltk.tokenize.html
* NLTK stem with wordnet lemmatizer
    * https://www.nltk.org/api/nltk.stem.html 
    * https://www.nltk.org/api/nltk.stem.wordnet.html

## Known problems and limitations ##
* Why and non-quantitative how questions not fully supported
* Not entirely accurate answers
* Answers may contain some extra words
* Symbols not included in answers (i.e. dollar signs)