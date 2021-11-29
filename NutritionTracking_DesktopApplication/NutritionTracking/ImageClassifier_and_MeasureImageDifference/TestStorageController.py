import cv2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import numpy as np
import base64,time
import os 
import xlwt
import xlrd
from xlutils.copy import copy
from PIL import Image
from io import BytesIO
import re

cred = credentials.Certificate("smkitchendb-firebase-adminsdk-a8z9b-9634b4119e.json")
firebase_admin.initialize_app(cred,{'databaseURL':'https://smkitchendb.firebaseio.com'})


ref = db.reference('/')
grabcutImages_ref=ref.child('TestImages')
desktopImages_ref=ref.child('DesktopTestImages')

class TestStorage:
  def __init__(self, mobilePath, grabcutMobilePath,predictedLabel):
    self.mobilePath = mobilePath
    self.grabcutMobilePath = grabcutMobilePath
    self.predictedLabel = predictedLabel
    
  # convert image from dtype('uint8') to Base64
  def convertImageToBytes(self,category):
      if category=='grabcut':
       path=self.grabcutMobilePath
      elif category=='mobile':
        path=self.mobilePath

      img=cv2.imread(path)
      retval, buffer = cv2.imencode('.jpg', img)
      jpg_as_text = base64.b64encode(buffer).decode("utf-8")
      return jpg_as_text


  def saveTestDataToFireBase(self):
        mobileByteString=self.convertImageToBytes('mobile')
        grabcutByteString=self.convertImageToBytes('grabcut')
        testChildRef =grabcutImages_ref.push()
        testChildRef.set({
          "Mobile_Image":mobileByteString,
          "Mobile_GrabcutImage":grabcutByteString,
          "Predicted_Label":self.predictedLabel
        })
        # print(fName)
        print("Image is saved to Firebase")

    
# t1=TestStorage("E:/NutritionTracking/TestCases/Test_Images/WebApple.jpg","E:/NutritionTracking/TestCases/Test_Images/PhotoApple.jpg","Apple")
# t2=TestStorage("E:/NutritionTracking/TestCases/Test_Images/Banana81.jpg","E:/NutritionTracking/TestCases/Test_Images/Banana80.jpg","Banana")  


# t1.saveTestDataToFireBase()
# t2.saveTestDataToFireBase()
 
class TestImagesLoader:
   def __init__(self):
     self.snapshot = grabcutImages_ref.order_by_key().get()
   
   # convert image from Base64 to  dtype('uint8')
   def convertBytesToImage(self,val,timestamp,category):
    jpg_original = base64.b64decode(val)
    nparr = np.frombuffer(jpg_original, np.uint8)
    extractImg = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if category=="grabcut":
      filename="E:/TEST/Grabcut/"+timestamp+'.jpg'
    elif category=="mobile":
      filename="E:/TEST/Mobile/"+timestamp+'.jpg'

    cv2.imwrite(filename, extractImg)
   
   # Rename the name of the files in the test directory
   def renameFiles(self):
       for count, filename in enumerate(os.listdir("E:/TEST/Grabcut/")):   
          os.rename(os.path.join("E:/TEST/Grabcut/",filename), os.path.join("E:/TEST/Grabcut/","MobileGrabCut_" + str(count) + ".jpg")) 
       for count, filename in enumerate(os.listdir("E:/TEST/Mobile/")):  
        os.rename(os.path.join("E:/TEST/Mobile/",filename), os.path.join("E:/TEST/Mobile/","Mobile_" + str(count) + ".jpg")) 
   
   
   def loadImagesFromFirebase(self):
        #create folder if folder does not exist
        if not os.path.exists("E:/TEST"):
          path = os.path.join("E:/","TEST")
          os.mkdir(path)
        if not os.path.exists("E:/TEST/Grabcut/"):
          path = os.path.join("E:/TEST/","Grabcut")
          os.mkdir(path)
        if not os.path.exists("E:/TEST/Mobile/"):
          path = os.path.join("E:/TEST/","Mobile")
          os.mkdir(path)
        
        # First clear existing files in respective folders  and reload files
        if os.stat("E:/TEST/Grabcut/").st_size >0:
         for f in os.listdir("E:/TEST/Grabcut/"):
           os.remove(os.path.join("E:/TEST/Grabcut/", f))
  
        if os.stat("E:/TEST/Mobile/").st_size >0:
         for f in os.listdir("E:/TEST/Mobile/"):
           os.remove(os.path.join("E:/TEST/Mobile/", f))
        
        # Load image from Firebase into the local directory of pc
        for key, val in self.snapshot.items():
            # print(grabcutImages_ref.child(key).child("Predicted_Label").get() )

            mobileByteString=grabcutImages_ref.child(key).child("Mobile_Image").get() 
            grabcutByteString=grabcutImages_ref.child(key).child("Mobile_GrabcutImage").get() 
            timestamp=str(time.time())
            self.convertBytesToImage(mobileByteString,timestamp,"mobile")
            self.convertBytesToImage(grabcutByteString,timestamp,"grabcut")  
        print("All Mobile Images loaded in: "+"E:/TEST/Mobile/\n")
        print("All Cropped Mobiles Images loaded in: "+"E:/TEST/Grabcut/\n")



