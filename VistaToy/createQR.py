from setting import LT_URL,QRCODE_PATH,MONGODB
import time,hashlib,os
from uuid import uuid4
import requests

res = requests.get(LT_URL%("123"))



def create_qr(num):
    code_list = []
    for i in range(num):
        code = f"{time.time()}{uuid4()}{time.time()}"
        code_hash = hashlib.md5(code.encode("utf8")).hexdigest()
        print(code_hash)
        res = requests.get(LT_URL % (code_hash))
        qr_path = os.path.join(QRCODE_PATH,f"{code_hash}.jpg")
        with open(qr_path, "wb") as f:
            f.write(res.content)

        code_info = {"device_key":code_hash}
        code_list.append(code_info)
        time.sleep(0.2)

    MONGODB.devices.insert_many(code_list)

create_qr(10)



