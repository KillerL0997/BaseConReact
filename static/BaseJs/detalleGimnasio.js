var cont = document.getElementById("contenedor");
detalleGimnasio(parseInt(document.getElementById("idGim").value));

function detalleGimnasio(idGim){
    fetch("/dGimnasio/" + idGim).then(response => {
        response.json().then(data => {
            cont.innerHTML = "<div class='contConFoto'><div><p>Nombre: " + data['nom']
            + "</p><p>Dirección: " + data['direc'] + "</p><p>Ubicación: "
            + data['ubi'] + "</p><p><a href='" + data['insta']
            + "'>Instagram</a></p><p><a href='" + data['face'] + "'>Facebook</a></p><p>Whatsapp: " + data['whats']
            + "</p></div><div><img src='" + data['logo']
            + "'></div></div><div class='tresBotones'><button class='btnRedondeado' onclick=location.href='/eGimnasio/"
            + idGim + "'>Editar</button><button class='btnRedondeado' " 
            + "onclick=location.href='/vGimnasio'>Regresar</button><button"
            + " class='btnRedondeado' onclick='vAluGimnasio(" + idGim + ")'>Alumnos</button></div>"
        });
    });
}
function vAluGimnasio(idGim){
    fetch("/vAluGimnasio/" + idGim).then(response => {
        response.json().then(data => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<div class='detalleEvento'><p>" + data['ape'][i]
                + "</p><p>" + data['nom'][i]
                + "</p><p>" + data['cate'][i] + "</p></div>"
            } 
            cont.innerHTML = text
            + "<button class='btnRedondeado unBoton' onclick=detalleGimnasio("
            + idGim + ")>Regresar</button>";
        });
    });
}