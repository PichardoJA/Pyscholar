from scopus_key import MY_API_KEY
import json
import requests

search_api_author_url = "http://api.elsevier.com/content/search/author?"
search_api_scopus_url = "http://api.elsevier.com/content/search/scopus?"


#Un diccionario con las listas 
Scopus_ids_merged_rep={}
Scopus_ids_merged_lists={}

#Voy a poner aqui lo que falta por hacer (TODO list) 

#Funciones para manejar las ids, hago implementaciones ingenuas que
#despues mejoraremos
#Vean https://en.wikipedia.org/wiki/Disjoint-set_data_structure

def _add_scopus_id(scopus_id):
    """Adds a scopus id to the merged list. Returns False if the ID
    is already in the merged list and false otherwise"""
    
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

def search_author():
    """A wrapper to the Scopus API"""
    #Pense que seria bueno un wrapper que provea todo lo del api
    pass

def get_papers(list_scopus_id_author=[]):
    """Returns a dictionary where the key is the ID of the 
    author and the value associated with the key 
    is a list of the ids of the papers that belong to the author."""

    headers = {"Accept":"application/json", "X-ELS-APIKey": MY_API_KEY}
    fields = "&field=identifier"
    papers_by_author=dict()
    if len(list_scopus_id_author)==0:
        print "Give me a list with at least one Id"
        return None
    else:
        for id_author in list_scopus_id_author:
            searchQuery = "query=AU-ID("+str(id_author)+")"
            resp = requests.get(search_api_scopus_url+searchQuery+fields, headers=headers)
            if resp.status_code != 200:
                print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))
                return None
            else:
                id_papers=[]
                data = resp.json()
                data = data['search-results']
                if data["opensearch:totalResults"] == '0':
                    print "None"
                    return None
                else:
                    for entry in data['entry']:
                        paperId = entry['dc:identifier'].split(':')
                        id_papers.append(paperId[1])
                    papers_by_author[id_author]=id_papers
    return papers_by_author
    #Hay que considerar que pudieran tener aliases
    
    

#FIN DE TODO LIST

def find_author_scopus_id_by_name(firstName="", lastName=""):
    """Searches for an author scopus id given its name."""
    
    
    headers = {"Accept":"application/json", "X-ELS-APIKey": MY_API_KEY}
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
        print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))
        return None
    
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