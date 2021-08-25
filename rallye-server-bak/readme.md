# Campusrallye Server

Dieses Tool soll die Punktevergabe und Auswertung der Campusrallye an der TUM erleichtern.


## Vision 

Der Server soll Folgende Punkte implementieren

- [ ] Server stellt Webseite zur verfügung auf der Tutoren Punkte für ihre Station eintragen können
- [ ] Server hält Datenbank vor in der die Daten organisiert sind
- [ ] erstellt Tutorzettel mit (spezifischem) QR-Code für jede Station
- [ ] erstellt Auswertung der Stationen und Gruppen
- [ ] zeigt alle Gruppennamen an und es besteht die Möglichkeit den besten Namen auszuwählen/kennzeichnen

## Config

- Aktuelles Semester

## Aufsetzen des Servers zur lokalen Nutzung
### Software
<ul>
    <li>python3</li>
    <li>django</li>
</ul>

### Virtual environment
<code>python3.6 -m venv set-tool</code> <br />
<code>cd set-tool</code> <br />
<code>source ./bin/activate</code> (Das aktivieren variiert je nach Shell) <br />
<code>pip3 install django</code> <br />
<code>git clone ...</code> <br />
<code>deactivate</code> (Nach getaner Arbeit zum Deaktivieren) <br />

### Nutzung in <a href="https://www.jetbrains.com/pycharm/">Pycharm</a>
Nach dem öffnen in Pycharm über die Inbuildcommandline zur Virtualenvironemnt navigieren. <br />
Diese aktivieren. <br />
In das Projekt navigieren. <br />
Server starten: <code>python3 manage.py runserver</code> <br />
Aufrufen der <a href="http://127.0.0.1:8000/admin">Admin-area</a> <br />
Aufrufen der Bewertungsseite: <code>http://127.0.0.1:8000/campus_rallye/tokenDesStandes</code>

### Deployen des Projekts
Virtualenv starten <code> source ./bin/activate</code> <br />
Gunicorn starten <code> ./gunicorn_start.sh </code>  <br />
Aufruf der Website  <br />
