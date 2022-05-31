function scanvas_load(elem){
    let properties = {
        "width": elem.getAttribute("width"),
        "height": elem.getAttribute("height"),
        "name": elem.getAttribute("playername"),
        "fov": elem.getAttribute("fov"),
        "zoom": elem.getAttribute("zoom"),
        "rotate": elem.hasAttribute("rotate"),
    };
    console.log(elem)
    let skinViewer = new skinview3d.SkinViewer({
        canvas: elem,
        width: properties.width == null ? 300 : properties.width,
        height: properties.height == null ? 400 : properties.height,
        skin: "/static/skins/"+properties.name+".png"
    });
    skinViewer.loadCape(null);
    skinViewer.background = document.body.style.backgroundColor;
    
    skinViewer.fov = properties.fov == null ? 40 : properties.fov;
    skinViewer.zoom = properties.zoom == null ? 0.9 : properties.zoom;
    
    let control = skinview3d.createOrbitControls(skinViewer);
    control.enableRotate = true;
    control.enableZoom = false;
    control.enablePan = false;
    
    if(properties.rotate){
        let rotateAnimation = skinViewer.animations.add(skinview3d.RotatingAnimation);
        rotateAnimation.speed = 0.3;
    }
    
    let idleAnimation = skinViewer.animations.add(skinview3d.IdleAnimation);
    idleAnimation.speed = 1;
    
    return skinViewer;
}

window.addEventListener("load", ()=>{
    for(let ce of document.getElementsByClassName("MCSkinDisplay"))
        scanvas_load(ce);
})
