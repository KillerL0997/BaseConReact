verEvento();
var deta = document.getElementById("detalles");
function verEvento() {
    let tipo = document.getElementById("tipoEvento");
    let fDesde = document.getElementById("fDesde");
    let fHasta = document.getElementById("fHasta");
    filtarEvento(
        "/verEvento/" + (((tipo.value) ? tipo.value : 0)) + "/" +
        ((fDesde.value) ? fDesde.value : "-") + "/" +
        ((fHasta.value) ? fHasta.value : "-")
    );
}
function filtarEvento(url) {
    tabla = document.getElementById("TablaEvento");
    tabla.innerHTML = "";
    fetch(url).then((response) => {
        response.json().then((data) => {
            for (let i = 0; i < data['lim']; i++) {
                tabla.innerHTML += "<tr><td>"
                    + data['fecha'][i] + "</td><td>"
                    + data['tipo'][i] + "</td><td><button class='btnRedondeado' onclick=detalleEvento("
                    + data['id'][i] + ")>Ver</button></td></tr>";
            }
        });
    });
}
function detalleEvento(idEve){
    fetch("/detalleEvento/" + idEve).then((response) => {
        response.json().then((data) => {
            deta.style.display = "block";
            let detaEve = document.getElementById("detalleEvento");
            detaEve.innerHTML = "<p>Tipo: " + data['tipo'] +
            "</p><p>Fecha: " + data['fecha'] + "</p><p>Descripcion: "
            + data['desc'] + "</p>";
            if(data['editar']){
                let botEdi = document.getElementById("btnEditar"); 
                botEdi.setAttribute(
                    "onclick","location.href='/eEvento/" + data['id'] + "'"
                );
                botEdi.style.display = "block";
            } else {
                document.getElementById("btnEditar").style.display = "none";
            }
            let bot = document.getElementById("btnAluExa");
            bot.setAttribute("onclick","vAluEvento(" + data['id'] + ")");
            bot.innerHTML = "Alumnos";
        });
    });
}
function vAluEvento(idEve){
    fetch("/vAluEvento/" + idEve).then((response) => {
        response.json().then((data) => {
            text = "";
            let detaEve = document.getElementById("detalleEvento");
            for(let i = 0; i < data['lim']; i++){
                text += "<tr><td>" + data['nom'][i]
                + "</td><td>" + data['ape'][i] + "</td><td>"
                + data['cate'][i] + "</td></tr>"
            }
            detaEve.innerHTML = "<h1>Alumnos</h1><table><thead><th></th><th></th><th></th></thead><tbody>"
            + text + "</tbody></table>";
            let botEdi = document.getElementById("btnEditar"); 
            botEdi.setAttribute("onclick","");
            botEdi.style.display = "none";
            let bot = document.getElementById("btnAluExa");
            bot.setAttribute("onclick","detalleEvento(" + data['idEve'] + ")");
            bot.innerHTML = "Regresar";
        });
    });
}
function cerrar(){
    deta.style.display = "none";
}