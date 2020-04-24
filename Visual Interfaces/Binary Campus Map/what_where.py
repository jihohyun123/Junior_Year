import cv2
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import sys


def main():
    buildings = combined_steps()


# text_to_dict --- returns dictionary of id : name pairs dict

def text_to_dict():
    f1 = open('new-table.txt', 'r')

    f = f1.readlines()
    
    id_name = {}
    for c in f:
        c.strip()

        # getting building id
        id = int(c[0:3])

        # getting building name
        name = c[3::].strip()

        # adding to dict
        id_name.update({id:name})
    
    return id_name



# A method for taking each step and putting it all together

def combined_steps():
    
    # getting dict of id : names
    id_name = text_to_dict()
    
    # reading in the image (labeled pgm)
    image = cv2.imread('new-labeled.pgm')
    
    # output file to write to
    output = open("output.txt", "w")
    
    # dictionary for storing name : coordinate pairs
    ref = {}
    
    """ I decided to structure the algorithm by extracting information
    from each building one at a time, then putting the pieces back together
    by using the data that was retrieved from each building """

    # for every building id, we repeat the process
    for id in id_name:
        
        name = id_name[id]

        # create a copy of the image
        im = image.copy()
        
        # process the image, isolating single building according to id
        p = process_img(id, im)
        
        # getting the description of the image
        desc = get_desc(p)

        # printing for reference
        #print(name, desc)
        
        # writing translated output to file
        output.write(translate(name, desc))
        output.write('\n')

        # coordinates of center, upper left, lower right points of bound rect
        coords = [desc[0], (desc[2][0], desc[2][1]), (desc[3][0], desc[3][1])]
        
        # adding name : coordinate pairings to dictionary for future use
        ref.update({name : coords})
        
    output.close()

    # return reference dictionary for use with relative location 

    return ref
   

    

# This method takes the name and the description 
# and translates it into a readable sentence 

def translate(name, desc):
    i = 0
    
    phrase = name

    """ basically, handling all pieces of information differently and returning
    # boilerplate template with values filled in """

    while i < len(desc):
        if i == 0:
            phrase += " has center of: " + str(desc[i]) + ", "
        elif i == 1:
            phrase += " has area of: " + str(desc[i]) + ", "
        elif i == 2:
            phrase += " upper left XY: " + str(desc[i]) + ", "
        elif i == 3:
            phrase += " lower right XY: " + str(desc[i]) + ", "
        elif i == 5:
            phrase += str(desc[i]) + ", "    
        elif i == 6:
            phrase += " is " + str(desc[i]) + ", "
        elif i == 9:
            phrase += " is " + str(desc[i][0])
            j = 1
            while j < len(desc[i]):
                phrase += " and is "+ str(desc[i][j])
                j += 1
        else:
            phrase += " is " + str(desc[i]) + ", "
        
        i += 1
    
    return phrase



# a function that takes the image and isolates a single building according to a single building code

def process_img(code, im):
    
    # creating a copy

    new_im = im.copy()
    count = 0
    
    # isolating the pixels that contain the code
    for row in new_im:
        for pixel in row:
            i = 0
            while i < len(pixel):
                
                # everything "not" the building is set to 0
                if int(pixel[i]) != code:
                    pixel[i] = 0
                
                # everything inside the building is set to 1
                else:
                    pixel[i] = 255
                i += 1

    return new_im


# a function that returns a description of the object in the image

def get_desc(im):
    
    """In this step, I ran all the computer vision algorithms:
    creating a binary image, finding the contours, flipping for symmetry,
    approximating a polygonal curve for shape, etc. """ 

    # binary threshold
    image = im.copy() 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    
    # using the number of layers in hierarchy to determine whether holes exist
    if len(hierarchy[0]) > 1:
        holes = "hasHoles"
    else:
        holes = "hasNoHoles"
    
    # using the contours as a parameter
    c = contours[0]

    # getting symmetry
    sym = isSymmetric(c, im)

    # getting shape
    shape = det_shape(c, sym[2], sym[3])

    # getting size
    s = sizeA(c)    
    
    # getting center of mass, area, small/medium/large
    center = com(c)
    area = s[0]
    sml = s[1]

    # putting all the descriptors in order and returning a list
    stats = [center, s[0], sym[0], sym[1], s[1], holes, sym[2], shape, sym[3], sym[4]]
        
    return stats
    
# a function for getting area
def sizeA(c):
    
    """ I used the contourArea function in openCV """

    s = cv2.contourArea(c)
    
    # cutoffs for small, medium, large
    if s < 2000:
        return (s, 'small')
    elif s < 5000:
        return (s, 'medium')
    else:
        return (s, 'large')

