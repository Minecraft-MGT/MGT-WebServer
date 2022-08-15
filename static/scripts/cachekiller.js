window.addEventListener("load", ()=>{
    for(let ce of document.getElementsByClassName("cachekill")){
        ce.setAttribute("src", ce.getAttribute("src")+"?cachekillerid="+randint(99999))
    }
        
})