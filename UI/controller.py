import flet as ft
from database.DAO import DAO

class Controller:
    def __init__(self, view, model):

        self._view = view
        self._model = model

    def fillDDGenre(self): #metodo per riempire il menù a tendina dei generi all'avvio dell'app
        generi = DAO.get_all_generes()
        #devo svuotare la tendina nel caso ci sia già qualcosa
        self._view._ddGenre.options.clear()
        for g in generi:
            self._view._ddGenre.options.append(ft.dropdown.Option(g))  #aggiungo ogni opzione nella tendina

        self._view.update_page() #dico all'interfaccia di aggiornarsi

    def handleCreaGrafo(self,e):
        genere_sel = self._view._ddGenre.value #va a leggere cosa l'utente ha attualmente selezionato nella tendina
        # .value estrae proprio la stringa di testo
        if genere_sel is None or genere_sel == "":
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text("Errore: Seleziona un genere prima di creare il grafo!", color="red"))
            self._view.update_page()
            return #Importantissimo! Ferma l'esecuzione della funzione qui. Se c'è un errore, non vogliamo che Python provi a creare il grafo.
        # 3. Avviso l'utente che sto lavorando ed elaboro il grafo nel Model
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Creazione del grafo in corso, attendere..."))
        self._view.update_page()

        self._model.crea_grafo(genere_sel)#Diamo l'ordine al Model di far partire i cicli for, gli itertools, di chiamare il database e di creare i nodi e gli archi con il genere scelto.

        # 4. Recupero i risultati calcolati dal Model
        n_nodi, n_archi = self._model.get_dettagli_grafo()
        nome_influente, val_influenza = self._model.get_artista_piu_influente()
        top_5 = self._model.get_top_5_archi()

            # 5. Stampo tutto a schermo esattamente come richiesto dal PDF
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato:"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {n_nodi}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {n_archi}"))

        if nome_influente:
            self._view.txt_result.controls.append(
                    ft.Text(f"Artista più influente: {nome_influente}, con influenza: {val_influenza}"))

        self._view.txt_result.controls.append(ft.Text("Top 5 archi:"))
        for arco in top_5:
                self._view.txt_result.controls.append(ft.Text(arco))

    # 6. Aggiorno la pagina per far comparire il testo
        self._view.update_page()

    def handleCammino(self, e):

            pass