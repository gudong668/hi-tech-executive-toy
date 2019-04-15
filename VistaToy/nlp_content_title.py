import time

from setting import NLP,MONGODB

start = time.time()
content_list = MONGODB.content.find()
for content in content_list:
    res = NLP.simnet(content.get("title"), "我想听小哈巴狗")
    time.sleep(0.0899)
    print(res)
    if res.get("score") >= 0.65:
        print(content)
        break

print(time.time() - start)


