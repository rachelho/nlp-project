# -*- coding: utf-8 -*-
"""
@author(s): Tory Leavitt and Rachel Ho
"""

import sys
import csv
import nltk
import re
import spacy
import collections
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


NER = spacy.load("en_core_web_trf")

#%% Classes
class Story():
        
        def __init__(self, story):
            
            self.story = story.strip() # Full story
            self.sentences = sent_tokenize(story) # Each sentence of the story normalized
            self.pos = [] # List of a list of tuples containing each word and POS tag (stop words not included)
            self.lemma = [] # List of lemmatized sentences (stop words not included)
            self.ner = [] # List of a list of tuples for each NER in the question 
            self.vocab = [] # List of words in story with frequency > 1 and stopwords removed

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

            
            for sentence in self.sentences:
                # Get the named entities within each sentence
                doc = NER(sentence)
                nesList = list(doc.ents)
                nerTuple = []
                for ent in nesList:
                    ner = []
                    ner.append(ent.text.strip())
                    ner.append(ent.label_.strip())
                    nerTuple.append(ner)
                    
                words = word_tokenize(sentence)
                pos = nltk.pos_tag(words)
                posList = []
                # Get the POS tags for each word in the sentence
                for tag in pos:
                    if tag[0].lower() not in stop and tag[0] not in punctuation:
                        posList.append(tag)
                        
                lemmaList = []
                # Get the lemmatization of each word in the sentence
                for word in words:
                    if word.lower() not in stop and word not in punctuation:
                        lemmaWord = lemmatizer.lemmatize(word).lower()
                        lemmaList.append(lemmaWord)
                        self.vocab.append(lemmaWord)
                
                self.lemma.append(lemmaList)        
                self.pos.append(posList)
                self.ner.append(nerTuple)
            
            frequency = collections.Counter(self.vocab)
            frequencyKeys = list(frequency.keys())
            
            for key in frequencyKeys:
                if frequency[key] == 1:
                    del frequency[key]
            
            self.frequency = frequency
            
            for word in self.vocab:
                if word not in self.frequency.keys():
                    self.vocab.remove(word)

            return

class Question():        
    
    def __init__(self, question):
        
        self.id = '' # Main question/story ID
        self.subQuestions = [] # List of questions for each Story
        tempId= ''
        
        for line in question:
            if line.startswith("QuestionID:"):
               tempId =  line.lstrip("QuestionID: ").strip()
               break
    
        self.id =  tempId[:(len(tempId)-2)]
        
        i = 0
        while i + 4 <= len(question):
            subQuestion = question[i:i+4]
            self.subQuestions.append(SubQuestion(subQuestion))
            i += 4
        
        return
    
