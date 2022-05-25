import os, yaml, time
import traceback
from flask import Flask, render_template, redirect, Markup, request, jsonify, escape, session
import json
from datetime import date, timedelta, datetime
from mongoengine.queryset.visitor import Q
from threading import Thread
import DBM

# Load settings
SETTINGS = {}
settingsPath = "config.yml"

if os.path.exists(settingsPath):
    with open(settingsPath, "r") as settingsFile: SETTINGS = yaml.safe_load(settingsFile)
    print("Loaded Settings:")
    print(SETTINGS)
else:
    print("could not load settings from \""+settingsPath+"\"...")


# Connect to database
DBM.load(f"{SETTINGS['mongodb']['method']}://{SETTINGS['mongodb']['username']}:{SETTINGS['mongodb']['password']}@{SETTINGS['mongodb']['path']}")

def render_mesage(text, error=False):
    return render_template("customMessage.html", PY_MSG=text, PY_ERROR=error)

def request_user():
    if not "authtoken" in request.cookies: return None
    return DBM.Session.objects.get(id=request.cookies["authtoken"]).owner



app = Flask(__name__)

@app.route("/")
def ep_index():
    return render_template("start.html")

@app.route("/user/team")
def ep_team():
    return render_mesage("Hier gibts noch nichts!")

@app.route("/user/acc")
def ep_account():
    return render_mesage("Hier gibts noch nichts... :D")

@app.route("/login")
def ep_login():
    return render_template("login.html")

@app.route("/register")
def ep_register():
    return render_template("register.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_mesage(f"Zu deiner Anfrage mit dem Pfad \"{request.path}\" konntent wir leider keine Ergebnisse finden!", error=True)

@app.before_request
def catcher():
    #parse json
    if request.path == "/api/":
        try:
            jsonObj = json.loads(request.data)
            def escape_json_values(obj):
                if isinstance(obj, dict):
                    cres = {}
                    for k, v in obj.items():
                        cres[k] = escape_json_values(v)
                    return cres
                elif isinstance(obj, list):
                    cres = []
                    for cv in obj:
                        cres.append(escape_json_values(cv))
                    return cres
                else:
                    return str(escape(obj))
            jsonObj = escape_json_values(jsonObj)
            request.data = json.dumps(jsonObj)
        except json.JSONDecodeError:
            print(f"Error parsing json \"{request.data.decode()}\"")
            return "Error processing Json...", 400
    
    if request.path.startswith("/user/") and not "authtoken" in request.cookies:
        return redirect("/login")
            

@app.route("/api/", methods=["POST"])
def ep_api():
    global orders, opened, baught
    rqd:json = json.loads(request.data)
    ok = False
    response = {}
    try:
        cmd:str = rqd["cmd"]
        args:dict = rqd["args"]
        

        if cmd == "user_login":
            if DBM.acc_check_access(args["username"], args["password"]):
                response ["authsync"] = str(DBM.session_create(DBM.Account.objects(username=args["username"])[0]))
                response ["usernamesync"] = str(args["username"])
                ok = True

        if cmd == "user_register":
            if not DBM.Account.objects(username=args["username"]):
                DBM.acc_create(args["username"], args["password"])
                response["msg"] = "successfully created account"
                ok = True
            else:
                response["msg"] = "username alerady taken"

        if cmd == "errorcatch":
            message = args["error"]
            print(f"""
            
            ---Clientside Error Occured---
            ErrorMessage: {message}

            """)
            ok = False

        if cmd == "ping":
            response["msg"] = "pong"
            response["mirror"] = args["mirror"]
            ok = True

    except KeyError as e:
        ok = False
        return "missing argument ("+str(e)+")", 400
    except Exception:
        ok = False
        response["fatal"] = "You screwed up!"
        print(traceback.format_exc())
    

    response["ok"] = ok
    print(f"API-FETCH[{request_user().username if request_user() != None else ''}] {rqd} --> {response}")
    return jsonify(response)


#start flask debug server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=25565, debug=True, threaded=True)