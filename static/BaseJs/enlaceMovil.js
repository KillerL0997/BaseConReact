let cont = document.getElementsByClassName("enlaces")[0];
let div3 = document.getElementById("div3");
let div2 = document.getElementById("div2");
let div1 = document.getElementById("div1");
if (!cont){
    cont = document.getElementsByClassName("filtro")[0];
}
cont.style.minHeight = (window.screen.height - 30) + "px";
if (window.screen.width <= 768){
    cont.style.left = "-35%";
}
document.getElementById("botonLink").onclick = mFiltrosLink;

function mFiltrosLink(){
    if(cont.style.left == "-35%"){
        cont.style.left = "0";
        div3.style.display = "none";
        document.getElementById("botonLink").style.justifyContent = "center";
        div2.style.position = div1.style.position = "absolute";
        div2.style.rotate = "45deg";
        div1.style.rotate = "-45deg";
    } else {
        cont.style.left = "-35%";
        div3.style.display = "block";
        document.getElementById("botonLink").style.justifyContent = "space-between";
        div2.style.position = div1.style.position = "unset";
        div2.style.rotate = div1.style.rotate = "0deg";
    }
}