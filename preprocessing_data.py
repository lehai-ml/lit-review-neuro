
import pandas as pd
import numpy as np
import time
from unidecode import unidecode
import difflib
import gensim #need to have pyemd, boto3 and smart_open
from gensim.models import KeyedVectors
from itertools import combinations



def printProgressBar (iteration, total, prefix = 'Progress', suffix = 'Complete', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
        
def lower_case_and_hyphenated(string):
    '''
    Make the string compatible with the Biovect word dictionary
    '''
    string=string.strip().lower()
    string=string.replace(' ','-')
    return unidecode(string)
    
def remove_value_from_list(list,val):
    return [value for value in list if value!=val]

def merge_annotations(original_mesh_data,becas_data):
    '''
    Merge the Mesh_Data column with the becas column
    Input: the two .csv file from the annotated_pubmed and pubmed_scrap
    original_mesh_data.columns=['Title','MeshHead','Abstract','Date','Type','PMID']
    becas_data.columns=['Title','Becas','PMID']
    '''
    if len(set(original_mesh_data.PMID).symmetric_difference(set(becas_data.PMID)))!=0:
        print('the PMID do not correspond to each other, check again')
        #sanity check
        for i in range(len(original_mesh_data.PMID)):
            if original_mesh_data['PMID'].iloc[i]!=becas_data['PMID'].iloc[i]:
                print('not corresponding at %d'%i)
                
    else:
        combined_data_Mesh_Becas=[','.join([original_mesh_data['MeshHead'][i],becas_data['Becas'][i]]) for i in range(len(original_mesh_data['MeshHead']))]
        combined_data_Mesh_Becas=[list(map(lower_case_and_hyphenated,i.split(','))) for i in combined_data_Mesh_Becas]#removing the leading whitespaces and use lowercase to avoid confusions
        

#         remove any 'nothing':
        emptyList=[]
        for idx,i in enumerate(combined_data_Mesh_Becas):
            combined_data_Mesh_Becas[idx]=remove_value_from_list(i,'nothingggggggg')
            if not i:
                print('the following idx are empty %d'%idx) # if any of the combined list is empty. print out the idx.
                emptyList.append(idx)

        new_data=pd.DataFrame({'Title':list(original_mesh_data['Title']),
                      'Date':list(original_mesh_data['Date']),
                      'Combined_Annotation':[','.join(i) for i in combined_data_Mesh_Becas],
                      'PMID':list(original_mesh_data['PMID'])})
                    
        
        new_data=new_data[~new_data.index.isin(emptyList)] # removes any rows that do not have any annotations.
        return new_data

def checkdate(date,threshold=2010):
    try:
        year=int(str.split(date,'-')[0])
        return year>=threshold
    except TypeError:
        return False
    

def most_common_key(model,key_words,number=3,return_counts=False):
    '''
    Essentially pulls out the most common words, such that words that are semantically close will be grouped together. E.g. 'inflammation' and 'inflammation-mediators' are similar and have high cosine similarity score, will be grouped together under one count.
    
    Input: model- that is the pretrained word embedding
    key_words=whatever the keywords, that is in string format, seperatable by comma.
    number= number of common words to extract
    return_counts= for pie chart, to return the number of highest counts.
    
    
    '''
    keys,counts=np.unique(str.split(key_words,','),return_counts=True)
    idx=np.argsort(counts)[::-1]

    if len(counts)>=2:
        combo=combinations(keys[idx],r=2)
        for i in combo:
            word1,word2=i
            count1,count2=counts[(np.where(keys==word1)[0])[0]],counts[(np.where(keys==word2)[0])[0]]
            if count1==0 or count2==0:
                continue
            similarity=(model.similarity(word1,word2))#this is necessary to make sure that semantically similar words are not excluded.
            if similarity>0.70:
                counts[(np.where(keys==word1)[0])[0]]+=count2
                counts[(np.where(keys==word2)[0])[0]]=0

        idx=np.argsort(counts)[::-1] #updated idx

    if return_counts:
        return (','.join(keys[idx[:number]]),np.sort(counts)[::-1][:number])
    else:
        return ','.join(keys[idx[:number]])
    

class Paper:
    '''
    Defining a paper, its attribute will be title, combined becas annotation and meshheadings, PMID, and mean vector of the combined annotation according to the Biovector word embedding.
    
    Requires INPUT:
    Title,combined_annotation of becas and meshheadings, PMID, the meshheading list and word embedding from Biovect.
    
    
    '''
    def __init__(self,title,date,key_words,PMID,meshhead_list,word_embedding):
        self.title=title
        self.date=date
        self.key_words=key_words
        self.PMID=PMID
        (self.vector,self.new_key_words)=self.get_word_vector(meshhead_list,word_embedding)
        self.word_embeddings=np.mean(self.vector,axis=0)
    
            
    def get_word_vector(self,meshhead_list,word_embedding):
        '''
        Essentially, this will search against the word embeddings if the word of interest exist. If yes, it will output the vector for that word. The mean vector of all word will represent the paper on the 200-dimensional space.
        
        Input: Run the following to generate a meshead_list, this is just the list of all mesh_headings you have in your documents. This is used to find the best matched word in the Becas, in case it is not recognised by the word_embedding dictionary.
        sorted_mesh_head=sorted(list(set(str.split(','.join(data['MeshHead']),','))))
        sorted_mesh_head=list(map(preprocessing_data.lower_case_and_hyphenated,sorted_mesh_head))
        '''
        vectors=[]
        new_key_words=[]
        for word in self.key_words.split(','):
            try:
                vectors.append(word_embedding.get_vector(word))
                new_key_words.append(word)    
            except KeyError:
                subwords=str.split(word,'-') # in case that the double word does not exist in the word embedding dictionary. I will divide them and try them separately.
                for subword in subwords:
                    try:
                        vectors.append(word_embedding.get_vector(subword))
                        new_key_words.append(subword)
                    except KeyError:
                        try:
                            vectors.append(word_embedding.get_vector(''.join([letter for letter in subword if letter.isalnum()])))#in case the subword doesn't work because of the special characters, i will remove them.
                            new_key_words.append(''.join([letter for letter in subword if letter.isalnum()]))
                        except KeyError:
                            try:
                                closest_word=difflib.get_close_matches(subword,meshhead_list)#in case this doesn't work, I will find the nearest word in the mesh-heading.
                                if not closest_word:
                                    #remove the word from the combined annotation
                                    print(subword+' is not in the dict')
                                    pass
                                else:
                                    vectors.append(word_embedding.get_vector(closest_word[0]))
                                    new_key_words.append(closest_word[0])
                            except KeyError:
                                #remove the word from the combined annotation
                                print(subword+' is not in the dict')
                                pass
        return vectors,','.join(new_key_words)
                                
                
            

        
        
        



        
