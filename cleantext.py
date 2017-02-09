import re
import os
from HTMLParser import HTMLParser

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

string = ""
i = 0
log = open('wiki_00', 'r+')
raw = log.read()

for j in raw.splitlines():
    i +=1
    print i
    cleanhtml(raw)

with open('clean.txt', 'w') as f:
    f.write(raw + '\n')
