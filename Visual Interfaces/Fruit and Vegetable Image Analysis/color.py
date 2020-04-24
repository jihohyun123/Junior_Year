from PIL import Image
import numpy as np
from scipy import ndimage
import sys
import imageio
import heapq
import matplotlib.pyplot as plt
import cv2
from utilities import *


def main():

    # running all the comparisons:
    result = ranking('color')
    print("my result for color is: ", result)
    
if __name__ == "__main__":
    main()

    