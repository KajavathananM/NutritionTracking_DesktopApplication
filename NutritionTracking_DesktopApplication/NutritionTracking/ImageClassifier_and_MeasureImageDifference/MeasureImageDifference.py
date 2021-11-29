from PIL import Image, ImageTk,ImageChops
import cv2
from CalorieEstimator import cropImageFromRect
import os
import requests
from io import BytesIO
import numpy as np
from matplotlib import pyplot as plt 
import re
import math
# E:/NutritionTracking/TestCases/Test_Images/WebApple.jpg
# E:/NutritionTracking/TestCases/Test_Images/PhotoApple.jpg 
# E:/NutritionTracking/TestCases/Test_Images/test.jpg
# E:/NutritionTracking/TestCases/Test_Images/idly1.jpg
# E:/NutritionTracking/TestCases/Test_Images/idly28.jpg
# E:/NutritionTracking/TestCases/Test_Images/Mobile_2.jpg
# E:/NutritionTracking/TestCases/Test_Images/Banana39.jpg
# E:/NutritionTracking/TestCases/Test_Images/Banana81.jpg
# E:/NutritionTracking/TestCases/Test_Images/Banana80.jpg
# E:/NutritionTracking/TestCases/Test_Images/rcDhal2.jpg
# E:/NutritionTracking/TestCases/Test_Images/rcDhal12.jpg

drawing1 = False # true if mouse is pressed
mode1 = True # if True, draw rectangle.
ix1,iy1 = -1,-1
# mouse callback function
def draw_selectedRegionWeb(event,x,y,flags,webImage):
  global ix1,iy1,drawing,mode

  if event == cv2.EVENT_LBUTTONDOWN:
      drawing1 = True
      ix1,iy1 = x,y

  elif event == cv2.EVENT_LBUTTONUP:
    drawing1 = False
    if mode1 == True:
        global objExtractWeb
        objExtractWeb=cropImageFromRect(webImage,ix1,iy1,x,y)
        cv2.imshow('ImageCropped_Web',objExtractWeb)
        cv2.rectangle(webImage,(ix1,iy1),(x,y),(0,0,255),2)
        cv2.imshow('Web_Image',webImage)
        filename='WebImageCropped.png'
        path='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Grabcut'
        cv2.imwrite(os.path.join(path ,filename),objExtractWeb) 
        rmvBlackBackground(os.path.join(path ,filename),filename,path,"Web_Image")
        

drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle.
ix,iy = -1,-1    
def draw_selectedRegionPhoto(event,x,y,flags,photoImage):
  global ix,iy,drawing,mode

  if event == cv2.EVENT_LBUTTONDOWN:
      drawing = True
      ix,iy = x,y

  elif event == cv2.EVENT_LBUTTONUP:
    drawing = False
    if mode == True:
        global objExtractPhoto
        objExtractPhoto=cropImageFromRect(photoImage,ix,iy,x,y)
        cv2.imshow('ImageCropped_Photo',objExtractPhoto)
        cv2.rectangle(photoImage,(ix,iy),(x,y),(0,0,255),2)
        cv2.imshow('Photo_Image',photoImage)
        path='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Grabcut'
        filename='PhotoImageCropped.png'
        cv2.imwrite(os.path.join(path ,filename),objExtractPhoto)
        rmvBlackBackground(os.path.join(path,filename),filename,path,"Photo_Image")
         

def drawRectInPhotoImage(webImage,photoImage):
    cv2.imshow('Web_Image',webImage)
    cv2.setMouseCallback('Web_Image',draw_selectedRegionWeb,webImage)
    cv2.imshow('Photo_Image',photoImage)
    cv2.setMouseCallback('Photo_Image',draw_selectedRegionPhoto,photoImage)
    cv2.waitKey(0)     
    cv2.destroyAllWindows() 

# Main Function called in food_cnn_predict.py
def checkImageSize(webPath,photoPath):
    global webImage
    global photoImage 
    if not "http" in str(webPath) or not "https" in str(webPath):
      webImage=cv2.imread(webPath)
    elif  "http" in str(webPath)  or  "https" in str(webPath):
      response = requests.get(webPath)
      img_Webstream = BytesIO(response.content)
      webImage = cv2.imdecode(np.fromstring(img_Webstream.read(), np.uint8), 1)
    photoImage=cv2.imread(photoPath) 
    

    # hsv = cv2.cvtColor((52,192,235), cv2.COLOR_BGR2HSV)
    # h,s,v = cv2.split(hsv)
    # print(h+" "+s+" "+v)
    

    colsWeb, rowsWeb, channelsWeb = webImage.shape
    colsPhoto,rowsPhoto,channelsPhoto=photoImage.shape
    assert colsPhoto==colsWeb 
    assert rowsPhoto==rowsWeb 
    checkShapeofImage(webImage,photoImage)
    return [objExtractWeb,objExtractPhoto]

