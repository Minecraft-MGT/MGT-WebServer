sensFrames = []

function bgfileUp_load(elem){
    let properties = {
        "action": elem.getAttribute("action"),
        "accept": elem.getAttribute("accept"),
        "finishEvent": elem.getAttribute("finishEvent")
    };

    let randomID = "backgroundFileUpload_"+randint(99999)+"_";
    while(document.getElementById(randomID))
        randomID = "backgroundFileUpload_"+randint(99999)+"_";

    let template = `
    <label for="${randomID}Upload" id="${randomID}"><ion-icon class="uploadIonicon" name="cloud-upload-outline"></ion-icon></label>
    <iframe style="display:none" name="${randomID}UploadFrame" onload="
    if(!sensFrames.includes('${randomID}')){
        sensFrames.push('${randomID}');
    }else{
        ${properties.finishEvent}
    }
    
    "></iframe>
    <form action="${properties.action}" target="${randomID}UploadFrame" method="post" enctype="multipart/form-data">
        <input name="content" id="${randomID}Upload" type="file" accept="${properties.accept}" hidden onchange="this.parentElement.submit();">
    </form>
    `;

    elem.innerHTML = template;
}

window.addEventListener("load", ()=>{
    for(let ce of document.getElementsByClassName("backgroundFileUploadIcon"))
        bgfileUp_load(ce);
})