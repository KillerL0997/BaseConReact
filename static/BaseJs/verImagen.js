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
            console.log(data);
            let limExaCap = data['limExaCap'];
            let limTor = data['limTor'];
            let limVar = data['limVar'];
            let limExaProb = data['limExaProb'];
            contenedor.innerHTML = "";
            contenedor.innerHTML += "<h1>Examen capital</h1><section>"
            + llenarTipo(0, limExaCap, data) + "</section>" ;
            contenedor.innerHTML += "<h1>Examen provincia</h1><section>"
            + llenarTipo(limExaCap, limExaCap + limExaProb, data) + "</section>" ;
            contenedor.innerHTML += "<h1>Torneos</h1><section>"
            + llenarTipo(limExaCap + limExaProb, limExaCap + limTor + limExaProb, data) + "</section>" ;
            contenedor.innerHTML += "<h1>Varios</h1><section>"
            + llenarTipo(limExaCap + limTor + limExaProb, limExaCap + limTor + limVar + limExaProb, data) + "</section>" ;
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