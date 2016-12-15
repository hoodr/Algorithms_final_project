"""
Image object class for an image w/ methods
@authors: danielle nash, ryan reede, drew hoo
12/08/16
"""
import numpy as np
from scipy import ndimage
import random
import pdb
import math

class Image(object):
    def __init__(self, data, name): # data is an np.array
        self.name = name
        self.data = data # original data matrix
        self.width = len(data[0])
        self.height = len(data)
        self.bounded = None  # matrix after bounding box complete
        self.rotated = None
        self.inverted = None  # set from denoise function
        self.foregroundPixels = None # foreground is the MAIN color of the image's central data
        self.backgroundPixels = None
        self.horizSym = None
        self.vertSym = None
        self.corners = None
        # self.isPolygon = self.getType()  # TODO set from corners method

    def makeFeatureVector(self):
        # make feature vector for KNN
        return (self.corners, self.horizSym, self.vertSym, (1.0 * self.foregroundPixels) / (self.foregroundPixels + self.backgroundPixels))

    def createLines(self):
        """
            Creates 3 lines for 20 random pixels on the edges to see which is the best fit line
        """
        X, Y = self.height, self.width
        thisSum = 0
        endCoord = (0,0)
        sum = 0
    
        for i in range(10):
            top = random.randint(3, Y)
            right = random.randint(3, X)
            
            for i in range(0, 3):
                thisSum, endCoord= self.calcDiagonal(0, top, 1, 1 - i)
                if thisSum > sum:
                    sum = thisSum
                    coord = [(0, top), endCoord]
            for j in range(0, 3):
                thisSum, endCoord= self.calcDiagonal(right, 0, 1 - j, 1)
                if thisSum > sum:
                    sum = thisSum
                    coord = [(right, 0), endCoord]
        
        self.degrees(coord)
        #print sum, coord


    def findMajorAxis(self):
        """
        Finds major axis then rotates the image
        """
        self.createLines()
        

    def calcDiagonal(self, startX, startY, xStep, yStep):

        """
            Calculates how many pixels are actually in the shape down this particular line
        """
   
        X, Y = self.height, self.width

        x, y = startX, startY
        
        pixel = 0
        if self.inverted == True:
            pixel = 1
    
        thisSum = 0
    
        while  -1 < x < X and -1 < y < Y:
            if pixel == self.data[x][y]:
                thisSum += 1
            
            x +=xStep
            y +=yStep
        
        return thisSum, (x-1, y-1)
        
    
    def degrees(self, coord):
        """
            Figures out the degrees between the major axis and the y axis to rotate
        """
        degs = 0
        
        if coord[1][0] - coord[0][0] ==0:
            degs = 90
        else:
            m = (-1.0) * (coord[1][1] - coord[0][1]) / (coord[1][0] - coord[0][0])
            degs = math.degrees(math.atan(m))
        
        self.rotate(degs)            

    def rotate(self, degrees):
        """
            Rotates the shape degrees and saves as new shape
        """
        newData = ndimage.interpolation.rotate(self.data, degrees, axes= (0, 1), reshape = True, order = 0)
        #Don't save this actually 
        self.rotated = newData
        self.data = newData
        self.width = len(newData[0])
        self.height = len(newData)

    def getSymmetry(self):
        """
           Finds the horizontal and vertical symmetries
        """
        hSymmetry = self.xSym()
        vSymmetry = self.ySym()
        
        self.horizSym = hSymmetry
        self.vertSym =vSymmetry 

    def xSym(self):

        data = self.bounded
        # h = self.height
        h = len(data)
        # w = self.width
        w = len(data[0])

        compare = 0
        if h%2 == 1:
            row = h/2
            for r in range(1, h/2):
                for i in range(w):
                    if data[row + r][i] == data[row -r][i]:
                        compare +=1
        else:
            r1 = h/2
            r2 = r1 - 1
            for row in range(0, h/2):
                for i in range(w):
                    # pdb.set_trace()
                    if data[r1 + row][i] == data[r2 - row][i]:
                        compare +=1
        return (2.0* compare) / (h*w)


    def ySym(self):
        data = self.bounded
        # h = self.height
        h = len(data)
        # w = self.width
        w = len(data[0])
        compare = 0
        if w % 2 == 1:
            col = w/2
            for R in range(h):
                for c in range(1, w/2):
                    if data[R][col + c] == data[R][col -c]:
                        compare +=1
        else:
            c1 = w/2
            c2 = c1 - 1
            for m in range(h):
                for c in range(0, w/2):
                    if data[m][c1 + c] == data[m][c2 -c]:
                        compare +=1
        return (2.0* compare) / (h*w)


    def combineList(self, lst):
        if len(lst) < 2:
            return lst
        comp = lst.pop()
        last = lst.pop()
        going = 1
        while going >= 1:
            if abs(comp[0] - last[0]) < 4 or abs(comp[1] - last[1]) < 4:
                if comp[2] > last[2]:
                    if len(lst) > 1:
                        last = lst.pop()
                    else:
                        lst.append(comp)
                        going = 0
                else:
                    if len(lst) > 1:
                        comp = last
                        last = lst.pop()
                    else:
                        lst.append(last)
                        going = 0
            else:
                lst.append(last)
                lst.append(comp)
                going = 0
        return lst


    def getCorners(self):
    	self.findCorners(self.data, 4, 0.05, 1)
    
    def findCorners(self, arry, window_size, k, thresh):
        height = len(arry)
        width = len(arry[0])

        dy, dx = np.gradient(arry)
        Ixx = dx ** 2
        Ixy = dy * dx
        Iyy = dy ** 2

        cornerList = []

        offset = window_size / 2
        count = 0
        last = []
        count1 = 0
        going = 1

        newCount = 0
        goingCount = 0

        for y in range(offset, height - offset):
            for x in range(offset, width - offset):

                windowIxx = Ixx[y - offset:y + offset + 1, x - offset:x + offset + 1]
                windowIxy = Ixy[y - offset:y + offset + 1, x - offset:x + offset + 1]
                windowIyy = Iyy[y - offset:y + offset + 1, x - offset:x + offset + 1]
                Sxx = windowIxx.sum()
                Sxy = windowIxy.sum()
                Syy = windowIyy.sum()

                # Find determinant and trace, use to get corner response
                det = (Sxx * Syy) - (Sxy ** 2)
                trace = Sxx + Syy
                r = det - k * (trace ** 2)

                # If corner response is over threshold, color the point and add to corner list
                if r > thresh:
                    # print x, y, r
                    cornerList.append([y, x, r])
                    cornerList = self.combineList(cornerList)
                    newCount += 1
        self.corners = len(cornerList)




    def writeOut(self, path, filename, version='full'):
        """"
        output the file to a .txt, given and path and filename
        version can either be 'full' or 'bounded'
        """
        file = open(path + '/' + filename + '.txt', "w")
        data = self.data if version == 'full' else self.bounded
        for row in data:
            file.write("\n")
            for item in row:
                file.write(str(int(item)) + " ")
        file.close()


    def countNaive(self, data):
        """"
        Iterate through all pixels, get counts for 1s and 0s
        """
        width, height = len(data[0]), len(data)
        ones = 0
        zeros = 0
        for w in range(width):
            for h in range(height):
                if data[h][w] == 1:
                    ones += 1
                else:
                    zeros += 1
        return ones, zeros


    def setCounts(self):
        # if inverted = False, background is 0
        d = self.bounded if self.bounded is not None else self.data
        ones, zeros = self.countNaive(d)
        if self.inverted:
            self.backgroundPixels, self.foregroundPixels = ones, zeros
        else:
            self.backgroundPixels, self.foregroundPixels = zeros, ones


    def encodeValues(self, vals):
        """"
        Determine if the values given as input are all ONE,
        ZERO or MIX. Encoded as follows:
            00 = all ZERO, 01 = MIX and 11 = all ONE
        """
        if vals.count(vals[0]) == len(vals):
            if vals[0] == 0:
                return '00'
            return '11'
        return '01'

    def checkWindow(self, posY, posX):
        # TODO: Parameterize this function for variable window sizes (not just 4)
        """"
        Checks 4x4 matrix from around specified X and Y coords
            that wraps around any edge of the given image's
            data matrix for noise removal. Will check
        Returns:
            - 4x4 matrix from around specified X and Y coords
                that wraps around any edge of the given image's
                data matrix for noise removal.
            - list of x/y indices that are in the middle of the
                4x4 matrix
            - 2-bit encoding where 00 = all ZERO, 01 = MIX and
                11 = all ONE. These values refer to what is on
                the outside edges of the 4x4 matrix
        """
        data = self.data
        height = self.height
        width = self.width
        outsideValues, insideIndices, final = [], [], []
        for c in range(4):
            posX_new = (posX + c) % height
            c_list = []
            for r in range(4):
                posY_new = (posY + r) % width
                c_list.append(data[posX_new][posY_new])
                if r == 1 or r == 2: # check to make sure we're in the middle
                    if c == 1 or c == 2:
                        insideIndices.append([posY_new, posX_new])
            final.append(c_list)
            if c == 0 or c == 3:
                outsideValues.extend(c_list)
            else:
                outsideValues.extend([c_list[0], c_list[3]])
        return final, insideIndices, self.encodeValues(outsideValues)

    def changeValues(self, indices, number):
        """"
        reassign all values to 'number' in 'indices'
        """
        for xyPair in indices:
            self.data[xyPair[1]][xyPair[0]] = number

    def denoise(self):
        # TODO: Parameterize this function for variable window sizes (not just 4)
        """
        1) Iterate though each pixel of the image, create a 4x4
        window with this pixel at the top left corner, and
        remove chunks of disconnected noise
        2) Check for majority of pixel changes to determine if image is
        white over black or black over white

        """
        # make 4x4 chunks, if center is dif from surrounding, make it the same as surrounding.
        # check inversion (bug prone)
        countOne, countZero = 0, 0
        for w in range(0, self.width):
            for h in range(0, self.height):
                final, insides, code = self.checkWindow(w, h)
                if code != '01':
                    if code == '00':
                        countZero += 1
                        self.changeValues(insides, 0)
                    else:
                        countOne += 1
                        self.changeValues(insides, 1)
        self.inverted = False if countZero >= countOne else True


    # Initiate the search
    def search(self, padding=2):
        """"
        add description
        """
        invert = self.inverted
        rows, cols = np.shape(self.data)
        left_col, top_row = self.start_top(rows, cols, invert)
        right_col, bot_row = self.start_bot(rows, cols, invert)

        # RESHAPE with the new dims
        r1 = top_row - padding if top_row - padding > 0 else top_row
        r2 = bot_row + padding if bot_row - padding > 0 else bot_row
        c1 = left_col - padding if left_col - padding > 0 else left_col
        c2 = right_col + padding if right_col + padding > 0 else right_col

        row_idx = np.array([x for x in range(r1, r2)])
        col_idx = np.array([x for x in range(c1, c2)])

        # MAKE SURE WERE NOT ON THE EDGES OR OVER THE INDEXING
        if col_idx[-1] == cols:
            col_idx = np.delete(col_idx, -1)

        if row_idx[-1] == rows:
            row_idx = np.delete(row_idx, -1)

        # pdb.set_trace()
        # new_image = image[row_idx[:, None], col_idx]
        # print new_image
        # pdb.set_trace()
        # return new_image
        # pdb.set_trace()
        self.bounded = self.data[row_idx[:, None], col_idx]
        # temp = "output/out_" + self.name[-8:]
        #np.savetxt(temp, self.bounded, fmt='%d')
        self.data = self.bounded
        self.height = len(self.data)
        self.width  = len(self.data[0])
        """
        row_idx = np.array([0, 1, 3])
        col_idx = np.array([0, 2])
        a[row_idx[:, None], col_idx]
        """

    # Top always starts at 0,0
    def start_top(self, rows, cols, invert=False):
        """"
        add description
        """
        left_col = []
        top_row = []
        flag = False
        i = 0
        j = 0
        x, y = False, False
        while not flag:
            while i < rows and j < cols:
                x, y = self.search_row(i, invert), self.search_col(j, invert)
                if x:
                    top_row.append(i)
                if y:
                    left_col.append(j)
                if x == True and y == True:
                    flag = True
                i += 1
                j += 1
            flag = True
        # Assumes we found something
        return left_col[0], top_row[0]

    # Bot always starts at shape - 1
    def start_bot(self, rows, cols, invert=False):
        """"
        add description
        """
        right_col = []
        bot_row = []
        i = rows - 1
        j = cols - 1
        flag = False
        x, y = False, False
        while (not flag):
            while i > 0 and j > 0:
                x, y = self.search_row(i, invert), self.search_col(j, invert)
                if x:
                    bot_row.append(i)
                if y:
                    right_col.append(j)
                if x and y:
                    flag = True
                i -= 1
                j -= 1
            flag = True
        # Assumes we found something
        return right_col[0], bot_row[0]

    def search_row(self, i, invert):
        """"
        add description
        """
        fg = 1
        if invert:
            fg = 0
        row = self.data[i, :]
        # SEARCHES SOLELY FOR 1 ans the "other"
        found = np.argwhere(row == fg)
        # print 'found: ', found
        # Threshold of "found" is just one pixel, can be adjusted
        if len(set(found.flatten())) >= 1:
            return True
        else:
            return False
            # for x in row:
            #     # TEMP => ADJUST FOR LATER
            #     if x == 1:
            #         return
            # return

    def search_col(self, j, invert):
        """"
        add description
        """
        fg = 1
        if invert:
            fg = 0
        col = self.data[:, j]
        # SEARCHES SOLELY FOR 1 ans the "other"
        found = np.argwhere(col == fg)
        # print 'found: ', found
        # Threshold of "found" is just one pixel, can be adjusted
        if len(set(found.flatten())) >= 1:
            return True
        else:
            return False