def checkShapeofImage(webImage,photoImage):
  drawRectInPhotoImage(webImage,photoImage)


def rmvBlackBackground(filePath,fileName,path,figName):
  x=re.search("([^.png])\w+",fileName)
  fileName=x.group(0)
  src = cv2.imread(filePath, 1)
  cols, rows, channels = src.shape
  # print(str(src.shape))
  BGRA = cv2.cvtColor(src,cv2.COLOR_BGR2BGRA) 
  for i in range(0,cols):
      for j in range(0,rows):
         pixel_val = src[i,j]
         if pixel_val[0]==0 and pixel_val[1]==0 and pixel_val[2]==0:
           BGRA[i,j,3]=0
         else:
           BGRA[i,j,3]=255
  cv2.imwrite(os.path.join(path ,fileName+"Test.png"), BGRA)
  img=cv2.imread(os.path.join(path ,fileName+"Test.png"),cv2.IMREAD_UNCHANGED)
  sketchContours(img,figName,fileName+"Test.png")

def plotGraphs(imageDifference_excelWriter):
    path='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Grabcut'
    WebImg=cv2.imread(os.path.join(path ,"WebImageCroppedTest.png"),cv2.IMREAD_UNCHANGED)
    PhotoImg=cv2.imread(os.path.join(path ,"PhotoImageCroppedTest.png"),cv2.IMREAD_UNCHANGED)
    
    

    valuesWebImg=removeTransPixels(WebImg)
    WebImg=valuesWebImg[0]

    #test1=WebImg.shape[0]*WebImg.shape[1]
    # print("L1:"+str(test1))

    # cv2.imshow("Test1",WebImg)
    WebImg=cv2.cvtColor(WebImg, cv2.COLOR_BGR2HSV)

  
    limWeb=int(valuesWebImg[1])+5000
    fig1 = plt.figure("WebImageCroppedTest")
    plt.xlabel('Pixel Values', fontsize=12)
    plt.ylabel('No of Pixels', fontsize=12)
    plt.ylim(0,limWeb)
    plt.hist(WebImg.ravel(),256,[0,256])
    fig1.show()

    fig1.canvas.draw()
    graph1img = np.fromstring(fig1.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    graph1img  = graph1img.reshape(fig1.canvas.get_width_height()[::-1] + (3,))
    graph1img = cv2.cvtColor(graph1img,cv2.COLOR_RGB2BGR)
    path='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Histograms'
    filename='WebImageHistogram.jpg'
    cv2.imwrite(os.path.join(path ,filename),graph1img)
    

    valuesPhotoImg=removeTransPixels(PhotoImg)
    PhotoImg=valuesPhotoImg[0]
    PhotoImg=cv2.cvtColor(PhotoImg, cv2.COLOR_BGR2HSV)

    # PhotoImg=cv2.resize(PhotoImg,(WebImg.shape[0],WebImg.shape[1]), interpolation = cv2.INTER_AREA)
    #cv2.imshow("Test2",PhotoImg)

    # test2=PhotoImg.shape[0]*PhotoImg.shape[1]
    # print("L2:"+str(test2))       
    
     
    
    
    fig2 = plt.figure("PhotoImageCroppedTest")
    plt.xlabel('Pixel Values', fontsize=12)
    plt.ylabel('No of Pixels', fontsize=12)
    limPhoto=int(valuesPhotoImg[1])+5000
    plt.ylim(0,limPhoto)
    plt.hist(PhotoImg.ravel(),256,[0,256])
    fig2.show()

    fig2.canvas.draw() 
    graph2img = np.fromstring(fig2.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    graph2img  = graph2img.reshape(fig2.canvas.get_width_height()[::-1] + (3,))
    graph2img = cv2.cvtColor(graph2img,cv2.COLOR_RGB2BGR)
    path='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Histograms'
    filename='PhotoImageHistogram.jpg'
    cv2.imwrite(os.path.join(path ,filename),graph2img)
  
    hist1 = cv2.calcHist([WebImg], [0,1], None, [180,256], [0,180,0,256])
    cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX);
    hist2= cv2.calcHist([PhotoImg], [0,1], None, [180,256], [0,180,0,256])
    cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX);


    
    
  
    #imageComparison= cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
    #imageComparison= cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    imageComparison= cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
    
    print ("\nComparison between Web Image and Mobile Camera Image: "+str(imageComparison)+"\n")
    if imageComparison<0.8:
      print("Both Images have similar color with respective to HSV.")
      imageDifference_excelWriter.writeHSVRange(imageComparison,"Both Images have similar color with respective to HSV.")
    else:
      print("Images have different color with respective to HSV.")
      imageDifference_excelWriter.writeHSVRange(imageComparison,"Images have different color with respective to HSV.")
    
    sizeDifference=0
    if valuesWebImg[1]>valuesPhotoImg[1]:
      sizeDifference=valuesWebImg[1]-valuesPhotoImg[1] 
    else:
      sizeDifference=valuesPhotoImg[1]-valuesWebImg[1]
    
    print("Size Difference between images: "+str(sizeDifference))
    if (sizeDifference)<=4000:
      print("Image size for both images is approximately equal in terms of pixels.") 
      imageDifference_excelWriter.writeSizeComparison(valuesWebImg[1],valuesPhotoImg[1],sizeDifference,"Image size for both images is approximately equal in terms of pixels.")
    else:
      print("Image size is not equal in terms of pixels.")
      imageDifference_excelWriter.writeSizeComparison(valuesWebImg[1],valuesPhotoImg[1],sizeDifference,"Image size is not equal in terms of pixels.")
    
 
  
