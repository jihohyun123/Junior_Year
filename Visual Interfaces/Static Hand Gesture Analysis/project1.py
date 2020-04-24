from PIL import Image
from numpy import *
import numpy as np
from scipy import ndimage
import sys
import imageio
import cv2
from matplotlib import pyplot as plt


# a method to binarize a given image file. I had to use different thresholds
# depending on whether I was working with images from 1.1-1.3 or 1.4
def color_process(name, setting):
    if setting == 0:    
        # to process the image, I used OpenCv extensively:

        image = cv2.imread(name)

        # first converting to grayscale: 
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # then creating a thresholded image:
        # I had to mess around before I found a decent threshold for my 
        # set of photos, around 130 seemed like a good number

        ret,thresh = cv2.threshold(gray,130,255,cv2.THRESH_BINARY_INV)

        #plt.imshow(thresh, cmap="gray")
        #plt.show()
        
        # I did some morphological operations to reduce noise in the image to make
        # finding the contours easier:

        # created a 50x50 kernel
        kernel = np.ones((50,50),np.uint8)

        # closing and opening to erase black and white spots
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # doing a bitwise not to get a white on black image
        thresh = cv2.bitwise_not(thresh)
        
        # blurring to make the contours smoother
        thresh = cv2.blur(thresh, (5,5))

        # showing the image for debugging purposes, commented out
        # plt.imshow(thresh, cmap="gray")
        # plt.show()

        # returning the modified image array to be used by other methods
        return thresh
    elif setting == 1:    
        
        # for the creativity step, I used an image processing method
        # almost identical to the one above, 
        # with a few tweaks in the parameters.

        image = cv2.imread(name)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        ret,thresh = cv2.threshold(gray,110,255,cv2.THRESH_BINARY_INV)

        kernel = np.ones((50,50),np.uint8)

        # closing and opening to erase black and white spots
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        #plt.imshow(thresh, cmap = 'gray')
        #plt.show()
        
        # blurring to make the contours smoother
        thresh = cv2.blur(thresh, (10,10))

        return thresh

# a method to find the convexity defects of a processed image
def find_defects(img):
    
    # in order to classify the images, I first needed to
    # find the contours from the thresholded image

    contours,_ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    # finding the hull of the shape
    hull = cv2.convexHull(contours[0])

    # using convexityDefects to find fluctuations outside the hull
    cnt = contours[0]
    hull = cv2.convexHull(cnt,returnPoints = False)
    defects = cv2.convexityDefects(cnt,hull)
    
    # counting the number of defects
    count = 0
    
    for i in range(defects.shape[0]):
        count += 1

    # returning the number of defects
    return count

# a method to classify the gesture in the image
# changes based on the setting: default (1.1-1.3) or creative (1.4)
def classify(setting, edges):

    # I used the number of convexity defects to classify the type of object. 
    # I assumed that a closed fist would have fewer defects than a splayed palm.

    # print("edges: ", edges)
    if setting == 0:
        
        if edges >= 0 and edges < 15:
            obj_type = 'fist'
        
        else:
            obj_type = 'splay'

        return obj_type

    # for the jutsu hand symbols, I had a different system of categorizing
    # still based on the number of defects.

    elif setting == 1:
        
        if edges > 10:
            obj_type = 'tiger'
        
        elif edges <= 5:
            obj_type = 'horse'
        elif 5 < edges < 8:
            obj_type = 'serpent'
        elif 8 <= edges < 10:
            obj_type = 'dog'
        else:
            obj_type = 'unknown'
        return obj_type

# a method that finds the center of mass of the image after thresholding
def position(img):
    
    # To find the location of the center of mass, I used
    # numpy's ndimage module that comes with a center of mass function.

    img = np.array(img)
    pos = ndimage.measurements.center_of_mass(img)
    print("position: ", pos)
    x = pos[1]
    y = pos[0]

    # I defined an object in the center as follows:

    if 1000 < x < 2000 and 1250 < y < 2750:
        return 'center'
    else:
        return 'corner'


