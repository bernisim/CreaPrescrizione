"""
Programma per creare precrizioni in formato PDF

DA FARE:
- gestisci timbro firmato
- aggiungi un pochino di random nel posizionamento della firma o le sue dimensioni o più firme
- opzione di inviare via email o mettere a disposizione in altro modo
- la prescrizione mettila in pdf se viene specificato qualcosa (manualmente o dall'elenco)

ORGANIZZAZIONE:

NUOVA ORGANIZZAZIONE:
Le caratteristiche di un farmaco le metto in una classe; delle istanze di essa la uso per rimepire la lista di farmaci

Dati farmaci contenuti nel file farmaci_prescrivibili.csv (Tab delimited perchè potrai usare virgole) con:
- titolo (e.g. antibiotico per mamma)
- categoria (antibiotico)
- nome commerciale
- principio attivo
- dosaggio/istruzioni

Dati pazienti contenuti nel file nominativi.csv :
- cognome & nome
- data di nascita

Per gestire la history potrei salvare ad ogni creazione di pdf un file csv con tutti i dati della ricetta (anche la data, anche se poi non la riuserò).

Alla partenza popolo la data odierna.

LOGICHE DI FUNZIONAMENTO DA IMPLEMENTARE
- crea una classe farmaco che contiene tutti i dati del farmaco (salvate come proprietà)
- per caricare una categoria, scorri tutti gli elementi aventi tale tipo di classe e filtrali in base alla proprietà categoria
= il punto è come risalire dalla scelta in un combobox al farmaco (cioè all'indice contenuto nell'elenco farmaci di classe farmaco):
   forse posso sfruttare la key che può essere qualunque cosa, mi pare...e.g. un id progressivo ed unico
- ricava automaticamente le categorie dai farmaci caricati e poi ordinale e mettile nel combobox delle categorie
- caricare in partenza tutti i farmaci in combobox Farmaci, mentre in Categorie le categorie
- se però seleziono una categoria, allora devo filtrare i farmaci da mettere in combo Farmaci
"""
from typing import List

import PySimpleGUI as sg
import csv
import os
import sys
import random
import datetime
from fpdf import FPDF


def data_odierna (delimitatore="/"):
 # Riporta la data odierna in formato gg/mm/aaaa.  Opzionalmente si può specificare il char delimitatore
 data = datetime.datetime.now()
 return data.strftime("%d"+ delimitatore + "%m" + delimitatore + "%Y")


class ClasseFarmaco():
    def __init__(self):
        self.id = 0
        self.titolo = ""
        self.principio_attivo = ""
        self.nome_commerciale = ""
        self.categoria = ""
        self.istruzioni = ""


def filtra_lista_farmaci(filtro_per_categoria="", filtro_per_il_nome=""):
    """Riporta una lista ordinata e filtrata dei farmaci in base alla categoria ed il filtro per nome (commerciale o principio attivo) specificati"""
    lista_temporanea_filtrata_farmaci = []
    for singolo_farmaco_presente in lista_farmaci:   # scorro tutti i farmaci
        # Gestione filtro-categorie
        if (filtro_per_categoria == "") or (filtro_per_categoria in singolo_farmaco_presente.categoria):   # se la categoria-filtro non è specificata oppure corrisponde ad una presente, allora proseguo con la selezione...
            if filtro_per_il_nome == "":   # gestione filtro nome non specificato (aggiungo sia il nome commerciale che il principio attivo)
                if singolo_farmaco_presente.nome_commerciale != "":  # se esiste il nome commerciale e non è nella lista, lo aggiungo
                    nome_composto = singolo_farmaco_presente.nome_commerciale + " (" + singolo_farmaco_presente.principio_attivo + ")"
                    if nome_composto not in lista_temporanea_filtrata_farmaci:
                        lista_temporanea_filtrata_farmaci.append(nome_composto)
                if singolo_farmaco_presente.principio_attivo != "":   # se il princio attivo esiste e non è nella lista, lo aggiungo
                    if singolo_farmaco_presente.principio_attivo not in lista_temporanea_filtrata_farmaci:
                        lista_temporanea_filtrata_farmaci.append(singolo_farmaco_presente.principio_attivo)
            else:
                # Gestione nome-filtro presente nel nome commerciale: # se esiste e non è nella lista, lo aggiungo
                if (singolo_farmaco_presente.nome_commerciale != "") and (filtro_per_il_nome in singolo_farmaco_presente.nome_commerciale):
                    nome_composto = singolo_farmaco_presente.nome_commerciale + " (" + singolo_farmaco_presente.principio_attivo + ")"
                    if nome_composto not in lista_temporanea_filtrata_farmaci:
                        lista_temporanea_filtrata_farmaci.append(nome_composto)

                # Gestione nome-filtro presente nel principio attivo
                if (singolo_farmaco_presente.principio_attivo != "") and (filtro_per_il_nome in singolo_farmaco_presente.principio_attivo):
                    if singolo_farmaco_presente.principio_attivo not in lista_temporanea_filtrata_farmaci:
                        lista_temporanea_filtrata_farmaci.append(singolo_farmaco_presente.principio_attivo)

    lista_temporanea_filtrata_farmaci.sort()  # ordino alfabeticamente i farmaci
    return lista_temporanea_filtrata_farmaci

