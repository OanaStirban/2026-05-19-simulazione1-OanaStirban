from oauthlib.uri_validate import query

from database.DB_connect import DBConnect
#inserimento di 3 funzioni con le SQL (vertici, popolarità, acquisti)

class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_all_generes(): #prende tutti i generi del DB
        connessione = DBConnect.get_connection() #chiama la classe di connessione data dal prof
        risultati =[] #lista dove andiamo a mettere tutti i pezzi

        query = """ 
                SELECT *
                FROM genre
                ORDER BY Name
                """
        #scrivo il codice SQL in modo ordinato e leggibile su più righe

        cursor = connessione.cursor(dictionary=True) # crea un ambasciatore che va avanti e indietro e riporta indietro i dati
                                                     # parametro dictionary = True inserisce i valori come se fossimo in un dizionario
        cursor.execute(query)  #invia la query SQL al database e lo fa eseguire

        for row in cursor:      #scorre tutti i risultati, per ogni giro la variabile contiene una singola riga della tabella dei generi
            risultati.append(row["Name"])# dalla riga prende solo il nome e lo aggiunge alla lista risultati

        cursor.close()  #Chiude il cursore, bisogna chiudere per liberare la memoria del computer una volta che ha finito il suo lavoro
        connessione.close()#IMPORTANTE. Chiudere la connessione con il database, rischio blocco e programma in crash
        return risultati #Restituisce la lista piena di nomi

    @staticmethod
    def get_vertici_artisti(genere_selezionato): #riceve in ingresso il genere selezionato dall'utente
        conn = DBConnect.get_connection() #chiama la classe di connessione data dal prof
        result = []#lista dove andiamo a mettere tutti i pezzi

        query = """
                    SELECT DISTINCT a.ArtistId, a.Name
                    FROM artist a
                    JOIN album al ON a.ArtistId = al.ArtistId
                    JOIN track t ON al.AlbumId = t.AlbumId
                    JOIN genre g ON t.GenreId = g.GenreId
                    WHERE g.Name = %s
                    """
                    #DISTINCT fondamentale per avere un solo nodo invece di avere ripetizioni per artista
                    #JOIN nel DB l'artista non è collegato direttamente al genere e quindi bisogna fare dei collegamenti
                    # g.Name = %s --> è un segnaposto ("Prendimi tutti i risultati dove il nome del genere è uguale a... aspetta, te lo dico tra un attimo")
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (genere_selezionato,)) # --> qui il %s viene descritto in genere_selezionato; la Virgola serve per indicare che è una tupla

        for row in cursor:
            result.append((row["ArtistId"], row["Name"])) #Qui inseriamo nella lista una tupla di due valori: l'ID e il Nome. L'ID ci servirà per i calcoli del grafo, il Nome per stamparlo a video alla fine.
        #tupla--> può contenere duplicati, è ordinata ed è immutabile, non si può fare .append() per aggiungere cose o rimuoverle
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_popolarita_artisti():
        conn = DBConnect.get_connection()
        result = {} #usiamo un dizionario perché vogliamo una struttura del tipo {Artista: Popolarità}

        query = """
                    SELECT a.ArtistId, SUM(il.Quantity) as Popolarita
                    FROM artist a
                    JOIN album al ON a.ArtistId = al.ArtistId
                    JOIN track t ON al.AlbumId = t.AlbumId
                    JOIN invoiceline il ON t.TrackId = il.TrackId
                    GROUP BY a.ArtistId
                    """
        # SELECT a.ArtistId, SUM(il.Quantity) as Popolarita
        # SUM() è una funzione di aggregazione SQL. Prende le quantità (Quantity) di tutti i brani venduti (invoiceline) e le somma.
        # Rinominiamo questa colonna "Popolarita" usando as.
        #Altra catena per arrivare dall'Artista fino alla ricevuta di acquisto (invoiceline, che contiene la quantità venduta).
        #GROUP BY a.ArtistId "non fare una somma totale ma fai la somma per artista"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)

        for row in cursor:
            result[row["ArtistId"]] = row["Popolarita"]
            # chiave = ID artista: valore = numero calcolato dalla SUM

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_acquisti_clienti():
        conn = DBConnect.get_connection()
        result = {} # anche qui utilizziamo un dizionario

        query = """
                    SELECT DISTINCT i.CustomerId, a.ArtistId
                    FROM invoice i
                    JOIN invoiceline il ON i.InvoiceId = il.InvoiceId
                    JOIN track t ON il.TrackId = t.TrackId
                    JOIN album al ON t.AlbumId = al.AlbumId
                    JOIN artist a ON al.ArtistId = a.ArtistId
                    """
        #Estraiamo sia l'id del cliente che quello dell'artista. Usiamo DISTINCT per evitare le ripetizioni
        # a noi interessa solo se un cliente ha comprato un certo artista e non quante
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)

        for row in cursor:
            c_id = row["CustomerId"]
            a_id = row["ArtistId"]

            if c_id not in result:
                result[c_id] = [] # se non troviamo il cliente nel dizionario, creiamo una lista vuota correlata al suo id
            result[c_id].append(a_id) # nella lista del cliente viene aggiunto l'artista corrispondente all'ID

        cursor.close()
        conn.close()
        return result