#!/usr/bin/python3

# Eudic词典生词本导出生成指定格式


from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import random
import time
import pyttsx3

def words(file):
    soup=BeautifulSoup(open(file),'html.parser')
    soup=soup.body.div.table.tbody.find_all('tr')
    words=[]
    for i in soup[1:]:
        words.append(i.find_all('td')[1].contents[0])
    return words

class Eudic:
    def __init__(self,word):
        #header=UserAgent(use_cache_server=False,cache=False,verify_ssl=False)
        #ua = UserAgent(verify_ssl=False)
        #eudic=requests.get("https://dict.eudic.net/dicts/en/"+word, header.firefox).text
        eudic=requests.get("https://dict.eudic.net/dicts/en/"+word).text
        self.soup=BeautifulSoup(eudic,'html.parser')

    def getPhonetic(self):
        soup=self.soup.find_all(class_='Phonitic')
        phonetic=[]
        for i in soup:
            phonetic.append(i.contents[0])
        return phonetic

    def getExp(self):
        expFCChild=self.soup.find_all(id='ExpFCChild')[0]
        condition=0 # 默认情况0

        # 共三种情况，前两种condition=0
        soup=expFCChild.find_all(class_='exp')
        if soup==[]:
            soup=[expFCChild.ol]
        if soup ==[None]:
            try:
                soup=expFCChild.contents[3:5]
                soup[0]=soup[0].contents[0]
            except:
                soup=expFCChild.contents[2:4]
                soup[0]=soup[0].contents[0]
            condition=1

        exp=[]
        if condition==0:
            for i in soup:
                expp=i.find_all('li')
                if expp !=[]:
                    for j in expp:
                        if len(j.contents) ==2:
                            j.contents[0]=j.contents[0].contents[0]
                        exp.append(j.contents)
                else:
                    exp.append(i.contents)
        if condition==1:
            exp.append(soup)
        return exp

    def getSample(self):
        expFCChild=self.soup.find_all(id='ExpLJChild')[0]
        soup=expFCChild.find_all(class_='lj_item')
        sample=[]
        for i in soup:
            s=''
            for j in range(len(i.div.p.contents)):
                try:
                    i.div.p.contents[j]=i.div.p.contents[j].contents[0]
                except:pass
                s+=str(i.div.p.contents[j])
            chinese=i.div.find_all('p')[1].contents[0]
            sample.append([s,chinese])
        return sample


class BingDict:
    def __init__(self,word):
        bingDict=requests.get("https://www.bing.com/dict/search?q="+word).text
        self.soup=BeautifulSoup(bingDict,'html.parser')

    def getWord(self):
        return self.soup.find('div',id='headword').get_text()

    def getPhonetic(self):
        phonetic=[]
        sound_US=self.soup.find_all(class_='hd_prUS b_primtxt') # 美式读音
        sound_UK=self.soup.find_all(class_='hd_pr b_primtxt')   # 英式读音
        phonetic.append(self.__extractPhonetic(sound_US[0].contents[0]))
        phonetic.append(self.__extractPhonetic(sound_UK[0].contents[0]))
        return phonetic

    def getDefinition(self):
        soup=self.soup.find_all(class_='qdef')[0].ul
        pos=soup.find_all(class_='pos')    # 所有词性
        for i in range(len(pos)):
            pos[i]=pos[i].contents[0]
            
        def_b_regtxt=soup.find_all(class_='def b_regtxt')  # 所有释义
        for i in range(len(def_b_regtxt)):
            def_b_regtxt[i]=def_b_regtxt[i].contents[0].contents[0]
        return pos,def_b_regtxt

    def getSentences(self):
        sentence=[]
        soup=self.soup.find_all(id='sentenceSeg')[0].find_all(class_='se_li')
        for sen in soup:
            sen_en=sen.find_all(class_='sen_en b_regtxt')[0]
            sen_cn=sen.find_all(class_='sen_cn b_regtxt')[0]
            sentence.append([self.__extractTextOfSentence(sen_en),self.__extractTextOfSentence(sen_cn)])
        return sentence
        
    def __extractTextOfSentence(self,sentence):
        sentence=sentence.find_all()
        text=''
        for i in sentence:
            text+=str(i.contents[0])
        return text

    def __extractPhonetic(self,phonetic):
        begin=phonetic.find('[')
        end=phonetic.rfind(']')
        return phonetic[begin:end+1]


# 语音播报，用于结束时
def alert():
    words='Glossary generated successfully!'
    engine=pyttsx3.init()
    rate=engine.getProperty('rate')
    engine.setProperty('rate',rate-50)
    engine.say(words)
    engine.runAndWait()

def eudicWrite():
    f=open("words.txt","w+")
    for i in words("Print.html")[100:160]:
        eudic=Eudic(i);

        # 写入单词
        f.write(i)
        try:
        #if 1==1:
            # 写入音标
            phonetic=eudic.getPhonetic()
            for j in phonetic:
                f.write(j)
            f.write("\n")

            # 写入释义
            exp=eudic.getExp()
            for j in exp:
                f.write("\t")
                for k in j:
                    f.write(str(k))
                f.write("\n")

            # 写入例句
            sample=eudic.getSample()
            sentence=random.choice(sample)
            f.write("\te.g. "+str(sentence[0])+"\n")
            f.write("\t    "+str(sentence[1]))
        except Exception as e:
            print(e)
        f.write("\n")
        time.sleep(random.randint(1,10))
    f.close()

def bingDictWrite():
    print('From lines:',end=' ')
    firstWord=int(input())
    print('To:',end=' ')
    lastestWord=int(input())

    f=open("words.txt","w+")
    for i in words("Print.html")[firstWord:lastestWord]:
        print(i)
        bingDict=BingDict(i)
        try:
            # 写入单词
            word=bingDict.getWord()
            f.write(word)

            # 写入音标
            phonetic=bingDict.getPhonetic()
            for j in phonetic:
                f.write(j)
            # 如果查找单词与原单词不同，写入原单词
            if word != i:
                f.write(' From: '+i)
            f.write("\n")

            # 写入释义
            exp=bingDict.getDefinition()
            sentenceCount=len(exp[0])
            for i in range(len(exp[0])):
                if exp[0][i]=='网络':
                    exp[0][i]='Web.'
                f.write('\t'+exp[0][i]+' '+exp[1][i]+'\n')

            # 写入例句
            if sentenceCount==1:
                sentenceCount=2
            sentences=random.sample(bingDict.getSentences(),sentenceCount-1)
            for sentence in sentences:
                f.write("\te.g. "+str(sentence[0])+"\n")
                f.write("\t    "+str(sentence[1])+'\n')
        except Exception as e:
            f.write('\n')
            print(e)
        time.sleep(random.randint(1,5))
    f.close()


if __name__ == '__main__':
    bingDictWrite()
    alert()
