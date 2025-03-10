let cont = document.getElementsByClassName("enlaces")[0];
if (!cont){
    cont = document.getElementsByClassName("filtro")[0];
    if(!cont){
        cont = document.getElementsByClassName("filtroAlu")[0];
    }
}
cont.style.minHeight = (window.screen.height - 30) + "px";
if (window.screen.width <= 768){
    cont.style.left = "-35%";
}
document.getElementById("botonLink").onclick = mFiltrosLink;

function mFiltrosLink(){
    if(cont.style.left == "-35%"){
        cont.style.left = "0";
    } else {
        cont.style.left = "-35%";
    }
}

function usuariosNotificados(idNoti){
    fetch("/usuariosNotificados/" + idNoti).then( response => {
        response.json().then( data => {
            let text = "No se encontraron usuarios notificadios";
            if (data['usuarios'] != null){
                text = "Usuarios notificados:\n";
                data['usuarios'].forEach( usu => {
                    text += usu + "\n";
                });
            }
            alert(text);
        })
    })
}