"""
Main Class to Extract Files and Find Nearest Neighbors
@authors: danielle nash, ryan reede, drew hoo
12/10/16
"""

from image_final import Image
import numpy as np
import sys, os
import time
from lshash import LSHash

def getFeatures(imgpath):
    main = Image(np.loadtxt(imgpath), imgpath)
    main.denoise() #Denoises the Image
    main.findMajorAxis() #Rotates around the Major Axis
    main.getPCA()
    main.search()  # Bounding Box
    main.getSymmetry() #Gets both Horizontal and Vertical Symmetries
    main.setCounts() #Sets the Foreground, and Background Pixel Counts (and ratio)
    main.getCorners() #Gets the Corners
    main.getCircledPixels() #Gets the Circled Pixels
    f = main.makeFeatureVector()  #Returns the feature vector
    return f


if __name__ == '__main__':
    """"
    cmd line args:
        0: unused (name of .py file)
        1: path to database of images
        2: path to query images
        3: path to output file
        4: k
    """
    t0 = time.clock()
    cmdline_args = sys.argv
    db = cmdline_args[1]
    query = cmdline_args[2]
    output_path = cmdline_args[3]
    k = cmdline_args[4]
    
    out_File = open(output_path+"/this_is_the_output", "w")
    imgPaths_qu = []
    imgPath_db = []
    query_vectors = []
    db_vectors = []
    output_string = ""

    f = []
        
    lsh = LSHash(6,11)

    # database calculations...
    for img in os.listdir(db):
        imgpath = db + '/' + str(img)
        
        #Error Checking-- If there are .DS_Store files in Directory
        if str(img).startswith("."):
            continue
        
        f = getFeatures(imgpath) #Gets the feature vector for this image
        lsh.index(f)    #Adds vector to the hash
        
        #Image names and the vectors are saved for lookup later
        imgPath_db.append(img)
        db_vectors.append(f)

    q_feat = []
    
    for img in os.listdir(query):
        imgpath = query + '/' + str(img)    #Full Path of Query Images
        
        if str(img).startswith("."):
            continue

        q = getFeatures(imgpath)        #Feature vector for Query Image
        answer = lsh.query(q, int(k))   #Gets K Nearest Neighbors using Hash

        out_File.write(img)     #Writes closest image names to file
    
        if len(answer) == 0:
            for i in range(int(k)):
                out_File.write(" "+str(img))
        else:
            outTotal = 0
            pos2 = []
            for i in range(int(k)):
                if i >= len(answer):    #Break if there are less than k images
                    break
                pos = db_vectors.index(list(answer[i][0]))
                pos2.append(answer[i][0])
                out_File.write(" "+str(imgPath_db[pos]))
                outTotal +=1
            if outTotal != int(k):    
                posCount = 0
                need = int(k) - outTotal
                while need > 0 and posCount < len(pos2):
                    answer2 = lsh.query(pos2[posCount], need)
                    for i in range(len(answer2)):
                        p = db_vectors.index(list(answer2[i][0]))
                        out_File.write(" "+str(imgPath_db[p]))
                    
                    posCount +=1
                    need = need - len(answer2)
                
                while need > 0:
                    out_File.write(" "+str(img))
                    need -=1
        out_File.write("\n")    
        
    

    out_File.close()    #closes Out File
    print time.clock() - t0
