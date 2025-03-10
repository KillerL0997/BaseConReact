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
            let text = "<div class='detalleEvento'><table border='1'><thead><th>Apellido y nombre</th><th>Categoria</th><th>Edad</th></thead><tbody>";
            for(let i = 0; i < data['lim']; i++){
                text += "<tr><td style='text-align: left;'>" + data['ape'][i]
                + " " + data['nom'][i]
                + "</td><td style='text-align: left;'>" + data['cate'][i] + "</td><td>" + data['edad'][i] + "</td></tr>"
            }
            cont.innerHTML = text
            + "</tbody></table><h3>Cantidad de alumnos: " + data['lim'] + "</h3></div><button class='btnRedondeado unBoton' onclick=detalleEvento("
            + idEve + ")>Regresar</button>";
        });
    });
}