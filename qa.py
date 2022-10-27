import sys, csv
from nltk.tokenize import sent_tokenize, word_tokenize

def main():
    responseFile = 'responseFile.csv'
    with open(sys.argv[1]) as input:
        lines = input.readlines()
        path = lines[0]
        stories = []
        ids = []
        opList = []
        wordCount = 0
        for qids in lines[1:]:
            qid = qids.strip()
            ids.append(qid)
    for id in ids:
        questionFile = id + ".questions"
        storyFile = id + ".story"
        questions = []
        answers = []
        with open(questionFile) as qfile:
            lines = qfile.readlines()
            for line in lines():
                l = line.split()
                tag = l[0]
                if (tag== "Question:"):
                    questions.append(l[1])
                    #for each question we probably look for the who, what, where, why
                    #followed by subject/objects probably using root form
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