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
from re import search


NER = spacy.load("en_core_web_trf")

#%% Classes
class Story():
        
        def __init__(self, story):
            
            self.story = story.strip() # Full story
            # self.sentences = sent_tokenize(story) # Each sentence of the story normalized
            self.pos = [] # List of a list of tuples containing each word and POS tag (stop words not included)
            self.lemma = [] # List of lemmatized sentences (stop words not included)
            self.ner = [] # List of a list of tuples for each NER in the question 
            self.vocab = [] # List of words in story with frequency > 1 and stopwords removed
            self.np = [] # List of all the noun phrases in each sentence
            self.spacyLemma = [] # compare spacy lemma to NLTK lemma
            self.dependencies = [] # List of all the dependencies in a sentence

            lemmatizer = WordNetLemmatizer()
            stop = stopwords.words('english')
            punctuation = ['?','.',',','!',':',";",'"',"'", '``', "'s"]
            
            lines = self.story.split('\n')
            for idx in range(0, len(lines)):
                line = lines[idx]
                if line.startswith("HEADLINE:"):
                    self.headline = line.lstrip("HEADLINE: ")          
                elif line.startswith("DATE:"):
                    self.date = line.lstrip("DATE:")
                elif line.startswith("STORYID:"):
                    self.storyID = line.lstrip("STORYID: ")
                elif line.startswith("TEXT:"):
                    break
        
            # Need to remove the Headline, Date, etc. from the first sentence
            story2 = ''
            for line in lines:
                if line.startswith("HEADLINE:") or line.startswith("DATE:") or line.startswith("DATE:") or line.startswith("STORYID:") or line.startswith("TEXT:"):
                    continue
                else:
                    story2 += line + ' '
                
            self.sentences = sent_tokenize(story2)
            
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
                posList = []
                spacyLemma = []
                depList = []
                
                for token in doc:
                    posTuple = []
                    depTuple = []
                    # if token.text.lower() not in stop and token not in punctuation:
                    posTuple.append(token.text)
                    posTuple.append((token.pos_))
                    posList.append(posTuple)
                    spacyLemma.append(token.lemma_)
                    depTuple.append(token.text)
                    depTuple.append(token.dep_)
                    depList.append(depTuple)
                
                npList = []
                for np in doc.noun_chunks:
                    npTuple = []
                    npTuple.append(np.text)
                    npTuple.append(np.start)
                    npList.append(npTuple)
                    
                        
                lemmaList = []
                # Get the lemmatization of each word in the sentence
                for word in words:
                    if word.lower() not in stop and word not in punctuation:
                        lemmaWord = lemmatizer.lemmatize(word).lower()
                        lemmaList.append(lemmaWord)
                        self.vocab.append(lemmaWord)
                
                self.spacyLemma.append(spacyLemma)
                self.lemma.append(lemmaList)        
                self.pos.append(posList)
                self.ner.append(nerTuple)
                self.np.append(npList)
                self.dependencies.append(depList)
            
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
        self.type = set() # who/what/when/where/why/how etc.
        self.typeTag = set() # Type of NER tag we should look for for the answer (who/what/when/where/why/how)
        self.spacyLemma = []
        
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
        
        for token in doc:
            depTuple = []
            depTuple.append(token.text)
            depTuple.append(token.dep_)
            self.dependencies.append(depTuple)
            posTuple = []
            # if token.text.lower() not in stop and token not in punctuation:
            posTuple.append(token.text)
            posTuple.append((token.pos_))
            self.pos.append(posTuple)
            self.spacyLemma.append(token.lemma_)
            
        for ent in nesList:
            ner = []
            ner.append(ent.text.strip())
            ner.append(ent.label_.strip())
            nerTuple.append(ner)
                
        words = word_tokenize(self.question)
            
        # Lists of words to help identify the type of answer we are looking for
        # whoList = {'who', 'person', 'organization', 'team', 'company', 'business', 'whose'}
        # whatList = {'what', 'name'}
        # whereList = {'where', 'located', 'location', 'site', 'venue', 'locale'}
        # whenList = {'when', 'time', 'date', 'month', 'year', 'old', 'age', 'often'}
        # whyList = {'why'}
        # quantityList = {'big', 'small', 'far', 'many', 'distance', 'capacity', 'length', 'tall'}
        # moneyList = {'much', 'cost', 'price', 'salary', 'budget', 'paid'}
            
        for word in words:
            # Lemmatize each word in the question for later comparisons in overlap
            if word not in stop and word not in punctuation:
                lemmaWord = lemmatizer.lemmatize(word).lower()
                self.lemma.append(lemmaWord)
        question = self.question.lower()
        regex = re.compile("who is|who was|whose|who")
        if search(regex, question):
            self.type = 'who'
            self.typeTag.add("PERSON")
            self.typeTag.add("ORG")
            self.typeTag.add("NORP")
        
        regex = re.compile("what is|what was|what did|what are|what does")
        if search(regex, question):
            self.type = "what"
            self.typeTag.add('PRODUCT')
        
        regex = re.compile("when did|when is|when was|how often|what time|what date")
        if search(regex, question):
            self.type = 'when'
            self.typeTag.add('DATE')
            self.typeTag.add('TIME')
        
        regex = re.compile("where is|where was|where did")
        if search(regex,question):
            self.type = 'where'
            self.typeTag.add('GPE')
            self.typeTag.add('LOC')
        
        regex = re.compile("why does|why did|why was") # Need to figure out what NER belongs in here
        if search(regex,question):
            self.type = "why"
        
        regex = re.compile("how big|how many|how much|how far|how close")
        if search(regex,question):    
            self.type = "how"
            self.typeTag.add('QUANTITY')
            self.typeTag.add('TIME')
        
        #More specific types to narrow down if possible
        regex = re.compile("cost|price|budget|salary|paid")
        if search(regex,question):
            self.type = "how much"
            self.typeTag.clear()
            self.typeTag.add(self.typeTag.add('MONEY'))
        
        regex = re.compile("how old|age")
        if search(regex,question):
            self.type = "how old"
            self.typeTag.clear()
            self.typeTag.add(self.typeTag.add('DATE'))
        
        regex = re.compile("person")
        if search(regex,question):
            self.type = 'who'
            self.typeTag.clear()
            self.typeTag.add("PERSON")
        
        regex = re.compile("company|organization")
        if search(regex,question):
            self.type = 'who'
            self.typeTag.clear()
            self.typeTag.add("ORG")
            self.typeTag.add("NORP")
        
        regex = re.compile("country|state|city|province")
        if search(regex,question):
            self.type = 'where'
            self.typeTag.clear()
            self.typeTag.add('GPE')
        
        regex = re.compile("percent|%")
        if search(regex,question):
            self.type = 'what'
            self.typeTag.clear()
            self.typeTag.add("PERCENT")
        
        regex = re.compile("language")
        if search(regex,question):
            self.type = "what"
            self.typeTag.clear()
            self.typeTag.add("LANGUAGE")
        
        regex = re.compile("what type")
        if search(regex,question):
            self.type = "what type"
            self.typeTag.clear()
            self.typeTag.add("NONE")        

        self.ner.append(nerTuple)

        return
        
