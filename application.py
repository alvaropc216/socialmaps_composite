from flask import Flask, Response, request
import requests
from datetime import datetime
import json
from flask_cors import CORS


application = Flask(__name__)
CORS(application)

# TODO Redirect to API GATEWAY
GATEWAY_URL = "https://xx0lgzff6h.execute-api.us-east-1.amazonaws.com/test/"
#GATEWAY_URL = "http://127.0.0.1:8000/"
#LOCAL_URL = "http://127.0.0.1:5011/"

class DatetimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


@application.route("/feed", methods=["GET"])
def get_user_feed():
    # TODO: Get userID from token
    user_id = 6
    request_url = GATEWAY_URL + "users/{}/friends".format(user_id)
    user_friends = requests.get(request_url)
    friends_post_url = GATEWAY_URL + "posts?"
    id_list=[]
    for user in user_friends.json():
        id_list.append(str(user["data"]["data"]["id"]))
    friends_post_url = friends_post_url + "user_id=" + "&user_id=".join(id_list)
    friends_post_url = friends_post_url + "&order_by=post_time&DESC=TRUE"
    friends_posts = requests.get(friends_post_url)
    rsp = Response(json.dumps(friends_posts.json(), cls=DatetimeEncoder), status=200, content_type="application.json")
    return rsp


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5012)