class SubQuestion(): 
    
    def __init__(self, question):
        
        self.id = '' # Question/Story set ID
        self.questionid = [] # Subquestion ID
        self.question = '' # The original question
        self.difficulty = [] # Difficulty of each question
        self.pos = [] # List of a list of tuples containing each word and POS tag (stop words not included)
        self.dependencies = []
        self.lemma = [] # List of lemmatized questions (stop words not included)
        self.ner = [] # List of a list of tuples for each NER in the question 
        self.type = set() # Type of NER tag we should look for for the answer (who/what/when/where/why/how)
        
        lemmatizer = WordNetLemmatizer()
        stop = stopwords.words('english')
        punctuation = ['?','.',',','!',':',";",'"',"'", '``', "'s"]
        
        
        for line in question:
            if line.startswith("QuestionID:"):
                self.questionid.append(line.lstrip("QuestionID: ").strip())
            if line.startswith("Question:"):
                self.question = (line.lstrip("Question: ").strip())
            if line.startswith("Difficulty:"):
                self.difficulty.append(line.lstrip("Difficulty: ").strip())
            
        self.id =  self.questionid[0][:(len(self.questionid[0])-2)]
        
        
        doc = NER(self.question)
        nesList = list(doc.ents)
        nerTuple = []
        depTuple = []
        
        for token in doc:
            dep = []
            dep.append(token.text)
            dep.append(token.dep_)
            depTuple.append(dep)
            
        for ent in nesList:
            ner = []
            ner.append(ent.text.strip())
            ner.append(ent.label_.strip())
            nerTuple.append(ner)
                
        words = word_tokenize(self.question)
        pos = nltk.pos_tag(words)
        posList = []
        # Get POS tags for each word in the question
        for tag in pos:
            if tag[0] not in stop and tag[0] not in punctuation:
                posList.append(tag)
            
        # Lists of words to help identify the type of answer we are looking for
        whoList = {'who', 'person', 'organization', 'team', 'company', 'business'}
        whatList = {'what'}
        whereList = {'where', 'located', 'location', 'site', 'venue', 'locale'}
        whenList = {'when', 'time', 'date', 'month', 'year'}
        whyList = {'why'}
        quantityList = {'big', 'small', 'far', 'many', 'distance', 'capacity', 'length', 'tall'}
        moneyList = {'much', 'cost', 'price', 'salary', 'budget', 'paid'}
            
        for word in words:
            # Lemmatize each word in the question for later comparisons in overlap
            if word not in stop and word not in punctuation:
                lemmaWord = lemmatizer.lemmatize(word).lower()
                self.lemma.append(lemmaWord)
                
            # Get the possible NER tags we should look for in the answer
            if word.lower() in whereList:
                self.type.add('GPE')
                    
            elif word.lower() in whoList:
                self.type.add("PERSON")
                self.type.add("ORG")
                
            elif word.lower() in quantityList:
                self.type.add('QUANTITY')
            
            elif word.lower() in moneyList:
                self.type.add('MONEY')
                
            elif word.lower() in whatList:
                self.type.add('PRODUCT')
                self.type.add('PERCENTAGE')
                    
            elif word.lower() in whenList:
                self.type.add('DATE')
                self.type.add('TIME')
                
            elif word.lower() in whyList:
                self.type.add('')
                
        self.pos.append(posList)
        self.ner.append(nerTuple)
        self.dependencies.append(depTuple)

        return
        
#%% Functions
def ReadStoryFile(file, type, stories):
    '''takes a story file and parses it into a story object'''
    try: 
        text = open(file)
        story = text.read()    
        stories.append(type(story))
    except:
        print("Unable to locate" + file)
    
def ReadQuestionFile(file, type, questions):
    '''takes a question file and parses it into a question object'''
    try:
        with open(file) as qfile:
            questionsLines = qfile.readlines()
            questions.append(type(questionsLines))
    except:
        print("Unable to locate" + file)        
        
def ArgValidation(args):
    '''Validates that 1 and only 1 argument was passed through the command line'''
    if len(sys.argv) != 2:
        raise Exception("Only 1 argument shoul be passed, a single input file")
    return

def RemoveFrequencyOne(values):

    frequency = collections.Counter(values)
    frequencyKeys = list(frequency.keys())
    
    for key in frequencyKeys:
        if frequency[key] == 1:
            del frequency[key]

    return frequency

def Overlap(story, question, bestSentenceMatch, bestSentenceLocation, matchingNERSentences):
    '''Takes a story and the question and records the overlap between each sentence in the story and the question'''
    location = 0 # Tells us which element in the story.sentences
    for sentence in matchingNERSentences:
        # Get the words in common between both sentence and question
        overlap = list(set(question.lemma) & set(story.lemma[sentence]))
        
        # Append the overlap to the dictionary
        if len(overlap) in bestSentenceMatch.keys():
            bestSentenceMatch[len(overlap)].append(sentence)
            bestSentenceLocation[len(overlap)].append(location)
        
        # Add the overlap to the dictionary
        else:
            bestSentenceMatch[len(overlap)] = [sentence]
            bestSentenceLocation[len(overlap)] = [location]
        
        location += 1
    
    return

def MatchingNER(story, question):
    '''Takes a story and the question and gets the sentences containing the right NER tag'''
    location = 0 # Tells us which element in the story.sentences
    questionType = question.type
    possibleSentences = set()
    
    for nerType in story.ner:
        for ner in nerType:
            if ner[1] in questionType:
                possibleSentences.add(location)
        location += 1

    return possibleSentences

