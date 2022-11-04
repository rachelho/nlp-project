import sys
import csv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
def main():
    responseFile = 'responseFile.csv'
    stories = {}
    #each questions key is the id, followed by the type of question, then the question itself
    questions = {}
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
        with open(questionFile) as qfile:
            lines = qfile.readlines()
            questionCount = 0
            questions[id] = {}
            for line in lines:
                if(line == "\n"):
                    break
                l = line.split()
                tag = l[0]
                # if(tag == "QuestionID:"):
                #     questions[l[1].strip()] = {}
                # if(tag == "QuestionID:"):
                #     questionId = str(item)
                if (tag== "Question:"):
                    item = l[1:]
                    question = ""
                    #convert to string for token; not sure if necessary
                    for w in item:
                        question+= w
                        question+= " "
                    question = question.strip().lower()
                    token_q = word_tokenize(question)
                    #remove question mark
                    if(token_q[len(token_q)-1][0]) == "?":
                        token_q.pop()
                    #pos tag
                    pos_q = pos_tag(token_q)
                    rmv = []
                    for word in pos_q:
                        if word[0] in stop:
                            rmv.append(word)
                    for rm in rmv:
                        if rm in pos_q:
                            pos_q.remove(rm)
                    #lemme uses different tag system 
                    lemm_tags = []
                    for pq in pos_q:
                        if pq[1].startswith('N'):
                            lemm_tags.append((pq[0], 'n'))
                        elif pq[1].startswith('V'):
                            lemm_tags.append((pq[0], 'v'))
                        elif pq[1].startswith('R'):
                            lemm_tags.append((pq[0], 'r'))             
                        elif pq[1].startswith('J'):
                            lemm_tags.append((pq[0], 'a'))
                        else:
                            lemm_tags.append((pq[0], ''))
                    #lemma
                    lemmatizer = WordNetLemmatizer()
                    lemm_q = []
                    for wrd in lemm_tags:
                        if(wrd[1]!= ''):
                            lemm_q.append(lemmatizer.lemmatize(wrd[0], pos=wrd[1]))
                        else:
                            lemm_q.append(wrd[0])
                    #combine lemmatized with proper pos
                    pos_lemm = []
                    for i in range(0, len(lemm_q)):
                        pos_lemm.append((lemm_q[i], pos_q[i][1]))
                    #that, what, whatever, which, whichever
                    for ps in pos_q:
                        t = ''
                        if ps[1] == 'WDT':
                            t = "wh-determiner"
                            pos_q.remove(ps)
                            questions[id][t] = pos_q
                    #that what whatever whatsoever which who whom whomsover
                        if ps[1] == 'WP':
                            t = "wh-pronoun"
                            pos_q.remove(ps)
                            questions[id][t] = pos_q
                    #whose
                        if ps[1] == 'WP$':
                            t = "wh-pronoun-possessive"
                            pos_q.remove(ps)
                            questions[id][t] = pos_q
                    #how however whence whenever where whereby whereever wherein whereof why
                        if ps[1] == 'WRB':
                            t = "wh-adverb"
                            pos_q.remove(ps)
                            questions[id][t] = pos_q
        #print(questions)
        with open(storyFile) as sfile:
            lines = sfile.readlines()
            stories[id] = []
            sentences = []
            for line in lines:
                if(line == "\n"):
                    continue
                l = line.split()
                tag = l[0].strip()
                #begin reading
                if (tag!= "TEXT:" and tag!= "HEADLINE:" and tag!= "DATE:" and tag!= "STORYID:"):
                    if(line == "\n"):
                        continue
                    sentence = line.strip().lower()
                    #print("SENTENCE: " + sentence)
                    token_s = word_tokenize(sentence)
                    #pos tag
                    pos_s = pos_tag(token_s)
                    rmv = []
                    for word in pos_s:
                        if word[0] in stop:
                            rmv.append(word)
                    for rm in rmv:
                        if rm in pos_s:
                            pos_s.remove(rm)
                    #lemme uses different tag system 
                    lemm_tags = []
                    for ps in pos_s:
                        if ps[1].startswith('N'):
                            lemm_tags.append((ps[0], 'n'))
                        elif ps[1].startswith('V'):
                            lemm_tags.append((ps[0], 'v'))
                        elif ps[1].startswith('R'):
                            lemm_tags.append((ps[0], 'r'))             
                        elif ps[1].startswith('J'):
                            lemm_tags.append((ps[0], 'a'))
                        else:
                            lemm_tags.append((ps[0], ''))
                    #lemma
                    lemmatizer = WordNetLemmatizer()
                    lemm_s = []
                    for wrd in lemm_tags:
                        if(wrd[1]!= ''):
                            lemm_s.append(lemmatizer.lemmatize(wrd[0], pos=wrd[1]))
                        else:
                            lemm_s.append(wrd[0])
                    #combine lemmatized with proper pos
                    for i in range(0, len(lemm_s)):
                        sentences.append((lemm_s[i], pos_s[i][1]))
            sentenceStarts = []
            sentenceEnds = []
            currentSentence = []
            newSentence = True
            for i in range(0, len(sentences)):
                if newSentence:
                    sentenceStarts.append(i)
                    newSentence = False
                elif sentences[i][1] == ".":
                    sentenceEnds.append(i+1)
                    newSentence = True
            for i in range(0, len(sentenceStarts)):
                stories[id].append(sentences[sentenceStarts[i]:sentenceEnds[i]-1])
                #read through story and look for answers based on the question's parts we parsed
                #if a word in line contains what we are looking for, put it down as the answer
        # with open(responseFile) as rf:
        #     writer = csv.writer(responseFile)
        #     for q in range(len(questions)):
        #         for a in range(answers):
        #             writer.writerow("QuestionID: " + id + a)
        #             writer.writerow("Answer: " + answers[a])
            
if __name__ == "__main__":
    main()
    
    
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