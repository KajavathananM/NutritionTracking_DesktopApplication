from CalorieEstimator import cropImageFromRect,getArea,getVolume,getCalorie
from MeasureImageDifference import checkImageSize,plotGraphs,compareShapesBetweenImages


from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array,image as image_utils
from keras.models import Sequential, load_model

import re

# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/ricewithdhal/rcDhal4.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/ricewithdhal/rcDhal3.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/ricewithdhal/rcDhal53.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/samosa/62383.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/french_fries/82535.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/idly/idly25.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/idly/idly4.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/idly/idly40.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/pizza/2965.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/pizza/2965.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/pizza/72716.jpg
# E:/NutritionTracking/ImageClassifier_and_MeasureImageDifference/dataset/training_set/samosa/6119.jpg

#load model
img_width, img_height = 128, 128
model_path = './models/model.h5'
model_weights_path = './models/weights.h5'
model = load_model(model_path)
model.load_weights(model_weights_path)


from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkinter import Tk,Label,Canvas,Entry,Button,Frame,ttk

#Libraries for plotting graph and loading dataset
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
import numpy as np
import math
from TestStorageController import ImageDifferenceExcelWriter
# Get the architecture of CNN Model
#print(model.summary())


imageDifference_excelWriter=ImageDifferenceExcelWriter()
imageDifference_excelWriter.setRowIndex()
#Generate Piechart from the relevant csv dataset
def sketchPieChart(nutritionAnalysisWindow,predictedLabel):
    nutritionData=pd.read_csv('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\nutrition_dataset\\'+predictedLabel+'.csv')
    calorie=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Calories"].index,1].squeeze()
    getCalorie(calorie)
    lbl = Label(nutritionAnalysisWindow, text="Calories: "+str(calorie)+" KCAL", font=("Helvetica", 12))
    lbl.place(x =40,y=60)
    fig=plt.figure(figsize=(8,3), dpi=100)
    plt.style.use('ggplot')
    carbohyrate = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Carbohydrate"].index,1].squeeze()
    fat= nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Fat"].index,1].squeeze()
    protein = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Protein"].index,1].squeeze()
    weights = [carbohyrate,fat,protein]
    label = ['Carbohydrate', 'Fat', 'Protein']
    plt.title('Weight for 3 Nutrient Classes %',size=12)
    plt.pie(weights, labels=label,pctdistance=0.8,autopct='%.2f %%')
    graphDiagram = FigureCanvasTkAgg(fig,nutritionAnalysisWindow)
    graphDiagram.get_tk_widget().place(x =11, y = 90)
    graphDiagram.get_tk_widget().config(width=530, height=500)
    graphDiagram.draw()
 
    
#Generate Vitamin Barchart from the relevant csv dataset
def sketchVitaminsHorizontalBarChart(nutritionAnalysisWindow,predictedLabel):
    nutritionData=pd.read_csv('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\nutrition_dataset\\'+predictedLabel+'.csv')
    
    vitaminA = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin A"].index,1].squeeze()/((10**6)*3.33)
    vitaminB6 = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin B6"].index,1].squeeze()/(10**3)
    vitaminB12 = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin B12"].index,1].squeeze()/((10**6)*3.33)
    vitaminC = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin C"].index,1].squeeze()/(10**3)
    vitaminD=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin D"].index,1].squeeze()/((10**6)*3.33)
    vitaminE=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin E"].index,1].squeeze()/(10**3)
    vitaminK=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Vitamin K"].index,1].squeeze()/((10**6)*3.33)


    fig=plt.figure(figsize=(8,3), dpi=100)
    labels = ('Vitamin A','Vitamin B6','Vitamin B12', 'Vitamin C','Vitamin D','Vitamin E','Vitamin K')
    y_pos = np.arange(len(labels))
    values = [vitaminA,vitaminB6,vitaminB12,vitaminC,vitaminD,vitaminE,vitaminK]
  
    plt.barh(y_pos,values, align='center', alpha=0.5,color='#FF4500')
    plt.yticks(y_pos, labels)
    plt.xlabel('Weight g')
    plt.title('Vitamins')
    graphVDiagram = FigureCanvasTkAgg(fig,nutritionAnalysisWindow)
    graphVDiagram.get_tk_widget().place(x =20, y = 70)
    graphVDiagram.get_tk_widget().config(width=950, height=500)
    graphVDiagram.draw() 