#%% Functions
def ReadStoryFile(file, type, stories):
    '''takes a story file and parses it into a story object'''

    text = open(file)
    story = text.read()    
    stories.append(type(story))

    
def ReadQuestionFile(file, type, questions):
    '''takes a question file and parses it into a question object'''
    with open(file) as qfile:
        questionsLines = qfile.readlines()
        questions.append(type(questionsLines))
     
        
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
        overlap = list(set(question.spacyLemma) & set(story.spacyLemma[sentence]))
        
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
    questionType = question.typeTag
    possibleSentences = set()
    
    for nerType in story.ner:
        for ner in nerType:
            if ner[1] in questionType:
                possibleSentences.add(location)
        location += 1

    return possibleSentences

def FindAnswer(question, story, bestSentenceMatch):
    '''Find the best answer based on overlap and type of question. Then print the answer to the output file'''
    
    questionNERTag = list(question.typeTag)
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
                
    WriteToFile(question, questionNERTag, bestSentence, story)            
    
    return
def DirectMatch(question, story):
    
    question1 = question.question
    lemmatizer = WordNetLemmatizer()
    answer = ''
    possibleSentence = -1
    
    #Use lemma to look for direct match on ROOT for what questions
    # if question.type == "what":
    #     root = ''
        
    #     for i in range(len(question.dependencies)):
    #         if question.dependencies[i][1] == 'ROOT':
    #             root = question.spacyLemma[i]
        
    #     for i in range(len(story.sentences)):
    #         if root in story.spacyLemma[i]:
    #             possibleSentence = i
    #             break
        
    #     location = -1
    #     for word in story.spacyLemma[possibleSentence]:
    #         if word != root:
    #             location += 1
    #         else:
    #             location += 1
    #             break
    #     minDistance = 99999
    #     for np in story.np[possibleSentence]:
    #         if (abs(int(np[1]) - location)) < minDistance:
    #             minDistance = abs(int(np[1]) - location)
    #             answer = np[0]
    
    # if question.type == 'why':
    root = ''
    for i in range(len(question.dependencies)):
        if question.dependencies[i][1] == 'ROOT':
            root = question.spacyLemma[i]
        
    for i in range(len(story.sentences)):
        if root in story.spacyLemma[i]:
            possibleSentence = i
            break
        
    # for dependency in story.dependencies[possibleSentence]:
    #     if dependency[1] == 'nsubj':
    #         answer = dependency[0]
    #         break
        
    regex = re.compile(answer)    
        # Look for a noun phrase containing the answer
    for np in story.np[possibleSentence]:
        words = np[0]
        answer += ' ' + words
    
    return answer
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
                
    if answer == '':
        answer = DirectMatch(question, story)
        
    qid = str(question.questionid).strip()
    qidClean = qid[2:-2]
    line1 = "QuestionID: " + str(qidClean)
    line2 = "Question: " + str(question.question)
    line3 = "Difficulty: " + str(question.difficulty)
    line4 = "Answer: " + answer.strip()
    line5 = "Sentence w/ answer: " +  story.sentences[sentence] + '\n'
    
    #redirect print to answer file, be sure to remove this if you want to print other things
    fileName = 'Solutions.response'
    writeOrAppend = ''

    # print(line1)
    # print(line2)
    # print(line3)
    # print(line4)
    # print(line5)
        
    
    with open(fileName, 'a') as file:
        file.writelines("QuestionID: " + str(qidClean) + '\n')
        file.writelines("Answer: " + answer.strip() + '\n\n')

    
        
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
