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
                        lemmaWord = lemmatizer.lemmatize(word)
                        lemmaList.append(lemmaWord)
                
                self.lemma.append(lemmaList)        
                self.pos.append(posList)
                self.ner.append(ner)
            
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
            
#%% Functions
def ReadStoryFile(file, type, stories):
      
    text = open(file)
    story = text.read()    
    stories.append(type(story))


def main():
    responseFile = 'responseFile.csv'
    stories = []
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
            questions[id] = []
            for line in lines:
                if(line == "\n"):
                    continue
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
                    rmv = []
                    for ps in pos_lemm:
                        t = ''
                        if ps[1] == 'WDT':
                            t = "wh-determiner"
                            rmv.append(ps)
                    #that what whatever whatsoever which who whom whomsover
                        elif ps[1] == 'WP':
                            t = "wh-pronoun"
                            rmv.append(ps)
                    #whose
                        elif ps[1] == 'WP$':
                            t = "wh-pronoun-possessive"
                            rmv.append(ps)
                    #how however whence whenever where whereby whereever wherein whereof why
                        elif ps[1] == 'WRB':
                            rmv.append(ps)
                            t = "wh-adverb"
                        elif ps[0] in stop:
                            rmv.append(ps)
                    for rm in rmv:
                        if rm in pos_lemm:
                            pos_lemm.remove(rm)
                    questions[id].append(pos_lemm)
        #print(questions)
        
        ReadStoryFile(storyFile, Story, stories)
        
        bestSentenceMatch = []
        bestSentenceLocation = []
        #print(stories[id])
        for i in range(0, len(questions[id])):
            bestSentenceMatchCount = 0
            qid = str(id[len(path):])+"-"+str(i+1)
            #print("QUESTION " + qid + " "+ str(questions[id][i]))
            qlist = []
            for word in questions[id][i]:
                qlist.append(word[0])
                
            for story in stories:
                if story.storyID == str(id[len(path):]):
                    location = 0
                    for sentence in story.lemma:

                        overlap = list(set(qlist) & set(sentence))
                        print(overlap)
                        
                        if len(overlap) == bestSentenceMatchCount:
                            bestSentenceMatchCount = len(overlap)
                            bestSentenceMatch.append(sentence)
                            bestSentenceLocation.append(location)
                            
                        if len(overlap) > bestSentenceMatchCount:
                            bestSentenceMatchCount = len(overlap)
                            bestSentenceMatch.clear()
                            bestSentenceLocation.clear()
                            bestSentenceMatch.append(sentence)
                            bestSentenceLocation.append(location)
                            
                        location += 1
            
                
                else:
                    continue
                
                print("MATCH: " +str(questions[id][i]) + "\n answerd by " + str(bestSentenceMatch))
            
            for j in range(0, len(stories[id])):
                overlap = list(set(questions[id][i]) & set(stories[id][j]))
                #print("OVERLAP: " + str(overlap))
                if len(overlap) == bestSentenceMatchCount:
                    bestSentenceMatchCount = len(overlap)
                    bestSentenceMatch.append(sentence)
                if len(overlap) > bestSentenceMatch:
                    bestSentenceMatchCount = len(overlap)
                    bestSentenceMatch[qid] = sentence
                    
                    
            print("MATCH: " +str(questions[id][i]) + "\n answerd by " + str(bestSentenceMatch[qid]))
        print(bestSentenceMatch)
        with open(responseFile) as rf:
            writer = csv.writer(responseFile)
            for q in range(len(questions)):
                for a in range(answers):
                    writer.writerow("QuestionID: " + id + a)
                    writer.writerow("Answer: " + answers[a])
            
if __name__ == "__main__":
    main()


    
 # with open(storyFile) as sfile:
 #     lines = sfile.readlines()
 #     stories[id] = []
 #     sentences = []
 #     for line in lines:
 #         if(line == "\n"):
 #             continue
 #         l = line.split()
 #         tag = l[0].strip()
 #         #begin reading
 #         if (tag!= "TEXT:" and tag!= "HEADLINE:" and tag!= "DATE:" and tag!= "STORYID:"):
 #             if(line == "\n"):
 #                 continue
 #             sentence = line.strip().lower()
 #             #print("SENTENCE: " + sentence)
 #             token_s = word_tokenize(sentence)
 #             #pos tag
 #             pos_s = pos_tag(token_s)
 #             rmv = []
 #             for word in pos_s:
 #                 if word[0] in stop:
 #                     rmv.append(word)
 #             for rm in rmv:
 #                 if rm in pos_s:
 #                     pos_s.remove(rm)
 #             #lemme uses different tag system 
 #             lemm_tags = []
 #             for ps in pos_s:
 #                 if ps[1].startswith('N'):
 #                     lemm_tags.append((ps[0], 'n'))
 #                 elif ps[1].startswith('V'):
 #                     lemm_tags.append((ps[0], 'v'))
 #                 elif ps[1].startswith('R'):
 #                     lemm_tags.append((ps[0], 'r'))             
 #                 elif ps[1].startswith('J'):
 #                     lemm_tags.append((ps[0], 'a'))
 #                 else:
 #                     lemm_tags.append((ps[0], ''))
 #             #lemma
 #             lemmatizer = WordNetLemmatizer()
 #             lemm_s = []
 #             for wrd in lemm_tags:
 #                 if(wrd[1]!= ''):
 #                     lemm_s.append(lemmatizer.lemmatize(wrd[0], pos=wrd[1]))
 #                 else:
 #                     lemm_s.append(wrd[0])
 #             #combine lemmatized with proper pos
 #             for i in range(0, len(lemm_s)):
 #                 sentences.append((lemm_s[i], pos_s[i][1]))
 #     sentenceStarts = []
 #     sentenceEnds = []
 #     currentSentence = []
 #     newSentence = True
 #     for i in range(0, len(sentences)):
 #         if newSentence:
 #             sentenceStarts.append(i)
 #             newSentence = False
 #         elif sentences[i][1] == ".":
 #             sentenceEnds.append(i+1)
 #             newSentence = True
 #     for i in range(0, len(sentenceStarts)):
 #         stories[id].append(sentences[sentenceStarts[i]:sentenceEnds[i]-1])

     # for sent in stories[id]:
     #     print("SENTENCE: ")
     #     for word in sent:
     #         print(str(word[0]))
 
         #read through story and look for answers based on the question's parts we parsed
         #if a word in line contains what we are looking for, put it down as the answer