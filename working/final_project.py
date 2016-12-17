from image import Image
import numpy as np
import sys, os
import time
from lshash import LSHash

def getFeatures(imgpath):
    # print ('\n' + imgpath)
    #print "Getting Feature \n"
    main = Image(np.loadtxt(imgpath), imgpath)
    main.denoise()
    #main.findMajorAxis()
    main.deskew()
    main.getPCA() #what is this?
    main.search()  # bounding box
    #main.createLines()
    main.setCounts()
    main.getSymmetry()
    main.getCorners()
    #main.getCorners()
    main.getCircledPixels() #what is this
    f = main.makeFeatureVector()
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
    #print db
    query = cmdline_args[2]
    #print query
    output_path = cmdline_args[3]
    #print output_path
    k = cmdline_args[4]
    #print k
    
    out_File = open(output_path+"/this_is_the_output", "w")
    imgPaths_qu = []
    imgPath_db = []
    query_vectors = []
    db_vectors = []
    output_string = ""

    database_map = {}
    f = []
        
    lsh = LSHash(6, 9)

    # database calculations...
    for img in os.listdir(db):
        imgpath = db + '/' + str(img)
        #print imgpath
        if str(img).startswith("."):
            continue
        f = getFeatures(imgpath)
        #print f
        #database_map[f] = imgpath
        lsh.index(f)
        imgPath_db.append(img)
        db_vectors.append(f)
        # print len(f)

    q_feat = []
    query_map = {}
    for img in os.listdir(query):
        imgpath = query + '/' + str(img)
        #print imgpath
        # imgpath = "/Users/daniellenash/Downloads/database/642073386"
        #print imgpath
        if str(img).startswith("."):
            continue

        q = getFeatures(imgpath)
        #print q
        #query_map[q] = imgpath
        answer = lsh.query(q, int(k))

        out_File.write(img)

        #a = answer[0][0]
    
        for i in range(int(k)):
            if i >= len(answer):
                break
            pos = db_vectors.index(list(answer[i][0]))
            out_File.write(" "+str(imgPath_db[pos]))
            #output_string+=" "+ imgPath_db[pos]
            #print pos
            #print imgPath_db[pos]

        #output_string += "\n"
        out_File.write("\n")
    

    out_File.close()
    #out_File.write(output_string)


    # cluster DB images once, find nearest neighbor foreach in query..
    #print time.clock() - t0