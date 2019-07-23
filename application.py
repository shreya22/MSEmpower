from flask import Flask
from flask import json, jsonify, request
import ssl
import pymongo
from pymongo import MongoClient
from difflib import SequenceMatcher
app = Flask(__name__)

uri = "mongodb://hackathon2019:dp0O0VMaTwXU8PUwdYUxEgeu4UNOeVB5Ve7kU5zqV3tmfz3gNb1sc6VMY3HCjUcBC4Ubq3T9fXs6lJfMUfVIXg==@hackathon2019.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)

# Get the database name
db = client.EmpowerMS
db.authenticate(name="hackathon2019",password="dp0O0VMaTwXU8PUwdYUxEgeu4UNOeVB5Ve7kU5zqV3tmfz3gNb1sc6VMY3HCjUcBC4Ubq3T9fXs6lJfMUfVIXg==")

@app.route("/", methods = ['POST'])
def api_message():

    # Get the collection
    uniqueProblems = db.UniqueProblems

    # Get the new problem from post data
    newProblem = request.json

    maxSimilarityScore = 0
    maxSimilarProblemId = None

    # Iterating through every unique problem of the same tag and calculating the similarity score with each. 
    for uniqueProblem in uniqueProblems.find({"tag" : newProblem["tag"]}):
        similarityScore = similar(newProblem["problemStatement"], uniqueProblem["problemStatement"])
        if similarityScore > maxSimilarityScore:
            maxSimilarityScore = similarityScore
            maxSimilarProblemId = uniqueProblem["_id"]

    newUniqueProblemEntry = {
            "title" : newProblem["title"],
            "problemStatement" : newProblem["problemStatement"],
            "tag" : newProblem["tag"],
            "contactAsker" : newProblem["contactAsker"],
            "relatedProblems" : [],
            "solutionId" : ""
        }

    if maxSimilarityScore >= 0.8:
        # Do something
        uniqueProblem = uniqueProblems.find_one({"_id" : maxSimilarProblemId})

        updatedList = uniqueProblem["relatedProblems"]
        updatedList.append(newUniqueProblemEntry)

        uniqueProblems.update(
            {"_id" : maxSimilarProblemId},
            {
                "$set": {
                    "relatedProblems" : updatedList 
                }
            }
        )
        return jsonify(
            {
                "status" : "true",
                "message" : "updated the related doc"
            }
        )
        
    else:
        # Treat this as a new problem, make a new entry in the UniqueProblems DB
        uniqueProblems.insert(newUniqueProblemEntry)
        return jsonify(
            {
                "status" : "true",
                "message" : "New entry inserted in Unique Problems table"
            }
        )
    
    {
        "status" : "false",
        "message" : "Don't know what went wrong"
    }

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()