from zlapi import ZaloAPI
from zlapi.models import *

client = ZaloAPI('</>', '</>', imei="<imei>", session_cookies="<session_cookies>")

# Fetch your account information, as `User` objects
account_info = client.fetchAccountInfo()
account_info = account_info.profile

print("Account ID: {}".format(account_info.userId))
print("Account name: {}".format(account_info.displayName))


# Fetches a user information using phone number, as `User` objects
user_info = client.fetchPhoneNumber("<Phone Number>")

print("User ID: {}".format(user_info.uid))
print("User name: {}".format(user_info.display_name))


# Fetches a list of all friends you're currently chatting with, as `User` objects
users = client.fetchAllFriends()

print("Users' IDs: {}".format([user.userId for user in users]))
print("Users' names: {}".format([user.displayName for user in users]))


# If we have a user id, we can use `fetchUserInfo` to fetch a `User` object
user = client.fetchUserInfo("<user id>").changed_profiles["<user id>"]

print("User ID: {}".format(user.userId))
print("User name: {}".format(user.displayName))
print("User photo: {}".format(user.avatar))
print("Is user client's friend: {}".format(user.isFr))


# Fetches a list of the groups you're currently chatting with as `Group` object
groups = client.fetchAllGroups()

print("Groups: {}".format(groups))


# If we have a group id, we can use `fetchGroupInfo` to fetch a `Group` object
group = client.fetchGroupInfo("<group id>").gridInfoMap["<group id>"]

print("Group name: {}".format(group.name))
print("Group type: {}".format(group.type))