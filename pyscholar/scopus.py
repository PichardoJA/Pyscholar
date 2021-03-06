import ConfigParser, os

class Key_Exception(Exception):
    def __str__(self):
        return "Scopus key not set."

keys = ConfigParser.ConfigParser()
pyscholarDir = os.path.join(os.path.expanduser("~"), ".pyscholar")
keys.read(os.path.join(pyscholarDir, 'keys.cfg'))
MY_API_KEY = keys.get('Keys', 'Scopus')

if MY_API_KEY == "":
    ans = raw_input("Scopus key not set. Do you want to set it now? (y/n) ")
    if ans.lower() == 'y':
        key = raw_input("Your scopus api key: ")
        keys.set('Keys', 'Scopus', key)
        cfgfile = open(os.path.join(pyscholarDir, 'keys.cfg'), 'w')
        keys.write(cfgfile)
        cfgfile.close()
        MY_API_KEY = key
    else:
        raise Key_Exception

import requests
import networkx as nx
import os
import itertools as it
import math
import pandas as pd
import matplotlib.pyplot as plt

search_api_author_url = "http://api.elsevier.com/content/search/author?"
search_api_scopus_url = "http://api.elsevier.com/content/search/scopus?"
search_api_abstract_url = "http://api.elsevier.com/content/abstract/scopus_id/"
search_api_author_id_url="http://api.elsevier.com/content/author/author_id/"
search_api_affiliation_url = "http://api.elsevier.com/content/search/affiliation?"
retrieve_api_affiliation_url="http://api.elsevier.com/content/affiliation/affiliation_id/"

headers = {"Accept":"application/json", "X-ELS-APIKey": MY_API_KEY}

scopus_authors_by_idpapers_cache=dict()
scopus_papers_by_authorid_cache=dict()
scopus_references_by_idpaper_cache=dict()

#Un diccionario con las listas
Scopus_ids_merged_rep={}
Scopus_ids_merged_lists={}

#Voy a poner aqui lo que falta por hacer (TODO list)

#Funciones para manejar las ids, hago implementaciones ingenuas que
#despues mejoraremos
#Vean https://en.wikipedia.org/wiki/Disjoint-set_data_structure

class Scopus_Exception(Exception):
    def __init__(self, resp):
        self.code = resp.status_code
        resp = resp.json()
        resp = resp[u'service-error'][u'status']
        self.statusCode=resp[u'statusCode']
        self.statusText=resp[u'statusText']
    def __str__(self):
        return "%s: %s"%(self.statusCode, self.statusText)


def load_authors_from_file(path=""):
    """
    Reads a file where each line of the file is an author id.
    """
    try:
        with open(directory, 'r') as f:
            return [str(line.strip()) for line in f]
    except IOError :
        print "Could not read file:", directory


def load_papers_from_file(path=""):
    """
    Reads a file where each line of the file is an paper id.
    """
    try:
        with open(directory, 'r') as f:
            return [line.strip() for line in f]
    except IOError :
        print "Could not read file:", directory


def _add_scopus_id(scopus_id):
    """
    Adds a scopus id to the merged list. Returns False if the ID is already in 
    the merged list and false otherwise
    """

    #Buscamos a ver si ya estaba en algunas lista, de ser
    #asi no hacemos nada
    for x in Scopus_ids_merged_lists:
        if scopus_id in D[x]:
            return False


    #No tiene "padre" y por tanto es la raiz
    Scopus_ids_merged_rep[scopus_id]=None

    #De momento el es el unico de la lista
    Scopus_ids_merged_lists[scopus_id]=[scopus_id]

    return list


def _get_root_id(scopus_id):
    """Follows the path of parents until it finds the root"""

    #Si no esta en la lista de representantes pues no hay nada que hacer
    if scopus_id not in Scopus_ids_merged_rep:
        return scopus_id


    root_scopus_id=scopus_id
    parent_scopus_id=t_scopus_id

    #seguimos los apuntadores hasta llegar a la raiz
    while Scopus_ids_merged_rep[root_scopus_id]!=None:
        root_scopus_id=Scopus_ids_merged_rep[root_scopus_id]

    return root_scopus_id

def _get_alias_list_id(scopus_id):
    """returns the list of alias id"""
    #En Scopus_ids_merged_lists[root_id] se van a guardar la lista
    #de alias

def _union_alias_id(scopus_id_1,scopus_id_2):
    #Junta a la lista de scopus_id_1 y scopus_id_2
    pass


def _get_alias_id(scopus_id):
    pass

###FIN DE FUNCIONES de IDs
def disable_graphical_interface():
    """
    Disables the graphical environment.
    """
    #import matplotlib.pyplot as plt
    plt.switch_backend('Agg')

def enable_graphical_interface():
    """
    Enables the graphical environment.
    """
    #['pdf', 'pgf', 'Qt4Agg', 'GTK', 'GTKAgg', 'ps', 'agg', 'cairo', 'MacOSX', 'GTKCairo', 'WXAgg', 'template', 'TkAgg', 'GTK3Cairo', 'GTK3Agg', 'svg', 'WebAgg', 'CocoaAgg', 'emf', 'gdk', 'WX']
    plt.switch_backend('GTK')




