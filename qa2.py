# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 20:47:29 2022

@author: toryl
"""

import sys
import csv
import nltk
import re
import spacy
#import en_core_we_sm
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from spacy import displacy


NER = spacy.load("en_core_web_lg")
#%% Classes
class Story():
        
        def __init__(self, story):
            
            self.story = story.strip()
            self.sentences = sent_tokenize(story)
            self.pos = []
            self.lemma = []
            self.ner = []
            lemmatizer = WordNetLemmatizer()
            stop = stopwords.words('english')
            punctuation = ['?','.',',','!',':',";",'"',"'", '``', "'s"]
            
            for token in self.sentences:
                # Grab the story information
                if token.startswith("HEADLINE:"):
                    lines = token.split('\n')
                    for line in lines:
                        if line.startswith("HEADLINE:"):
                            self.headline = line.lstrip("HEADLINE: ")
                            
                        elif line.startswith("DATE: "):
                            self.date = line.lstrip("DATE:")
                            
                        elif line.startswith("STORYID: "):
                            self.storyID = line.lstrip("STORYID: ")
                        
                        elif line.startswith("TEXT:"):
                             break
                
                else:
                    break
        
            # Need to remove the Headline, Date, etc. from the first sentence
            firstSentence = word_tokenize(self.sentences[0])
            i = 0
            
            # Find the location of the first word after "TEXT:"
            for token in firstSentence:
                i += 1
                if token.startswith("TEXT"):
                    break
            
            self.sentences[0] = '' 
            i += 1
            
            # Now append the sentence together
            while i < len(firstSentence):
                if i + 2 < len(firstSentence):
                    self.sentences[0] += firstSentence[i] + ' '
                    i += 1
                else:
                    self.sentences[0] += firstSentence[i]
                    i += 1

            # Get the POS for each word of each sentence in the story and store it as a list of tuples
            for sentence in self.sentences:
                doc = NER(sentence)
                nesList = list(doc.ents)
                
                ner = []
                for ent in nesList:
                    ner.append(ent.text)
                    ner.append(ent.label_)
                    
                words = word_tokenize(sentence)
                pos = nltk.pos_tag(words)
                posList = []
                for tag in pos:
                    if tag[0] not in stop and tag[0] not in punctuation:
                        posList.append(tag)
                        
                lemmaList = []
                
                for word in words:
                    if word not in stop and word not in punctuation:
                        lemmaWord = lemmatizer.lemmatize(word).lower()
                        lemmaList.append(lemmaWord)
                
                self.lemma.append(lemmaList)        
                self.pos.append(posList)
                self.ner.append(ner)
                
                for sentence in self.sentences:
                    sentence = sentence.lower()
            
            # # Lemmatize each word in the sentence and store it as a list 
            # for sentence in self.sentences:
            #     words = word_tokenize(sentence)
            #     lemmaList = []
                
            #     for word in words:
            #         if word not in stop and word not in punctuation:
            #             lemmaWord = lemmatizer.lemmatize(word)
            #             lemmaList.append(lemmaWord)
                
            #     self.lemma.append(lemmaList)
            
            return

class Question():        
    
    def __init__(self, question):
        
        self.id = ''
        self.questionid = []
        self.questions = []
        self.difficulty = []
        self.lines = []
        self.pos = []
        self.lemma = []
        self.ner = []
        self.type = []
        lemmatizer = WordNetLemmatizer()
        stop = stopwords.words('english')
        punctuation = ['?','.',',','!',':',";",'"',"'", '``', "'s"]
        
        
        for line in question:
            if line.startswith("QuestionID:"):
                self.questionid.append(line.lstrip("QuestionID: ").strip())
            if line.startswith("Question:"):
                self.questions.append(line.lstrip("Question: ").strip())
            if line.startswith("Difficulty:"):
                self.difficulty.append(line.lstrip("Difficulty: ").strip())
            
        self.id =  self.questionid[0][:(len(self.questionid[0])-2)]
        
        for question in self.questions:
            doc = NER(question)
            nesList = list(doc.ents)
            
            ner = []
            for ent in nesList:
                ner.append(ent.text)
                ner.append(ent.label_)
                
            words = word_tokenize(question)
            pos = nltk.pos_tag(words)
            posList = []
            for tag in pos:
                if tag[0] not in stop and tag[0] not in punctuation:
                    posList.append(tag)
                    
            lemmaList = []
            typeList = set()
            
            whoList = {'who'}
            whatList = {'what'}
            whereList = {'where', 'located'}
            whenList = {'when', 'time', 'date'}
            howList = {'big', 'how', 'small', 'much', 'cost', 'far'}
            whyList = {'why'}
            
            for word in words:
                if word not in stop and word not in punctuation:
                    lemmaWord = lemmatizer.lemmatize(word).lower()
                    lemmaList.append(lemmaWord)
                
                # Not sure of the best way to approach this
                if word.lower() in whereList:
                    typeList.add('GPE')
                    
                elif word.lower() in whoList:
                    typeList.add("PERSON")
                    typeList.add("ORG")
                
                elif word.lower() in howList:
                    typeList.add('QUANTITY')
                    typeList.add('MONEY')
                
                elif word.lower() in whatList:
                    typeList.add("PRODUCT")
                    typeList.add("ORG")
                    typeList.add('PERCENTAGE')
                    
                elif word.lower() in whenList:
                    typeList.add("DATE")
                    typeList.add("TIME")
                
                elif word.lower() in whyList:
                    typeList.add()
                
            
            self.lemma.append(lemmaList)        
            self.pos.append(posList)
            self.ner.append(ner)
            self.type.append(typeList)
        
        return
        
#%% Functions
def ReadStoryFile(file, type, stories):
      
    text = open(file)
    story = text.read()    
    stories.append(type(story))
    
def ReadQuestionFile(file, type, questions):
    
    with open(file) as qfile:
        questionsLines = qfile.readlines()
    questions.append(type(questionsLines))

def ArgValidation(args):
    
    if len(sys.argv) != 2:
        raise Exception("Only 1 argument shoul be passed, a single input file")
    return

def Overlap(story, question, bestSentenceMatch, bestSentenceLocation):
    
    location = 0
    for sentence in story.lemma:

        overlap = list(set(question) & set(sentence))
        print(overlap)
        
        if len(overlap) in bestSentenceMatch.keys():
            bestSentenceMatch[len(overlap)].append(sentence)
            bestSentenceLocation[len(overlap)].append(location)
        
        else:
            bestSentenceMatch[len(overlap)] = [sentence]
            bestSentenceLocation[len(overlap)] = [location]
        
        location += 1
    
    return

#%% Main
def main():
    ArgValidation(sys.argv)
    responseFile = 'responseFile.csv'
    stories = []
    #each questions key is the id, followed by the type of question, then the question itself
    questions = []
    ids = []
    stop = stopwords.words('english')
    path = ''
    with open(sys.argv[1]) as input:
        lines = input.readlines()
        path = lines[0].strip()
        for qids in lines[1:]:
            qid = qids.strip()
            ids.append(path + qid)
    for id in ids:
        questionFile = id + ".questions"
        storyFile = id + ".story"
        answers = []
        
        ReadQuestionFile(questionFile, Question, questions)
        ReadStoryFile(storyFile, Story, stories)
        
        bestSentenceMatch = {}
        bestSentenceLocation = {}
        #print(stories[id])
        for question in questions:
            for question2 in question.lemma:

                for story in stories:
                    if story.storyID == question.id:
                        Overlap(story, question2, bestSentenceMatch, bestSentenceLocation)
                        
                
                print('stop')

            
if __name__ == "__main__":
    main()