colore_per_campi_obbligatori = 'yellow'
# CARICO I DATI NEI VARI COMBOBOX DAI RELATIVI FILE-------------------------------------

# CARICO I NOMINATIVI dei pazienti dal file .csv  2222222222222222222222222222222222
nominativi_da_file = []
with open('csv-files/nominativi.csv', 'r',) as file:   # Apre l'accesso in lettura al file .csv dei nominativi
    reader = csv.reader(file)       # Crea un oggetto iterabile reader, comma-delimited
    for riga in reader:				# Scorro le singole righe ed uso i valori delle colonne per caricare le liste dei pazienti
        nominativi_da_file.append(riga[0] + " (" + riga[1] + ")")   # creo il nominativo con cognome-nome e data di nascita

# # CARICO LA LISTA DI TUTTI I FARMACI dal file .csv 2222222222222222222222222222222222
istanza_farmaco = ClasseFarmaco ()
lista_farmaci = []
# titolo_da_file = []
# categoria_da_file = []
# principio_attivo_da_file = []
# nome_commerciale_da_file = []
# istruzioni_da_file = []
with open('csv-files/farmaci_prescrivibili.csv', 'r') as file:   # Apre l'accesso in lettura al file .csv "|"-delimited dei farmaci
    reader = csv.reader(file, delimiter='|')       # Crea un oggetto iterabile reader
    intestazioni = next(reader, None)  # salto la riga di intestazione: riporta l'intestazione oppure `None` se non c'è nulla
    for id_progressivo, riga in enumerate(reader):				# Scorro le singole righe ed uso i valori delle colonne per caricare le caratteristiche di ogni farmaco
        print("Leggo la riga nel csv: " + riga[2])
        if riga == "":
            break # se trovo una riga vuota (in genere l'ultima) , esco dal ciclo
        istanza_farmaco = ClasseFarmaco()   # mettendo dentro il for-loop la creazione di istanza, crea ogni volta un oggetto diverso
        istanza_farmaco.id = id_progressivo
        istanza_farmaco.titolo = riga[0]
        istanza_farmaco.categoria = riga[1]
        istanza_farmaco.principio_attivo = riga[2].upper()
        istanza_farmaco.nome_commerciale = riga[3].capitalize()
        istanza_farmaco.istruzioni = riga[4]
        lista_farmaci.append(istanza_farmaco)
        print("Ho aggiunto alla lista ",istanza_farmaco.titolo+ " " + istanza_farmaco.categoria)

# CREO LA LISTA DELLE CATEGORIE dei farmaci 22222222222222222222222222222222
lista_categorie = []
for singolo_farmaco in lista_farmaci:
    print("Sto valutando la categoria " + singolo_farmaco.categoria + " " + singolo_farmaco.titolo)
    if singolo_farmaco.categoria not in lista_categorie:   # Se non esiste già, aggiungo questa catecoria
        lista_categorie.append(singolo_farmaco.categoria)
        print ("Aggiungo realmente " + singolo_farmaco.categoria)