# method that returns a list of filenames based on the desired setting and sequence of images
def logistics(setting):
    
    if setting == 0:
        # listing out all the possible sequences:
        print("seq1: fist center, splay right upper corner → correct true")
        print("seq2: fist center, splay left upper corner → correct true")
        print("seq3: fist center, splay right lower corner → correct true")
        print("seq4: fist center, splay left lower corner → correct true")
        print("seq5: fist corner, splay corner → incorrect true")
        print("seq6: splay corner, fist center → incorrect true")
        print("seq7: splay center, splay corner → incorrect true")
        print("seq8: splay center, fist corner → incorrect true")
        print("seq9: fist center, 'C' corner → correct false")
        print("seq10: ‘C’ center, splay corner → correct false (my program fills in gaps so an ‘o’ shape would be tagged as a fist)")
        print("seq11: ‘wider’ fist center, splay corner → incorrect false")
        print("seq12: fist center, smaller splay corner → incorrect false (program finds less concavity when part of hand is cut off)")
        
        # getting the list of filenames
        choice = input("please select a sequence: ")
        if choice == 'seq1':
            files = 'fist.jpg splay.jpg' # works
        elif choice == 'seq2':
            files = 'fist.jpg splay_upper_left.jpg' # works
        elif choice == 'seq3':
            files = 'fist.jpg splay_lower_right.jpg' # works
        elif choice == 'seq4':
            files = 'fist.jpg splay_lower_left.jpg' # works
        elif choice == 'seq5':
            files = 'fist_upper_right.jpg splay_lower_left' # works
        elif choice == 'seq6':
            files = 'splay_upper_left.jpg fist.jpg' # works
        elif choice == 'seq7':
            files = 'splay_center.jpg splay.jpg' # works
        elif choice == 'seq8':
            files = 'splay_center.jpg fist_upper_right.jpg' # works
        elif choice == 'seq9':
            files = 'fist.jpg C_upper_left.jpg' # works
        elif choice == 'seq10':
            files = 'C_center.jpg splay.jpg' # works
        elif choice == 'seq11':
            files = 'loose_fist_center.jpg splay.jpg' # works
        elif choice == 'seq12':
            files = 'fist.jpg splay_false_left' # works
        else: 
            print("invalid choice")
            files = None

        #files = input("enter setting, filenames: ")
        name_list = files.split()
            
        return name_list
    elif setting == 1:
        # similar series as above, written to give user information about the combinations
        # numbers behind images indicate the same symbol but in a different photo
        print("seq1: serpent tiger dog horse → correct true")
        print("seq2: serpent serpent serpent tiger dog horse → correct true")
        print("seq3: serpent tiger dog horse2 → correct true")
        print("seq4: serpent tiger dog2 horse → correct true")
        print("seq5: serpent dog2 tiger horse → incorrect true")
        print("seq6: horse2 horse2 serpent tiger dog → incorrect true")
        print("seq7: horse2 dog → incorrect true")
        print("seq8: dog2 → incorrect true")
        print("seq9: serpent tiger dog fist → correct false (my program processes a fist as a horse instead of as unknown)")
        print("seq10: serpent splay dog horse → correct false (my program processes a splay as a tiger instead of as unknown)")
        print("seq11: serpent tiger3 dog horse → incorrect false (program reads a tiger as an unknown)")
        print("seq12: serpent2 tiger dog horse → incorrect false (program reads a serpent as a horse)")

        choice = input("please select a sequence: ")
        if choice == 'seq1':
            files = 'serpent.jpg tiger.jpg dog.jpg horse.jpg' # works
        elif choice == 'seq2':
            files = 'serpent.jpg serpent.jpg serpent.jpg tiger.jpg dog.jpg horse.jpg' # works
        elif choice == 'seq3':
            files = 'serpent.jpg tiger.jpg dog.jpg horse2.jpg' # works
        elif choice == 'seq4':
            files = 'serpent.jpg tiger.jpg dog2.jpg horse.jpg' # works
        elif choice == 'seq5':
            files = 'serpent.jpg dog.jpg tiger.jpg horse.jpg' # works
        elif choice == 'seq6':
            files = 'horse2.jpg horse2.jpg serpent.jpg tiger.jpg dog.jpg' # works
        elif choice == 'seq7':
            files = 'horse2.jpg dog.jpg' # works
        elif choice == 'seq8':
            files = 'dog2.jpg' # works
        elif choice == 'seq9':
            files = 'serpent.jpg tiger.jpg dog.jpg fist.jpg' # works
        elif choice == 'seq10':
            files = 'serpent.jpg splay.jpg dog.jpg horse.jpg' # works
        elif choice == 'seq11':
            files = 'serpent.jpg tiger3.jpg dog.jpg horse.jpg' # works
        elif choice == 'seq12':
            files = 'serpent2.jpg tiger.jpg dog.jpg horse.jpg' # works
        else: 
            print("invalid choice")
            files = None

        
        name_list = files.split()   
        return name_list
    
    else:
        return None

# my main method: runs the actual program
def main():
    
    #have to load in image sequence from command line
    #two possible combinations: input 0, two image sequence, input 1: naruto style sequence
    
    # setting of 1 indicates (fist, center), (splay corner) as key
    # setting of 2 indicates naruto-style sequences
    
    setting = int(input("please enter a setting: 0 or 1: "))
    
    if setting == 0: 
        filenames = logistics(setting)
        print(setting, filenames)    
        # I implemented my basic lock so that if the number of inputs wasn't exactly 2, 
        # it would refuse to open.

        if len(filenames) != 2:
            print("Incorrect sequence! Locked")
            return

        # The key as a list of tuples:
        key = [('fist', 'center'), ('splay', 'corner')]
        i = 0
        
        # for each file, the image is processed and returns 
        # various information about the type of gesture as well
        # as the position of the hand in the image

        for filen in filenames:
            
            # getting the binarized file
            im = color_process(filen, 0)
            
            # counting the number of convexity defects
            count = find_defects(im)

            # classifying the image
            obj_type = classify(setting, count)
            
            # getting the location of center of mass
            pos = position(im)

            # obtaining result as a tuple
            result = (obj_type, pos)
            print("result: ", result )

            # comparing the results against the key
            if result != key[i]:
                print("Incorrect sequence! Locked")
                return
            i += 1
            
        print("Correct sequence! Unlocked")
        return
    else:
        filenames = logistics(setting)
        
        key = ['serpent', 'tiger', 
               'dog', 'horse']
        i = 0
        seq = 0
        for filen in filenames:
            
            # different loop this time: as long as the correct sequence 
            # is entered at any point, the lock unlocks.
            
            # processing the image under the 1 setting
            im = color_process(filen, 1)
            count = find_defects(im)
            obj_type = classify(1, count)
            result = obj_type
            
            print("key: ", key[i%4])
            print("result: ",result)

            # incrementing the counter if a correct image is found
            if result == key[i%4]:
                seq += 1
                i += 1
            
            # resetting on incorrect output
            else:
                seq = 0
                i = 0
            
            # if a sequence of images matches the key
            if seq == 3:
                print("Correct sequence! Unlocked")
                return

        print("Incorrect sequence! Locked")
        
            
        
        
if __name__ == "__main__":
    main()

    