def FindAnswer(question, story, bestSentenceMatch):
    '''Find the best answer based on overlap and type of question. Then print the answer to the output file'''
    
    questionNERTag = list(question.type)
    validSentences = []
    foundSentence = False
    # Iterate though the overlaps, high to low, until we find the correct NER tag
    while len(bestSentenceMatch) > 0:
        highOverlap = max(bestSentenceMatch.keys()) # Get high overlap
        toCheck = list(bestSentenceMatch[highOverlap]) # List of sentence locations with that overlap
        if foundSentence is False:
            for sentence in toCheck:
                if len(story.ner[sentence]) > 0:
                    sentenceNERTag = list(story.ner[sentence])
                    for questionTag in questionNERTag:
                        for sentenceTag in sentenceNERTag:
                            if questionTag == sentenceTag[1]:
                                validSentences.append(sentence)
                                # foundSentence = True
            bestSentenceMatch.pop(highOverlap)
        # Found a sentence in highOverlap
        else:
            break 
    
    highCount = 0
    bestSentence = -1
    
    # Still garbage I am really struggling to find something that works without importing a bunch of stuff 
    countOfNER = collections.Counter(validSentences)
    sentenceKeys = countOfNER.keys()
    mostNER = 0
    for key in sentenceKeys:
        if countOfNER[key] > mostNER:
            bestSentence = key
            mostNER = countOfNER[key]
    
    # Not sure how to determine which is the best from here    
    # for sentence in validSentences:
    #     sentenceNERCount = 0
    #     for ner in story.ner[sentence]:
    #         if ner[1] in questionNERTag:
    #             sentenceNERCount += 1
        
    #     if sentenceNERCount > highCount:
    #         highCount = sentenceNERCount
    #         bestSentence = sentence
                
    WriteToFile(question, questionNERTag, bestSentence, story)            
    
    return

def WriteToFile(question, questionNERTag, sentence, story):
    '''Writes the answers to the output in the correct format'''
    # For now I am just print I will work on writing to file later
    answer = ''
    
    
    # If we look at the location of the tags within the sentence and if they are far apart we do not join them
    # that might help narrow our answer down more
    if sentence != -1:
        for tag in story.ner[sentence]:
            if tag[1] in questionNERTag:
                answer += tag[0] + ' '
    qid = str(question.questionid).strip()
    qidClean = qid[2:-2]
    line1 = "QuestionID: " + str(qidClean)
    line2 = "Question: " + str(question.question)
    line3 = "Difficulty: " + str(question.difficulty)
    line4 = "Answer: " + answer.strip()
    line5 = "Sentence w/ answer: " +  story.sentences[sentence] + '\n'
    
    #redirect print to answer file, be sure to remove this if you want to print other things
    fileName = 'Soutions.response'
    writeOrAppend = ''

    # print(line1)
    # print(line2)
    # print(line3)
    print(line4)
    # print(line5)
        
    
    # with open(fileName, 'a') as file:
    #     file.writelines("QuestionID: " + str(qidClean) + '\n')
    #     file.writelines("Answer: " + answer.strip() + '\n\n')

    
        
    return
#%% Main
def main():
    ArgValidation(sys.argv)
    responseFile = 'responseFile.csv'
    stories = []
    #each questions key is the id, followed by the type of question, then the question itself
    questions = []
    ids = []
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
        
    bestSentenceMatch = {} # Just for spot checking at this point
    bestSentenceLocation = {}
    Location = 0
    
    for question in questions:
        for subQuestion in question.subQuestions:
            for story in stories:
                if story.storyID == question.id:
                    
                    sentenceWNERMatch = MatchingNER(story, subQuestion)
                    Overlap(story, subQuestion, bestSentenceMatch, bestSentenceLocation, sentenceWNERMatch)   # Not working well like you said
                    
                    break
                                       
            FindAnswer(subQuestion, story, bestSentenceMatch)
            bestSentenceLocation.clear()
            bestSentenceMatch.clear()

            
if __name__ == "__main__":
    main()
