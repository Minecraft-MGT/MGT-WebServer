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
DBM.load(f"mongodb+srv://{SETTINGS['mongodb']['username']}:{SETTINGS['mongodb']['password']}@{SETTINGS['mongodb']['path']}")

def request_user():
    if not "authtoken" in request.cookies: return None
    return DBM.Session.objects.get(id=request.cookies["authtoken"]).owner


#server side ticker (runs every 30 sec)
def server_ticker():
    lastdate = ""#datetime.today().strftime('%Y-%m-%d')
    while True:
        ctime = DBM.current_time()
        ctime_min = DBM.timeToDayMin(DBM.current_time())
        for ct in DBM.Task.objects():
            if ct.time_end() is not None:
                if ct.is_planned() and ct.time_end()<ctime_min and not ct.is_finished() and not ct.is_repeating():
                    ct.finish()
                    print(f"finished {ct.title}")
        
        cdate = datetime.today().strftime('%Y-%m-%d')
        if not cdate == lastdate:
            print(f"Datechange [{cdate}]")
            lastdate = cdate
            #automatically sort in tasks that are marked for that day
            for ct in DBM.Task.objects():
                if ct.ts_date == cdate or ct.ts_weekday == (date.today()+timedelta(days=1)).weekday():  #if task was planned for today
                    if ct.ts_time == "": #no startTime selected jet
                        for cowner in ct.owners:
                            success = ct.auto_sortin_perform(cowner)
                            print(f"autosortin(caused by dateChange) {ct.title} from {cowner} --> {success}")
        time.sleep(30)

t_mintick = Thread(target=server_ticker)
t_mintick.daemon = True
t_mintick.start()


#load flask server

app = Flask(__name__)

@app.route("/")
def ep_index():
    return render_template("start.html")


#tasking
@app.route("/user/toDay")
def ep_user_toDay():
    return render_template("toDay.html")

@app.route("/user/taskList")
def ep_user_taskList():
    return render_template("taskList.html")

@app.route("/user/taskView")
def ep_user_taskView():
    return render_template("taskView.html")




@app.route("/user/account")
def ep_user_accout():
    return render_template("accountManager.html")

@app.route("/login")
def ep_login():
    return render_template("login.html")

@app.route("/register")
def ep_register():
    return render_template("register.html")

@app.errorhandler(404)
def page_not_found(e):
    return f"{request.path} not found :C"

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

        if cmd == "tasking":
            taskid = args["taskID"]
            if taskid == "" and args["method"] == "setdata":     #create new task
                taskid = DBM.Task(title="No Title :(", content="", owners=[request_user()]).save().id

            task = DBM.Task.objects.get(id=taskid)
            if request_user() in task.owners:   #requestor has access to task
                method = args["method"]
                
                if method == "getspecdata":
                    response["values"] = {}
                    for name in args["fields"]:
                        response["values"][name] = task[name] if name in task else None
                    ok = True
                
                if method == "getdata":
                    response["data"] = task.data_representation()
                    ok = True
                
                if method == "setdata":
                    for k, v in args["values"].items():
                        task[k] = v
                    ok = True

                if method == "delete":
                    task.delete()
                    ok = True

                if method == "sortin":
                    ok, response["msg"] = task.auto_sortin_perform(request_user())
                
                if method == "throwOut":
                    task.day_throwout()
                    ok = True
                
                if method == "finish":
                    task.finish()
                    ok = True

                if method == "unfinish":
                    task.unfinish()
                    ok = True
                
                task.save()
            else:
                task["msg"] = "access denied"
        
        if cmd == "autofillup":
            for ct in request_user().get_tasks_sorted():
                ct.auto_sortin_perform(request_user())
            ok = True

        if cmd == "tasklist":
            if "fin" in args["spec"]:
                result = DBM.Task.objects(Q(owners=request_user()) & Q(finishtime__ne=-1))
            else:
                result = DBM.Task.objects(Q(owners=request_user()) & Q(finishtime=-1))
            def sorter(x):
                return -x.priority()
            result = sorted(result, key=sorter)
            response["list"] = []
            for csi in result:
                response["list"].append(csi.data_representation())
            ok = True
        
        if cmd == "task_today":
            #result = DBM.Task.objects(Q(owners=request_user()) |Q(ts_date=str(date.today())) | Q(ts_weekday=(date.today()+timedelta(days=1)).weekday()))
            result = request_user().currentday_tasks()
            response["list"] = []
            for entry in result:
                response["list"].append(entry.data_representation())
            ok = True

        if cmd == "session_username":
            token = args["token"]
            if DBM.Session.objects(id=token):
                response["name"] = DBM.Session.objects.get(id=token).owner.username
                ok = True


        if cmd == "user_login":
            if DBM.acc_check_access(args["username"], args["password"]):
                response ["authsync"] = str(DBM.session_create(DBM.Account.objects(username=args["username"])[0]))
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