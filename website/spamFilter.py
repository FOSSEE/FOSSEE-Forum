# coding=utf-8

import openpyxl
import numpy as np
from cleanText import cleanString
from collections import Counter
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix, f1_score

# Get the original dataset
def store():

    workBookOld = openpyxl.load_workbook('DataSet.xlsx')
    dataSheetOld = workBookOld['Data set']

    xData = []
    yData = []

    rows = dataSheetOld.max_row

    for i in range(2, rows+1):

        if (str(dataSheetOld.cell(row = i, column = 2).value) != 'None'):
            if (str(dataSheetOld.cell(row = i, column = 2).value) == '1'):
                for k in range(4):
                    yData.append(1)
                    xData.append(cleanString(dataSheetOld.cell(row = i, column = 1).value.encode('utf-8')))

    for i in range(2, rows+1):

        if (str(dataSheetOld.cell(row = i, column = 2).value) != 'None'):
            if (str(dataSheetOld.cell(row = i, column = 2).value) == '0'):
                yData.append(0)
                xData.append(cleanString(dataSheetOld.cell(row = i, column = 1).value.encode('utf-8')))
        
    
    return xData, yData

    # # NOTE: to train data on the entire dataset, simply return xData and yData
    # # Splitting the data like this is to obtain test cases and calculate the F-score of the learning algorithm
    # xTrain, xTest, yTrain, yTest = train_test_split(xData, yData, test_size = 0.2, random_state = 42)
    # return xTrain, xTest, yTrain, yTest

# make a dictionary of the most common words
def makeDictionary(xData):

    all_words = []
    
    for mail in xData:

        words = mail.split()
        all_words.extend(words)
    
    dictionary = Counter(all_words)
    dictionary = dictionary.most_common(3000)
    return dictionary

# construct a feature vector for each mail
def extractFeatures(xData, dictionary):
    
    featureMatrix = np.zeros((len(xData), 3000))
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

def train():

    print("Training spam filter...")

    # Create training data
    xTrain, yTrain = store()

    global trainDictionary
    trainDictionary = makeDictionary(xTrain)

    # Create feature vector and matrix for yTrain and xTrain
    yTrainMatrix = np.zeros(len(yTrain))
    for i in range(len(yTrain)):
        if (yTrain[i] == 1):
            yTrainMatrix[i] = 1

    xTrainMatrix = extractFeatures(xTrain, trainDictionary)

    # Training SVM classifier
    global model
    model = model.fit(xTrainMatrix, yTrainMatrix)

# Calculating the F-score
def calcFScore(xTest, yTest):

    xTestMatrix = extractFeatures(xTest, trainDictionary)
    yTestMatrix = np.zeros(len(yTest))
    for i in range(len(yTest)):
        if (yTest[i] == 1):
            yTestMatrix[i] = 1

    result = model.predict(xTestMatrix)
    matrix = confusion_matrix(yTestMatrix, result)

    fScore = f1_score(yTestMatrix, result, pos_label = 0)
    return fScore, matrix

# Test new data for Spam
def predict(emailBody):

    # featureMatrix = extractFeatures([cleanString(emailBody)], trainDictionary)
    # result = model.predict(featureMatrix)
    # print("Predicting...")

    # if (1 in result):
    #     return "Spam"
    # else:
    #     return "Not Spam"
    return "Not Spam"

# model = LinearSVC()
# trainDictionary = {}
# train()