# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 01:03:42 2022

@author: toryl
"""
import sys
from nltk.tokenize import sent_tokenize, word_tokenize

#%% Classes
class Story():
    
    def __init__(self, story):
        
        self.story = story
        self.sentences = sent_tokenize(story)
        
        
        
        for token in self.sentences:
            # Is it the headline?
            if token.startswith("HEADLINE: "):
                lines = token.split('\n')
                for line in lines:
                    if line.startswith("HEADLINE: "):
                        self.headline = line.lstrip("HEADLINE: ")
                        
                    elif line.startswith("DATE: "):
                        self.date = line.lstrip("DATE: ")
                        
                    elif line.startswith("STORYID: "):
                        self.storyID = line.lstrip("STORYID: ")
                    
                    elif line.startswith("TEXT:") or line.startswith(''):
                        break
                    
        return
            # if token.startswith(start) and token.endswith(end):
            #     # Get rid of identifiers 
            #     self.target = token.lstrip(start).rstrip(end)
            #     return
            # self.spot += 1
            
#%% Functions
def ReadFile(file, type):
    
    stories = []
    answers = []
    questions = []
    
    text = open(file)
    
    
    # while True:
    #     line = text.readline()
    #     if not line or line == "\n":
    #         text.close()
    #         return sentences
        
    if type is None: # If we want to go this route then we just need to implement for each type
        while True:
            line = text.readline()
            if not line or line == "\n":
                text.close()
                return answers
        
        answers.append(line.strip())
                   
        # Should be the TestSentence and Sense
    
    elif type is Story:
        story = text.read()    
        stories.append(type(story))
    
        
    else: 
        questions.append(type(story))
            
#%% Main
story = sys.argv[1]
ReadFile(story, Story)
