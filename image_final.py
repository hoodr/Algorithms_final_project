"""
Image object class for an image w/ methods
@authors: danielle nash, ryan reede, drew hoo
12/08/16
"""
import numpy as np
import random
import math
import fast12
from scipy import ndimage
from scipy import linalg

class Image(object):
    def __init__(self, data, name): # data is an np.array
        self.name = name
        self.data = data # Data Matrix - Gets updated after rotation, and bounding box
        self.width = len(data[0])
        self.height = len(data)
        self.inverted = None  # set from denoise function
        self.foregroundPixels = None # foreground is the MAIN color of the image's central data
        self.backgroundPixels = None
        self.ratioPixels = None     #Foreground / Background Pixel Ratio
        self.horizSym = None
        self.vertSym = None
        self.numCorners = None
        self.pca1 = 0
        self.pca2 = 0
        self.circles = None
        self.centroid = None
        self.topHalf = 0
        self.rightHalf =0
        
    def makeFeatureVector(self):
       return [(1.0 * self.numCorners)/ self.foregroundPixels,  self.ratioPixels , self.horizSym, self.vertSym, (1.0 * self.circles) / (self.foregroundPixels + self.backgroundPixels),
                self.pca1/10.0, self.pca2/10.0, (1.0 * self.centroid[0]) / self.width, (1.0 * self.centroid[1]) / self.height, (1.0 * self.topHalf)/ (self.foregroundPixels), (1.0 * self.rightHalf) / (self.foregroundPixels)]
        
    
    def getPCA(self):
        """
            Method to get the Eigenvalues of the image
        """
        if len(self.data) == len(self.data[0]):
            eVal, eVec = linalg.eig(self.data)
            idx = eVal.argsort()[::-1]
            eVal = eVal[idx]
            self.pca1 = eVal[0].real
            self.pca2 = eVal[1].real
        return

    def checkHoriz(self, h, w):
        """
            Method to check if the horizontal pixels were a part of the circle
        """
        pixel = self.data[h][w]
        row = self.data[h]
        pos = w
        pre = row[:pos]
        post = row[pos:]
        check = 1 - pixel
        if check in pre and check in post:
            return True
        return False


    def checkVert(self, h, w, height):
        """
            Method to check if the vertical pixels were a part of the circle
        """
        pixel = self.data[h][w]
        col = [self.data[i][w] for i in range(height)]
        pos = h
        pre = col[:pos]
        post = col[pos:]
        check = 1 - pixel
        if check in pre and check in post:
            return True
        return False


    def getCircledPixels(self):
        """
            Method to find the number of circled pixels
        """
        count = 0
        height = len(self.data)
        width = len(self.data[0])
        for row in range(height):
            for col in range(width):
                pixel = self.data[row][col]
                if self.checkHoriz(row, col):
                    if self.checkVert(row, col, height):
                        count += 1
                    else:
                        continue
                else:
                    continue
        self.circles = count 


    def createLines(self):
        """
            Creates 3 lines for 14 random pixels on the starting at either top or right of the image
                and moving either horizontally, vertically, or in a diagonal of slope 1
        """
        X, Y = self.height, self.width
        thisSum = 0
        endCoord = (0,0)
        sum = 0
        
        for k in range(7):
            top = random.randint(3, Y-1)
            right = random.randint(3, X-1)
            
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
        
        #print coord
        self.degrees(coord)

    
    def findMajorAxis(self):
        """
        Finds major axis then rotates the image
        """
        self.createLines()
  

    def calcDiagonal(self, startX, startY, xStep, yStep):

        """
            Calculates how many pixels are actually in the shape down this particular line
                xStep and yStep give the slope of the line
        """
        X, Y = self.height, self.width

        x, y = startX, startY
        
        pixel = 1
        if self.inverted == True:
            pixel = 0
    
        thisSum = 0
    
        while  -1 < x < X and -1 < y < Y:
            if pixel == int(self.data[x][y]):
                thisSum += 1
            
            x +=xStep
            y +=yStep
        
        return thisSum, (x-1, y-1)
        
    
    def degrees(self, coord):
        """
            Calculates the degrees between the found major line, and the y axis using the inverse tangent.
            Only rotates if the the degrees is either more than 5 and less than 85
        """
        degs = 0
        
        if coord[1][0] - coord[0][0] ==0:
            self.data = np.rot90(self.data)
        else:
            m = (-1.0) * (coord[1][1] - coord[0][1]) / (coord[1][0] - coord[0][0])
            degs = math.degrees(math.atan(m))
            if degs > 5.0 and degs < 85.0:
                self.rotate(degs)      

    
    def rotate(self, degrees):
        """
           Rotates the shape using scipy.interpolation.rotate a certain number of degrees
        """
        newData = ndimage.interpolation.rotate(self.data, degrees, axes= (0, 1), reshape = True, order = 0)
        self.data = newData
        self.width = len(newData[0])
        self.height = len(newData)

    def getSymmetry(self):
        """
           Finds the horizontal and vertical symmetries
        """
        hSymmetry = self.xSym()
        vSymmetry = self.ySym()
        
        self.horizSym = 1.0 * (hSymmetry/ (self.width * 0.5 * self.height))
        self.vertSym = 1.0 * (vSymmetry / (self.width * 0.5 * self.height))

    def xSym(self):
        """
            Horizontal Symmetry AND number of pixels in the shape AND topHalf Pixels
        """
        total = 0
        pixel = 1
        
        if self.inverted ==True:
            pixel = 0
        
        data = self.data
        h = self.height
        w = self.width
        #outs = ""
        topHalf = 0

        compare = 0
        if h%2 == 1:
            row = h/2
            for r in range(1, h/2):
                for i in range(w):
                    if data[row + r][i] == pixel or data[row - r][i] == pixel:
                        if data[row + r][i] == data[row -r][i]:
                            compare +=1
                            total +=2
                        else:
                            total+=1
                            if data[row + r][i] == pixel:
                                topHalf +=1
            for col in range(w):
                if data[row][col] == pixel:
                    total+=1
        else:
            r1 = h/2
            r2 = r1 - 1
            for row in range(0, h/2):
                for i in range(w):
                    if data[r2 - row][i]==pixel or data[r1 + row][i]==pixel:
                        if data[r1 + row][i] == data[r2 - row][i]:
                            compare +=1
                            total+=2
                        else:
                            total+=1
                            if data[r2 - row][i]== pixel:
                                topHalf +=1
        
        self.foregroundPixels = total
        self.topHalf = topHalf
        return compare


    def ySym(self):
        """
            Vertical Symmetry and Right Half Pixels
        """
        pixel = 1
        if self.inverted ==True:
            pixel = 0
        data = self.data
        h = self.height
        w = self.width
        compare = 0
        rightHalf = 0

        if w % 2 == 1:
            col = w/2
            for R in range(h):
                for c in range(1, w/2):
                    if data[R][col + c] == data[R][col -c] and data[R][col -c]==pixel:
                        compare +=1
                    if data[R][col + c] == pixel:
                        rightHalf +=1
        else:
            c1 = w/2
            c2 = c1 - 1
            for m in range(h):
                for c in range(0, w/2):
                    if data[m][c1 + c] == data[m][c2 -c] and data[m][c2 -c] == pixel:
                        compare +=1
                    if data[m][c1+c] == pixel:
                        rightHalf +=1
        self.rightHalf = rightHalf
        return compare


    def getCorners(self):
        """
            Uses Fast Corner Detection to detect the number of corners and the centroid
        """
        corners, scores = fast12.detect(self.data, 0.10)
        self.numCorners = len(corners)
        corners = np.asarray([list(x) for x in corners])
        length = corners.shape[0]
        if length > 0:
            sum_x = corners[:, 0]
            sum_y = corners[:, 1]
            self.centroid = (sum(sum_x)/length, sum(sum_y)/length)
            return
        else:
            self.centroid = (0, 0)
            return