lista_categorie.sort()   # ordino alfabeticamente le categorie

# Creo un elenco di farmaci filtrato per categoria
# Se un farmaco appare con il nome commerciale ed il principio attivo, metto entrambi nella lista
lista_filtrata_farmaci = filtra_lista_farmaci("","")   # creo una lista di fatto non filtrata in questo primo passaggio formata dai nomi/nomi commerciali

# ------ CREAZIONE LAYOUT ---------------------------------------------------------------
layout =  [ [sg.Combo(lista_filtrata_farmaci,size=(50,20), tooltip="farmaco", key="farmaci_cb", default_value="Farmaco da prescrivere", background_color = colore_per_campi_obbligatori),
                 sg.Combo(lista_categorie,size=(20,20), tooltip="Categoria farmaco", default_value="Categoria farmaco", key="categorie_cb", enable_events=True, readonly = True),
                 sg.Text("Ricerca veloce"),sg.InputText(tooltip="cosa cercare",size=(20,20))],
            [sg.Checkbox("Inserisci istruzioni dosaggio"),sg.Text (' Prescrizione='),sg.InputText(size=(50,50), tooltip="Prescrizione finale")],
            [sg.HorizontalSeparator()],
            [sg.Input("Cognome, nome e data di nascita",tooltip="cognome, nome e data di nascita",size=(50,10),key="cognome_nome_cb", background_color = colore_per_campi_obbligatori),
              sg.Combo(nominativi_da_file,size=(30,10),default_value="Elenco pazienti con data di nascita",key='pazienti_cb',enable_events=True, readonly = True),sg.Button("Salva paziente") ],
            [sg.HorizontalSeparator()],
            [ sg.Text("Data ricetta"), sg.Input(data_odierna(),tooltip="data della ricetta",size=(10, 10), key="data_ricetta"),
              sg.Combo(["Abano Terme","Monselice", "Padova","Piove di Sacco"], size=(30,10), default_value="Padova", key="citta"),
              sg.Column([
                    [sg.Radio("No timbro", "timbratura", size=(20,10))],
                    [sg.Radio("Inserisci timbro", "timbratura")],
                    [sg.Radio("Inserisci timbro firmato", "timbratura",default=True)]
                        ])
            ],
            [sg.Button(' Annulla ',size=(15,1), key="cancel"),
             sg.Combo(["A5","A4"],size=(5,20), tooltip="formato_pagina", default_value="A5", key="formato_pagina"),
             sg.Button(" Crea PDF ",size=(50,2),key="crea_pdf"), sg.Button("Reset valori", key='reset')]  ]

sg.theme('DarkTeal6')

