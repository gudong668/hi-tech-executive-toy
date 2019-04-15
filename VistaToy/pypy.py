from pypinyin import lazy_pinyin,TONE2,TONE3,TONE
a = "淡淡的忧伤"
b = "蛋蛋的忧伤"
c = "音乐"

text = lazy_pinyin(c,style=TONE)
print(text)



