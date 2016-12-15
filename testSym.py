from image import Image
import numpy as np

path = '/Users/daniellenash/Downloads/database/28454530'
name = '28454530'

img = Image(np.loadtxt(path), name)
img.denoise()
img.deskew()
img.search()
img.setCounts()
img.getSymmetry()
img.getCircledPixels()

print "name ", name
print "foreground px ", img.foregroundPixels
print "ratio px ", img.ratioPixels
print "horiz sym ", img.horizSym
print "vert sym ", img.vertSym
print "circled points ", img.circles


#         self.foregroundPixels = None # foreground is the MAIN color of the image's central data
#         self.backgroundPixels = None
#         self.horizSym = None
#         self.vertSym = None
#         self.corners = None
#         self.longestLine = None
#         self.secondHighest = None
# 
#         self.circles = None
#         self.longestLine = None
#         self.secondHighest = None
# 
#         self.circles = None