def compareShapesBetweenImages():
  path='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Grabcut'
  web_filename='WebImageCroppedTest.png'
  WebImg= cv2.imread(os.path.join(path ,web_filename))
  orig_WebImage=WebImg.copy()
  img_gray=cv2.cvtColor(orig_WebImage,cv2.COLOR_BGR2GRAY)
  ret, thresh=cv2.threshold(img_gray.copy(),2,255,cv2.THRESH_BINARY)
  img_gray1=img_gray.copy()
  contours, hierarchy=cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  for c in contours:
        x,y,w,h=cv2.boundingRect(c)
        cv2.drawContours(orig_WebImage,[c],-1,(255,0,0),3)

  Photo_filename='PhotoImageCroppedTest.png'
  PhotoImg= cv2.imread(os.path.join(path ,Photo_filename))
  orig_PhotoImage=PhotoImg.copy()
  img_gray=cv2.cvtColor(orig_PhotoImage,cv2.COLOR_BGR2GRAY)
  ret, thresh=cv2.threshold(img_gray.copy(),2,255,cv2.THRESH_BINARY)
  img_gray1=img_gray.copy()
  contours, hierarchy=cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  for c in contours:
        x,y,w,h=cv2.boundingRect(c)
        cv2.drawContours(orig_PhotoImage,[c],-1,(255,0,0),3)
  alpha=0.6
  beta = (1.0 - alpha)
  overlappedImages = cv2.addWeighted(orig_WebImage, alpha, orig_PhotoImage, beta, 0.0)
  cv2.imshow('Images Overlapped', overlappedImages)
  newPath='E:/NutritionTracking/TestCases/ImageProcessed_Pictures/Overlay'
  cv2.imwrite(os.path.join(newPath,"Overlapped Images.png"),overlappedImages)

def removeTransPixels(img):
      orig_image=img.copy()
      img_gray=cv2.cvtColor(orig_image,cv2.COLOR_BGR2GRAY)
      ret, thresh=cv2.threshold(img_gray.copy(),2,255,cv2.THRESH_BINARY)
      img_gray1=img_gray.copy()
      # cv2.imshow("Thresh_test",thresh)
      contours, hierarchy=cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)


      for c in contours:
        x,y,w,h=cv2.boundingRect(c)
        ROI = img[y:y+h, x:x+w]
  
      ROI_ImgTransCols=[]
      ROI_ImgTransRows=[]
      enc_TransPixels=0
      for i in range(0,ROI.shape[0]):
          for j in range(0,ROI.shape[1]):
            pixel_val = ROI[i,j]
            if pixel_val[3]==255:   
                #  ROI_ImgTransCols.append(ROI[i])
                #  ROI_ImgTransRows.append(ROI[j])
                enc_TransPixels+=1  
                            
      objPixels=(ROI.shape[0]*ROI.shape[1])-enc_TransPixels
      print("Object Pixels: "+str(objPixels))
      # ROI=np.delete(ROI, ROI_ImgTransCols,1)     
      # ROI=np.delete(ROI,ROI_ImgTransRows,0)
      return ROI,objPixels

def sketchContours(img,figName,fileName):
      orig_image=img.copy()
      img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
      ret, thresh=cv2.threshold(img_gray.copy(),2,255,cv2.THRESH_BINARY)
      img_gray1=img_gray.copy()
      # cv2.imshow("Thresh_test",thresh)
      contours, hierarchy=cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    
          
      for c in contours:
        x,y,w,h=cv2.boundingRect(c)
        # obj_image = orig_image[y:y+h, x:x+w]
        cv2.rectangle(orig_image,(x,y),(x+w,y+h),(0,0,255),2)
        # cv2.drawContours(orig_image,[c],-1,(255,0,0),3)
       
      # print("Predicted Shape: "+shape)
      s=re.search("(Photo|Web)",figName)
      figName="ImageCropped_"+s.group(0)
      # print(name)
      cv2.imshow(figName,img)
      # cv2.imwrite(os.path.join(path ,filename),img_gray)


      

