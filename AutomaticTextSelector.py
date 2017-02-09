import nltk
import sys
import operator
import os
import re
reload(sys)
# sys.setdefaultencoding('utf-8')

# Replace with your own text. Note: If using nltk corpora, set openfile to eg. nltk.corpus.gutenberg.raw('file.txt')
# and also replace line 28 with
# data = openfile
openfile = open("wikifile.txt")



arpabet = nltk.corpus.cmudict.dict()
weightDict = {}
pronDict = {}
countDict = {}
wordDict = {}
wordWeightDict = {}
diphoneDict = {}
diphoneDictRare = {}
sentenceWeight = {}
words = []
lowered = []
barephonelist = []
englishPhones = []
outputlist = []
nums = ['0', '1', '2']
probability = 0

#convert text to sentences
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
data=openfile.read()
data = unicode(data, errors='replace')

sentenceList = tokenizer.tokenize(data)

#convert sentences to words and add them to wordDict, with a freq count for each word in the overall text
def getWordsFromText(sentenceList):
    for sentence in sentenceList:
        words = nltk.word_tokenize(sentence)
        for word in words:
            if word in wordDict:
                wordDict[word] += 1
            else:
                wordDict[word] = 1

# convert words to lowercase
def unCapitalize(wordDict):
    for word in wordDict:
        low_word = word.lower()
        lowered.append(low_word)

# get the pronunciations of words from cmudict and format them in pronDict as word: pronunciation
def createProns(pronDict):
    for word in lowered:
        if word in pronDict:
            pass
        else:
            if word in arpabet:
                pronDict[word] = arpabet[word][0]
            else:
                pass

# strip the phones of their u' tags and tone numbers, put them in their own list as well as updating the pronDict
def stripPhones(pronDict):
    for word in pronDict:
        newList = []
        for phone in pronDict[word]:
            if len(phone) < 3:
                phone = phone.lower()
                phone = str(phone)
                barephonelist.append(phone)
                newList.append(phone)
            elif phone[2] in nums:
                phone = phone.lower()
                phone = str(phone)
                phone = phone[0:2]
                barephonelist.append(phone)
                newList.append(phone)
        pronDict[word] = newList

# give frequency weights to the bare phonemes as they appear in the text
def getPhoneWeights(barephonelist):
    for phoneme in barephonelist:
            if phoneme in weightDict:
                weightDict[phoneme] += 1
            else:
                weightDict[phoneme] = 1

#create diphones -- this remains unused
def getEnglishPhones(weightDict):
    for phone in weightDict.keys():
        englishPhones.append(phone)

def getDiphones(englishPhones):
    for phone in englishPhones:
        for phone2 in englishPhones:
            diphone = (phone, phone2)
            if diphone in diphoneDict:
                diphoneDict[diphone] += 1
            else:
                diphoneDict[diphone] = 1

# get the total number of each diphone in the diphoneDict.
def getDiphoneWeights(pronDict):
    for word in pronDict:
        for phone in pronDict[word]:
            pos = pronDict[word].index(phone)
            try:
                diphone = (pronDict[word][pos], pronDict[word][pos + 1])
                diphoneDict[diphone] += 1
            except IndexError:
                pass

# Give each diphone a weight between 0 and 1, such that rarer diphones have higher weights. This will allow for a wider
# range of diphones in the final output sentence list. Append to diphoneDictRare.
def decayWeights(diphoneDict):
    sorted_dict = sorted(diphoneDict.items(), key=operator.itemgetter(1), reverse=True)
    newRange = float(1 - 0)
    oldMin = 0
    oldMax = len(sorted_dict)
    oldRange = float(len(sorted_dict) - 0)
    scaleFactor = newRange / oldRange
    newList = []
    for oldValue in sorted_dict:
        newValue = ((sorted_dict.index(oldValue) - oldMin) * scaleFactor) + 0
        newList.append((oldValue, newValue))

    for i in newList:
        diphone = i[0][0]
        diphoneRareWeight = i[1]

        diphoneDictRare[diphone] = (diphoneDict[diphone], diphoneRareWeight)

