from flask import Flask,render_template,url_for,flash,redirect,jsonify

from pymongo import MongoClient
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import json
from bson import ObjectId
import os




app=Flask(__name__)

client = MongoClient("mongodb+srv://group3:000Georgian@cluster0.woppbjn.mongodb.net/?retryWrites=true&w=majority")
db = client["HousingDB"]
collection = db["HS"]
reportDF =""
house_count =""
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/inserttodb")
def inserttodb():

    with open('export.json', 'r') as f:
        datatoimport = json.load(f)
    
    collection.drop()
    result = collection.insert_many(datatoimport)
    return render_template('DBreport.html',total = len(result.inserted_ids))

@app.route("/readfromcsv")
def readfromcsv():
    global reportDF
    global house_count
    columns = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD',
           'TAX', 'PTRATIO', 'B', 'LSTAT', 'MEDV']
    df = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/housing/housing.data',
                 delim_whitespace=True, names=columns)
    bins = [0, 20, 30, 40, 50, 100]
    df['Age Range'] = pd.cut(df['AGE'], bins=bins, labels=['<20', '20-30', '30-40', '40-50', '>50'])
    dfToInsert = df[["Age Range","MEDV"]]
    house_count = dfToInsert.groupby('Age Range')['MEDV'].count()
    reportDF  = pd.DataFrame({'Age Range': house_count.index, 'Number of Houses': house_count.values})
    dfToInsert.to_json("export.json",orient='records')

    return render_template('index.html',data=dfToInsert.to_html(columns=['Age Range', 'MEDV'], index=False) )
@app.route("/barchart")
def barchart():
    fig1 = px.bar(reportDF,x="Age Range",y="Number of Houses",color="Age Range",barmode='group')

    return render_template("report.html",plot =fig1.to_html())
@app.route("/piechart")
def piechart():
    
    fig2 = px.pie(reportDF,values='Number of Houses', names='Age Range')

    return render_template("report.html", plot =fig2.to_html())
    
# api part :
#user can send following input as range :
# 1 for '<20',2 for '20-30',3 for '30-40',5 for '40-50',6 for '>50'
@app.route('/api1/<range>')
def api1(range):
    list1=['<20', '20-30', '30-40', '40-50', '>50']
    r = list1[int(range)-1]
    searchResult = collection.find({"Age Range": r})
    documents = []
    for res in searchResult:
        res['_id'] = str(res['_id'])
        documents.append(res)

    return jsonify({'Docs_in_Ranges': documents})

if __name__=="__main__":
    

    app.run(debug=True)