window = sg.Window('Crea prescrizione ', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'cancel':
        break  # Esco dal loop per chiudere il programma
    # qui le elaborazioni che non determinano chiusura della finestra
    print (event)
    print("-------------------------------------------------------------------------------------")
    print (values)
    match event:
        case "categorie_cb":  # cambiata categoria di filtro
            #print("\n ------------------ Elaboro nuova categoria")
            #print("Tutti i farmaci numero =", len(lista_farmaci))
            print (values ["categorie_cb"])
            lista_filtrata_farmaci = filtra_lista_farmaci(values ["categorie_cb"], "")  # creo una lista filtrata in base alla categoria
            #print("categorie filtrate", len(lista_filtrata_farmaci))
            window ["farmaci_cb"].update (value="", values=lista_filtrata_farmaci)

        case 'pazienti_cb':
            window["cognome_nome_cb"].update(value=values["pazienti_cb"])

        case "reset":   # resetto farmaci e categorie
            window["categorie_cb"].update(value="", values=lista_categorie)
            lista_filtrata_farmaci = filtra_lista_farmaci("","")  # creo una lista di fatto non filtrata in questo primo passaggio formata dai nomi/nomi commerciali
            window["farmaci_cb"].update(value="", values=lista_filtrata_farmaci)
            window["pazienti_cb"].update(value="")

        case "crea_pdf":        # ---------------------------------------------------------------------------------------------
            esci = False
            farmaco_da_prescrivere = values["farmaci_cb"]
            if (farmaco_da_prescrivere == "") or  (farmaco_da_prescrivere == "Farmaco da prescrivere"):
                sg.popup('Occorre specificare il farmaco da prescrivere')
                esci = True

            nome_paziente = values["cognome_nome_cb"]
            if (nome_paziente == "") or (nome_paziente == "Cognome, nome e data di nascita"):
                sg.popup('Occorre specificare il nome del paziente')
                esci = True

            formato_della_pagina = values["formato_pagina"]
            citta = values["citta"]
            data_ricetta = values["data_ricetta"]

            if not esci:   # se non c'è stato un errore in precedenza...
                pdf = FPDF(format=formato_della_pagina)    #istanzio l'oggetto PDF
                pdf.add_page()  # aggiungo una nuova pagina vuota
                #pdf.set_font("helvetica", "B", 10)  # definisco il font della pagina appena creata
                pdf.set_margins(15,10,15)   # definisco i margini sinistro, superiore e destro
                bordo = 0  #lo attivo solo per la fase di debug, per vedere meglio l'impaginazione

                # Timbro-intestazione in alto
                larghezza_intestazione = 40
                altezza_intestazione = 3.5
                pdf.set_font(family="helvetica", style="B", size=8)
                pdf.cell(larghezza_intestazione, altezza_intestazione, 'Dott. BERNARDINI Simone', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)
                pdf.set_font(style="I")
                pdf.cell(larghezza_intestazione, altezza_intestazione,'Medico specialista in Medicina', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)
                pdf.cell(larghezza_intestazione, altezza_intestazione,'fisica e riabilitazione (Fisiatria)', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)
                pdf.set_font(style="")
                pdf.cell(larghezza_intestazione, altezza_intestazione, 'Iscrizione Ordine Medici presso', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)
                pdf.set_font(style="B")
                pdf.cell(larghezza_intestazione, altezza_intestazione, ' Padova n. 8642', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)

                pdf.cell(0, 15, '', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)  # creo uno spazio vuoto

                # gestione data
                larghezza_data = 50
                altezza_data = 3.5

                pdf.set_font("helvetica", "I", 11)
                pdf.cell(0, altezza_data, citta + ", " + data_ricetta , new_x="LMARGIN", new_y="NEXT", align='R', border=bordo)

                pdf.cell(0, 30, '', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)  # creo uno spazio vuoto

                # Gestione nome e prescrizione
                pdf.set_font(style="B")
                pdf.cell(0, 6,"      " + nome_paziente, new_x="LMARGIN", new_y="NEXT", align='L', border=bordo)
                pdf.set_font(style="")

                pdf.cell(0, 20,"        - " +  farmaco_da_prescrivere, new_x="LMARGIN", new_y="NEXT", align='L', border=bordo)
                pdf.cell(0, 30, '', new_x="LMARGIN", new_y="NEXT", align='C', border=bordo)  # creo uno spazio vuoto

                # Gestione firma
                pdf.cell(0, 6, "                         _____________________________", new_x="LMARGIN", new_y="NEXT", align='L', border=bordo)
                # credo un po' di casualità nel posizionamento della firma
                spostamento_x = random.randint(0,10)
                spostamento_y = random.randint(0,2)
                print("spostamenti",spostamento_x," # ", spostamento_y)
                dimensione_firma = 50   #60
                pdf.image("autog/1.rma", x = 40+spostamento_x, y = 130 + spostamento_y, w = dimensione_firma, h = 0, type = 'png', link = '')

                # Creazione finale del file pdf
                pdf.output("Prescrizione.pdf")
                os.system("Prescrizione.pdf")
                sys.exit()

window.close()  # chiusura finale della finestra
