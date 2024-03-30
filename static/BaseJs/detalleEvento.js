var cont = document.getElementById("contenedor");
detalleEvento(parseInt(document.getElementById("idEve").value));

function detalleEvento(idEve){
    fetch("/dEvento/" + idEve).then(response => {
        response.json().then(data => {
            let text = "";
            if (data['cargo']){
                text = "<div class='tresBotones'><button class='btnRedondeado' onclick=location.href='/eEvento/"
                + idEve + "'>Editar</button><button class='btnRedondeado'"
                + " onclick=location.href='/vEvento'>Regresar</button>"
                + "<button class='btnRedondeado' onclick=vAluEvento(" + idEve
                + ")>Ver Alumnos</button></div>";
            } else {
                text = "<div class='dosBotones'><button class='btnRedondeado'"
                + " onclick=location.href='/vEvento'>Regresar</button>"
                + "<button class='btnRedondeado' onclick=vAluEvento(" + idEve
                + ")>Ver Alumnos</button></div>";
            }
            cont.innerHTML = "<div class='detalle'><p>Fecha: " + data['fecha']
            + "</p><p>Tipo de evento: " + data['tipo'] + "</p><p>Descripción: " + data['desc']
            + "</p></div>" + text;
        });
    });
}
function vAluEvento(idEve){
    fetch("/vAluEvento/" + idEve).then(response => {
        response.json().then(data => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<div class='detalleEvento'><p>" + data['ape'][i]
                + "</p><p>" + data['nom'][i]
                + "</p><p>" + data['cate'][i] + "</p></div>"
            }
            cont.innerHTML = text
            + "<button class='btnRedondeado unBoton' onclick=detalleEvento("
            + idEve + ")>Regresar</button>";
        });
    });
}