def load_graph_pickle(path=""):
    """
    Loads a graph object saved using :mod:`pickle` and returns a networkx graph object.
    """
    return nx.read_gpickle(path)

def save_graph_pickle(G,path="",name_graph=""):
    """
    Saves a graph object using :mod:`pickle`.
    """
    nx.write_gpickle(G,path+name_graph+".gpickle")

def find_affiliation_scopus_id_by_name(organization=""):
    """
    Returns a data frame which contains all matches found by the search of an affiliation name.
    """    
    searchQuery = "query=affil("+organization+")"
    fields = ""
    resp = requests.get(search_api_affiliation_url+searchQuery+fields, headers=headers)
    if resp.status_code != 200:
            raise Scopus_Exception(resp)
    id_affil=[]
    data = resp.json()
    data = data['search-results']
    if data["opensearch:totalResults"] == '0':
        print "None"
        return None
    affiliation_scopus_id_by_name=dict()
    for entry in data['entry']:
        affiliation_name=entry['affiliation-name']
        identifier=entry['dc:identifier']
        ident=entry['dc:identifier'].split(":")[1]
        #affil_id = entry['dc:identifier'].split(':')
        eid= entry["eid"]
        document_count=entry['document-count']
        if 'country' in entry.keys():
            country =entry['country']
        else:
            country=""
        if 'city' in entry.keys():
            city =entry['city']
        else:
            city=""
        list_names_variants=[]
        if 'name-variant' in entry.keys():
            for name_variant in entry['name-variant']:
                list_names_variants.append(name_variant['$'])

        affiliation_scopus_id_by_name[str(ident)]={'affiliation_name':affiliation_name,'identifier':str(identifier),'eid':str(eid),'document_count':int(document_count),'country':str(country),'city':str(city),'name_variant':list_names_variants}
    table=[]
    for id_affiliation,attributes_affil in affiliation_scopus_id_by_name.items():
        register=[]
        register.append(id_affiliation)
        for key_val,val_affil in attributes_affil.items():
            register.append(val_affil)
        table.append(register)
    headers_table=['id', 'city', 'country', 'name_variant', 'eid', 'affiliation_name', 'identifier', 'document_count']
    affiliation_table=pd.DataFrame(table)
    for i in range(len(headers_table)):
        affiliation_table.rename(index=str, columns={i:headers_table[i]},inplace=True)
    affiliation_table.sort_values(['document_count'],ascending=[False],inplace=True)
    affiliation_table = affiliation_table.reset_index(drop=True)

    return affiliation_table

