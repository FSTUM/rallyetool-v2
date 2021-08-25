import json
import subprocess
import argparse
import sys

template=""

def compilePage(page):
    path=str(page["index"]) +"_letter_" + page["letter"]+".tex"
    subprocess.call(['bash','-c', 'cp ' + template + ' ' + path])
    param = r'\\def \\letter {' + page["letter"]
    param += r'} \\def \\place {' + "You are here: "+page["place"]+ ' \(' + str(page["index"])+'\)'
    param += r'} \\def \\nxt {'
    if 'next' in page:
        param += "Location of the next letter: " + page['next']
    else:
        param += ""
    param += r'} \\input {' + path + '}'
    subprocess.call(['bash', '-c', 'pdflatex ' + param]) 

def generateAllPages(data):
    lastPage=None
    for i, page in enumerate(data["pages"]):
        page["index"]=i
        print(page["index"], page["letter"], page["place"])
        if(not(lastPage is None)):
            lastPage["next"]=page["place"]
            compilePage(lastPage)
        lastPage=page
    compilePage(lastPage)

def init(jsonFile):
    with open(jsonFile) as data_file:
        data = json.load(data_file)
    return data

def main():
    data=init(sys.argv[1])
    global template 
    template=sys.argv[2]
    generateAllPages(data)
        
main()