#   The Following 2 Functions were used in Harris Corner Detection Implementation            
#     def findCorners(self, arry, window_size, k, thresh):
#         height = len(arry)
#         width = len(arry[0])
# 
#         dy, dx = np.gradient(arry)
#         Ixx = dx ** 2
#         Ixy = dy * dx
#         Iyy = dy ** 2
# 
#         cornerList = []
# 
#         offset = window_size / 2
#         count = 0
#         last = []
#         count1 = 0
#         going = 1
# 
#         newCount = 0
#         goingCount = 0
# 
#         for y in range(offset, height - offset):
#             for x in range(offset, width - offset):
# 
#                 windowIxx = Ixx[y - offset:y + offset + 1, x - offset:x + offset + 1]
#                 windowIxy = Ixy[y - offset:y + offset + 1, x - offset:x + offset + 1]
#                 windowIyy = Iyy[y - offset:y + offset + 1, x - offset:x + offset + 1]
#                 Sxx = windowIxx.sum()
#                 Sxy = windowIxy.sum()
#                 Syy = windowIyy.sum()
# 
#                 # Find determinant and trace, use to get corner response
#                 det = (Sxx * Syy) - (Sxy ** 2)
#                 trace = Sxx + Syy
#                 r = det - k * (trace ** 2)
# 
#                 # If corner response is over threshold, color the point and add to corner list
#                 if r > thresh:
#                     # print x, y, r
#                     cornerList.append([y, x, r])
#                     cornerList = self.combineList(cornerList)
#                     newCount += 1
#         self.corners = len(cornerList)
    """
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
    """

    def writeOut(self, path, filename, version='full'):
        """"
        output the file to a .txt, given and path and filename
        version can either be 'full' or 'bounded'
        """
        file = open(path + '/' + filename + '.txt', "w")
        #data = self.data if version == 'full' else self.bounded
        data = self.data
        for row in data:
            file.write("\n")
            for item in row:
                file.write(str(int(item)) + " ")
        file.close()
    
    def setCounts(self):
        """
            Sets the foreground and background Pixel counts, as well as the ratio
        """
        totalPixels = self.width * self.height
        self.backgroundPixels = totalPixels - self.foregroundPixels
        self.ratioPixels = (1.0 * self.foregroundPixels)/ (totalPixels)
    
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

        self.data = self.data[row_idx[:, None], col_idx]
        self.height = len(self.data)
        self.width  = len(self.data[0])

    # Top always starts at 0,0
    def start_top(self, rows, cols, invert=False):
        """"
        Starts at top looking diagonal looking for shape
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
        Starts at bottom looking diagonal looking for shape
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
            Searches the individual row
        """
        fg = 1
        if invert:
            fg = 0
        row = self.data[i, :]
        found = np.argwhere(row == fg)
        # Threshold of "found" is just one pixel, can be adjusted
        if len(set(found.flatten())) >= 1:
            return True
        else:
            return False

    def search_col(self, j, invert):
        """"
            Searches the individual column
        """
        fg = 1
        if invert:
            fg = 0
        col = self.data[:, j]
        found = np.argwhere(col == fg)
        # Threshold of "found" is just one pixel, can be adjusted
        if len(set(found.flatten())) >= 1:
            return True
        else:
            return False