def search_affiliation_by_id(list_scopus_id_affiliation):
    """
    This function returns a dictionary where the key is the ID of the
    affiliation and the value associated with the key is a dictionary
    with the following keys: date_created, preferred_name, author_count
    and document_count.

    :param list_scopus_id_affiliation: If you are looking for an affiliation, you can send the id as a string but if you want to multiple affiliations you can send a list of their ids.
    :type list_scopus_id_affiliation: String or List
    :returns: Dictionary where the key is the ID of theaffiliation and the value associated with the key is a dictionary with the following keys: date_created, preferred_name, author_count and document_count.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.search_affiliation_by_id("60017323")
    {'60017323': {'date_created': '03/02/2008', 'author_count': 5522, 'document_count': 19266, 'preferred_name': 'Centro de Investigacion y de Estudios Avanzados'}}
    >>> pyscholar.search_affiliation_by_id(["60017323","60018216"])
    {'60017323': {'date_created': '03/02/2008', 'author_count': 5522, 'document_count': 19266, 'preferred_name': 'Centro de Investigacion y de Estudios Avanzados'}, '60018216': {'date_created': '03/02/2008', 'author_count': 285, 'document_count': 1011, 'preferred_name': 'CINVESTAV Unidad Guadalajara'}}
    >>>
    
    """
    if isinstance(list_scopus_id_affiliation, str):
        list_scopus_id_affiliation=[list_scopus_id_affiliation]
    fields=""
    dict_affiliation_by_id=dict()
    for id_affiliation in list_scopus_id_affiliation:
        searchQuery = str(id_affiliation)
        resp = requests.get(retrieve_api_affiliation_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
        data=resp.json()
        data=data["affiliation-retrieval-response"]
        date_created=str(data["institution-profile"]['date-created']['@day']+"/"+data["institution-profile"]['date-created']['@month']+"/"+data["institution-profile"]['date-created']['@year'])
        preferred_name=str(data["institution-profile"]['preferred-name'])
        author_count=int(data['coredata']['author-count'])
        document_count=int(data['coredata']['document-count'])
        attributes={'date_created':date_created,'preferred_name':preferred_name,'author_count':author_count,'document_count':document_count}
        dict_affiliation_by_id[id_affiliation]=attributes
    return dict_affiliation_by_id

def get_authors_by_id_affiliation(list_scopus_id_affiliation):
    """
    This function returns a dictionary where the key is the ID of the
    paper and the value associated with the key is a set
    of the ids of the papers cited by the main paper.

    :param list_scopus_id_affiliation: If you are looking for an affiliation, you can send the id as a string but if you want to multiple affiliations you can send a list of their ids.
    :type list_scopus_id_affiliation: String or List
    :returns: Dictionary where the key is the ID of theaffiliation and the value associated with the key is a dictionary with the following keys: date_created, preferred_name, author_count and document_count.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.get_authors_by_id_affiliation("60017323")
    {'60017323': {'10039155200','10041045600','10041193100','10041905300','10043843600','10044307900','10138970000','10140877800',...,'10739229200'}
    >>>

    """    
    if isinstance(list_scopus_id_affiliation, str):
        list_scopus_id_affiliation=[list_scopus_id_affiliation]
    authors_by_id_affiliation=dict()
    for id_affiliation in list_scopus_id_affiliation:
        affiliation_attributes=search_affiliation_by_id(id_affiliation)
        author_count=affiliation_attributes[id_affiliation]["author_count"]
        iterations=math.ceil(author_count/200.0)
        chunks=[]
        for size_chunk in range(0,int(iterations)+1):
            if size_chunk==0:
                chunks.append(0)
            else:
                if ((200*size_chunk)+1+200)<=5000:
                    chunks.append((200*size_chunk)+1)
                else:
                    if 4801 not in chunks:
                        chunks.append(4801)
        iterations=len(chunks)
        index_chunk=0
        ids_author=set()
        while(iterations!=0):
            if chunks[index_chunk]!=4801:
                fields = "&field=dc:identifier&count=200"+"&start="+str(chunks[index_chunk])
            else:
                fields = "&field=dc:identifier&count=199"+"&start="+str(chunks[index_chunk])
            searchQuery = "query=AF-ID("+str(id_affiliation)+")"
            #print search_api_author_url+searchQuery+fields
            resp = requests.get(search_api_author_url+searchQuery+fields, headers=headers)
            if resp.status_code != 200:
                raise Scopus_Exception(resp)
            data=resp.json()
            data = data['search-results']
            if data["opensearch:totalResults"] == '0':
                #Check after.
                print "None"
                return None
            for entry in data['entry']:
                authorId = entry['dc:identifier'].split(':')
                ids_author.add(str(authorId[1]))
            iterations-=1
            index_chunk+=1
        authors_by_id_affiliation[id_affiliation]=ids_author

    return authors_by_id_affiliation

def get_references_by_paper(list_scopus_id_paper):
    """
    This function returns a dictionary where the key is the ID of the paper and 
    the value associated with the key is a set of the ids of the papers cited by each paper searched.

    :param list_scopus_id_paper: If you are looking for the ids of the papers cited by an paper, you can send the id as a string but if you want to get the ids of the papers cited from several papers you can send a list of their ids.
    :type list_scopus_id_author: String or List
    :returns: Dictionary where the key is the ID of the paper and the value associated with the key is a set of the ids of the papers cited by each paper.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.get_references_by_paper("84924004559")
    {'84924004559': set(['84897620666', '84923945772', '0039555230', '84870039666', '84923947094', '3042511364', '84870033200', '0038961022', '0038961019', '0040696207', '84922016024', '0039331818', '84892691931'])}
    >>> pyscholar.get_references_by_paper(["84924004559","77950850685"])
    {'84924004559': set(['84897620666', '84923945772', '0039555230', '84870039666', '84923947094', '3042511364', '84870033200', '0038961022', '0038961019', '0040696207', '84922016024', '0039331818', '84892691931']), '77950850685': set(['0039555230', '84893392206', '0038961022', '3042511364', '33644645839', '0001387789', '0038961019', '84867934819', '0001434692', '0039331818', '77950815647', '0002436460'])}
    >>>
    
    """
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]

    references_by_paper=dict()
    for id_paper in list_scopus_id_paper:
        if id_paper in scopus_references_by_idpaper_cache.keys():
            if len(scopus_references_by_idpaper_cache[id_paper])==0:
                print "I didn't find references for this paper."
            references_by_paper[id_paper]=scopus_references_by_idpaper_cache[id_paper]
        else:
            fields = "?view=REF"
            searchQuery = id_paper
            resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
            if resp.status_code != 200:
                raise Scopus_Exception(resp)
            data = resp.json()
            if data[u'abstracts-retrieval-response'] is not None:
                data=data[u'abstracts-retrieval-response'][u'references'][u'reference']
                references_ids=set()
                for id_reference in data:
                    references_ids.add(str(id_reference['scopus-id']))
                references_by_paper[id_paper]=references_ids
                scopus_references_by_idpaper_cache.update({id_paper:references_ids})
            else:
                print "I didn't find references for this paper."
                scopus_references_by_idpaper_cache.update({id_paper:set()})

    return references_by_paper

def get_cache_references_by_idpaper():
    """
    Returns the global variable scopus_references_by_idpaper_cache which is
    a dictionary where the key is the id of the paper and the value associated
    with the key is a set of the ids of the papers cited by the main paper
    """
    return scopus_references_by_idpaper_cache


