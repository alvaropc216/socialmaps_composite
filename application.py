from flask import Flask, Response, request
import requests
from datetime import datetime
import json
from flask_cors import CORS

application = Flask(__name__)
CORS(application)

# TODO Redirect to API GATEWAY
GATEWAY_URL = "https://xx0lgzff6h.execute-api.us-east-1.amazonaws.com/test/"
# GATEWAY_URL = "http://52.23.170.133:5011/"
#GATEWAY_URL = "http://127.0.0.1:8000/"
#LOCAL_URL = "http://127.0.0.1:5011/"

class DatetimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


@application.route("/feed/<user_id>", methods=["GET"])
def get_user_feed(user_id):
    # TODO: Get userID from token
    # user_id = 6
    request_url = GATEWAY_URL + "users/{}/friends".format(user_id)
    user_friends = requests.get(request_url)
    friends_post_url = GATEWAY_URL + "posts?"
    id_list=[]
    for user in user_friends.json():
        id_list.append(str(user["data"]["data"]["id"]))
    friends_post_url = friends_post_url + "user_id=" + "&user_id=".join(id_list)
    friends_post_url = friends_post_url + "&order_by=post_time&DESC=TRUE"
    print("Here", friends_post_url)
    friends_posts = requests.get(friends_post_url)
    print(friends_posts)
    # rsp = Response(json.dumps(friends_posts.json(), cls=DatetimeEncoder), status=200, content_type="application.json")
    return "ok"


# Deleting user *(delete all uder-friend pairs, delete user posts and delete user)
@application.route("/users/<id>/remove", methods=["DELETE"])
def delete_user(id):
    user_id =  id
    # check if the user exists:
    try:
        request_url = GATEWAY_URL + "users/{}".format(user_id)
        msg = requests.get(request_url)
        if msg.text == "Invalid ID":
            return "User does not exist", 500
    except requests.exceptions.RequestException as e:
        return e 

    # delete from feeds db
    request_url = GATEWAY_URL + "users/{}/posts".format(user_id)
    get_all_posts = requests.get(request_url)
    for posts in get_all_posts.json():
        try:
            print(posts["data"])
            print(GATEWAY_URL + "posts/{}".format(posts["data"]["post_id"]))
            res = requests.delete(GATEWAY_URL + "posts/{}".format(posts["data"]["post_id"]))
            print(res)
        except requests.exceptions.RequestException as e:
            return e
    
    # request_url = GATEWAY_URL + "users/{}/friends".format(user_id)
    # get_all_friends = requests.get(request_url).json()
    # for user in get_all_friends:
    #     friend_id = user["data"]["data"]["user_id"]
    #     try:
    #         res = requests.delete(
    #             GATEWAY_URL + "users/{}/friends".format(user_id), 
    #             data = {
    #                 "id": friend_id
    #             }
    #         )

    #     except requests.exceptions.RequestException as e:
    #         return e

    
    # delete all friends and the user
    request_url = GATEWAY_URL + "users/{}".format(user_id)
    try:
        res = requests.delete(request_url)
    except requests.exceptions.RequestException as e:
        return e
    
    return "Deleted user", 200

 
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5012, debug=True)

