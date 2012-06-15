#!/usr/local/bin/python
'''
Created on June 14, 2011
sky segmentation sketch
@author: Fabian
'''

import cv2

def combineImages(img1, img2):
    
    outImg = img1.copy()
    
    if len(img2.shape) < 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

    y0 = 0 
    y1 = outImg.shape[0]
    x0 = outImg.shape[1] / 2
    x1 = outImg.shape[1]
    
    outImg[y0:y1, x0:x1] = img2[y0:y1, x0:x1]

    return outImg

class App(object):
    def __init__(self, video_src):
        
        self.cannyLow = 71
        self.cannyHigh = 208
        self.morphKernSize = (9,9)
        self.threshVal = 140
        self.minPathLength = 400

        self.videoSrc = video_src

        self.cap = cv2.VideoCapture()
        self.cap.open(self.videoSrc)
        
        #window names
        self.inputWinName = "input"
        self.edgeWinName = "edge"
        self.outputWinName = "output"

        cv2.namedWindow(self.inputWinName)
        cv2.namedWindow(self.outputWinName)
        cv2.namedWindow(self.edgeWinName)

        cv2.createTrackbar("cannyLow", self.outputWinName, self.cannyLow, 1000, self.onSliderCannyLow)
        cv2.createTrackbar("cannyHigh", self.outputWinName, self.cannyHigh, 1000, self.onSliderCannyHigh)
        #cv2.createTrackbar("thresh", self.outputWinName, self.threshVal, 255, self.onThreshSlider)
        cv2.createTrackbar("morphKernSize", self.outputWinName, self.morphKernSize[0], 255, self.onKernSlider)
        cv2.createTrackbar("contourSlider", self.outputWinName, self.minPathLength, 1000, self.onContourSlider)

        print("hello cvScope tester\n")

        #if len(sys.argv) > 2 :
        #    self.threshVal = int(sys.argv[1])
        #else:
        #    self.threshVal = 140

    def onSliderCannyLow(self, val):
        self.cannyLow = val

    def onSliderCannyHigh(self, val):
        self.cannyHigh = val

    def onKernSlider(self, val):
        if not val%2:
            val-=1
        self.morphKernSize = (val, val)

    def onContourSlider(self, val):
        self.minPathLength = val
    
    def onThreshSlider(self, val):
        self.threshVal = val

    def run(self):

        while True:

            # next frame
            ret,img = self.cap.read()
            
            if not ret:
                self.cap.release()
                self.cap.open(self.videoSrc)
                continue

            scaleFactor = 0.5
            scaledSize = (int(scaleFactor * img.shape[1]),int(scaleFactor * img.shape[0]))
            scaledImg = cv2.resize(img, scaledSize)
            
            gray = cv2.cvtColor(scaledImg, cv2.COLOR_BGR2GRAY)
    
            #equalize histogram
            #gray = cv2.equalizeHist(gray)

            thresh = cv2.threshold(gray, self.threshVal, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            edges = cv2.Canny(gray, self.cannyLow, self.cannyHigh)
            
            workImg = edges.copy()

            cv2.dilate(         edges,
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE,self.morphKernSize),
                                workImg,
                                (-1,-1),
                                2)
            cv2.morphologyEx(   thresh,
                                cv2.MORPH_CLOSE,
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE,self.morphKernSize),
                                thresh,
                                (-1,-1),
                                2)
            
            workImg |= thresh

            #Calculate blobs #cv2.RETR_EXTERNAL
            contours0, hierarchy = cv2.findContours(workImg.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            #contours = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours0]
    
            #sort out short contours
            longContours = []

            for cnt in contours0:
                if len(cnt) > self.minPathLength:
                    longContours.append(cnt)  

            #create output image
            outImage = combineImages(scaledImg, edges)

            #(-1, 3)[levels <= 0]
            levels = 1
            cv2.drawContours( outImage, longContours, -1, (128,255,255), 
            3, cv2.CV_AA)
            #cv2.drawContours( outImage, longContours, -1, (128,255,255), 
            #3, cv2.CV_AA, hierarchy, abs(levels) )

            #show images
            cv2.imshow(self.inputWinName, scaledImg)
            cv2.imshow(self.outputWinName, outImage)
            cv2.imshow(self.edgeWinName, thresh)

            ch = 0xFF & cv2.waitKey(5)
            if ch == 27:
                break
    
        #out="%.4d.jpg" % (i) 
        #cv2.imwrite(out, edges)
        #i=i+1
    
        self.cap.release()

        print   "Values:\n\n"\
                "--> Canny: %d - %d\n"\
                "--> MorphKernSize: %s\n" %(self.cannyLow,self.cannyHigh,self.morphKernSize)
        print "ciao\n" 
   

if __name__ == '__main__':
  
    import sys
    try: video_src = sys.argv[1]
    except: video_src = 0
    print __doc__
    App(video_src).run()