def get_common_papers(id_author_1="",id_author_2=""):
    """
    This function returns the intercession of papers between two authors.
    
    :param id_author_1: Id of the first author.
    :param id_author_2: Id of the second author.
    :type id_author_1: String 
    :type id_author_2: String 
    :returns: The intercession of papers between the two authors which is a set.
    :rtype: Set
    
    :Example:
    
    >>> import pyscholar
    >>> pyscholar.get_common_papers("56013555800","8931919100")
    {'84924004559', '84925067887'}
    >>>
    """
    if id_author_1=="" and id_author_2=="":
        print "Give me the two Authors"
    else:
        papers_author_1=get_papers([id_author_1])[id_author_1]
        papers_author_2=get_papers([id_author_2])[id_author_2]
        papers_in_common=papers_author_1.intersection(papers_author_2)
    return papers_in_common


def get_title_abstract_by_idpaper(id_paper=""):
    """
    This function returns a tuple with the identification, title and summary of the paper that you searched.
    
    :param id_paper: Id of the paper that you want to search. 
    :type id_paper: String 
    :returns: Tuple with the identification, title and summary of the paper that you searched
    :rtype: Tuple
    
    :Example:
    
    >>> import pyscholar
    >>> pyscholar.get_ids_authors_by_id_paper("77950850685")
    ('77950850685',u'Empty monochromatic triangles',u'We consider a variation of a problem stated by Erd\xf6s and Guy in 1973 about the number of convex k-gons determined by any set S of n points in the plane. In our setting the points of S are colored and we say that a spanned polygon is monochromatic if all its points are colored with the same color. As a main result we show that any bi-colored set of n points in R2 in general position determines a super-linear number of empty monochromatic triangles, namely \u03a9(n5/4).')
    >>>
    """    
    fields = "?field=dc:description,title"

    searchQuery = (id_paper)
    resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
    if resp.status_code != 200:
        raise Scopus_Exception(resp)

    data=resp.json()
    data=data["abstracts-retrieval-response"]["coredata"]
    return (id_paper,(data['dc:title']),(data['dc:description']))


