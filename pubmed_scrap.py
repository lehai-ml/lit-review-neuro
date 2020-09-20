'''
webscraper
conda install -c conda-forge biopython
no more than 3 URL request per second and limit large jobs to either weekends or between 9:PM and 5:00 AM eastern time.
'''


from Bio import Entrez
import csv
import time
from preprocessing_data import printProgressBar

def search(query,retmax,retstart,email):
    '''
    This func will pull unique IDs of articles, which are sorted by relevance.
    Retmax= number of articles, limit the large jobs to avoid bans.
    Retstart= start from an index.
    '''
    Entrez.email=email
    handle=Entrez.esearch(db='pubmed',
                          sort='relevance',
                          retmax=retmax, retstart=retstart,
                          retmode='xml',
                          term=query)
    results=Entrez.read(handle)
    return results

def fetch_details(id_list,email):
    '''
    This func takes the ID list and fetch the actual information of the paper
    '''
    ids=','.join(id_list)
    Entrez.email=email
    handle=Entrez.efetch(db='pubmed',
                         retmode='xml',
                         id=ids)
    results=Entrez.read(handle)
    return results


def pubmed_scrapping(search_term,retmax,retstart,email,filename):
    
    '''
    Input the search term, fetch articles in chunk size of 50.
    Output to a csv table: Title, MeshHeadingList, Abstract, Date, Publication Type.
    '''
    chunk_size=50
    results=search(search_term,retmax,retstart,email)
    id_list=results['IdList']
    for chunk_i in range(0,len(id_list),chunk_size):
        chunk=id_list[chunk_i:chunk_i+chunk_size]
        with open(filename, mode='a+',newline='') as data_file:
            file_writer=csv.writer(data_file,delimiter=',',quoting=csv.QUOTE_MINIMAL)
            papers=fetch_details(chunk,email)
            printProgressBar(iteration=chunk_i+chunk_size,
                                total=len(id_list))
            time.sleep(3.0) # to not overload the system.
            for i,paper in enumerate(papers['PubmedArticle']):
                try:
                    title=paper['MedlineCitation']['Article']['ArticleTitle']
                except: #just in case the paper doesn't have title.
                    title='nothingggggggg'
                try:
                    PMID=paper['MedlineCitation']['PMID']
                except:
                    PMID='nothingggggggg'
                try:
                    meshidx=','.join([str(x['DescriptorName']) for x in paper['MedlineCitation']['MeshHeadingList']])
                except KeyError:
                    meshidx='nothingggggggg'
                try:
                    abstract=' '.join((str.split(paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0],' '))[:])
                except KeyError:
                    abstract='nothingggggggg'
                try:
                    date='-'.join([value for key,value in paper['MedlineCitation']['Article']['ArticleDate'][0].items()])
                except IndexError:
                    date='NA'
                try:
                    publication=str(paper['MedlineCitation']['Article']['PublicationTypeList'][0])
                except:
                    publication='NA'            
                file_writer.writerow([title,meshidx,abstract,date,publication,PMID])
    

if __name__ == "__main__":
    

    search_term=input('Search terms:')
    # search_term='neurodevelopment'
    retmax=int(input('Retmax:'))
    retstart=int(input('Retstart:'))
    email=input('Email: ')
    filename=input('Output file name: ')
    pubmed_scrapping(search_term,retmax,retstart,email,filename)