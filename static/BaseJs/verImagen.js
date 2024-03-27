var contenedor = document.getElementById("contenedor");
vTodoImagen()
function filtrarImagen(tipo){
    fetch("/filtrarImagen/" + tipo).then((response) => {
        response.json().then((data) => {
            contenedor.innerHTML = "<h1>" + data['tipo'] +
            "</h1><section>" + llenarTipo(0, data['lim'],data) + "</section>";
        });
    });
}
function vTodoImagen(){
    fetch("/vTodoImagen").then((response) => {
        response.json().then((data) => {
            let limExa = data['limExa'];
            let limTor = data['limTor'];
            let limVar = data['limVar'];
            contenedor.innerHTML = "";
            contenedor.innerHTML += "<h1>Examenes</h1><section>"
            + llenarTipo(0, limExa, data) + "</section>" ;
            contenedor.innerHTML += "<h1>Torneos</h1><section>"
            + llenarTipo(limExa, limExa + limTor, data) + "</section>" ;
            contenedor.innerHTML += "<h1>Varios</h1><section>"
            + llenarTipo(limExa + limTor, limExa + limTor + limVar, data) + "</section>" ;
        });
    });
}
function llenarTipo(cont, lim, data){
    text = "";
    while (cont < lim){
        text += "<div><img src='static/" + data['direc'][cont]
        + "'><button class='btnRedondeado' onclick=borrarFoto('" + data['id'][cont]
        + "','" + data['direc'][cont] + "')>Eliminar</button></div>";
        cont ++;
    }
    return text;
}
function borrarFoto(id,direc){
    location.href="/eImagen/" + id + "/" + direc.replaceAll("/","ƒ");
}