def search_author(list_scopus_id_author):
    """
    This function returns a dictionary where the key is the ID of the
    author and the value associated with the key is a dictionary
    with the following keys: name, surname, h-index and coauthor-count.

    :param list_scopus_id_affiliation: If you are looking for an author, you can send the id as a string but if you want to multiple authors you can send a list of their ids.
    :type list_scopus_id_affiliation: String or List
    :returns: Dictionary where the key is the ID of the author and the value associated with the key is a dictionary with the following keys: name, surname, h-index and coauthor-count.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.search_author("56013555800")
    {'56013555800': {'coauthor-count': 60,'document-count': 32,'h-index': 3,'name': u'Ruy','surname': u'Fabila-Monroy'}}
    >>> pyscholar.search_author(["56013555800","56578611900"])
    {'56013555800': {'coauthor-count': 60,'document-count': 32,'h-index': 3,'name': u'Ruy','surname': u'Fabila-Monroy'},
    '56578611900': {'coauthor-count': 1,'document-count': 1,'h-index': 0,'name': u'Carlos',  'surname': u'Hidalgo-Toscano'}}
    >>>

    """
    fields = "?field=dc:identifier,given-name,surname,h-index,coauthor-count,document-count"
    dict_authors=dict()
    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]
    for id_author in list_scopus_id_author:
        attributes=dict()
        searchQuery = str(id_author)
        resp = requests.get(search_api_author_id_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
        data=resp.json()
        data=data['author-retrieval-response'][0]
        attributes={'name':data['preferred-name']['given-name'],
        'surname':data['preferred-name']['surname'],'h-index':int(data['h-index']),'coauthor-count':int(data['coauthor-count']),'document-count':int(data['coredata']['document-count'])}
        dict_authors[id_author]=attributes
    return dict_authors

def get_coauthors(id_author,min_year="",max_year="",dict_knowledge=dict()):
    """
    This function returns a tuple in certain time interval with the next elemets id_author,set of co-authors associated with an id of an author 
    and a dictionary where the key is the ID of the co-authors 
    and the value associated is a set with the ids of the papers between the author and co-author.
    
    :param id_author: Id of the author that you want to search. 
    :param min_year: The initial year in the time interval.
    :param max_year: The final year in the time interval.
    :type id_author: String 
    :type min_year: String
    :type max_year: String
    :returns: Tuple with the next elements: id_author,set of co-authors associated with an id of an author,dictionary where the key is the ID of the co-authors.
    :rtype: Tuple
    
    :Example:
    
    >>> import pyscholar
    >>> pyscholar.get_ids_authors_by_id_paper("77950850685")
    ('56013555800', set(['36117782600', '6603259241', '7005223038', '12645109800',...,'56606293700', '6701488992', '8931919100']), 
    {'36117782600': ['84864280014'], '6603259241': ['84864280014'], '7005223038': ['84928742486'], '12645109800': ['84897620666', '84883004734'],...,'56606293700': ['84928490197'], '6701488992': ['84864280014'], '8931919100': ['84924004559', '84925067887']})
    >>>
    """
    scopus_authors_by_idpapers_cache.update(dict_knowledge)
    papers_author=get_papers([id_author],min_year,max_year)[id_author]
    papers_with_coauthors=dict()
    list_authors=set()
    for paper in papers_author:
        if paper in scopus_authors_by_idpapers_cache.keys():
            #print "Here"
            for coauthor in scopus_authors_by_idpapers_cache[paper]:
                if coauthor!=id_author:
                    list_authors.add(coauthor)
                    papers_with_coauthors[coauthor]=papers_with_coauthors.setdefault(coauthor,[])+[paper]
        else:
            authors=get_ids_authors_by_id_paper(paper)
            scopus_authors_by_idpapers_cache.update(authors)
            for author in authors[paper]:
                if author not in list_authors and author!=id_author:
                    list_authors.add(author)
                    papers_with_coauthors[author]=[paper]
                elif author!=id_author:
                    papers_with_coauthors[author].append(paper)


    return (id_author,list_authors,papers_with_coauthors)

def get_cache_papers():
    """
    Returns the scopus_authors_by_idpapers_cache dictionary which
    is a cache of papers consulted where the key is the id of the paper
    and the associated value is a set of authors who wrote the article.
    """
    return scopus_authors_by_idpapers_cache


def get_coauthors_graph(list_scopus_id_author,distance,min_year="",max_year="",directory="",name=""):
    """
    This function returns a tuple where the first element is the graph induced by several authors
    and the second element is a list of sets where each set is a set of authors to distance d.

    :param list_scopus_id_author: If you are looking for the paper of an author you can send the id as a string but if you want to get the papers from several authors you can send a list of their ids.
    :param min_year: The initial year in the time interval you want to look for papers.
    :param max_year: The final year in the time interval you want to look for papers.
    :type list_scopus_id_author: String or List.
    :type min_year: String
    :type max_year: String
    :returns: Tuple where the first element is the graph induced by several authors and the second element is a list of sets where each set is a set of authors to distance d.
    :rtype: Tuple

    :Example:

    >>> import pyscholar
    >>> pyscholar.get_papers("56578611900")
    {'56578611900': set(['84959332636'])}
    >>> pyscholar.get_papers(['7006176684','55647751400','56072631800'])
    {'7006176684': set(['5444229075', '17144467193', '0001031138', '79959322537', '84911059592', '84955069066', '0037233714', '38249018110', '52149122079', '0009416953', '84892551677', '51249164413', '0000772349', '0007057901', '13544277720', '33847670994', '0031146399', '84921029337', '84886394293', '0034363462', '67651172822', '0035869886', '0038931174', '38249040825', '33947675881', '0010211186', '84905729730', '0031285726', '23044528188', '0033072608', '0009247597', '84947051661', '84951039519', '0033531899', '77958482876', '0000385874', '33646915730', '84886435449', '0032221906', '58149129161', '21844489552', '52549094277', '0034656467', '0037953609', '84907056975', '38249018633', '84903995394', '84867339764', '33845367161', '0040629757', '0039530566', '0000740606', '22444453689', '84892368124', '76449084340', '84856747354', '27744453855', '34250143856', '84902675107', '27844526213', '0030078477', '0001503960', '0038980939', '0035636479', '79955933749', '0030602470', '17344380224', '0002130779', '80054044270', '79954497708', '47249108096', '34250110161', '0040631446', '0041195239', '67349106698', '0034347051', '33845783250', '84886738410', '0038625364', '34247172128', '21844507175', '84902371560', '0039529250']),
    '55647751400': set(['84924256130', '84924228967', '84876052381']), '56072631800': set(['84896417515', '84947558059'])}
    >>> pyscholar.get_papers(['7006176684','55647751400','56072631800'],"2014","2016")
    {'7006176684': set(['84902675107', '84905729730', '84892368124', '84951039519', '84907056975', '84947051661', '84911059592', '84903995394', '84921029337', '84886738410', '84955069066', '84902371560', '84886435449']),
    '55647751400': set([]), '56072631800': set([])}
    >>>

    """
    node_colors=["red","blue","green","yellow","brown"]
    node_distance=distance
    iteration=distance+1
    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]
    nodes=set()
    index_color=0
    edge_list=[]
    attribute_edge=[]
    resource_not_found=[]
    G_coauthors=nx.Graph()
    D=[]
    dist_count=0
    dict_knowledge_papers=dict()
    while(iteration!=0):
        new_search=set()
        #print "Nivel: "+str(distance)
        #print len(list_scopus_id_author)
        #print list_scopus_id_author
        for id_author in list_scopus_id_author:
            #print id_author
            if id_author not in nodes:
                nodes.add(id_author)
                G_coauthors.add_node(str(id_author),color=node_colors[index_color%5],distance=dist_count)
            if(iteration==1):
                continue
            else:
                coauthors=get_coauthors(str(id_author),min_year,max_year,dict_knowledge_papers)
                #print coauthors
                dict_knowledge_papers.update(coauthors[2])
                for coauthor in coauthors[1]:
                    edge_list.append((id_author,str(coauthor)))
                    attribute_edge.append((id_author,str(coauthor),coauthors[2][coauthor]))
                    new_search.add(str(coauthor))
        if (iteration==1):
            print "Here"
            #print list_scopus_id_author
            dict_last_authors=dict()
            list_scopus_id_author_found=set()
            for id_author in list_scopus_id_author:
                try:
                    coauthors_of_author=get_coauthors(id_author,min_year,max_year,dict_knowledge_papers)
                    dict_knowledge_papers.update(coauthors_of_author[2])
                    dict_last_authors[id_author]=coauthors_of_author[1]
                    list_scopus_id_author_found.add(id_author)
                except:
                    resource_not_found.append(id_author)
                    continue
            check_edge=it.combinations(list_scopus_id_author_found,2)
            for edge in check_edge:
                print "Check edge"
                print edge[0],edge[1]
                intersection_papers=get_common_papers(edge[0],edge[1])
                if len(intersection_papers)>0:
                    edge_list.append((edge[0],edge[1]))
                    attribute_edge.append((edge[0],edge[1],intersection_papers))
        list_scopus_id_author=new_search.copy()
        iteration-=1
        index_color+=1
        dist_count+=1
    G_coauthors.add_edges_from(edge_list)
    for dis in range(node_distance+1):
        D.append([])
    for id_node in G_coauthors.nodes():
        D[G_coauthors.node[id_node]['distance']].append(id_node)
    """
    custom_node_color={}
    pos = nx.spring_layout(G_coauthors,k=0.15,iterations=200)
    for id_node in G_coauthors.nodes():
        custom_node_color[id_node]=G_coauthors.node[id_node]['color']
    nx.draw(G_coauthors,pos,node_list = custom_node_color.keys(), node_color=custom_node_color.values())
    """
    nx.draw(G_coauthors)
    if  os.path.exists(directory):
        plt.savefig(directory+name+".png")
    for atribute in attribute_edge:
        if 'papers' in G_coauthors[atribute[0]][atribute[1]]:
            G_coauthors[atribute[0]][atribute[1]]['papers']+=atribute[2]
        else:
            G_coauthors[atribute[0]][atribute[1]]['papers']=[]
            G_coauthors[atribute[0]][atribute[1]]['papers']+=atribute[2]
    return (G_coauthors,D)

