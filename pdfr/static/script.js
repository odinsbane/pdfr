
function toggle(elemId){
    elem = document.getElementById(elemId);
    
    if(elem.style.display==="none"){
        elem.style.display="inline";
    }else{
        elem.style.display="none";
    }
}
