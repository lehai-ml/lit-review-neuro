# Visualising Pubmed publications with Pubmed API, BeCAS and BioWordVect to aid literature review process

#### Table of content
1. [Objective](#objective)
2. [Methods](#methods)
    * [Pubmed scrapping](##pubmed-scrapping)
    * [BeCAS Annotation](##becas-annotation)
    * [BioWordVect Word Embedding](##biowordvect-word-embedding)
3. [Results](#results)
4. [References](#references)
5. [Packages requirement](#packages-requirement)
6. [Logs](#logs)


# Objective

Because my research question is so broad, to aid my literature review process, I want to visualise the current areas of research in the field of neurodevelopment and neuropsychiatry. Is there a particular biological pathway or neurodevelopmental process that is well-researched, has been examined across multiple model organims (including neonates and adults), and has relevance to neuropsychiatric disorders of interest. By doing a top-down analysis, I aim to find hypotheses, that are well-established in the literature (or not), for my next work with preterm neonates.

# Methods

## Pubmed scrapping

The [Pubmed API](https://www.ncbi.nlm.nih.gov/home/develop/api/) E-utilities allows access to all Entrez database including Pubmed, PMC, Gene, Nuccore and Protein.

With the [pubmed_scrapping](./pubmed_scrap.py) function I can specify the search term, number of documents I want organised by their relevance to the term. For each document, I return its title, [MeshHeading](https://www.nlm.nih.gov/mesh/meshhome.html), Abstract, Publication Date, and ID.

To run this function you need to specify the ```search_term```,```retmax```(number of documents),```retstart```(starting index),```email``` and output ```filename```.

## BeCAS Annotation

Although I can just use the MeshHeadings words, I can also get more information about the documents by looking at their abstracts and titles. However, because I didn't want to train a new word embedding with whole sentences from scratch (as there is already a good [pre-trained model](#biowordvect-word-embedding)), I used the biomedical concept recognition services and visualization tool ([BeCAS](https://pubmed.ncbi.nlm.nih.gov/23736528/)) and its [python package](http://tnunes.github.io/becas-python/) to annotate the key biological terminologies (it also has a web-interface [here](http://bioinformatics.ua.pt/becas/)). This BeCAS tool essentially acts as a big dictionary that performs part-of-sentence tagging and recognizes concepts of species, anatomical concepts, miRNAs, enzymes, chemicals, drugs, diseases, metabolic pathways, cellular components, biological processes, and molecular functions, which are compiled from multiple meta-sources such as UMLS and NCBI Biosystems.

With the [annotating_df_to_file](./annotate_pubmed.py) function I call BeCAS tool to annotate the titles and abstracts of the documents that I have gotten from [pubmed_scrap.py](./pubmed_scrap.py).

To use this function you need to specify the input ```df```, ```email```, and output ```filename```. The output will be another table containing the documents' titles, annotations and IDs.

## BioWordVect Word Embedding

Once I have gotten my two documents from the aboved mentioned functions. I [merge the annotations and MeshHeadings](./preprocessing_data.py) and specify the date range of my documents. I then use the combined annotations of MeshHeading and BeCAS to represent each document.

[BioWordVect](https://www.nature.com/articles/s41597-019-0055-0) is a pretrained word embedding that contains over 2.7 million tokens, and has been trained on a large body of PubMed abstracts and MeshHeadings. Rather than training on individual words as in Word2Vec, the authors trained on subwords, which is very useful in biomedical data, which contains many compound words. Here, each word in BioWordVect is represented by a 200-dimensional vector.

To run the [get_word_vector](./preprocessing_data.py), you need to download the [bio_embedding_intrinsic](https://figshare.com/articles/dataset/Improving_Biomedical_Word_Embeddings_with_Subword_Information_and_MeSH_Ontology/6882647/2) pretrained model.

# Results

See the appended notebook.


# References

Sayers, E. (2010) A General Introduction to the E-utilities. Entrez Program. Util. Help

Nunes, T., Campos, D., Matos, S., and Oliveira, J. L. (2013) BeCAS: Biomedical concept recognition services and visualization. Bioinformatics. 29, 1915–1916

Zhang, Y., Chen, Q., Yang, Z., Lin, H., and Lu, Z. (2019) BioWordVec, improving biomedical word embeddings with subword information and MeSH. Sci. Data. 6, 1–9

# Packages requirement

[biopython](https://biopython.org/wiki/Download), [becas](http://tnunes.github.io/becas-python/), [gensim](https://radimrehurek.com/gensim/) (which also requires smart_open and boto3)

# Logs:

19/09/2020- First uploaded





