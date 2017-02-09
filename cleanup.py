import nltk
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
import pprint

reg = re.compile(r'[A-Z]+')

dance = open("DanceDomainText.txt")

arpabet = nltk.corpus.cmudict.dict()

weightDict = {}
pronDict = {}
countDict = {}
wordDict = {}
wordWeightDict = {}
diphoneDict = {}
sentenceWeight = {}
words = []
lowered = []
barephonelist = []
englishPhones = []
nums = ['0', '1', '2']

#convert text to sentences
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
data=dance.read()

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


# give each word a weight which is the sum of all phonemes' weights within that word
def getWordWeights(pronDict):
    for word in pronDict:
        weightsum = 0
        for phone in pronDict[word]:
            weightsum += weightDict[phone]
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


getWordsFromText(sentenceList)
unCapitalize(wordDict)
createProns(pronDict)
stripPhones(pronDict)
getPhoneWeights(barephonelist)
getEnglishPhones(weightDict)
getDiphones(englishPhones)
getWordWeights(pronDict)
getSentenceWeight(sentenceList)


with open('DanceDomainSentences.txt', 'w') as f:
    sortedsw = sorted(sentenceWeight.items(), key=lambda x: x[1], reverse=True)
    for i in sortedsw:
        f.write(str(i) + "\n")