def getSentenceWeightRare(pronDict, sentenceList):
    # inputList = [sentence for sentence in sentenceList if sentence not in outputlist]
    # try:
    #     sentenceList.remove([x for x in sentenceList if x in outputlist])
    # except ValueError:
    #     pass
    for sentence in sentenceList:
        # print sentence
        words = nltk.word_tokenize(sentence)
        wordsum = 0.
        sentsum = 0.
        diphoneWeight = 0.
        diphone = ""
        for word in words:
            try:
                small = word.lower()
                for phone in pronDict[word]:
                    pos = pronDict[word].index(phone)
                    try:
                        diphone = (pronDict[word][pos], pronDict[word][pos + 1])
                        diphoneWeight = diphoneDictRare[diphone][0]
                        diphoneMultiplier = diphoneDictRare[diphone][1]
                        diphoneWeight *= diphoneMultiplier
                        wordsum += diphoneWeight
                        diphoneDictRare[diphone] = (diphoneWeight/2,diphoneMultiplier/2)
                        # print word + str(pronDict[word])
                        # print diphone
                        # # print diphoneWeight
                        # print "wordsum: " + str(wordsum)
                    except IndexError:
                        sentsum += wordsum
                        wordsum = 0
                        continue
            except KeyError:
                pass
        newsentsum = sentsum / len(sentence)
        # print "sentsum: " + str(sentsum)
        # print "newsentsum: " + str(newsentsum)
        if len(sentence) <= 75:
            sentenceWeight[sentence] = newsentsum
        else:
            sentenceWeight[sentence] = 0
    dictList = sorted(sentenceWeight.items(), key=lambda x: x[1], reverse=True)
    outputlist.append(dictList[0:600])
    # print sentenceList
    # print dictList


# give each word a weight which is the sum of all phonemes' weights within that word
def getWordWeights(pronDict):
    for word in pronDict:
        weightsum = 0
        for phone in pronDict[word]:
            weightsum += weightDict[phone]
        wordWeightDict[word] = weightsum

def getWordWeightsDiphones(pronDict):
    for word in pronDict:
        weightsum = 0
        for phone in pronDict[word]:
            pos = pronDict[word].index(phone)
            try:
                diphone = (pronDict[word][pos], pronDict[word][pos + 1])
                weightsum += diphoneDict[diphone]
            except IndexError:
                pass
        wordWeightDict[word] = weightsum


# give each sentence a final weight. The weight is a sum of its words' weights, divided by the length of the sentence.
# Pass if the word is not in nltk's dictionary.

def getSentenceWeight(sentenceList):
    for sentence in sentenceList:
        words = nltk.word_tokenize(sentence)
        sentsum = 0
        for word in words:
            try:
                small = word.lower()
                sentsum += wordWeightDict[small]
            except KeyError:
                pass
        sentsum /= len(sentence)
        sentenceWeight[sentence] = sentsum





#####
#
# All of these should be run in this order to create a list of sentences sorted by score.
# To base the word weights on single phonemes, use getWordWeights.
# To base the word weights on diphones, use getWordWeightsDiphones.
# Do not use both getwWordWeights and getWordWeightsDiphones.
# NB: This script scores based on the most common phonemes/diphones in the text you supply. It is not representative of
# all English phoneme/diphone occurrences, nor does it take into account all English words. As such, this is a domain-
# specific tool. Hypothetically, if run on a very large and English-representative corpus, it would be more representative
# of the language's features.
#
#####

getWordsFromText(sentenceList)
unCapitalize(wordDict)
createProns(pronDict)
stripPhones(pronDict)
getPhoneWeights(barephonelist)
getEnglishPhones(weightDict)
getDiphones(englishPhones)
getDiphoneWeights(pronDict)
decayWeights(diphoneDict)

getSentenceWeightRare(pronDict,sentenceList)
print outputlist
print sentenceList
# getWordWeights(pronDict)
# getWordWeightsDiphones(pronDict)
# getSentenceWeight(sentenceList)


with open('wikiout.txt', 'a+') as f:
    sortedsw = sorted(sentenceWeight.items(), key=lambda x: x[1], reverse=True)
    for i in outputlist:
        f.write(str(i) + os.linesep)