#!/usr/bin/env python3
import subprocess
import json
import pyqrcode
import argparse


ANZ_STATIONEN = 23
ANZ_GRUPPEN = 200
URL = "https://set.lamf.de/campus_rallye/" #Hinter diese URL wird das Token aus dem JSON File angefügt
F_PREF_ANLEITUNG = "a-"
F_PREF_PUNKTE = "p-"
F_SUF = ".tex"


def generate_qr_code(link, filename):
    '''
    Erstellt den QR-Code aus Token und URL
    '''
    filename_export = filename + ".png"
    url = pyqrcode.create(link)
    url.png(filename_export, scale=20, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])


def generate_pdf(nummer, name, ansprechpartner, link, anleitung_file,
                 punkte_file, kontakt_file, karte_file, anzahl_gruppen, hinweise, vorlagen_nummer):
    '''
    Erstellt aus allen Informationen und tmp-files das fertige PDF
    '''
    qr_code_file_name = "QR-" + str(nummer)
#    generate_qr_code(link, qr_code_file_name)

    param = r'\\def \\stationsNummer {' + str(nummer)
    param += r'} \\def \\stationsName {' + name
    param += r'} \\def \\stationsAnsprechpartner {' + ansprechpartner
    param += r'} \\def \\stationsLink {' + link
    param += r'} \\def \\stationsQRCode {' + qr_code_file_name
    param += r'} \\def \\stationsAnleitung {' + anleitung_file
    param += r'} \\def \\stationsAnleitungPunkte {' + punkte_file
    param += r'} \\def \\stationsAnleitungKontakt {' + kontakt_file
    param += r'} \\def \\stationsKarte {'+ karte_file
    param += r'} \\def \\hinweise {'+ hinweise
    param += r'} \\def \\anzahlGruppen {' + str(anzahl_gruppen)
    param += r'} \\input{Tutorzettel-'+ str(vorlagen_nummer) +'.tex}'

    subprocess.call(['bash', '-c', 'pdflatex ' + param])

    print("\n")
    print(param)

#------------------ Subfiles

def create_sub_files(station):
    '''
    Erstellt tex-files Punkte und Anleitung
    '''
    nummer = station['ID']
    create_anleitung(station, nummer)
    create_punkte(station, nummer)

def create_punkte(station, nummer):
    '''
    Erstellt tex-files aus den JSON informationen (Punkteverteilung)
    '''
    punkte = station['Punkteverteilung'] + "\\ \\\\ \n"
    write_file(F_PREF_PUNKTE + str(nummer) + F_SUF, punkte)


def create_anleitung(station, nummer):
    '''
    Erstellt tex-files aus den JSON inforamtionen (Anleitungen)
    '''
    pref = "\\begin{description} \n"
    suf = "\\end{description} \n"

    ort = "\\item[Location:] " + station['Ort'] + "\\\\ \n"
    utensilien = "\\item[Materials:] " + str(station['Utensilien']) + " \n"
    aufbau = "\\item[Setup:] " + station['Aufbauanleitung'] + " \n"
    ablauf = "\\item[Process:] " + station['Ablauferklaerung'] + " \n"

    cnt = pref + ort + utensilien + aufbau + ablauf + suf

    write_file(F_PREF_ANLEITUNG + str(nummer) + F_SUF, cnt)


def write_file(name, content):
    '''
    Auslagerung des Datei schreibens
    '''
    file = open(name, 'w')
    file.write(content)

#------------------ Erstellung eines Stationsfiles
def create_one_station(data, nummer):
    station = data['stationen'][nummer-1]

    '''
    Diese Funktion erstellt einen Tutorzettel.
    Die Vorlage wird kopiert, die Inhalte werden Temporär erzeugt und nach dem compilen gelöscht.

    @param station : station ist ein dic, das die Informationen zu dieser Station enthält
    @param vorlagen_nummer : die Nummer der Vorlage, die für den Compile-Vorgang benutzt werden soll
    '''
    print("Gen Station " + str(nummer) + "...")
    
    command = 'cp ./res/Vorlage.tex Tutorzettel-' + str(nummer) + '.tex'

    # Vorbereiten der Vorlage
    subprocess.call(['bash', '-c', command])

    nummer = str(station["ID"])
    name = station["Name"]
    ansprechpartner = station["Ansprechpartner"]
    link = URL + station["Token"]
    kontakt = "res/kontakt"
    karte = "res/karte"
    hinweise = "res/hinweise"

    create_sub_files(station)
    generate_pdf(nummer, name, ansprechpartner, link, F_PREF_ANLEITUNG + str(nummer),
                 F_PREF_PUNKTE + str(nummer), kontakt, karte, ANZ_GRUPPEN, hinweise, nummer)
    clean_vorlagen()

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

