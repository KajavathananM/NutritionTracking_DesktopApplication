from io import BytesIO
import cv2
from PIL import Image
import numpy as np
import requests

#Pass coordinates top left and bottom right of rectangle and image matrix for cropping
def cropImageFromRect(imgC,ix,iy,x,y):
    #Width and height of the selected region
    # width=(x-ix)
    # height=(y-iy)
    #Top left point
    # print(str(ix)+" "+str(iy))
    # #Bottom Right Point
    # print(str(x)+" "+str(y))
    w=x-ix
    h=y-iy
     
    mask=np.zeros(imgC.shape[:2],np.uint8) 
    bgModel=np.zeros((1,65),np.float64)
    #This the extracted object is located
    fgModel=np.zeros((1,65),np.float64)
    #Selected Region is constructed
    # rect = (0,0,width,height)
    rect = (ix,iy,w,h)
    
    #Here we are converting Background of the image as black to extract the object
    cv2.grabCut(imgC,mask,rect,bgModel,fgModel,7,cv2.GC_INIT_WITH_RECT)
    mask2=np.where((mask==2)|(mask==0),0,1).astype('uint8')
    imgC = imgC*mask2[:,:,np.newaxis]
    
    imgCV=imgC.copy()
    # imgCV=cv2.rectangle(imgCV, (ix,iy), (width,height), (255, 0, 0) , 8)
    # imgCV=cv2.rectangle(imgCV, (ix,iy), (x,y), (255, 0, 0) , 8)
    findArea(imgCV)
    return imgC
#Draw contours around the image to calculate the area
def findArea(imgC):
     global real_food_area
     real_food_area=0
     ret,thresh = cv2.threshold(cv2.cvtColor(imgC,cv2.COLOR_BGR2GRAY), 120,255,cv2.THRESH_BINARY)
     contours = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
     for contour in contours:
        #approx = cv2.approxPolyDP(contour, 0.009 * cv2.arcLength(contour, True), True) 
        cv2.drawContours(imgC, contour, -1, (0, 0, 255), 5)
        #cv2.drawContours(imgC, [approx], 0, (0, 0, 255), 5)  
        real_food_area+=cv2.contourArea(contour)/0.955
     real_food_area=(real_food_area*(0.0264583333**2))
     
#Method to return the area of the extracted object
def getArea(predictedLabel):
    print('Area: '+str(real_food_area)+' squared cm')
    return real_food_area

#Calculate calorie of the extracted object
def getCalorie(calorie): 
  density =0.6
  mass = real_food_volume*density*1.0
  calorie_tot = (calorie/100.0)*mass
  print("Total Calories: "+ str(calorie_tot)+" KCAL")
  #return mass, calorie_tot

#Calculate volume of the extracted object
def getVolume(predictedLabel):
	
    global real_food_volume

    real_food_volume = 0
    if predictedLabel is 'Apple': 
      radius = np.sqrt(real_food_area/np.pi)
      real_food_volume = (4/3)*np.pi*radius*radius*radius
    

    elif predictedLabel is 'Banana'or 'Pizza' or 'Rice with Dhal' or 'Idly': 
      height = 914*0.0264583333
      radius = real_food_area/(2.0*height)
      real_food_volume = np.pi*radius*radius*height

    elif predictedLabel is 'Samosa': 
      real_food_volume = real_food_area*0.5 
 
    print('Volume: '+str(real_food_volume)+' cubic cm')
 
