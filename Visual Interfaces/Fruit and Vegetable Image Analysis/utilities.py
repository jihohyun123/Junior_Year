"""
This is a general purpose library file I've created for Assignment 2
in an effort to keep my code modularized and easy to follow.
I did not look at any code online other than the documentation for the libraries listed below.

"""

from PIL import Image
import numpy as np
from scipy import ndimage
import sys
import imageio
import heapq
import matplotlib.pyplot as plt
import cv2



# GENERAL--these methods are shared by color.py, texture.py, and shape.py


# wrote a function to generate all the filenames as strings
def getnames():
    
    """Appending stringnames together with numbers """
    
    k = 1
    names = {}

    
    while k <= 40:
        if k < 10:
            name = 'i0' + str(k) + '.jpg'
        else:
            name = 'i' + str(k) + '.jpg'
        names[k] = name
        k+=1

    """Returning a dictionary with filenames and indices """
    return names


# This method returns the results of comparisons 
def plot_figures(typec, arrimages):
    
    """I chose to display the results as an html file."""
    
    # read in both Crowd and MyPreference text files.
    f1 = open('Crowd.txt', 'r')
    my = open('MyPreferences.txt', 'r')
    crowd = []
    mypref = []
    
    # line by line
    for line in f1:
        crowd.append(line.split())
    for line in my:
        mypref.append(line.split())
    
    row = 0
    scores = []
    counts = []
    common = 0
    special = 0

    for entry in arrimages:
        
        # creating two sets to use for set intersection between the results and the Crowd file, as well as 
        # between 
        s1 = {}
        s1 = set()
        s2 = {}
        s2 = set()
        
        # setting a count 
        score = 0
        
        rowcount = []
        
        # the top three choices, from index 1-4
        for idx in range(1, 4):
            
            # number of the image (parsing the filename)
            t = int(entry[idx][1:3])
            
            # adding to set 1
            s1.add(t)
            
            # crowd score
            count = crowd[row][t-1]
            rowcount.append(count)

            # incrementing the score for the score 
            score = score + int(count)
            mynum = mypref[row][idx]
            
            # adding my preference to set 2
            s2.add(int(mynum))
        
        # common returns the number of elements in the set intersection:
        intersect = s1.intersection(s2)
        size_of = len(s1.intersection(s2))
        if size_of == 3:
            print("row of identical elements: ", intersect)
            special += 1
        common = common + size_of
        rowcount.append(crowd[row][int(entry[4][1:3])-1])
        counts.append(rowcount)
        scores.append(score)
        
        row += 1
    # closing the files
    f1.close()
    my.close()
    print("special: ", special)
    # creating a new file to return the results
    name = str(typec) + ".html"
    f2 = open(name,'w')

    grandtotal = np.sum(scores)
    # lots of HTML string manipulation, but I've created a table with 40 rows and 5 columns
    message = """<html><body>
    <table><tr><h1>"""+""" """+typec+""" """+""" comparison</h1></tr><tr>Sum of Scores: """+""" """+str(grandtotal)+""" """+"""</tr>"""

    row = ""
    
    i = 0
    # for all rows
    while i < 40:
        
        images = ""
        j = 0

        # for all columns
        while j < 5:
            filename = arrimages[i][j]
            image = """ <td align="left">"""  + """<img src=""" + """ """ + filename + """ """ + """ 
            align="middle"><br>"""+ filename[1:3]
            
            # if it is the first image in a row, it is the target, so I return the Score calculation result
            if j == 0:
                first = """ <br> """ + """ Score: """  + """ """ + str(scores[i]) + """ """ +  """</td>"""
                image = image + first

            # otherwise, I attach the count of the image as more information
            else:
                reg = """ <br> """ + """ Count: """  + """ """ + str(counts[i][j-1]) + """ """ + """</td>"""
                image = image + reg

            # more string manipulation
            images = images + image
            j += 1
        row = row + images + """</tr>"""
        i += 1
    end = """<tr></html></body></table>"""
   
    # the final message in HTML to be written to the file
    message = message + row + end

    f2.write(message)
    f2.close()
    return common
    