def get_citation_graph(list_scopus_id_paper,distance,directory="",name=""):
    """
    Returns a tuple where the first element is the graph induced by papers
    and the second element is a list of sets where each set is a set of papers to distance d.
    and the last element is a set of papers not found.
    """
    node_distance=distance
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]
    iteration=distance+1
    G_citation=nx.DiGraph()
    nodes=set()
    edge_list=[]
    paper_not_found=set()
    dist_count=0
    D=[]
    while(iteration!=0):
        #print list_scopus_id_paper
        #print len(list_scopus_id_paper)
        new_search=set()
        for paper in list_scopus_id_paper:
            if paper not in nodes:
                nodes.add(paper)
                G_citation.add_node(str(paper),distance=dist_count)
            if(iteration==1):
                continue
            else:
                try:
                    cites=get_references_by_paper(str(paper))
                    for cite in cites[str(paper)]:
                        edge_list.append((str(paper),str(cite)))
                        new_search.add(str(cite))
                except:
                    paper_not_found.add(str(paper))
                    continue
        if(iteration==1):
            dict_last_nodes=dict()
            for id_paper in list_scopus_id_paper:
                try:
                    #print id_paper
                    cites=get_references_by_paper(str(id_paper))
                    dict_last_nodes[id_paper]=cites[str(id_paper)]
                except:
                    paper_not_found.add(str(id_paper))
                    continue
            check_edge=it.permutations(dict_last_nodes.keys(),2)
            for edge in check_edge:
                if edge[1] in dict_last_nodes[edge[0]]:
                    edge_list.append((str(edge[0]),str(edge[1])))
                    edge_list.append((str(edge[0]),str(edge[1])))
        list_scopus_id_paper=new_search.copy()
        iteration-=1
        dist_count+=1
    G_citation.add_edges_from(edge_list)
    for node_to_remove in paper_not_found:
        G_citation.remove_node(node_to_remove)
    nx.draw(G_citation)
    if  os.path.exists(directory):
        plt.savefig(directory+name+".png")
    for dis in range(node_distance+1):
        D.append([])
    for id_node in G_citation.nodes():
        D[G_citation.node[id_node]['distance']].append(id_node)
    return (G_citation,D,paper_not_found)

def get_ids_authors_by_id_paper(list_scopus_id_paper):
    """
    This function returns a dictionary where the key is the ID of the
    paper and the value associated with the key is a list
    of the ids of the authors who wrote the paper.

    :param list_scopus_id_paper: If you are looking for the ids of the authors who wrote an paper, you can send the id as a string but if you want to get the ids of the authors from several papers you can send a list of their ids.
    :type list_scopus_id_author: String or List
    :returns: Dictionary where the key is the ID of the paper and the value associated with the key is a list of the ids of the authors who wrote the paper.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.get_ids_authors_by_id_paper("84945466401")
    {'84945466401': ['7003988000', '56286038700', '8847635500', '56013555800', '56815189300']}
    >>> pyscholar.get_ids_authors_by_id_paper(['84924256130', '84924228967', '84876052381','84864280014','84867281605','77950850685'])
    {'84876052381': ['55647751400'], '84864280014': ['6506110957', '7006657985', '23388216300', '7005508480', '6603865823', '36117782600', '56013555800', '36117667600', '7006733509', '6701488992', '36118513000', '6603259241', '6504765315'], '84924256130': ['55647751400'], '77950850685': ['7004102317', '56013555800', '56013629200', '12645615700', '56240672400', '35566511400'], '84867281605': ['8847635500', '56013555800', '56013629200', '37107692000', '35566511400'], '84924228967': ['55647751400']}
    >>>
    """
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]

    fields = "?field=dc:description,authors"
    authors_by_id_paper=dict()

    for id_paper in list_scopus_id_paper:
        searchQuery = str(id_paper)
        resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)

        id_authors=[]
        data=resp.json()
        data=data["abstracts-retrieval-response"]["authors"]["author"]
        for author in data:
            id_authors.append(str(author["@auid"]))
        authors_by_id_paper[id_paper]=id_authors
    return authors_by_id_paper

