from flask import Blueprint,jsonify
from setting import MONGODB

content = Blueprint("content",__name__)

@content.route("/content_list",methods=["POST"])
def content_list():
    res_list = list(MONGODB.content.find({}))

    for index,content in enumerate(res_list):
        res_list[index]["_id"] = str(content.get("_id"))

    return jsonify(res_list)