'''Annotating title and abstract for biological terms with BECAS'''

import becas
import sys
import pandas as pd
import csv
import time
from preprocessing_data import printProgressBar

def becas_annotation(title,abstract,email):
    
    '''
    Annotating title and abstract for biological terms with BECAS
    Input: text from title and abstract from pubmed_scrap.py output
    '''
    becas.email=email
    try:
        title_annotate=becas.annotate_text(title)
    except AttributeError:
        title_annotate={'entities':['nothingggggggg']}        
    try:
        abstract_annotate=becas.annotate_text(abstract)
    except AttributeError:
        abstract_annotate={'entities':['nothingggggggg']}
    if not title_annotate['entities']:
        title_annotation='nothingggggggg'
    else:
        title_annotation=','.join([str.split(i,'|')[0] for i in title_annotate['entities']])
    if not abstract_annotate['entities']:
        abstract_annotation='nothingggggggg'
    else:
        abstract_annotation=','.join([str.split(i,'|')[0] for i in abstract_annotate['entities']])
    combined_annotation=','.join([title_annotation,abstract_annotation])
    return combined_annotation

def annotating_df_to_file(df,email,filename):
    
    '''
    Make sure the columns of the dataframe is defined as follows:
    'Title', 'MeshHeadIndex', 'Abstract', 'Date', 'Type','PMID' 
    
    Take input the csv file. Note to remove the header. 
    Output: A new csv file with annotated biological terms.
    '''
    
    chunksize=10
    for chunk_i in range(0,df.shape[0],chunksize):
        chunk=df.iloc[chunk_i:chunk_i+chunksize,:]
        with open(filename,'a+',newline='') as data_file:
            file_writer=csv.writer(data_file,delimiter=',',quoting=csv.QUOTE_MINIMAL)
            for row in range(chunk.shape[0]):
                annotation=becas_annotation(chunk['Title'].iloc[row],chunk['Abstract'].iloc[row],email)
                file_writer.writerow([chunk['Title'].iloc[row],annotation,
                                      chunk['PMID'].iloc[row]])
        printProgressBar(iteration=chunk_i+chunksize,total=df.shape[0])#shows a progress bar on the console.
        time.sleep(3.0)#to not overload the system
    
    
    
    

if __name__ == "__main__":
    

    
    email=input('Email: ')
    df=pd.read_csv(sys.argv[1],header=None)
    df.columns=['Title','MeshHeadIndex','Abstract','Date','Type','PMID']
    filename=input('Output csv filename: ')
    annotating_df_to_file(df,email,filename)