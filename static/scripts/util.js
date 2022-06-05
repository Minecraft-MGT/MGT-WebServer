//Helper functions
function randint(max) {
    return Math.floor(Math.random() * max);
}
function getCurrentTime(){
    var today = new Date();
    return today.getHours() + ":" + today.getMinutes();
}


//js executed on page load
window.addEventListener("load", ()=>{
    auth.loadAuthToken();
    navbarUpdate();
})

async function navbarUpdate(){
    //build clientinfo
    if(auth.loggedIn()){//when logged in
        $("#navbar-acctile").html(auth.currentUsername());
        $("#navbar-acctile").attr("href", "/user/acc");
    }else 
        for(ce of $(".requirelogin").get()){
            $(ce).attr("disabled", "disabled");
            $(ce).removeAttr("href");
            ce.style.color = "rgb(100, 100, 100)";
        }
  }


//account/session controll

var acc = {
    "preregister": async function(username, password){
        let payload = {
            "cmd": "user_preregister",
            "args": {"username": username, "password": password}
        }
        let response = await apiRequest(payload);
        if(!response["ok"]) alert(response["msg"]);
        return response;
    },
    "register": async function(username, password, authtoken){
        let payload = {
            "cmd": "user_register",
            "args": {"username": username, "password": password, "authtoken": authtoken}
        }
        let response = await apiRequest(payload);
        return response;
    },
    "login": async function (username, password){
        let payload = {
            "cmd": "user_login",
            "args": {"username": username, "password": password}
        }
        let response = await apiRequest(payload);
        if(response["ok"]){
            auth.saveAuthToken(response["authsync"]);
            auth.setUsername(response["usernamesync"]);

            document.location.pathname = "/user/acc";
        }else{
            alert("Login fehlgeschlagen.")
        }
        navbarUpdate();
        return response;
    },
    "terminateSession": async function (){
        let payload = {
            "cmd": "session_terminate",
            "args": {}
        }
        let response = await apiRequest(payload);
        if(response["ok"]){
            auth.resetSession();
            document.location.reload();
        }else{
            alert("logout failed...")
        }
        navbarUpdate();        
    },
    "delete": async function (){
        let payload = {
            "cmd": "accdelete",
            "args": {}
        }
        let response = await apiRequest(payload);
        if(response["ok"]){
            auth.resetSession();
            document.location.reload();
        }else{
            alert("account deletion failed...");
        }
        navbarUpdate();        
    }
}

var auth = {
    "view": function(){
        console.log("LS: "+localStorage.getItem("authtoken"))
        console.log("CK: "+getCookie("authtoken"))
        console.log("UN: "+localStorage.getItem("username"))
    },
    "saveAuthToken": function (token){
        localStorage.setItem("authtoken", token);
        auth.loadAuthToken();
    },
    "loadAuthToken": function (){
        if(localStorage.getItem("authtoken")!=null)
            setCookie("authtoken", localStorage.getItem("authtoken"));
        else
            deleteCookie("authtoken");
    },
    "resetSession": function (){
        localStorage.removeItem("authtoken");
        auth.loadAuthToken();
        localStorage.removeItem("username");
    },
    "loggedIn": function (){
        return localStorage.getItem("authtoken")!=null
    },
    "setUsername": function (username){
        localStorage.setItem("username", username);
    },
    "currentUsername": function (){
        if(localStorage.getItem("username") == null) return null;
        return localStorage.getItem("username");
    }
}

var team = {
    "create": async function (teamname){
        let payload = {
            "cmd": "team_create",
            "args": {"teamname": teamname}
        }
        let response = await apiRequest(payload);
        return response;
    }, 
    "switch": async function (teamid){
        let payload = {
            "cmd": "team_switch",
            "args": {"teamid": teamid}
        }
        let response = await apiRequest(payload);
        return response;
    },
    "leave": async function (){
        let payload = {
            "cmd": "team_leave",
            "args": {}
        }
        let response = await apiRequest(payload);
        return response;
    },
    "update": async function (name, shortName, opened){
        let payload = {
            "cmd": "team_update",
            "args": {"name": name, "short_name": shortName, "opened": opened}
        }
        let response = await apiRequest(payload);
        return response;
    }
    
}