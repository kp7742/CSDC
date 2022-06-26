from flask import Flask, session, render_template
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import DecisionTreeClassificationModel

# SPARK SETUP
spark = SparkSession.builder.getOrCreate()
corona_dt = DecisionTreeClassificationModel.load("model/corona_dt_model")

# SERVER SETUP
app = Flask(__name__)
app.config['SERVER_HOST'] = '127.0.0.1'
app.config['SERVER_PORT'] = 8282
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

CORS(app)
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")


# Bot Sockets
@socketio.on('greetings')
def greetings(req):
    return {
        "len": 2,
        "msgs": [
            {"msg": "Hey there!", "delay": 800},
            {"msg": "Welcome, Send \"Start\" to Go", "delay": 1500}
        ]
    }


@socketio.on('chatbot')
def chatbot(req):
    answer = req['Answer']

    # Start
    if answer == "Start" and not session.get("started"):
        session["started"] = True
        return {
            "len": 2,
            "msgs": [
                {
                    'question': "Let's start your diagnosis",
                    'hasbuttons': False
                },
                {
                    'question': "Do you have cough?",
                    'hasbuttons': True,
                    'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                }
            ]
        }
    elif answer == "Restart" and session.get("started"):
        session["Q1"] = False
        session["Q2"] = False
        session["Q3"] = False
        session["Q4"] = False
        session["Q5"] = False
        session["Q6"] = False
        session["Q7"] = False
        return {
            "len": 1,
            "msgs": [
                {
                    'question': "Do you have cough?",
                    'hasbuttons': True,
                    'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                }
            ]
        }
    # Question 1
    elif not session.get("Q1"):
        if answer == "Yes":
            session["Q1_answer"] = 1
        elif answer == "No":
            session["Q1_answer"] = 0

        if session.get("Q1_answer") is not None:
            session["Q1"] = True
            return {
                "len": 1,
                "msgs": [
                    {
                        'question': "Do you have fever?",
                        'hasbuttons': True,
                        'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                    }
                ]
            }
    # Question 2
    elif not session.get("Q2"):
        if answer == "Yes":
            session["Q2_answer"] = 1
        elif answer == "No":
            session["Q2_answer"] = 0

        if session.get("Q2_answer") is not None:
            session["Q2"] = True
            return {
                "len": 1,
                "msgs": [
                    {
                        'question': "Do you have sore throat?",
                        'hasbuttons': True,
                        'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                    }
                ]
            }
    # Question 3
    elif not session.get("Q3"):
        if answer == "Yes":
            session["Q3_answer"] = 1
        elif answer == "No":
            session["Q3_answer"] = 0

        if session.get("Q3_answer") is not None:
            session["Q3"] = True
            return {
                "len": 1,
                "msgs": [
                    {
                        'question': "Do you having shortness of breath?",
                        'hasbuttons': True,
                        'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                    }
                ]
            }
    # Question 4
    elif not session.get("Q4"):
        if answer == "Yes":
            session["Q4_answer"] = 1
        elif answer == "No":
            session["Q4_answer"] = 0

        if session.get("Q4_answer") is not None:
            session["Q4"] = True
            return {
                "len": 1,
                "msgs": [
                    {
                        'question': "Do you have headache?",
                        'hasbuttons': True,
                        'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                    }
                ]
            }
    # Question 5
    elif not session.get("Q5"):
        if answer == "Yes":
            session["Q5_answer"] = 1
        elif answer == "No":
            session["Q5_answer"] = 0

        if session.get("Q5_answer") is not None:
            session["Q5"] = True
            return {
                "len": 1,
                "msgs": [
                    {
                        'question': "Is your age above 60?",
                        'hasbuttons': True,
                        'buttons': [{'name': "Yes", 'value': "Yes"}, {'name': "No", 'value': "No"}]
                    }
                ]
            }
    # Question 6
    elif not session.get("Q6"):
        if answer == "Yes":
            session["Q6_answer"] = 1
        elif answer == "No":
            session["Q6_answer"] = 0

        if session.get("Q6_answer") is not None:
            session["Q6"] = True
            return {
                "len": 1,
                "msgs": [
                    {
                        'question': "What is your gender?",
                        'hasbuttons': True,
                        'buttons': [{'name': "Male", 'value': "Male"}, {'name': "Female", 'value': "Female"}]
                    }
                ]
            }
    # Question 7
    elif not session.get("Q7"):
        if answer == "Male":
            session["Q7_answer"] = 1
        elif answer == "Female":
            session["Q7_answer"] = 0

        if session.get("Q7_answer") is not None:
            session["Q7"] = True

            # Predicting corona
            inputs = (session["Q1_answer"], session["Q2_answer"], session["Q3_answer"], session["Q4_answer"],
                      session["Q5_answer"], session["Q6_answer"], session["Q7_answer"])

            columns = ["cough", "fever", "sore_throat", "shortness_of_breath", "head_ache", "age_60_and_above",
                       "gender"]

            df = spark.sparkContext.parallelize([inputs]).toDF(columns)
            data = VectorAssembler(inputCols=df.columns, outputCol='features').transform(df)
            prediction = corona_dt.transform(data)
            have_corona = bool(prediction.select("prediction").collect()[0][0])

            if have_corona:
                return {
                    "len": 3,
                    "msgs": [
                        {
                            'question': f"Corona Prediction: {have_corona}",
                            'hasbuttons': False
                        },
                        {
                            'question': "You are corona positive",
                            'hasbuttons': False
                        },
                        {
                            'question': "Please consult your nearest doctor",
                            'hasbuttons': False
                        }
                    ]
                }
            else:
                return {
                    "len": 4,
                    "msgs": [
                        {
                            'question': f"Corona Prediction: {have_corona}",
                            'hasbuttons': False
                        },
                        {
                            'question': "You are safe",
                            'hasbuttons': False
                        },
                        {
                            'question': "Thank you for checking",
                            'hasbuttons': False
                        },
                        {
                            'question': "Want to start again?",
                            'hasbuttons': True,
                            'buttons': [{'name': "Yes", 'value': "Restart"}, {'name': "No", 'value': "No"}]
                        }
                    ]
                }

    # Default response
    return {
        "len": 1,
        "msgs": [
            {
                'question': "Invalid Response, Try Again!",
                'hasbuttons': False
            }
        ]
    }


# APIS
@app.route('/')
def home():
    return render_template('index.html')


# SERVER RUN
if __name__ == '__main__':
    print('[=>] Corona Chatbot Server Starting')
    print('[=>] Loading Models...')
    print('[=>] Spark Session:', spark)
    print('[=>] Model:', corona_dt.toDebugString)
    print('[=>] Model Has', corona_dt.numFeatures, 'Features')
    print('[=>] Model Has', corona_dt.numClasses, 'Classes')
    print('[=>] Service Running on http://{}:{}'.format(app.config['SERVER_HOST'], app.config['SERVER_PORT']))
    socketio.run(app, host=app.config['SERVER_HOST'], port=app.config['SERVER_PORT'], debug=True)
