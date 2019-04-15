import jieba

a = "我想听祖国祖国我们爱你"
b = "我想听祖国我爱你"

jieba.add_word("我想听")
jieba.add_word("请播放")
jieba.add_word("我要听")

# res = list(jieba.cut(a))
# res = list(jieba.cut(a))
res_search = list(jieba.cut_for_search(a))
res = list(jieba.cut_for_search(b))
print(res)
print(res_search)

# 0:我想听  1:祖国  2:我爱你  3:我们  4:爱  5:你
# 01(2,45)
# 01(345,45)