# a function for getting center of mass
def com(c):

    # I used the moments of the image
    
    m = cv2.moments(c)
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])
    c_o_m = (x, y)
    
    return c_o_m

# a function for determining the symmetry of an image
def isSymmetric(c, image):

    # getting the bounding rectangle
    rect = cv2.boundingRect(c)

    x, y, w, h = rect
    
    # if width and height are significantly different,
    # I gave the image an orientation

    if w/h > 1.5:
        orient = "East2West"
    elif h/w > 1.5:
        orient = "North2South"
    else:
        orient = "No Single Orientation"
    
    center = int(x + w/2), int(y + h/2)
    
    uLeft = x, y
    lRight = x + w, y + h
    
    # getting rel location using the upper left and lower right coords
    loc = rel_Location(uLeft, lRight)
    

    """For symmetry, I cropped the image so only the building remained.
    Then, I flipped the image both horizontally and vertically, and compared
    with the original building to see where it overlapped. """

    # getting dimensions to crop
    x1 = int(center[0] - w/2)
    x2 = int(center[0] + w/2)
    y1 = int(center[1] - h/2)
    y2 = int(center[1] + h/2)
    
    # copying the image

    temp = image.copy()
    # cropping the image
    temp = temp[y1 : y2, x1 : x2]
    # copying and rotating 180
    temp2 = temp.copy()
    temp2 = Image.fromarray(temp2)
    temp2 = temp2.rotate(180)
    temp2 = np.array(temp2)
    
    # copying and rotating 90
    temp3 = temp.copy()
    temp3 = Image.fromarray(temp3)
    temp3 = temp3.rotate(90)
    temp3 = np.array(temp3)
    

    temp = np.array(temp)
    j = 0
    count_h = 0
    count_v = 0
    
    # running loop and counting differences
    while j < len(temp):
        
        i = 0
        while i < len(temp[0]):
            
            # since image is binary, first value of pixel array is same as all
            if temp[j][i][0] != temp2[j][i][0]:
                count_h += 1
            
            if temp[j][i][0] != temp3[j][i][0]:
                count_v += 1
            
            i += 1

        j += 1
    size1 = temp.shape
    
    # dividing the count by the dimensions of the image
    # if the image is symmetrical either horizontally or vertically
    # the function returns symmetric

    if count_h/(29*274) < 0.15:
        sym = "symmetric"

        # returns upper left, lower right, symmetry,
        # orientation, and relative location
        return (uLeft, lRight, sym, orient, loc)
    if count_v/(29*274) < 0.15:
        sym = "symmetric"
        return (uLeft, lRight, sym, orient, loc)
    else:
        sym = "non-symmetric"
        return (uLeft, lRight, sym, orient, loc)
    
    

# a function that returns the relative location of the building
def rel_Location(u_l, l_r):
    
    """ I decided to define "on border" as x or y being above or below
    a certain value close to the edges of the image. """
    
    # returns a list because the building can be on 
    # more than one border
    dir = []
    
    if l_r[1] > 450:
        dir.append("on South Border") 
    elif u_l[1] < 10:
        dir.append("on North Border") 
    else:
        dir.append("not Northmost or Southmost") 
    if u_l[0] < 10:
        dir.append("on West Border") 
    elif l_r[0] > 250:
        dir.append("on East Border") 
    else:
        #print("x", x, "y", y)
        dir.append("not Eastmost or Westmost") 
    return dir
    


def det_shape(c, sym, orientation):
    
    # getting a polygon approximation
    p = cv2.arcLength(c, True)

    # a factor of 0.026 deviation outside the curve worked best for me
    poly = cv2.approxPolyDP(c, 0.026 * p, True)

    # getting the bounding rectangle
    x, y, w, h = cv2.boundingRect(c)
    ratio = w/h
    
    # the number of vertices
    v = len(poly)

    # a symmetric shape with less than 6 vertices is likely a quadrilateral
    if v  < 6 and sym == "symmetric":
        if ratio >= 0.80 and ratio <= 1.20:
            shape = "square"  
        else: 
            shape = "rectangle"

    # for non-symmetric shapes
    elif sym != "symmetric":
        
        if v > 6 and v < 9: 
            shape = "C-shaped"
        elif v <= 6:
            shape = "L-shaped"
        else:
            shape = "complicated Shape"
    
    elif sym == "symmetric" and orientation != "No Single Orientation":
        if v == 7:
            shape = "rectangularish" 
        elif v > 4 and v <= 8:
            shape = "I-shaped"
        else:
            shape = "complicated Shape"
    else:
        shape = "complicated Shape"

    return shape



if __name__ == "__main__":
    main()

