import subprocess
import sys

def caesar(plaintext, shift):
    ciphertext=""
    shift=shift%26
    for c in plaintext:
        if c==" ":
            ciphertext+=c
            continue
        x = ord(c) + shift
        if x > ord('Z'):
            x-=26
        elif x < ord('A'):
            x+=26
        ciphertext+=chr(x)
    return ciphertext


def isalphaspace(s):
    res=True
    for c in s:
        if(not(c.isalpha() or c==" ")):
            res=False
    return res
def compile(s):
    param = r'\\def \\cipher {' + s + r'} \\input {' + "Krypto.tex" + '}'
    subprocess.call(['bash', '-c', 'pdflatex ' + param])

def main():
    plaintext=sys.argv[1]
    shift=int(sys.argv[2])
    if(isalphaspace(plaintext)):
        plaintext=plaintext.upper()
        print("Plaintext: " + plaintext)
        ciphertext=caesar(plaintext, shift)
        print("Ciphertext: " + ciphertext)
        compile(ciphertext)
    else: 
        print("Input must only contain space or the letters A-Z")

main()
