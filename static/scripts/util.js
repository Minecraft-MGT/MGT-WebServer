
CLIENTINFO = {}


async function acc_register(username, password){
    let payload = {
        "cmd": "user_register",
        "args": {"username": username, "password": password}
    }
    let response = await apiRequest(payload);
    alert(response["msg"]);
    return response;
}

async function acc_login(username, password){
    let payload = {
        "cmd": "user_login",
        "args": {"username": username, "password": password}
    }
    let response = await apiRequest(payload);
    if(response["ok"]){
        saveAuthToken(response["authsync"]);
        document.location.pathname = "/user/account";
    }else{
        alert("login failed...")
    }
    navbarUpdate();
    return response;
}

async function currentUsername(){
    let payload = {
        "cmd": "session_username",
        "args": {"token": localStorage.getItem("authtoken")}
    }
    let response = await apiRequest(payload);
    if(response["ok"]){
        return response["name"];
    }else{
        return "";
    }
}


function authView(){
    console.log("LS: "+localStorage.getItem("authtoken"))
    console.log("CK: "+getCookie("authtoken"))
}

function saveAuthToken(token){
    localStorage.setItem("authtoken", token);
    loadAuthToken();
}

function loadAuthToken(){
    if(localStorage.getItem("authtoken")!=null)
        setCookie("authtoken", localStorage.getItem("authtoken"));
    else
        deleteCookie("authtoken");
}

function resetAuthToken(){
    localStorage.removeItem("authtoken");
    loadAuthToken();
}

function loggedIn(){
    return localStorage.getItem("authtoken")!=null
}

//load token to cookies when lading the page

window.addEventListener("load", ()=>{
    loadAuthToken();
    navbarUpdate();

    if(!loggedIn())
        for(ce of $(".requirelogin").get()){
            $(ce).attr("disabled", "disabled");
            $(ce).removeAttr("href");
            ce.style.color = "rgb(100, 100, 100)";
        }

})

function getCurrentTime(){
    var today = new Date();
    return today.getHours() + ":" + today.getMinutes();
}

async function navbarUpdate(){
    //build clientinfo
    if(loggedIn()){//when logged in
        CLIENTINFO["username"] = await currentUsername();
        $("#navbar-acctile").html(CLIENTINFO.username);
        $("#navbar-acctile").attr("href", "/user/account");
    }
  }


converter = {
    "timeToDayMin": (time)=>{
        return Number(time.split(":")[0])*60+Number(time.split(":")[1])
    },
    "dayMinToTime": (daysec)=>{
        return String(Math.floor(daysec/60))+":"+Math.floor(String(daysec%60))
    }
}

// send all Errors as debug to the server
var foundErrors = []
window.addEventListener("error", async function (e) {
    let error = e.error;
    let errorRepr = error.stack;
    if(!foundErrors.includes(errorRepr)){
        if((await apiRequest({"cmd": "errorcatch", "args": {"error": errorRepr}}))["ok"]) foundErrors.push(errorRepr);
    }
    return false;
 })

 function randint(max) {
    return Math.floor(Math.random() * max);
  }