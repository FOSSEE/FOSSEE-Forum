# coding=utf-8

import openpyxl
import numpy as np
from cleanText import cleanString
from collections import Counter
from sklearn.svm import NuSVC
from sklearn.metrics import confusion_matrix, f1_score

# Get the original dataset
def store():

    workBookOld = openpyxl.load_workbook('DataSet.xlsx')
    dataSheetOld = workBookOld['Data set']

    xData = []
    yData = []

    rows = dataSheetOld.max_row

    for i in range(400, rows+1):

        if (str(dataSheetOld.cell(row = i+2, column = 2).value) != 'None'):
            xData.append(cleanString((dataSheetOld.cell(row = i+2, column = 1).value).encode('utf-8')))
            if (str(dataSheetOld.cell(row = i+2, column = 2).value) == "Spam"):
                yData.append(1)
            else:
                yData.append(0)

    return xData, yData

# make a dictionary of the most common words
def makeDictionary(xData):

    all_words = []
    
    for mail in xData:

        words = mail.split()
        all_words.extend(words)

    dictionary = Counter(all_words)
    list_to_remove = dictionary.keys()
    
    for item in list_to_remove:
        if item.isalpha() == False: 
            del dictionary[item]
        elif len(item) == 1:
            del dictionary[item]

    dictionary = dictionary.most_common(2000)
    return dictionary

# construct a feature vector for each mail
def extractFeatures(xData, dictionary):
    
    featureMatrix = np.zeros((len(xData), 2000))
    emailId = 0

    for mail in xData:
        for word in mail:
            wordId = 0
            for i,d in enumerate(dictionary):
                if (d[0] == word):
                    wordId = i
                    featureMatrix[emailId, wordId] = mail.count(word)
        emailId += 1

    return featureMatrix

# Create training data
xTrain, yTrain = store()
trainDictionary = makeDictionary(xTrain)

# Create feature vector and matrix for yTrain and xTrain
yTrainMatrix = np.zeros(len(yTrain))
for i in range(len(yTrain)):
    if (yTrain[i] == 1):
        yTrainMatrix[i] = 1

xTrainMatrix = extractFeatures(xTrain, trainDictionary)

# Training SVM classifier
model = NuSVC(nu=0.07, class_weight='balanced')
model.fit(xTrainMatrix, yTrainMatrix)

# Test new data for Spam
def predict(emailBody):

    featureMatrix = extractFeatures([cleanString(emailBody)], trainDictionary)
    result = model.predict(featureMatrix)

    if (1 in result):
        return "Spam"
    else:
        return "Not Spam"