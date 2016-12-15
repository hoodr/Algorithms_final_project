import numpy as np

class circler():
    def __init__(self, data):
        self.bounded = data


    def checkHoriz(self, h, w):
        pixel = self.bounded[h][w]
        row = self.bounded[h]
        pos = w
        pre = row[:pos]
        post = row[pos:]
        check = 1 - pixel
        if check in pre and check in post:
            return True
        return False


    def checkVert(self, h, w, height):
        pixel = self.bounded[h][w]
        col = [self.bounded[i][w] for i in range(height)]
        pos = h
        pre = col[:pos]
        post = col[pos:]
        check = 1 - pixel
        if check in pre and check in post:
            return True
        return False


    def hasCircle(self):
        count = 0
        height = len(self.bounded)
        width = len(self.bounded[0])
        for row in range(height):
            for col in range(width):
                pixel = self.bounded[row][col]
                if self.checkHoriz(row, col):
                    if self.checkVert(row, col, height):
                        count += 1
                    else:
                        continue
                else:
                    continue
        if count > 12:
            return True
        return False

data = np.asarray(
    [[0,0,1,1,1,1,0,0],
     [0,0,0,0,0,1,0,0],
     [1,0,0,0,0,1,0,0],
     [0,0,1,0,0,0,0,0],
     [0,0,1,1,1,1,0,0]])

path = '/Users/Reede/Desktop/107862113'

test = circler(np.loadtxt(path))
print(test.hasCircle())