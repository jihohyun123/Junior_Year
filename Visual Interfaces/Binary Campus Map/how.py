import cv2
import numpy as np
import imutils
from PIL import Image
from matplotlib import pyplot as plt
import what_where as p1



def main():
    b_c = p1.combined_steps()
    n = NSEW('n', b_c)
    s = NSEW('s', b_c)
    e = NSEW('e', b_c)
    w = NSEW('w', b_c)
    for key in b_c:
        print(key + " is south of: ")
        if key in n:
            print(n[key])
        else:
            print("nothing")
        print(key + " is north of: ")
        if key in s:
            print(s[key])
        else:
            print("nothing")
        print(key + " is west of: ")
        if key in e:
            print(e[key])
        else:
            print("nothing")
        print(key + " is east of: ")
        if key in w:
            print(w[key])  
        else:
            print("nothing")  


def NSEW(direction, b_c):
    
    
    #print(b_c)
    if direction == 'n':
        n = getNorthVals(b_c)
        return n
    elif direction == 's':
        s = getSouthVals(b_c)
        return s
    elif direction == 'e':
        e = getEastVals(b_c)
        return e
    elif direction == 'w':
        w = getWestVals(b_c)
        return w    

# a function to generate all key : north[] pairings
def getNorthVals(b_c):
    
    north = {}
    for key1 in b_c:
        
        l1 = b_c[key1]
        for key2 in b_c:
            if key2 != key1:
                l2 = b_c[key2]
                if l2[1][1] < l1[1][1] and l2[2][1] < l1[2][1]:
                    hdist = abs(l1[1][0] - l2[1][0])
                    vdist = abs(l1[1][1] - l2[1][1])
                    
                    # ratio of horizontal and vertical distance is less than 6
                    if hdist/vdist < 6:
                        
                        if key1 not in north:
                            north.update({key1 : []})
                            north[key1].append(key2)
                        else:
                            north[key1].append(key2)
    

    # transitive reduction step
    for b in north:
        
        for b2 in north:
            l1 = north[b]
            
            for e in l1:
                if e in north:
                    l2 = north[e]
                    for e2 in l2:
                        if e2 in l1:
                            l1.remove(e2)
    return north

# a function to generate all key : south[] pairings
def getSouthVals(b_c):
    
    south = {}
    for key1 in b_c:
        
        l1 = b_c[key1]
        for key2 in b_c:
            if key2 != key1:
                l2 = b_c[key2]

                # making sure that both corners of the target building
                # are lower than the second
                if l2[1][1] > l1[1][1] and l2[2][1] > l1[2][1]:
                    hdist = abs(l1[1][0] - l2[1][0])
                    vdist = abs(l1[1][1] - l2[1][1])
                    
                    # ratio of horizontal and vertical distance is less than 6
                    # to ensure that buildings on the otherside of campus but only 
                    # incrementally more south are excluded

                    if hdist/vdist < 6:
                        
                        if key1 not in south:
                            south.update({key1 : []})
                            south[key1].append(key2)
                        else:
                            south[key1].append(key2)
    
    k = 0
    for b in south:
        
        for b2 in south:
            l1 = south[b]
            
            for e in l1:
                if e in south:
                    l2 = south[e]
                    for e2 in l2:
                        if e2 in l1:
                            l1.remove(e2)
    #print(south)

    return south


def getEastVals(b_c):
    
    east = {}
    for key1 in b_c:
        
        l1 = b_c[key1]
        for key2 in b_c:
            if key2 != key1:
                l2 = b_c[key2]

                # making sure that both corners of the target building
                # are lower than the second
                if l2[1][0] > l1[1][0] and l2[2][0] > l1[2][0]:
                    hdist = abs(l1[1][0] - l2[1][0])
                    vdist = abs(l1[1][1] - l2[1][1])
                    
                    # ratio of horizontal and vertical distance is less than 6
                    # to ensure that buildings on the otherside of campus but only 
                    # incrementally more east are excluded

                    if vdist/hdist < 6:
                        
                        if key1 not in east:
                            east.update({key1 : []})
                            east[key1].append(key2)
                        else:
                            east[key1].append(key2)
    
    k = 0
    for b in east:
        
        for b2 in east:
            l1 = east[b]
            
            for e in l1:
                if e in east:
                    l2 = east[e]
                    for e2 in l2:
                        if e2 in l1:
                            l1.remove(e2)

    return east


def getWestVals(b_c):
    
    west = {}
    for key1 in b_c:
        
        l1 = b_c[key1]
        for key2 in b_c:
            if key2 != key1:
                l2 = b_c[key2]

                # making sure that both corners of the target building
                # are lower than the second
                if l2[1][0] < l1[1][0] and l2[2][0] < l1[2][0]:
                    hdist = abs(l1[1][0] - l2[1][0])
                    vdist = abs(l1[1][1] - l2[1][1])
                    
                    # ratio of horizontal and vertical distance is less than 6
                    # to ensure that buildings on the other side of campus vertically but only 
                    # incrementally more west are excluded

                    if vdist/hdist < 8:
                        
                        if key1 not in west:
                            west.update({key1 : []})
                            west[key1].append(key2)
                        else:
                            west[key1].append(key2)
    
    k = 0
    for b in west:
        
        for b2 in west:
            l1 = west[b]
            
            for e in l1:
                if e in west:
                    l2 = west[e]
                    for e2 in l2:
                        if e2 in l1:
                            l1.remove(e2)

    return west

def North(S, T, b_c):
    n = NSEW('n', b_c)
    return search(n, S, T) 
    
def South(S, T, b_c):
    s = NSEW('s', b_c)
    return search(s, S, T)

def East(S, T, b_c):
    e = NSEW('e', b_c)
    return search(e, S, T)

def West(S, T, b_c):
    w = NSEW('w', b_c)
    return search(w, S, T)


# recursively searches for the target 
def search(n, S, T):
    
    # if Target is Source
    if S == T:
        return True
    # checking Source is valid
    if S in n:
        # children of search
        l = n[S]

        # if Target is in the children of Source
        if T in l:  
            return True
        # else recursively call search again, using each child as Source
        else:
            for e in l:
                return search(n, e, T)
    # if not, false
    else:

        return False
    



main()