def count_citations_by_id_paper(list_scopus_id_paper):
    """
    This function returns a dictionary where the key is the ID of the
    paper and the value associated with the key is the
    number citations.

    :param list_scopus_id_paper: If you are looking for the number of citations of an paper you can send the id as a string but if you want to get the number of citations from several papers you can send a list of their ids.
    :type list_scopus_id_author: String or List
    :returns: Dictionary where the key is the ID of the paper and the value associated with the key is the number citations.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.count_citations_by_id_paper("84864280014")
    {'84864280014': 5}
    >>> pyscholar.count_citations_by_id_paper(['84924256130', '84924228967', '84876052381','84864280014','84867281605','77950850685'])
    {'84876052381': 0, '84864280014': 5, '84924256130': 0, '77950850685': 1, '84867281605': 3, '84924228967': 0}
    >>>
    """
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]

    fields = "?field=dc:description,citedby-count"
    cited_by_count=dict()

    for id_paper in list_scopus_id_paper:
        searchQuery = str(id_paper)
        resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)

        number_citations=0
        data=resp.json()
        data=data["abstracts-retrieval-response"]["coredata"]
        number_citations=int(data['citedby-count'])
        cited_by_count[id_paper]=number_citations
    return cited_by_count

def check_years(min_year="",max_year=""):
    """
    Return the filter if the given interval is correct
    otherwise returns None
    """
    filtr=""
    if min_year =="":
        if max_year=="":
            filtr=""
            return filtr
        else:
            if max_year.isdigit():
               filtr+="AND (PUBYEAR < "+ str(int(max_year)+1) +")"
               return filtr
            else:
                print "max_year must be a number"
                return None
    else:
        if min_year.isdigit():
            if max_year=="":
                filtr+="AND (PUBYEAR > "+ str(int(min_year)-1) +")"
                return filtr
            else:
                if max_year.isdigit():
                    if int(max_year)<int(min_year):
                        print "Max_year must be greater than min_year"
                        return None
                    else:
                        filtr+="AND (PUBYEAR > "+ str(int(min_year)-1) +") AND (PUBYEAR < "+ str(int(max_year)+1)+")"
                        return filtr
                else:
                    print "max_year must be a number"
                    return None
        else:
            if max_year.isdigit():
                print "min_year must be a number"
                return None
            else:
                print "min_year and max_year must be numbers"
                return None



