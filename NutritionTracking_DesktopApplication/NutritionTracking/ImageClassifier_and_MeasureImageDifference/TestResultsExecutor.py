from TestStorageController import ImageDifferenceExcelWriter,TestImagesLoader

# Erase Directory and worksheets in MS Excel Workbook
def clearDesktopTestCase():
    excelWriter=ImageDifferenceExcelWriter()
    excelWriter.clearBackupPhase1()
    excelWriter.clearBackupPhase2()
    excelWriter.clearExcelSheets()


# Load images from Firebase to Desktop
def loadImagesToDesktop():
    testImagesLoader=TestImagesLoader()
    testImagesLoader.loadImagesFromFirebase() 
    testImagesLoader.renameFiles()

clearDesktopTestCase()
#loadImagesToDesktop()