#Generate Minerals Barchart from the relevant csv dataset   
def sketchMinearalsHorizontalBarChart(nutritionAnalysisWindow,predictedLabel):
    nutritionData=pd.read_csv('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\nutrition_dataset\\'+predictedLabel+'.csv')
    
    
    fluoride = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Fluoride, F"].index,1].squeeze()/(10**6)
    calcium = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Calcium, Ca"].index,1].squeeze()/(10**3)
    sodium = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Sodium, Na"].index,1].squeeze()/(10**3)
    potassium = nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Potassium, K"].index,1].squeeze()/(10**3)
    iron=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Iron, Fe"].index,1].squeeze()/(10**3)
    phosphorus=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Phosphorus, P"].index,1].squeeze()/(10**3)
    magnesium=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Magnesium, Mg"].index,1].squeeze()/(10**3)
    zinc=nutritionData.iloc[nutritionData.loc[nutritionData['Nutrient'] == "Zinc, Zn"].index,1].squeeze()/(10**3)

    fig=plt.figure(figsize=(8,1), dpi=100)
    labels = ('Fluoride','Calcium','Sodium','Potassium','Iron','Phosphorus','Magnesium','Zinc')
    y_pos = np.arange(len(labels))
    values = [fluoride,calcium,sodium,potassium,iron,phosphorus,magnesium,zinc]
  
    width=0.4
    plt.barh(y_pos,values,width,align='center', alpha=0.5,color='#FF4500')
    plt.yticks(y_pos, labels)
    plt.xlabel('Weight g')
    plt.title('Minerals')
    graphMDiagram = FigureCanvasTkAgg(fig,nutritionAnalysisWindow)
    graphMDiagram.get_tk_widget().place(x =20, y = 70)
    graphMDiagram.get_tk_widget().config(width=800, height=500)
    graphMDiagram.draw()


def getRiceColorPixel(arr):
    hsv_frame = cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)
    low_rice = np.array([0, 0, 150])
    high_rice = np.array([255,55, 255])
    rice_mask = cv2.inRange(hsv_frame, low_rice, high_rice)
    riceColor = cv2.bitwise_and(arr, arr, mask=rice_mask)
    print("Rice color pixels: "+str(cv2.countNonZero(rice_mask)))
    cv2.imshow('Rice',riceColor)
    return cv2.countNonZero(rice_mask)

#Get the dhal color    
def getDhalColorPixel(arr):
    hsv_frame = cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)
    low_dhal = np.array([20, 100, 100])
    high_dhal = np.array([30, 255, 255])
    dhal_mask = cv2.inRange(hsv_frame, low_dhal, high_dhal)
    dhalColor = cv2.bitwise_and(arr, arr, mask=dhal_mask)
    print("Dhal color pixels: "+str(cv2.countNonZero(dhal_mask)))
    cv2.imshow('Dhal Color',dhalColor)
    return cv2.countNonZero(dhal_mask)

#Get the Sambal color         
def getSambalColorPixel(arr):
    hsv_frame = cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)
    low_Sambal = np.array([10, 100, 20])
    high_Sambal = np.array([20, 255, 200])
    sambal_mask = cv2.inRange(hsv_frame, low_Sambal, high_Sambal)
    sambalColor = cv2.bitwise_and(arr, arr, mask=sambal_mask)
    print("Sambal color pixels: "+str(cv2.countNonZero(sambal_mask)))
    cv2.imshow('Sambhal',sambalColor) 
    return cv2.countNonZero(sambal_mask)