def create_all_stations(data):
    '''
    Diese Funktion erstellt alle Stationen
    '''
    for json_index in range(0, ANZ_STATIONEN):
        create_one_station(data, json_index+1)
    clean_vorlagen()

def create_stationen_uebersicht(data):
    cont = r'\\section*{Stationen} \\begin{itemize}'
    vorlagen_file_name = "Uebersicht-Zettel"
    
    command = 'cp ./res/wrapper.tex ' + vorlagen_file_name + '.tex'
    subprocess.call(['bash', '-c', command])

    for station in data['stationen']:
        cont += r'\\item [' + str(station['ID']) + r'] ' + station["Name"] + " - " +  station["Tutorenanzahl"]

    cont += r'\\end{itemize}'
    print(cont)

    param = r'\\def \\cont {' + cont + r'} \\input{' + vorlagen_file_name + r'.tex }'
    subprocess.call(['bash', '-c', 'pdflatex ' + param])
    clean_vorlagen()


def create_orga_zettel(data):
    '''
    Erstellt eine Uebersicht über alle Stationen, ohne Hinweise QR-Code ect
    '''
    vorlagen_file_name = "Orga-Zettel"
     
    command = 'cp ./res/wrapper.tex ' + vorlagen_file_name + '.tex'
    subprocess.call(['bash', '-c', command])


    sep = r'\\newpage'
    cont = r''
    for station in data['stationen']:
        create_sub_files(station)
        index = station['ID']
        cont += r'\\ \\\\ \\section*{' + str(index) + r' - ' + station['Name'] + r'}'
        cont += r'\\subsection*{Anleitung} \\input{a-' + str(index) + r'.tex}'
        cont += r'\\subsection*{Punkte} \\input{p-' + str(index) + r'.tex}'
        cont += sep
    print(cont)
    param = r'\\def \\cont {' + cont + r'} \\input{' + vorlagen_file_name + r'.tex }'
    subprocess.call(['bash', '-c', 'pdflatex ' + param])
    clean_vorlagen()



def create_utensilien_liste(data):
    '''
    Erstellt eine Liste mit allen Utensilien
    '''
    vorlagen_file_name = "Utensilien-Liste"
     
    command = 'cp ./res/wrapper.tex ' + vorlagen_file_name + '.tex'
    subprocess.call(['bash', '-c', command])

    cont = r''
    for station in data['stationen']:
        index = station['ID']
        cont += r'\\section*{' + str(index) + r' - ' + station['Name'] + r'} '
        cont += r'\\begin{itemize} '
        for utensil in station['Utensilien']:
            cont += r'\\item ' + str(utensil) + r' '

        cont += r'\\end{itemize} '
     
   # print(cont)
    param = r'\\def \\cont {' + cont + r'} \\input{' + vorlagen_file_name + r'.tex}'
    subprocess.call(['bash', '-c', 'pdflatex ' + param])
    clean_vorlagen()


def init(json_file):
    '''
    Diese Funktion liest das JSON File ein und gibt es zurück.
    '''
    with open(json_file) as data_file:
        data = json.load(data_file)
    return data


def clean_vorlagen():
    '''
    Diese Funktion Löscht alle beim compilen angelegten tmp daten.
    '''
    subprocess.call(['bash', '-c', './res/clean.sh'])

#----------------------------------------------------------- Main

def main():
    '''
    Main Function
    '''
    data = init('stationen.json')
    
    parser=argparse.ArgumentParser(description="Dies ist ein Tool zu generierung der Tutorzettel fuer die SET Campus Rallye")
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', nargs='?', type=int, const=-1, help="generiere Tutorenzettel")
    group.add_argument('-u', action='store_true', help="generiere Utensilienliste")
    group.add_argument('-o', action='store_true', help="generiere Orgaliste")
    group.add_argument('-s', action='store_true', help="generiere Stationenuebersicht")
    group.add_argument('-a', action='store_true', help="generiere Alles")
    args=parser.parse_args()

    if args.u:
        print("Drucke Utensilien")
        create_utensilien_liste(data)
    elif args.a:
        create_orga_zettel(data)
        create_all_stations(data)
        create_orga_zettel(data)
        create_utensilien_liste(data)
    elif args.o:
        print("Drucke Orga")
        create_orga_zettel(data)
    elif args.s:
        print("Drucke Uebersicht")
        create_stationen_uebersicht(data)
    elif args.t==-1:
        create_all_stations(data)
    else:
        create_one_station(data, args.t)

main()
