# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 21:47:01 2022

@author: toryl
"""

import gensim, sys, numpy as np

ids = []
stories = []

#%% Function

# I have been using https://www.youtube.com/watch?v=Q2NtCcqmIww to see what to do here
def TrainModel (fileName):
    '''This will make a list of all the stories and then train a model based on the given stories'''
    
    stories = []
    
    # Read in all the story names into a list
    with open(fileName) as input:
        lines = input.readlines()
        path = lines[0].strip()
        for qids in lines[1:]:
            qid = qids.strip()
            ids.append(path + qid)
            for id in ids:
                storyFile = id + ".story"
                stories.append(storyFile)
    
    storyList = []
    
    # Read all the stories into a list so we can train the model
    for story in stories:
        try:
            with open(story, "r", encoding = "utf-8") as f:
                 storyList.append(f.read())
        except:
            pass
        
    cleanStory = []   
    # 'Normalize the vocab
    for story in storyList:
        cleanStory.append(gensim.utils.simple_preprocess(story))
        
    #print(cleanStory)
    model = gensim.models.Word2Vec(cleanStory, vector_size = 150, window = 10, min_count = 2, workers = 4)
    model.build_vocab(cleanStory, progress_per = 750)
    # print(model.epochs)
    # print(model.corpus_count)
    # print(model.corpus_total_words)
    print(model.train(cleanStory, total_examples = model.corpus_count, epochs = model.epochs))
    # model.save("./word2vec_QA.model")
#%% Testing
    print(model.wv.most_similar("scotia"))
#%%
    
    words = list(model.wv.index_to_key)
    vectors = []
    # for word in words:
    #     vectors.append(model[word].tolist())
    # data = np.array(vectors)
    # print(data)
    return    
                
def main():

    filename = sys.argv[1]
    TrainModel(filename)
    
if __name__ == "__main__":
    main()