def getBananaColorPixel(arr):     
    hsv_frame = cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)
    low_banana = np.array([20,0,0])
    high_banana = np.array([50,255,255])
    banana_mask = cv2.inRange(hsv_frame,low_banana, high_banana)
    bananaColor = cv2.bitwise_and(arr, arr, mask=banana_mask)
    print("Banana color pixels: "+str(cv2.countNonZero(banana_mask)))
    cv2.imshow('Banana',bananaColor) 
    return cv2.countNonZero(banana_mask)

def erodeImage(imgGray):
  ret, otsu = cv2.threshold(imgGray, 0, 255, 
  cv2.THRESH_BINARY | cv2.THRESH_OTSU)
  ret2, triangle = cv2.threshold(imgGray, 0, 255, 
  cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)
  kernels = np.ones((5, 5), np.uint8)
  img_erode = cv2.erode(objExtract, kernels, iterations=5)
  return img_erode

def detectBlobs():
  #img=erodeImage(path,fileName)
  img = cv2.cvtColor(objExtract, cv2.COLOR_BGR2GRAY)
  img=erodeImage(img)
  # Set up the detector with default parameters.
  detector = cv2.SimpleBlobDetector_create()
  # Detect blobs.
  keypoints = detector.detect(img)
  # Draw detected blobs as red circles.
  # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
  blobs = cv2.drawKeypoints(img, keypoints, np.array([]), (255, 0, 0),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#   print("Number of Blobs: "+str(len(keypoints)))
#   cv2.imshow("Keypoints", blobs)  
  # Show keypoints
  return len(keypoints)

#Color extractor algorithm used to classify between Idly and Rice with Dhal   
def getColorFromImage(imgC):
    total_pixels = imgC.shape[0]*imgC.shape[1]
    #print("Total Pixels of Image before checking for black pixels: "+total_pixels)

    for i in range(len(imgC)):
        for  j in range(len(imgC[i])):
            pixel_value = imgC[i,j]
            if pixel_value[0]==0 and pixel_value[1]==0 and pixel_value[2]==0:
                total_pixels-=1
                  
            
    #print("Total Pixels of Image after checking for black pixels: "+total_pixels)    
    percent_riceColor=(getRiceColorPixel(objExtract)/total_pixels) * 100
    percent_DhalColor=(getDhalColorPixel(objExtract)/total_pixels) * 100
    percent_SambalColor=(getSambalColorPixel(objExtract)/total_pixels) * 100
    percent_BananaColor=(getBananaColorPixel(objExtract)/total_pixels) * 100

    print("Percentage of Rice Color: "+str(percent_riceColor))
    print("Percentage of Dhal Color: "+str(percent_DhalColor))
    print("Percentage of Sambal Color: "+str(percent_SambalColor))
    print("Percentage of Banana Color: "+str(percent_BananaColor))

    return percent_riceColor,percent_DhalColor,percent_SambalColor,percent_BananaColor

def getColorFromImageTest(imgC,objExtract):
    total_pixels = imgC.shape[0]*imgC.shape[1]
    #print("Total Pixels of Image before checking for black pixels: "+total_pixels)

    for i in range(len(imgC)):
        for  j in range(len(imgC[i])):
            pixel_value = imgC[i,j]
            if pixel_value[0]==0 and pixel_value[1]==0 and pixel_value[2]==0:
                total_pixels-=1
                  
    riceColor=getRiceColorPixel(objExtract)
    dhalColor= getDhalColorPixel(objExtract)
    sambalColor=getSambalColorPixel(objExtract)
    bananaColor=getBananaColorPixel(objExtract)

    #print("Total Pixels of Image after checking for black pixels: "+total_pixels)   
    percent_riceColor=(riceColor/total_pixels) * 100
    percent_DhalColor=(dhalColor/total_pixels) * 100
    percent_SambalColor=(sambalColor/total_pixels) * 100
    percent_BananaColor=(bananaColor/total_pixels) * 100

    print("Percentage of Rice Color: "+str(percent_riceColor))
    print("Percentage of Dhal Color: "+str(percent_DhalColor))
    print("Percentage of Sambal Color: "+str(percent_SambalColor))
    print("Percentage of Banana Color: "+str(percent_BananaColor))

    imageDifference_excelWriter.writePercentOfColor(percent_riceColor,percent_DhalColor,percent_SambalColor,percent_BananaColor)
    imageDifference_excelWriter.writePixelsOfColor(riceColor,dhalColor,sambalColor,bananaColor)
    return percent_riceColor,percent_DhalColor,percent_SambalColor,percent_BananaColor

#Program loads nutrition Nutrition data based on predicted label
#Python code for User interface nutritionAnalysisWindow
def openNutritionAnalysis(predictedLabel):
    nutritionAnalysisWindow = Tk()
         
    #Create Tab Control  
    tabControl=ttk.Notebook(nutritionAnalysisWindow) 
    #Tab2  
    tab1=Frame(tabControl)  
    tabControl.add(tab1, text='View 3 Nutrients')   
    #Tab2  
    tab2=Frame(tabControl)  
    tabControl.add(tab2, text='View Vitamins')  
    #Tab3 
    tab3=Frame(tabControl)  
    tabControl.add(tab3, text='View Minerals')  
    tabControl.pack(expand=1, fill="both")
        
    nutritionAnalysisWindow.title("Nutrition Analysis") 
    nutritionAnalysisWindow.geometry('800x2000')
    lbl = Label(nutritionAnalysisWindow, text=predictedLabel, font=("Helvetica", 18))
    lbl.place(x=400,y=30)
    sketchPieChart(tab1,predictedLabel)
    sketchVitaminsHorizontalBarChart(tab2,predictedLabel)
    sketchMinearalsHorizontalBarChart(tab3,predictedLabel)

    nutritionAnalysisWindow.mainloop()




def click_showCoordinates(event, x, y, flags, imgC): 
    # checking for left mouse clicks 
    if event == cv2.EVENT_LBUTTONDOWN: 
        # displaying the coordinates on the Shell  
        print(x, ' ', y) 
        # displaying the coordinates on the image window 
        font = cv2.FONT_HERSHEY_SIMPLEX 
        cv2.putText(imgC, str(x) + ',' +str(y), (x,y), font,1, (255, 255, 255), 2) 
        cv2.imshow('image', imgC) 
  
    # checking for right mouse clicks      
    if event==cv2.EVENT_RBUTTONDOWN: 
        # displaying the coordinates on the Shell 
        print(x, ' ', y) 
  
        # displaying the coordinates on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX 
        b = imgC[y, x, 0] 
        g = imgC[y, x, 1] 
        r = imgC[y, x, 2] 
        cv2.putText(imgC, str(b) + ',' +str(g) + ',' + str(r),(x,y), font, 1,(255, 255, 255), 2) 

        cv2.namedWindow('Resized Window', cv2.WINDOW_NORMAL)
        #resize the window according to the screen resolution
        cv2.resizeWindow('Resized Window', 400, 400)
        #cv2.imshow('image', params) 
        cv2.imshow('Resized Window', imgC) 

drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle.
ix,iy = -1,-1
# mouse callback function
def draw_selectedRegion(event,x,y,flags,imgC):
  global ix,iy,drawing,mode

  if event == cv2.EVENT_LBUTTONDOWN:
      drawing = True
      ix,iy = x,y

  elif event == cv2.EVENT_LBUTTONUP:
    drawing = False
    if mode == True:
        global objExtract
        objExtract=cropImageFromRect(imgC,ix,iy,x,y)
        cv2.imshow('ImageCropped',objExtract)
        cv2.rectangle(imgC,(ix,iy),(x,y),(0,0,255),2)
        cv2.imshow('Image',imgC)
    else:
        cv2.circle(imgC,(x,y),5,(255,0,0),-1)

 
#Here we can view the coordinates by clicking on any pixel of image in cv window
def plotCoordinatesInWebImage(response):
    img_stream = BytesIO(response.content)
    imgC = cv2.imdecode(np.fromstring(img_stream.read(), np.uint8), 1)
    imgC=cv2.resize(imgC, (400, 400))
    cv2.imshow('image',imgC)
    cv2.setMouseCallback('image', click_showCoordinates,imgC) 
    cv2.waitKey(0) 
    cv2.destroyAllWindows()

#Drawing of the selected region in cv window where Grab cut algorithm to get the object
def drawRectInWebImage(response):
    img_stream = BytesIO(response.content)
    imgC = cv2.imdecode(np.fromstring(img_stream.read(), np.uint8), 1)
    imgC=cv2.resize(imgC, (400, 400))  
    cv2.imshow('Image',imgC)
    cv2.setMouseCallback('Image',draw_selectedRegion,imgC)
    cv2.waitKey(0)     
    cv2.destroyAllWindows() 

def drawRectInPhotoImage(photoPath):
    imgC=cv2.imread(photoPath) 
    imgC=cv2.resize(imgC, (400, 400))  
    cv2.imshow('Image',imgC)
    cv2.setMouseCallback('Image',draw_selectedRegion,imgC)
    cv2.waitKey(0)     
    cv2.destroyAllWindows() 

#Program identifies the food from the image and provides the the label for the image
#Python code for User interface foodLabelWindow
foodLabelWindow = Tk()
foodLabelWindow.title("Welcome to Food Image Classifier") 
foodLabelWindow.geometry('800x2000')


HtabControl=ttk.Notebook(foodLabelWindow) 
#Tab1  
htab1=Frame(HtabControl)  
HtabControl.add(htab1, text='Identify Image')   
#Tab2  
htab2=Frame(HtabControl)  
HtabControl.add(htab2, text='Validate Images')    
HtabControl.pack(expand=1, fill="both")
head = Label(htab1, text="Identify Food Item", font=("Serif",18))
head.place(x=5,y=10)
lbl = Label(htab1, text="Enter the URL of the image or File Path", font=("Helvetica", 12))
lbl.place(x=10,y=50)
# Image Recognition is performed on the image to retrieve the predicted label as well as relevant nutrional values 
#from the csv dataset
def ScanImage():
    global url
    global predictedLabel
    lbl.configure()
    if "http" in str(url_input.get()) or "https" in str(url_input.get()):
        url  = (url_input.get())
        response = requests.get(url)
        test_image = Image.open(BytesIO(response.content))

        img = Image.open(webPath)
        img = cv2.resize(img,(384,400),3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        test_image = Image.fromarray(img)
         
    elif not "http" in str(url_input.get()) or not "https" in str(url_input.get()):
        photoPath=str(url_input.get())
        checKBackSlashPhoto=re.search("(\\\\)", photoPath)
        if checKBackSlashPhoto==True:
           photoPath = re.sub("(\\\\)", "/", photoPath)  
        test_image = Image.open(photoPath)

        img = cv2.imread(photoPath)
        img = cv2.resize(img,(384,400),3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        test_image = Image.fromarray(img)

   
      
    put_image = test_image.resize((400,400)) 
    test_image = test_image.resize((128,128))

    img = ImageTk.PhotoImage(put_image)
    pic = Label(htab1,image=img)
    pic.place(x=100,y=200)
    
    pic.image = img
    test_image = image_utils.img_to_array(test_image)/255
    test_image = np.expand_dims(test_image, axis=0)
    
 

    result = model.predict_proba(test_image)
    # print(result)
    # print(result[0][2])
    #print("Baseline: %.2f%% (%.2f%%)" % (result.mean()*100, result.std()*100))
  
    if "http" in str(url_input.get()) or "https" in str(url_input.get()):
        drawRectInWebImage(response)
    if not "http" in str(url_input.get()) or not "https" in str(url_input.get()):
        drawRectInPhotoImage(photoPath) 
        
    #Check percentage of white pixels and dhal and sambal color pixels
    #cv2.imwrite('croppedImage.jpg',objExtract)
    verifyColorFromImage=getColorFromImage(objExtract)
 
  
    predictedLabel = 'Unknown' 

    if result[0][4]>0.8:
       predictedLabel = 'Pizza'

    elif result[0][0]==np.max(result) and result[0][0]>0.7:   
       predictedLabel = 'Apple'

    elif result[0][2]==np.max(result) and  result[0][2]>0.6:  
        predictedLabel = 'French Fries'
    elif  verifyColorFromImage[3]>=5 and result[0][1]>=0.3:
         predictedLabel = 'Banana'
    elif verifyColorFromImage[0]>=2 and verifyColorFromImage[0]<=60 and verifyColorFromImage[1]<=60 and detectBlobs()>0:
         predictedLabel = 'Rice with Dhal'
    elif verifyColorFromImage[0]>=7 and verifyColorFromImage[2]>1 or result[0][3]>=0.65 and verifyColorFromImage[0]>=7: 
          predictedLabel = 'Idly'     
          
    elif result[0][6]==np.max(result) and result[0][6]>0.7:
        predictedLabel = 'Samosa'   
    
    
    
    out = Label(htab1, text='Predicted answer : ' +  predictedLabel, font=("Helvetica", 16))
    out.place(x=540,y=290)
    
    if predictedLabel !='Unknown':
       getArea(predictedLabel)
       getVolume(predictedLabel)
       openNutritionAnalysis(predictedLabel)
       
    
    


url_input = Entry(htab1,width = 100)
url_input.place(x=10,y=80)
btn = Button(htab1,bg='#A0522D',activebackground='#A0522D',fg='white',text="Detect Image", font=("Helvetica", 12), command=ScanImage)
btn.place(x=10,y=116)

head = Label(htab2, text="Validate between web image downloaded and photo captured from Smart Phone", font=("Serif",16))
head.place(x=5,y=20)

WPName = Label(htab2, text="Web Image File Path: ", font=("Serif",12))
WPName.place(x=45,y=560)
WPName_input = Entry(htab2,width = 160,textvariable="")
WPName_input.place(x=400,y=560)
PTName = Label(htab2, text="Photo Image File Path: ", font=("Serif",12))
PTName.place(x=45,y=580)
PTName_input = Entry(htab2,width = 160,textvariable="")
PTName_input.place(x=400,y=580)


global img1
global img2
img1=None
img2=None

def getPredictLabel(item,paramExtract,imgC):
    objExtract=paramExtract.copy()
    if "http" in str(item) or "https" in str(item):
        url  = item
        response = requests.get(url)
        test_image = Image.open(BytesIO(response.content))
    elif not "http" in str(item) or not "https" in str(item):
        photoPath=str(item) 
        checKBackSlash=re.search("(\\\\)", photoPath)
        if checKBackSlash==True:
         photoPath= re.sub("(\\\\)", "/", photoPath)

        test_image = Image.open(photoPath)
        img = cv2.imread(photoPath)
        img = cv2.resize(img,(384,400),3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        test_image = Image.fromarray(img)
    
    test_image=test_image.resize((128,128))
    test_image = image_utils.img_to_array(test_image)/255
    test_image = np.expand_dims(test_image, axis=0)

    result = model.predict_proba(test_image)
    verifyColorFromImage=getColorFromImageTest(imgC,objExtract)
    predictedLabel = 'Unknown' 

    if result[0][4]>0.8:
       predictedLabel = 'Pizza'
    elif result[0][0]==np.max(result) and result[0][0]>0.7:   
       predictedLabel = 'Apple'
    elif result[0][2]==np.max(result) and  result[0][2]>0.7:  
        predictedLabel = 'French Fries'
    elif verifyColorFromImage[0]<2 and verifyColorFromImage[3]>95 and result[0][1]>0.5:
         predictedLabel = 'Banana'
    elif verifyColorFromImage[0]>=2 and verifyColorFromImage[0]<=60 and verifyColorFromImage[1]>verifyColorFromImage[2]:
         predictedLabel = 'Rice with Dhal'
    elif verifyColorFromImage[0]>=2 and verifyColorFromImage[2]>verifyColorFromImage[1] and verifyColorFromImage[2]>1: 
          predictedLabel = 'Idly'    
    elif result[0][6]==np.max(result) and result[0][6]>0.7:
        predictedLabel = 'Samosa'  

    return predictedLabel 

def validateImageDifference():
    if str(WPName_input.get())!="" and str(PTName_input.get())!="":
        # print("TEST")
        # webImg = Image.open("E:/NutritionTracking/TestCases/Test_Images/WebApple.jpg")
        # photoImg = Image.open("E:/NutritionTracking/TestCases/Test_Images/PhotoApple.jpg)
        if not "http" in str(WPName_input.get()) or not "https" in str(WPName_input.get()):
          webPath=str(WPName_input.get())
          checKBackSlashWeb=re.search("(\\\\)", webPath)
          if checKBackSlashWeb==True:
           webPath= re.sub("(\\\\)", "/", webPath)
          
          webImg = Image.open(webPath)
          cv_webImg=cv2.imread(webPath)

        elif  "http" in str(WPName_input.get())  or  "https" in str(WPName_input.get()):
          response = requests.get(str(WPName_input.get()))
          webImg = Image.open(BytesIO(response.content))
          cv_webImg=cv2.imread(WPName_input.get())
        
        photoPath=str(PTName_input.get())
        checKBackSlashPhoto=re.search("(\\\\)", photoPath)
        if checKBackSlashPhoto==True:
           photoPath = re.sub("(\\\\)", "/", photoPath)

        cv_photoImg=cv2.imread(photoPath)
        photoImg = Image.open(photoPath)

        img1=ImageTk.PhotoImage(webImg)
        htab1.img1=img1
        img2=ImageTk.PhotoImage(photoImg)
        htab1.img2=img2
        WebImage = Label(htab2,image=img1)
        WebImage.place(x=5,y=50)
        PhotoImage = Label(htab2,image=img2)
        PhotoImage.place(x=500,y=100)
               
        imageDifference_excelWriter.writeTestImages(str(WPName_input.get()),str(PTName_input.get())  )
        
        items=checkImageSize(str(WPName_input.get()),str(PTName_input.get()))
        webLabel = Label(htab2,text=getPredictLabel(str(WPName_input.get()),items[0],cv_webImg),font=("Serif",16))
        webLabel.place(x=5,y=50)
        photoLabel= Label(htab2,text=getPredictLabel(str(PTName_input.get()),items[1],cv_photoImg),font=("Serif",16))
        imageDifference_excelWriter.writePredictedLabels(webLabel.cget("text"),photoLabel.cget("text"))
        photoLabel.place(x=500,y=100)
        plotGraphs(imageDifference_excelWriter)
        compareShapesBetweenImages()
        
        imageDifference_excelWriter.writeGrabcutImages()
        imageDifference_excelWriter.writeOverlayImage()
        imageDifference_excelWriter.writeHistograms()
        

        imageDifference_excelWriter.autoAdjustExcelSheet()

btn_ = Button(htab2,bg='#A0522D',activebackground='#A0522D',fg='white',text="Validate", font=("Helvetica", 12), command=validateImageDifference)
btn_.place(x=460,y=620)

foodLabelWindow.mainloop()

