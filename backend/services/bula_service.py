import redis
import uuid
import json
from datetime import datetime
from backend.services.user_service import UserService
from backend.utils.utils import Utils

class BulaService:
    bulasDB = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
    hashtagDB = redis.Redis(host="127.0.0.1", port=6379, db=2, decode_responses=True)

    def getAllBulas()-> dict:
        bulasDictionary: dict = {"bulas" : []}
        for bula in BulaService.bulasDB.scan_iter('*'):
            bulasDictionary['bulas'].append(bula)
        return bulasDictionary


    def getBulasIdOfUser(userId: str) -> json:
        if(UserService.usersDB.exists(userId)):
            user: json = json.loads(UserService.usersDB.get(userId))
            del user['password']
            return user
        return Utils.returnError("userId doesn't exist.")


    def createBula(userId: str, bulaText: str) -> None:
        bulaId = str(uuid.uuid1())
        bula = {
            'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'author': userId,
            'text': bulaText,
            'meows': [],
            'rebulas': []
        }
        BulaService.bulasDB.set(bulaId, json.dumps(bula))
        BulaService.addBulaIdToUser(userId=userId, bulaId=bulaId)
        BulaService.findHashtags(bulaText=bulaText, bulaId=bulaId)


    def addBulaIdToUser(userId: str, bulaId: str) -> None:
        user: json = json.loads(UserService.usersDB.get(userId))
        user['bulas'].append(bulaId)
        UserService.usersDB.set(userId, json.dumps(user))

    
    def findHashtags(bulaText: str, bulaId: str) -> None:
        words = bulaText.split()
        hashtags = []
        for word in words:
            if word.startswith("#"):
                hashtags.append(word)
        for hashtag in hashtags:
            if(BulaService.hashtagDB.exists(hashtag)):
                hashtagJson: json = json.loads(BulaService.hashtagDB.get(hashtag))
                hashtagJson['bulas'].append(bulaId)
                BulaService.hashtagDB.set(hashtag, json.dumps(hashtagJson))
            else:
                BulaService.hashtagDB.set(hashtag, json.dumps({'bulas': [bulaId]}))        

    
    def rebula(userId: str, bulaId: str) -> None:
        user: json = json.loads(UserService.usersDB.get(userId))
        user['bulas'].append(bulaId)
        UserService.usersDB.set(userId, json.dumps(user))
        
        bula: json = json.loads(BulaService.bulasDB.get(bulaId))
        bula['rebulas'].append(userId)
        BulaService.bulasDB.set(bulaId, json.dumps(bula))
        
        
    def getAllHashtags()-> dict:
        hashtagsDictionnary: dict = {"hashtags" : []}
        for hashtag in BulaService.hashtagDB.scan_iter('*'):
            hashtagsDictionnary['hashtags'].append(hashtag)
        return hashtagsDictionnary


    def getBulasOfHashtag(hashtag: str) -> str:
        if(BulaService.hashtagDB.exists(hashtag)):
            return json.loads(BulaService.hashtagDB.get(hashtag))
        else:
            return Utils.returnError("hashtag doesn't exist.")