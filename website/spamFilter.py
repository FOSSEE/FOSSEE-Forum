# coding=utf-8

import os
import openpyxl
import joblib
import numpy as np
from cleanText import cleanString
from collections import Counter
from sklearn.svm import LinearSVC, NuSVC, SVC

# Get the original dataset
def store():

    workBookOld = openpyxl.load_workbook('DataSet.xlsx')
    dataSheetOld = workBookOld['Data set']

    xData = []
    yData = []

    rows = dataSheetOld.max_row

    for i in range(2, rows+1):

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
    
    featureMatrix = np.zeros((len(xData), len(dictionary)))
    emailId = 0

    for mail in xData:
        for word in mail:
            wordId = 0
            for i,d in enumerate(dictionary):
                if (d[0] == word):
                    wordId = i
                    featureMatrix[emailId, wordId] = mail.count(word)
                    break
        emailId += 1

    return featureMatrix

# Test new data for Spam
def predict(emailBody):

    featureMatrix = extractFeatures([cleanString(emailBody)], trainDictionary)
    result = model.predict(featureMatrix)

    if (1 in result):
        return "Spam"
    else:
        return "Not Spam"

try:

    # Create training data
    xTrain, yTrain = store()
    
    model = joblib.load('training_model.pkl')
    trainDictionary = makeDictionary(xTrain)

except:

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
    model = LinearSVC(class_weight='balanced')
    model = model.fit(xTrainMatrix, yTrainMatrix)

    joblib.dump(model, "training_model.pkl")

print(predict("python print error DWSIM laptop fossee python python please help"))