def get_papers(list_scopus_id_author,min_year="",max_year=""):
    """
    This function returns a dictionary where the key is the ID of the
    author and the value associated with the key
    is a set of the ids of the papers that belong to
    the author in a certain time interval.The values of min_year and max_year are optional,
    if you omit min_year and max_year returns the dictionary in all time.

    :param list_scopus_id_author: If you are looking for the paper of an author you can send the id as a string but if you want to get the papers from several authors you can send a list of their ids.
    :param min_year: The initial year in the time interval you want to look for papers.
    :param max_year: The final year in the time interval you want to look for papers.
    :type list_scopus_id_author: String or List.
    :type min_year: String
    :type max_year: String
    :returns: Dictionary where the key is the identifier of the author and the associated value is the set of papers that belong to each author.
    :rtype: Dictionary

    :Example:

    >>> import pyscholar
    >>> pyscholar.get_papers("56578611900")
    {'56578611900': set(['84959332636'])}
    >>> pyscholar.get_papers(['7006176684','55647751400','56072631800'])
    {'7006176684': set(['5444229075', '17144467193', '0001031138', '79959322537', '84911059592', '84955069066', '0037233714', '38249018110', '52149122079', '0009416953', '84892551677', '51249164413', '0000772349', '0007057901', '13544277720', '33847670994', '0031146399', '84921029337', '84886394293', '0034363462', '67651172822', '0035869886', '0038931174', '38249040825', '33947675881', '0010211186', '84905729730', '0031285726', '23044528188', '0033072608', '0009247597', '84947051661', '84951039519', '0033531899', '77958482876', '0000385874', '33646915730', '84886435449', '0032221906', '58149129161', '21844489552', '52549094277', '0034656467', '0037953609', '84907056975', '38249018633', '84903995394', '84867339764', '33845367161', '0040629757', '0039530566', '0000740606', '22444453689', '84892368124', '76449084340', '84856747354', '27744453855', '34250143856', '84902675107', '27844526213', '0030078477', '0001503960', '0038980939', '0035636479', '79955933749', '0030602470', '17344380224', '0002130779', '80054044270', '79954497708', '47249108096', '34250110161', '0040631446', '0041195239', '67349106698', '0034347051', '33845783250', '84886738410', '0038625364', '34247172128', '21844507175', '84902371560', '0039529250']),
    '55647751400': set(['84924256130', '84924228967', '84876052381']), '56072631800': set(['84896417515', '84947558059'])}
    >>> pyscholar.get_papers(['7006176684','55647751400','56072631800'],"2014","2016")
    {'7006176684': set(['84902675107', '84905729730', '84892368124', '84951039519', '84907056975', '84947051661', '84911059592', '84903995394', '84921029337', '84886738410', '84955069066', '84902371560', '84886435449']),
    '55647751400': set([]), '56072631800': set([])}
    >>>

    """
    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]

    papers_by_author=dict()
    filter_year=""
    filter_year=check_years(min_year,max_year)
    if filter_year==None:
        return None

    for id_author in list_scopus_id_author:
        if (id_author in scopus_papers_by_authorid_cache.keys()) and (min_year+"-"+max_year in scopus_papers_by_authorid_cache[id_author].keys()):
            papers_by_author[id_author]=set()
            papers_by_author[id_author]=papers_by_author[id_author].union(scopus_papers_by_authorid_cache[id_author][min_year+"-"+max_year])
        else:
            author_attributes=search_author(id_author)
            document_count=author_attributes[id_author]['document-count']
            iterations=math.ceil(document_count/200.0)
            chunks=[]
            for size_chunk in range(0,int(iterations)+1):
                if size_chunk==0:
                    chunks.append(0)
                else:
                    chunks.append((200*size_chunk)+1)
            index_chunk=0
            id_papers=set()
            while (iterations!=0):
                #print iterations
                fields = "&field=dc:identifier&count=200"+"&start="+str(chunks[index_chunk])
                searchQuery = "query=AU-ID("+str(id_author)+") "+filter_year
                #print searchQuery
                resp = requests.get(search_api_scopus_url+searchQuery+fields, headers=headers)
                data = resp.json()
                if resp.status_code != 200:
                    raise Scopus_Exception(resp)
                data = resp.json()
                data = data['search-results']
                if data["opensearch:totalResults"] == '0':
                    papers_by_author[id_author]=dict()
                    papers_by_author[id_author].update({min_year+"-"+max_year:id_papers})
                else:
                    for entry in data['entry']:
                        paperId = entry['dc:identifier'].split(':')
                        id_papers.add(str(paperId[1]))
                iterations-=1
                index_chunk+=1
            papers_by_author[id_author]=set()
            papers_by_author[id_author]=papers_by_author[id_author].union(id_papers)
            if id_author not in scopus_papers_by_authorid_cache.keys():
                scopus_papers_by_authorid_cache[id_author]=dict()
                scopus_papers_by_authorid_cache[id_author].update({min_year+"-"+max_year:id_papers})
            else:
                scopus_papers_by_authorid_cache[id_author].update({min_year+"-"+max_year:id_papers})
    return papers_by_author

def get_cache_papers_by_authorid():
    """
    Returns the global variable scopus_papers_by_authorid_cache which is
    a dictionary of dictionaries where the first dictionary key is
    the id of the author and the key to the second dictionary is
    the time interval whose associated value is a set of papers.
    """
    return scopus_papers_by_authorid_cache

def find_author_scopus_id_by_name(firstName="", lastName=""):
    """
    Searches for an author scopus id given its name.
    """
    searchQuery = "query="

    if firstName:
        searchQuery += "AUTHFIRST(%s)" % (firstName)
    if lastName:
        if firstName:
            searchQuery += " AND "
        searchQuery += "AUTHLASTNAME(%s)" % (lastName)

    #print searchQuery

    fields = "&field=identifier"
    resp = requests.get(search_api_author_url+searchQuery+fields, headers=headers)

    if resp.status_code != 200:
       raise Scopus_Exception(resp)

    data = resp.json()
    #print "-----------JSON----------"
    #print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))

    #print "----------DATA----------"
    data = data['search-results']
    #print data

    if data["opensearch:totalResults"] == '0':
        print "None"
        return None

    ids = []

    for entry in data['entry']:
        authorId = entry['dc:identifier'].split(':')
        ids.append(authorId[1])

    return ids

def get_author_affiliations(firstName="", lastName=""):
    """Searches for an author scopus id given its name."""

    searchQuery = "query="

    if firstName:
        searchQuery += "AUTHFIRST(%s)" % (firstName)
    if lastName:
        if firstName:
            searchQuery += " AND "
        searchQuery += "AUTHLASTNAME(%s)" % (lastName)
   
    #print searchQuery
   
    #fields = "&field=identifier"
    fields = ""
    resp = requests.get(search_api_author_url+searchQuery+fields, headers=headers)
   
    if resp.status_code != 200:
       raise Scopus_Exception(resp)
   
    data = resp.json()
    #print "-----------JSON----------"
    #print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))
   
    #print "----------DATA----------"
    data = data['search-results']
    #print data
   
    if data["opensearch:totalResults"] == '0':
        print "None"
        return None
                                                                                          
    affiliations = []
                                                                                          
    for entry in data['entry']:
	if 'affiliation-current' in entry:
            affiliations.append(entry['affiliation-current'])
                                                                                                                      
    return affiliations