class ImageDifferenceExcelWriter:
  def __init__(self):
   rb = xlrd.open_workbook('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Testcase.xls')
   self.wb=copy(rb)
   self.wsheet = self.wb.get_sheet(0) 
   self.rsheet=rb.sheet_by_index(0)
   self.wHSVsheet = self.wb.get_sheet(1) 
   self.rHSVsheet=rb.sheet_by_index(1)
   self.wsheetColor = self.wb.get_sheet(2)
   self.rsheetColor=rb.sheet_by_index(2)  
   self.newIndex=None
   self.testCaseId=None
   self.testChildRef =desktopImages_ref.push()
   self.testChildRef.set({
          "TestCase_id":self.testCaseId,
          "Desktop_Image":" ",
          "Mobile_Image":" ",
          "Mobile_GrabcutImage":" ",
          "Desktop_GrabcutImage":" ",
          "Overlay_Image":" ",
          "Web_Histogram":" ",
          "Mobile_Histogram":" "
   })

   
  # Generate Testcase Id and generate new entry for test result
  def setRowIndex(self):
      self.newIndex= self.rsheet.nrows
      rowId=str(self.newIndex)
      d=0
      print("Row Index: "+rowId)
      for c in rowId:
          if c.isdigit():
              d=d+1
      if d==1:
        self.testCaseId="T00"+str(rowId)
      elif d==2:  
        self.testCaseId="T0"+str(rowId)
      elif d==3:  
        self.testCaseId="T"+str(rowId)

      self.wsheet.write(self.newIndex,0,self.testCaseId)
      self.wHSVsheet.write(self.newIndex,0,self.testCaseId)
      self.wsheetColor.write(self.newIndex,0,self.testCaseId)
  
  # Save Images as bytestring in Firebase
  def saveTestImageToFirebase(self,path,category):
      img=cv2.imread(path)
      img=cv2.resize(img,(384,400),3)
      retval, buffer = cv2.imencode('.jpg', img)
      jpg_as_text = base64.b64encode(buffer).decode("utf-8")
      if category=='desktop_image':
        self.testChildRef.update({
            'Desktop_Image': jpg_as_text
        })
      elif category=='mobile_image':
        self.testChildRef.update({
            'Mobile_Image': jpg_as_text
        })
      elif category=='grabcutDesktop_image':
        self.testChildRef.update({
            'Desktop_GrabcutImage': jpg_as_text
        })
      elif category=='grabcutMobile_image':
        self.testChildRef.update({
            'Mobile_GrabcutImage': jpg_as_text
        })
      elif category=='overlay_image':
        self.testChildRef.update({
            'Overlay_Image': jpg_as_text
        })
      elif category=='web_histogram':
        self.testChildRef.update({
            'Web_Histogram': jpg_as_text
        })
      elif category=='mobile_histogram':
        self.testChildRef.update({
            'Mobile_Histogram': jpg_as_text
        })
        
  # store bitmaps in Ms Excel workbook
  def writeTestImages(self,webPath,mobilePath):
    wwPath='E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Images'
    mmPath='E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Images'
    if self.rsheet.nrows>1:
        wdirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Images")
        mdirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Images")
        iw=len(wdirs)-1
        im=len(mdirs)-1
        iw-=1
        im-=1
        for rowIndex in range(1,self.rsheet.nrows):
          testCaseId=str(self.rsheet.cell(rowIndex,0).value)
         
          wPath=os.path.join(wwPath,wdirs[iw])
          wImg=Image.open(wPath)
          wArr = BytesIO()
          wImg.save(wArr, format='bmp')
          self.wsheet.insert_bitmap_data(wArr.getvalue(),rowIndex,1)
          wImg.close() 
          iw-=1 
              
        
          mPath=os.path.join(mmPath,mdirs[im])
          mImg=Image.open(mPath)
          mArr = BytesIO()
          mImg.save(mArr, format='bmp')
          self.wsheet.insert_bitmap_data(mArr.getvalue(),rowIndex,3)
          mImg.close()
          im-=1

          if iw<0 and im<0:
            break 
        self.wb.save('Testcase.xls')  
               
    self.saveTestImageToFirebase(webPath,"desktop_image")               
    webimg = Image.open(webPath)
    webimg = webimg.resize((round(webimg.size[0]/30), round(webimg.size[1]/30)))
    wimage_parts = webimg.split()
    rw = wimage_parts[0]
    gw = wimage_parts[1]
    bw = wimage_parts[2]
    webimg = Image.merge("RGB", (rw, gw, bw))

  
    filename="Web_Image"+self.testCaseId+'.jpg'
    filepath=os.path.join(wwPath,filename)
    webimg.save(filepath)

    webArr = BytesIO()
    webimg.save(webArr, format='bmp')
    self.wsheet.insert_bitmap_data(webArr.getvalue(),self.newIndex,1)
    self.wb.save('Testcase.xls')
    webimg.close()

    self.saveTestImageToFirebase(mobilePath,"mobile_image") 
    mobileimg = Image.open(mobilePath)
    mobileimg = mobileimg.resize( (round(mobileimg.size[0]/30),round(mobileimg.size[1]/30) ))
    mimage_parts = mobileimg.split()
    rm = mimage_parts[0]
    gm = mimage_parts[1]
    bm = mimage_parts[2]
    mobileimg = Image.merge("RGB", (rm, gm, bm))

    filename="Mobile_Image"+self.testCaseId+'.jpg'
    filepath=os.path.join(mmPath,filename)
    mobileimg.save(filepath)



    mobileArr = BytesIO()
    mobileimg.save(mobileArr, format='bmp')
    self.wsheet.insert_bitmap_data(mobileArr.getvalue(),self.newIndex,3)
    self.wb.save('Testcase.xls')
    mobileimg.close()

 
  def writeGrabcutImages(self):
    webpath=os.path.join('E:\\NutritionTracking\\TestCases\\ImageProcessed_Pictures\\Grabcut','WebImageCropped.png')
    mobilepath=os.path.join('E:\\NutritionTracking\\TestCases\\ImageProcessed_Pictures\\Grabcut','PhotoImageCropped.png')
    wwPath="E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Grabcut"
    mmPath="E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Grabcut"
    if self.rsheet.nrows>1:
        wdirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Grabcut")
        mdirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Grabcut")
        iw=len(wdirs)-1
        im=len(mdirs)-1
        iw-=1
        im-=1
        for rowIndex in range(1,self.rsheet.nrows):
          testCaseId=str(self.rsheet.cell(rowIndex,0).value)
         
          wPath=os.path.join(wwPath,wdirs[iw])
          wImg=Image.open(wPath)
          wArr = BytesIO()
          wImg.save(wArr, format='bmp')
          self.wsheet.insert_bitmap_data(wArr.getvalue(),rowIndex,10)
          wImg.close() 
          iw-=1 
          
             
          
          mPath=os.path.join(mmPath,mdirs[im])
          mImg=Image.open(mPath)
          mArr = BytesIO()
          mImg.save(mArr, format='bmp')
          self.wsheet.insert_bitmap_data(mArr.getvalue(),rowIndex,11)
          mImg.close()
          im-=1

          if iw<0 and im<0:
            break
        self.wb.save('Testcase.xls')  
               
    self.saveTestImageToFirebase(webpath,"grabcutDesktop_image")               
    webimg = Image.open(webpath)
    webimg = webimg.resize((round(webimg.size[0]/30), round(webimg.size[1]/30)))
    wimage_parts = webimg.split()
    rw = wimage_parts[0]
    gw = wimage_parts[1]
    bw = wimage_parts[2]
    webimg = Image.merge("RGB", (rw, gw, bw))

    
    filename="Web_ImageGrabcut"+self.testCaseId+'.png'
    filepath=os.path.join(wwPath,filename)
    webimg.save(filepath)

    webArr = BytesIO()
    webimg.save(webArr, format='bmp')
    self.wsheet.insert_bitmap_data(webArr.getvalue(),self.newIndex,10)
    self.wb.save('Testcase.xls')
    webimg.close()

    self.saveTestImageToFirebase(webpath,"grabcutMobile_image") 
    mobileimg = Image.open(mobilepath)
    mobileimg = mobileimg.resize( (round(mobileimg.size[0]/30),round(mobileimg.size[1]/30) ))
    mimage_parts = mobileimg.split()
    rm = mimage_parts[0]
    gm = mimage_parts[1]
    bm = mimage_parts[2]

    mobileimg = Image.merge("RGB", (rm, gm, bm))
    filename="Mobile_ImageGrabcut"+self.testCaseId+'.png'
    filepath=os.path.join(mmPath,filename)
    mobileimg.save(filepath)
    mobileArr = BytesIO()
    mobileimg.save(mobileArr, format='bmp')
    self.wsheet.insert_bitmap_data(mobileArr.getvalue(),self.newIndex,11)
    self.wb.save('Testcase.xls')
    mobileimg.close()

  def writeHistograms(self):
    webpath=os.path.join('E:\\NutritionTracking\\TestCases\\ImageProcessed_Pictures\\Histograms','WebImageHistogram.jpg')
    mobilepath=os.path.join('E:\\NutritionTracking\\TestCases\\ImageProcessed_Pictures\\Histograms','PhotoImageHistogram.jpg')
    wwPath="E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Histograms"
    mmPath="E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Histograms"
    if self.rsheet.nrows>1:      
        wdirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Histograms")
        mdirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Histograms")
        iw=len(wdirs)-1
        im=len(mdirs)-1
        iw-=1
        im-=1
        for rowIndex in range(1,self.rsheet.nrows):
          testCaseId=str(self.rsheet.cell(rowIndex,0).value)
         
          wPath=os.path.join(wwPath,wdirs[iw])
          wImg=Image.open(wPath)
          wArr = BytesIO()
          wImg.save(wArr, format='bmp')
          self.wHSVsheet.insert_bitmap_data(wArr.getvalue(),rowIndex,3)
          wImg.close() 
          iw-=1 
            
       
          mPath=os.path.join(mmPath,mdirs[im])
          mImg=Image.open(mPath)
          mArr = BytesIO()
          mImg.save(mArr, format='bmp')
          self.wHSVsheet.insert_bitmap_data(mArr.getvalue(),rowIndex,4)
          mImg.close()
          im-=1

          if iw<0 and im<0:
            break
        self.wb.save('Testcase.xls')  
               
    self.saveTestImageToFirebase(webpath,"web_histogram")               
    webimg = Image.open(webpath)
    webimg = webimg.resize((round(webimg.size[0]/10), round(webimg.size[1]/30)))
    wimage_parts = webimg.split()
    rw = wimage_parts[0]
    gw = wimage_parts[1]
    bw = wimage_parts[2]
    webimg = Image.merge("RGB", (rw, gw, bw))

    
    filename="Web_ImageHistogram"+self.testCaseId+'.png'
    filepath=os.path.join(wwPath,filename)
    webimg.save(filepath)

    webArr = BytesIO()
    webimg.save(webArr, format='bmp')
    self.wHSVsheet.insert_bitmap_data(webArr.getvalue(),self.newIndex,3)
    self.wb.save('Testcase.xls')
    webimg.close()

    self.saveTestImageToFirebase(mobilepath,"mobile_histogram")  
    mobileimg = Image.open(mobilepath)
    mobileimg = mobileimg.resize( (round(mobileimg.size[0]/10),round(mobileimg.size[1]/30) ))
    mimage_parts = mobileimg.split()
    rm = mimage_parts[0]
    gm = mimage_parts[1]
    bm = mimage_parts[2]
   
    mobileimg = Image.merge("RGB", (rm, gm, bm))

    filename="Mobile_ImageHistogram"+self.testCaseId+'.png'
    filepath=os.path.join(mmPath,filename)
    mobileimg.save(filepath)



    mobileArr = BytesIO()
    mobileimg.save(mobileArr, format='bmp')
    self.wHSVsheet.insert_bitmap_data(mobileArr.getvalue(),self.newIndex,4)
    self.wb.save('Testcase.xls')
    mobileimg.close()

  def writeOverlayImage(self):
    ovlpath=os.path.join('E:\\NutritionTracking\\TestCases\\ImageProcessed_Pictures\\Overlay\\Overlapped Images.png')
    ovl_Path='E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Overlay_Images'
   
    if self.rsheet.nrows>1:      
        ovldirs=os.listdir("E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Overlay_Images")
        iovl=len(ovldirs)-1
        iovl-=1
        for rowIndex in range(1,self.rsheet.nrows):
          testCaseId=str(self.rsheet.cell(rowIndex,0).value)
         
        
      
          ovlPath=os.path.join(ovl_Path,ovldirs[iovl])
          ovlImg=Image.open(ovlPath)
          ovlArr = BytesIO()
          ovlImg.save(ovlArr, format='bmp')
          self.wsheet.insert_bitmap_data(ovlArr.getvalue(),rowIndex,12)
          ovlImg.close() 
          iovl-=1 
          
          if iovl<0:
            break
        self.wb.save('Testcase.xls')  
               
    self.saveTestImageToFirebase(ovlpath,"overlay_image")               
    ovlImg = Image.open(ovlpath)
    ovlImg = ovlImg.resize((round(ovlImg.size[0]/30), round(ovlImg.size[1]/30)))
    ovlimage_parts = ovlImg.split()
    rl = ovlimage_parts[0]
    gl = ovlimage_parts[1]
    bl = ovlimage_parts[2]
    ovlImg = Image.merge("RGB", (rl, gl, bl))

 
    filename="overlayed_Image"+self.testCaseId+'.png'
    filepath=os.path.join(ovl_Path,filename)
    ovlImg.save(filepath)

    ovlArr = BytesIO()
    ovlImg.save(ovlArr, format='bmp')
    self.wsheet.insert_bitmap_data(ovlArr.getvalue(),self.newIndex,12)
    self.wb.save('Testcase.xls')
    ovlImg.close()
  
  # Store label in Ms Excel Workbook
  def writePredictedLabels(self,webPrediction,mobilePrediction):
    self.wsheet.write(self.newIndex,2,webPrediction)
    self.wsheet.write(self.newIndex,4,mobilePrediction)
    self.wb.save('Testcase.xls')
  
  # Store HSV Range and Feedback in Ms Excel Workbook
  def writeHSVRange(self,hsvRange,hsvFeedback):
    self.wHSVsheet.write(self.newIndex,1,hsvRange)
    self.wHSVsheet.write(self.newIndex,2,hsvFeedback)
    self.wb.save('Testcase.xls')
  
  # Store Number of pixels for web image and mobile image,size difference as well as its feedback
  def writeSizeComparison(self,web_size,mobile_size,size_diff,size_feedback):
    self.wsheet.write(self.newIndex,6,web_size)
    self.wsheet.write(self.newIndex,7,mobile_size)
    self.wsheet.write(self.newIndex,8,size_diff)
    self.wsheet.write(self.newIndex,9,size_feedback)
    self.wb.save('Testcase.xls')
  
  # Store number of pixels for curries and banana with respective to color
  def writePixelsOfColor(self,riceColor,dhalColor,sambalColor,bananaColor):
    self.wsheetColor.write(self.newIndex,1,riceColor)
    self.wsheetColor.write(self.newIndex,2,dhalColor)
    self.wsheetColor.write(self.newIndex,3,sambalColor)
    self.wsheetColor.write(self.newIndex,4,bananaColor)
    self.wb.save('Testcase.xls')

  def writePercentOfColor(self,percent_riceColor,percent_DhalColor,percent_SambalColor,percent_BananaColor):
    self.wsheetColor.write(self.newIndex,5,percent_riceColor)
    self.wsheetColor.write(self.newIndex,6,percent_DhalColor)
    self.wsheetColor.write(self.newIndex,7,percent_SambalColor)
    self.wsheetColor.write(self.newIndex,8,percent_BananaColor)
    self.wb.save('Testcase.xls')
  
  # Two methods erase image files in Directory
  def clearBackupPhase1(self):
      if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Grabcut').st_size >0:
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Grabcut'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Grabcut', f))
      
      if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Grabcut').st_size >0: 
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Grabcut'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Grabcut', f))

      if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Images').st_size >0: 
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Images'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Images', f))
      
      if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Images').st_size >0: 
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Images'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Images', f))



      print("Backup images Phase 1 are all Cleared")
  
  def clearBackupPhase2(self):
    if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Overlay_Images').st_size >0: 
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Overlay_Images'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Overlay_Images', f))

    if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Histograms').st_size >0: 
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Histograms'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Web_Histograms', f))

    if os.stat('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Histograms').st_size >0: 
        for f in os.listdir('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Histograms'):
          os.remove(os.path.join('E:\\NutritionTracking\\ImageClassifier_and_MeasureImageDifference\\Backup_images\\Mobile_Histograms', f))

    print("Backup images Phase 2 are all Cleared")
  
  # Erase record for the worksheets in Excel Workbook
  def clearExcelSheets(self):
    endIndex=self.rsheet.nrows
    self.wsheet._cell_overwrite_ok = True
    self.wsheetColor._cell_overwrite_ok = True
    # print(self.wsheet._cell_overwrite_ok )
    # print(self.wsheetColor._cell_overwrite_ok )
    if self.rsheet.nrows>1:
        for rowIndex in range(1,endIndex):
          #print(self.rsheetColor.cell(rowIndex,0))
          self.wsheet.write(rowIndex,0,"")
          self.wsheet.write(rowIndex,1,"")
          self.wsheet.write(rowIndex,2,"")
          self.wsheet.write(rowIndex,3,"")
          self.wsheet.write(rowIndex,4,"")
          self.wsheet.write(rowIndex,5,"")
          self.wsheet.write(rowIndex,5,"")
          self.wsheet.write(rowIndex,6,"")
          self.wsheet.write(rowIndex,7,"")
          self.wsheet.write(rowIndex,8,"")
          self.wsheet.write(rowIndex,9,"")
          self.wsheet.write(rowIndex,10,"")
          self.wsheet.write(rowIndex,11,"")
          self.wsheet.write(rowIndex,12,"")
          
      

          self.wHSVsheet.write(rowIndex,0,"")
          self.wHSVsheet.write(rowIndex,1,"")
          self.wHSVsheet.write(rowIndex,2,"")
          self.wHSVsheet.write(rowIndex,3,"") 
          self.wHSVsheet.write(rowIndex,4,"")
           


          self.wsheetColor.write(rowIndex,0,"")
          self.wsheetColor.write(rowIndex,1,"")
          self.wsheetColor.write(rowIndex,2,"")
          self.wsheetColor.write(rowIndex,3,"")
          self.wsheetColor.write(rowIndex,4,"")
          self.wsheetColor.write(rowIndex,5,"")
          self.wsheetColor.write(rowIndex,6,"")
          self.wsheetColor.write(rowIndex,7,"")
          self.wsheetColor.write(rowIndex,8,"")

    desktopImages_ref.delete()  
    self.wsheet._cell_overwrite_ok = False
    self.wsheetColor._cell_overwrite_ok = False
    self.wb.save('Testcase.xls')
    print("Excel Sheets are cleared")


  # Adjust width of columns and height of rows
  def autoAdjustExcelSheet(self):
    #print(self.wsheet.row(self.newIndex).height)
    endIndex1=self.rsheet.nrows
    endIndex2=self.rHSVsheet.nrows
    if self.rsheet.nrows>1:
        for rowIndex in range(1,endIndex1):
          self.wsheet.row(rowIndex).height_mismatch = True
          self.wsheet.row(rowIndex).height=4500

    if self.rHSVsheet.nrows>1:
        for rowIndex in range(1,endIndex2):
          self.wHSVsheet.row(rowIndex).height_mismatch = True
          self.wHSVsheet.row(rowIndex).height=5500
          #print(self.wsheet.row(rowIndex).height)

    self.wsheet.col(0).width=15220
    self.wsheet.col(1).width=15220
    self.wsheet.col(2).width=15220
    self.wsheet.col(3).width=15220
    self.wsheet.col(4).width=15220
    self.wsheet.col(5).width=15220
    self.wsheet.col(6).width=15220
    self.wsheet.col(7).width=15220
    self.wsheet.col(8).width=15220
    self.wsheet.col(9).width=15220
    self.wsheet.col(10).width=15220
    self.wsheet.col(11).width=15220
    self.wsheet.col(12).width=15220
    

    self.wHSVsheet.col(0).width=15220
    self.wHSVsheet.col(1).width=15220
    self.wHSVsheet.col(2).width=15220
    self.wHSVsheet.col(3).width=60000
    self.wHSVsheet.col(4).width=60000
    

    self.wsheetColor.col(0).width=17220
    self.wsheetColor.col(1).width=17220
    self.wsheetColor.col(2).width=17220
    self.wsheetColor.col(3).width=17220
    self.wsheetColor.col(4).width=17220
    self.wsheetColor.col(5).width=17220
    self.wsheetColor.col(6).width=17220
    self.wsheetColor.col(7).width=17220
    self.wsheetColor.col(8).width=17220

    self.wsheet.row(self.newIndex).height_mismatch = True
    self.wsheet.row(self.newIndex).height=4500
    self.wHSVsheet.row(self.newIndex).height_mismatch = True
    self.wHSVsheet.row(self.newIndex).height=5500
    self.wb.save('Testcase.xls') 
  
