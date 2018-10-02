#import sys
import heapq
import csv
import pickle
import json
from PIL import Image                      # funciones para cargar y manipular imágenes
import numpy as np                # funciones numéricas (arrays, matrices, etc.)
import matplotlib.pyplot as plt 
def get_probabilities(content):
    total = 128*128 # Agregamos uno por el caracter FINA
    count = 0
    v = {}
    for k in range (256):
        for i in range(128):
            for j in range(128):
                if (content[i,j])==k:
                    count = count + 1
        v[k]=count/total
        count = 0
    #v['end'] = 1.0/total
    return v

def make_tree(probs):
    q = []
    # Agregamos todos los símbolos a la pila
    for ch,pr in probs.items():
        # La fila de prioridad está ordenada por
        # prioridad y profundidad
        heapq.heappush(q,(pr,0,ch))
    # Empezamos a mezclar símbolos juntos
    # hasta que la fila tenga un elemento
    while len(q) > 1:
        e1 = heapq.heappop(q) # El símbolo menos probable
        e2 = heapq.heappop(q) # El segundo menos probable        
        # Este nuevo nodo tiene probabilidad e1[0]+e2[0]
        # y profundidad mayor al nuevo nodo
        nw_e = (e1[0]+e2[0],max(e1[1],e2[1])+1,[e1,e2])
        heapq.heappush(q,nw_e)
    return q[0] # Devolvemos el arbol sin la fila

def make_dictionary(tree):
    res = {}
    search_stack = []
    search_stack.append(tree+("",)) # El último elemento de la lista es el prefijo!
    while len(search_stack) > 0:
        elm = search_stack.pop()
        if type(elm[2]) == list:
            prefix = elm[-1]
            search_stack.append(elm[2][1]+(prefix+"0",))
            search_stack.append(elm[2][0]+(prefix+"1",))
            continue
        else:
            res[elm[2]] = elm[-1]
        pass
    return res

def compres(dic,content):
    #res = ""
    new ={}
    for k in range(256):
        for i in range(128):
            for j in range(128):
                if (k==content[i,j]):
                    new[i,j]=dic[k]
    return new

def store(data,dic,outfile):
    # Guardamos la cadena de bits en un archivo, que abrimos
    # en modo binario (por eso 'wb')
    outf = open(outfile,'wb')
    pickle.dump(compressed,outf)
    outf.close()
    # Guardamos el diccionario en otro archivo en formato JSON
    outf = open(outfile+".dic",'w')
    json.dump(dic,outf)
    outf.close()
    pass

def eficiencia (probs,dic):
    sumat=0
    for i in range (256):
        sumat=len(dic[i])*probs[i]+sumat
    return sumat

def decode(comprimido,dic):
    v={}
    matriz =  np.matrix(np.empty(shape=(0,128), dtype=np.float32))
    for k in range (256):
        for i in range(128):
            for j in range(128):
                if(comprimido[i,j]==dic[k]):
                    v[i,j]=k
                    matriz=np.insert(matriz, i, [1, 0, 0], axis = 0) 
    return matriz

I = Image.open("./pruebas.jpg")
I1=I.convert('L') # convierte a escala de grises
a=np.asarray(I1,dtype=np.float32)  
probs = get_probabilities(a)
# Construimos el árbol de parseo! : )
tree = make_tree(probs)
# Construimos el diccionario para codificar
dic = make_dictionary(tree)
# Creamos el contenido del nuevo archivo
compressed = compres(dic,a)    
store(compressed,dic,"encodeImg")
#Calculamos la eficiencia del algoritmo
#eficiend = eficiencia(probs,dic)
decode = decode(compressed,dic)

