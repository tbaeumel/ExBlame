# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 09:23:47 2016

@author: Tanja
"""

import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
import copy


#creates a tree out of a .xml file
def tree(xml_doc):
    if '.vgl' in xml_doc:
        f = open(xml_doc)
        text = f.read()
        no_footer = text[:text.index('---SOURCE')-2]
        elem = ET.fromstring(no_footer)
        tree = ET.ElementTree(elem)
        return tree        
    else:        
        tree = ET.parse(xml_doc)
        return tree

#sourcestory

def story(file):
    f = open(file)
    text = f.read()
    story = text[text.index('BELOW---')+8:]
    return story    


# choose the .vgl file (ich lass das else mal drinnen, sodass man im notfall auch
# mit einem .xml started kann, das funktioniert dann aber mit der source story nicht)
xml = input('Choose a .vgl-file: ')
tree = tree(xml)
root = tree.getroot()
story = story(xml)

# fills list 'links' with the storypoints that contain links
storypoints = len(root[1])
#print(storypoints)
links = []

print('')        
#for i in range (0, storypoints): 
    #if 'linkInterpElements' in root[1][i].text:
        #links.append(root[1][i].text)
        
for i in range (0, storypoints): 
    if root[1][i].text.startswith('linkInterpElements'):
        links.append(root[1][i].text)
        #print (root[1][i].text)
        #print('')
#print(len(links))

# deepcopy links to remember all of them         
temp_links = copy.deepcopy(links)
'''
This following long part considers the combinations: actualizes+damages and 
ceases+providesfor. 
It could be easily extended to test other theories of combinations, by adding/
replacing new combinations of links to these ones.

''' 
'''
### list with all interpretative nodes (to look up agents of goals that are 
    damaged)       
print('')
print('InterpretativeNodes')
for i in range (0, storypoints): 
    if 'assignInterpNode' in root[1][i].text:
        print(root[1][i].text)
        print('')
'''

#look for actualizes and the corresponding node (interp-action, 
# interp-interp or interp-condition -> since the A is always 
# an action / property we don't have to worry about this finding
#A instead of B (where a is linked to b))
actualized = []
for i in range (0, len(links)):
    if 'InterpretativeArcType.Actualizes' in links[i]:
        #print(i, 'JA')
        words = word_tokenize(links[i])
        for w in words: 
            if w.startswith('interp'):
                actualized.append(w)
                actualized.append(i)
        # to make sure that the same link is not considered 
        # again later
        links[i]= '0' 
#print(actualized)       
#blame = []
blame2= []
#in actualized sind jetzt alle actualized B's -> need to see, if 
# B damages something
for i in range (0, len(actualized),2):
    #print(actualized[i])
    damage = False
    for j in range (0, len(links)):
        if actualized[i] in  word_tokenize(links[j]):
            #search for corresponding damages link:
            if 'Damages' in links[j]: 
                words2= word_tokenize(links[j])
                for w in words2:
                    #we want to find out what goal is damaged
                    if w.startswith('interp') and not w == actualized[i]:
                        damage = True
                        blame2.append(temp_links[actualized[i+1]])
    
#print(blame2)
#print(len(blame2))                   
#Die selbe geschichte für ceases + providesFor                        
ceased = []
for i in range (0, len(links)):
    if 'InterpretativeArcType.Ceases' in links[i]:
        #print(links[i], 'JA')
        words = word_tokenize(links[i])
        for w in words: 
            if w.startswith('interp'):
                ceased.append(w)
                ceased.append(i)
        # to make sure that the same link is not considered 
        # again later
        links[i]= '1'
        
#print(ceased)
#in ceased sind jetzt alle ceased B's -> need to see, if 
# B ProvidesFor something
for i in range (0, len(ceased),2):
    for j in range (0, len(links)):
        if ceased[i] in  word_tokenize(links[j]):
            #search for corresponding providesfor link:
            if 'ProvidesFor' in links[j]: 
                words2= word_tokenize(links[j])
                for w in words2:
                    #we want to find out what goal is providedfor
                    if w.startswith('interp') and not w == ceased[i]:
                        blame2.append(temp_links[ceased[i+1]])
'''
for i in range (0, len(blame2)):
    print(blame2[i])
    print('')
 '''
toPrint = []
for i in range (0, len(blame2)):
    text = blame2[i]
    source = text[text.index('**5')+1: text.index(')**')]
    found = False
    j = 0 
    while not found: 
        if source in root[1][j].text:
            toPrint.append(root[1][j].text) 
            found = True
        else: j = j+1

toPrint_singles = set(toPrint)        
'''
for i in range (0, len(toPrint_singles)):
    print(toPrint[i])
    print('')
'''        
#print corresponding sentences
# +1 nicht vergessen
index = []
toPrint_list = list(toPrint_singles)
for i in range (0, len(toPrint_list)):  
    index.append(toPrint_list[i].index('span'))
    index.append(toPrint_list[i])
#print(index)    
index_range = []
for i in range (0, len(index),2):
    pos = index[i] + 4
    index_range.append(index[i+1][pos:])
    
for i in range (0, len(index_range)):
    start = index_range[i][:index_range[i].index('-')]    
    #print(start)
    end = index_range[i][index_range[i].index('-')+1:index_range[i].index(',')]
    #print(end)
    print(story[int(start)+1:int(end)+1])
    print('')
    




# include active agents   
#characters intentions -> evil vs stupid
# trace back to intentional action  
# would cause arcs      

# PROBLEM: apparently actualizes + provides for is outputted to -> WRONG
# komisch zB bei wolf in sheeps clothing: 3* actualizes, aber eigentlich 
# nur 2mal (wieder aczualizes + provides)        
# RIGHT now: only ceases arcs, not the actualizes arcs   

#um untereinheiten von zielen mitzuberücksichtigen:
# EVTL EINBAUEN: if ... ceases/actualizes interp-interp_8: 
#                   if attachInterpPredicate zu interp-...:
#                       gucken ob interp-... etwas damaged oder provided 