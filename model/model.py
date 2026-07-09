#qui verrà importato nteworkx e si scrive la funzione per costruire il grafo incrociando il dato

import networkx as nx
import itertools
from database.DAO import DAO

class Model:
    def __init__(self):
        self.grafo = nx.DiGraph() #Directed Graph
        self.id_to_name = {} # Dizionario di supporto: ci serve per ricordarci i Nomi degli artisti a partire dal loro ID
        # (perché nel grafo inseriremo gli ID per comodità di calcolo)



    def crea_grafo(self,genere_selezionato): #mi serve l'input dell' utente

        #puliamo in grafo per evitare che i nodi nuovi si mischino con quelli vecchi (l'utente potrebbe cercare due generi in poco tempo)
        self.grafo.clear()
        self.id_to_name.clear()

        artisti = DAO.get_vertici_artisti(genere_selezionato) #lista di tuple(id,nome)
        for a_id,a_name in artisti:
            self.grafo.add_node(a_id) #aggiunge fisicamente il nodo al nostro grafo
            self.id_to_name[a_id] = a_name #nel dizionario di supporto alla chiave a_id si aggiunge il valore a_name

        popolarita = DAO.get_popolarita_artisti()
        acquisti = DAO.get_acquisti_clienti()

        #ora bisogna trovare le connesioni valide (archi)
        #usiamo i set() per non avere doppioni, se due clienti comprano gli stessi due artisti l'arco va creato una sola volta
        coppie_valide = set()
        for cliente_id, lista_artisti in acquisti.items():
            artisti_nel_grafo = [a for a in lista_artisti if a in self.grafo.nodes] #crea una lista
            #Questa riga butta via la musica Classica e tiene solo gli artisti che abbiamo effettivamente inserito nel grafo al passaggio precedente.
            #Come se scrivessimo:
            #artisti_nel_grafo = []
            #for a in lista_artisti:
                # if a in self.grafo.nodes:
                    #artisti_nel_grafo.append(a)
            artisti_unici = list(set(artisti_nel_grafo))# rimuoviamo tramite set() (no duplicati) eventuali duplicati
            for u,v in itertools.combinations(artisti_unici,2): #La funzione combinations prende la lista di artisti unici comprati dal cliente e genera tutte le possibili coppie di dimensione 2. Se Mario ha comprato A, B e C, genera in un colpo solo le coppie (A,B), (A,C), (B,C).
                coppia = tuple(sorted([u,v])) #La funzione sorted() mette in ordine gli ID
                coppie_valide.add(coppia)

        #crazione archi con dir e peso
        for u, v in coppie_valide:
            # Recuperiamo la popolarità. Se un artista non c'è, diamo 0 di default
            pop_u = popolarita.get(u, 0)
            pop_v = popolarita.get(v, 0)

            # Il peso è la somma delle rispettive popolarità[cite: 1]
            peso_totale = pop_u + pop_v

            # Condizioni per la direzione[cite: 1]
            if pop_u > pop_v:
                self.grafo.add_edge(u, v, weight=peso_totale)
            elif pop_v > pop_u:
                self.grafo.add_edge(v, u, weight=peso_totale)
            else:
                # Popolarità uguale: aggiungiamo due archi in entrambi i versi[cite: 1]
                self.grafo.add_edge(u, v, weight=peso_totale) # salva il peso sul collegamento.
                self.grafo.add_edge(v, u, weight=peso_totale)

    def get_dettagli_grafo(self):
        """Restituisce il numero di nodi e di archi da stampare nell'interfaccia[cite: 1]."""
        return len(self.grafo.nodes), len(self.grafo.edges) #nodes e edges sono liste interne a NetworkX che contengono tutti i vertici e i vertici
    #len() ne conta il nujmero

    def get_artista_piu_influente(self):
        """Calcola l'influenza (peso archi uscenti - peso archi entranti) e trova il maggiore[cite: 1]."""
        if len(self.grafo.nodes) == 0:
            return None, 0

        max_influenza = -999999 #visto che si tratta di una sottrazione potremmo avere numeri negativi, inizializzare ad un numero molto basso aiuta
        best_artista_id = None

        for nodo in self.grafo.nodes: #il ciclo for serve solo a ricordarsi quale è l'artista che ha il peso maggiore
            # Calcolo somma pesi degli archi uscenti
            peso_uscenti = sum(attr['weight'] for u, v, attr in self.grafo.out_edges(nodo, data=True))#grafo.out_edges va su un nodo specifica e guarda tutte le frecce che escono
            #data = True ci permette di leggere i dizionari deve avevamo salvato il nostro Weight
            # Calcolo somma pesi degli archi entranti
            peso_entranti = sum(attr['weight'] for u, v, attr in self.grafo.in_edges(nodo, data=True))

            influenza = peso_uscenti - peso_entranti

            if influenza > max_influenza:
                max_influenza = influenza
                best_artista_id = nodo

        # Restituiamo il Nome (usando il dizionario di supporto) e il valore dell'influenza
        return self.id_to_name[best_artista_id], max_influenza

    def get_top_5_archi(self):
        """Restituisce i 5 archi con peso maggiore in ordine decrescente[cite: 1]."""
        lista_archi = []

        # self.grafo.edges(data=True) ci permette di accedere anche al 'weight'
        for u, v, attr in self.grafo.edges(data=True): #prendiamo tutti gli archi del grafo ed estraiamo da loro tuttii pesi
            lista_archi.append((u, v, attr['weight'])) #aggiungiamo nella lista nodo A, nodo B e il peso dell'arco

        # Ordiniamo la lista basandoci sul peso (indice 2 della tupla), reverse=True per ordine decrescente
        lista_archi.sort(key=lambda x: x[2], reverse=True)

        # Formattiamo le prime 5 stringhe da stampare a video
        top_5 = []
        for u, v, peso in lista_archi[:5]:
            nome_u = self.id_to_name[u]
            nome_v = self.id_to_name[v]
            top_5.append(f"{nome_u} -> {nome_v}: {peso}")

        return top_5






