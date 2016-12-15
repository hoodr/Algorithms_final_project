import numpy as np
from image import Image

path = '/Users/Reede/Desktop/107862113'

test = Image(np.loadtxt(path), '107862113')
test.deskew()
file = open('new.txt', "w")
# data = self.data if version == 'full' else self.bounded
data = test.data
for row in data:
    file.write("\n")
    for item in row:
        file.write(str(int(item)) + " ")
file.close()


