from accounts.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("shopping-firebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'databaseURL'
})

def createUserNode(name, id, profile_image, role):
    firebase_admin.get_app()
    root = db.reference('users')
    root.child('user_'+str(id)).set({
        'id':str(id),
        'name': name,
        'profilePic': profile_image,
        'role':role,
        'isOnline':False
    })

def updateUserNode(first_name, last_name, id, profile_image):
    firebase_admin.get_app()
    root = db.reference('users')
    root.child('user_'+str(id)).update({
        'name': first_name+' ' +last_name,
        'profile_image': profile_image
    })

def updateOnlineStatus(id, status):
    firebase_admin.get_app()
    root = db.reference('users')
    root.child('user_'+str(id)).update({
        'isOnline': status
    })

def deleteUserNode(id):
    firebase_admin.get_app()
    root = db.reference('users')
    root.child('user_'+str(id)).delete()
