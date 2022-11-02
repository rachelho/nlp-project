import sys
import csv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
def main():
    responseFile = 'responseFile.csv'
    stories = []
    #each questions key is the id, followed by the type of question, then the question itself
    questions = {}
    ids = []
    stop = stopwords.words('english')
    with open(sys.argv[1]) as input:
        lines = input.readlines()
        path = lines[0]
        for qids in lines[1:]:
            qid = qids.strip()
            ids.append(qid)
    for id in ids:
        questionFile = id + ".questions"
        storyFile = id + ".story"
        answers = []
        with open(questionFile) as qfile:
            lines = qfile.readlines()
            questionCount = 0
            questions[id] = []
            for line in lines():
                l = line.split()
                tag = l[0]
                item = l[1:]
                # if(tag == "QuestionID:"):
                #     questionId = str(item)
                if (tag== "Question:"):
                    q = ""
                    #convert to string for token; not sure if necessary
                    for w in item:
                        question+= w
                    token_q = word_tokenize(q)
                    #remove stop words
                    for wr in token_q:
                        if wr in stop:
                            token_q.pop(wr)
                    #pos tag
                    pos_q = pos_tag(token_q)
                    #lemma
                    lemmatizer = WordNetLemmatizer()
                    lemm_q = []
                    for wrd in pos_q:
                        lemm_q.append(lemmatizer.lemmatize(wrd[0], pos=wrd[1]))
                    #that, what, whatever, which, whichever
                    for ps in pos_q:
                        if ps[0] == 'WDT':
                            t = "wh-determiner"
                            questions[id][t] = pos_q
                    #that what whatever whatsoever which who whom whomsover
                        if ps[0] == 'WP':
                            t = "wh-pronoun"
                            questions[id][t] = pos_q
                    #whose
                        if ps[0] == 'WP$':
                            t = "wh-pronoun-possessive"
                            questions[id][t] = pos_q
                    #how however whence whenever where whereby whereever wherein whereof why
                        if ps[0] == 'WRB':
                            t = "wh-adverb"
                            questions[id][t] = pos_q
                    
        with open(storyFile) as sfile:
            lines = sfile.readlines()
            for line in lines():
                l = line.split()
                #read through story and look for answers based on the question's parts we parsed
                #if a word in line contains what we are looking for, put it down as the answer
        with open(responseFile) as rf:
            writer = csv.writer(responseFile)
            for q in range(len(questions)):
                for a in range(answers):
                    writer.writerow("QuestionID: " + id + a)
                    writer.writerow("Answer: " + answers[a])
        for q in questions[id]:
            
if __name__ == "__main__":
    main()
    
    
#%% Classes
class Story():
    
    def __init__(self, story):
        
        self.story = story.strip()
        self.sentences = sent_tokenize(story)
        self.pos = []
        self.lemma = []
        lemmatizer = WordNetLemmatizer()
        
        
        for token in self.sentences:
            # Grab the story information
            if token.startswith("HEADLINE: "):
                lines = token.split('\n')
                for line in lines:
                    if line.startswith("HEADLINE: "):
                        self.headline = line.lstrip("HEADLINE: ")
                        
                    elif line.startswith("DATE: "):
                        self.date = line.lstrip("DATE: ")
                        
                    elif line.startswith("STORYID: "):
                        self.storyID = line.lstrip("STORYID: ")
                    
                    elif line.startswith("TEXT:"):
                         break
            
            else:
                break
    
        # Remove the Headline, Date, etc. from the first sentence (121 - 140)
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
            words = word_tokenize(sentence)
            pos = nltk.pos_tag(words)
            posList = []
            for tag in pos:
                posList.append(tag)
            self.pos.append(posList)
        
        # Lemmatize each word in the sentence and store it as a list 
        for sentence in self.sentences:
            words = word_tokenize(sentence)
            lemmaList = []
            
            for word in words:
                lemmaWord = lemmatizer.lemmatize(word)
                lemmaList.append(lemmaWord)
            
            self.lemma.append(lemmaList)
        
        return
            
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

for story in stories:
    ReadFile(story, Story)