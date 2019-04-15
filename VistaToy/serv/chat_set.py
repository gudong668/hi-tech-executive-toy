import json

from setting import REDISDB


# 存储 - 未读 和 离线 消息数量
def set_chat(to_user,from_user):
    my_world = REDISDB.get(to_user)
    if not my_world:
        setchat = {from_user: 1}
        setchat_json = json.dumps(setchat)
    else:
        my_world_dict = json.loads(my_world)
        if my_world_dict.get(from_user):
            my_world_dict[from_user] += 1
        else:
            my_world_dict[from_user] = 1

        setchat_json = json.dumps(my_world_dict)

    REDISDB.set(to_user,setchat_json)


# 读取未读 和 离线 所有消息数量
# app获取未读消息角标时
def get_chat_all(to_user):
    chat = REDISDB.get(to_user)  # None
    if not chat:
        return {"count":0}
    else:
        chat_dict = json.loads(chat)
        chat_dict["count"] = sum(chat_dict.values())

        return chat_dict


# 读取未读 和 离线 一个用户的消息数量
# 玩具收取一个人的未读消息数量时执行此函数
def get_chat(to_user,from_user):
    chat = REDISDB.get(to_user)  # None
    count = 0
    if not chat:
        return 0
    else:
        chat_dict = json.loads(chat)
        if chat_dict.get(from_user):
            # 收取完事儿之后，清空未读消息
            count = chat_dict.get(from_user)

        chat_dict[from_user] = 0
        REDISDB.set(to_user, json.dumps(chat_dict))
        return count