# This is a method that takes in a comparison type and runs the specified comparison method
def ranking(typec):
    names = getnames()
    arrimages = []

    for cur in names:
        scores = []
        for key in names:

            if names[key] != names[cur]:
                
                # run the comparison:
                
                # color comparison
                if typec == 'color':
                    c_score = colcompare(names[key], names[cur])   
                    scores.append((c_score, names[key]))
                
                # texture comparison
                elif typec == 'texture':
                    t_score = texcompare(names[key], names[cur])
                    scores.append((t_score, names[key]))
                
                # shape comparison
                elif typec == 'shape':
                    s_score = shapecompare(names[key], names[cur])
                    scores.append((s_score, names[key]))
                
                # combined comparison:
                elif typec == 'combined':
                    
                    g_score = 0.6*colcompare(names[key], names[cur]) + 0.15*texcompare(names[key], names[cur]) + 0.45*shapecompare(names[key], names[cur])
                    
                    scores.append((g_score, names[key]))
        
        # ranking the three closest images for each image
        

        # I chose to use a heap to easily access the three smallest scores every time
        heapq.heapify(scores)

        # the three images with the smallest scores
        smallest = heapq.nsmallest(3, scores)
        first = names[cur]
        images = []
        images.append(first)
        
        
        i = 1
        for image in smallest:
            images.append(image[1])  
            i += 1

        # obtaining the element with the largest score, i.e. the most different
        large = heapq.nlargest(1, scores)
        
        far = large[0][1]
        
        images.append(far)
        
        arrimages.append(images)
    
    out = plot_figures(typec, arrimages)
    return out



# COLOR

# a function that returns an array of 3 color histograms: blue, green, and red, respectively
def colortest(i1):
    img = cv2.imread(i1, -1)

    # creating the three dimensional color histogram: 
    
    """I used 4, 16, 16 as my partition for b,g,r"""
    
    hist = cv2.calcHist([img],[0, 1, 2], None, [4, 16, 16], [0,256]*3)
    
    return hist


# a function that compares two images
def colcompare(i1, i2):
    hist1 = colortest(i1)
    hist2 = colortest(i2)
    i = 0

    # This is where I run the L1 calculation:
    diff = (np.sum(abs(hist1-hist2)))/(2*60*89)
    
    return diff



# SHAPE

# This is a function that does the binary threshold in shape comparison
def binthresh(img):
    
    image = cv2.imread(img)
    
    gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    

    # I set the threshold minimum at 90; this is something I determined through trial and error.
    thresh, bw = cv2.threshold(gs, 90, 255, cv2.THRESH_BINARY)
    
    return bw
 

def shapecompare(i1, i2):
    bw1 = binthresh(i1)
    bw2 = binthresh(i2)
    
    
    j = 0
    count = 0
    while j < len(bw1):
        i = 0
        while i < len(bw1[0]):
            if bw1[j][i] != bw2[j][i]:
                count += 1
            i += 1
        j += 1
    count = count / (60*89)
    return count

    






# TEXTURE


# This is a method that gets a Lapacian image for texture comparison
def tex(i1):

    # converting to grayscale
    gray = cv2.imread(i1, cv2.IMREAD_GRAYSCALE)

    # creating a kernel
    kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])

    # filtering the grayscale with the kernel
    temp = cv2.filter2D(gray, -1, kernel)
    
    # obtaining single channel histogram for intensity changes
    histr = cv2.calcHist([temp],[0],None,[8],[0,256])
    
    
    return histr


# This is a method that again calculates the L1 Distance between two histograms
def texcompare(i1, i2):
    
    hist1 = tex(i1)
    hist2 = tex(i2)
    
    diff = (np.sum(abs(hist1-hist2)))/(2*60*89)
    
    return diff


