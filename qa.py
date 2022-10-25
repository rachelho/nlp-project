import sys
import csv
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