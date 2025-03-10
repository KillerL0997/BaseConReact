var cont = document.getElementById("contenedor");
detalleAlumno(parseInt(document.getElementById("tdoc").value),document.getElementById("doc").value);

function detalleAlumno(tdoc,doc){
    fetch("/dAlumno/" + tdoc + "/" + doc).then( response => {
        response.json().then( data => {
            let text = "";
            if(data['matri']){
                text = "<div class='cuatroBotones'>"
                + "<button class='btnRedondeado' onclick=location.href='/eAlumno/"
                + tdoc + "/" + doc + "'>Editar</button>"
                + "<button class='btnRedondeado' onclick=location.href='/vAlumno'>Regresar</button>"
                + "<button class='btnRedondeado' onclick=vEveAlumno("
                + tdoc + "," + doc + ")>Eventos</button><button class='btnRedondeado' onclick=vMatriAlu("
                + tdoc + "," + doc + ")>Matriculas</button></div>";
            } else {
                text = "<div class='tresBotones'>"
                + "<button class='btnRedondeado' onclick=location.href='/eAlumno/"
                + tdoc + "/" + doc + "'>Editar</button>"
                + "<button class='btnRedondeado' onclick=location.href='/vAlumno'>Regresar</button>"
                + "<button class='btnRedondeado' onclick=vEveAlumno("
                + tdoc + "," + doc + ")>Eventos</button></div>";
            }
            cont.innerHTML = "<div class='contConFoto'><div><p>Nombre: " + data['nom']
            + "</p><p>Apellido: " + data['ape'] + "</p><p>Categoria: " + data['cate']
            + "</p><p>Nacionalidad: " + data['nacio'] + "</p><p>Fecha de nacimiento: "
            + data['fnac'] + "</p><p>" + data['tdoc'] +": " + data['doc'] + "</p><p>Fecha de inscripcion: " + data['finsc']
            + "</p><p>Observaciones: " + data['obs'] + "</p><p>Email: " + data['mail']
            + "</p><p>Localidad: " + data['loc']
            + "</p><p>Instructor: " + data['nominstru'] + " " + data['apeinstru']
            + "</p><p>Lugar de practica: " + data['nomgim']
            + "</p></div><div><img src='" + data['foto'] + "'></div></div>" + text;
        });
    });
}
function vEveAlumno(tdoc,doc){
    fetch("/vEveAlumno/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<div class='detalleEvento'><p>Fecha: " + data['fecha'][i]
                + "</p><p>Tipo: " + data['tipo'][i] + "</p><p>Categoria: "
                + data['cate'][i] + "</p></div>"
            }
            cont.innerHTML = text
            + "<div class='tresBotones'><button class='btnRedondeado' onclick='agregarEventos("
            + tdoc + "," + doc + ")'>Agregar eventos previos"
            + "</button><button class='btnRedondeado' onclick=detalleAlumno("
            + tdoc + "," + doc + ")>Regresar</button><button class='btnRedondeado' onclick='eliminarEventos("
            + tdoc + "," + doc + ")'>Quitar eventos previos</button></div>"
        });
    });
}
function agregarEventos(tdoc,doc){
    fetch("/aPrevEve/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let text = "<table><thead><th></th><th>Fecha</th><th>Tipo</th></thead><tbody>";
            for(let i = 0; i < data['lim']; i++){
                text += "<tr><td><input type='checkbox' name='checkAluEve' value='"
                + data['id'][i] + "'></td><td>" + data['fecha'][i] + "</td><td>" + data['tipo'][i] + "</td></tr>";
            }
            cont.innerHTML = text + "</tbody></table><div class='dosBotones'><button class='btnRedondeado' onclick='vEveAlumno("
            + tdoc + "," + doc + ")'>Regresar</button><button class='btnRedondeado' onclick='aAluEve("
            + tdoc + "," + doc + ")'>Aceptar</button></div>"
        });
    });
}
function aAluEve(tdoc, doc){
    let text = "";
    document.getElementsByName("checkAluEve").forEach(elem => {
        if(elem.checked){
            text += elem.value + ",";
        }
    })
    if(text != ""){
        location.href="/agregaEvento/" + tdoc + "/" + doc + "/" + text.substring(0,(text.length - 1));
    }
}
function eliminarEventos(tdoc,doc){
    fetch("/ePrevEven/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let text = "<table><thead><th></th><th>Fecha</th><th>Tipo</th></thead><tbody>";
            for(let i = 0; i < data['lim']; i++){
                text += "<tr><td><input type='checkbox' name='checkAluEve' value='"
                + data['id'][i] + "'></td><td>" + data['fecha'][i] + "</td><td>" + data['tipo'][i] + "</td></tr>";
            }
            cont.innerHTML = text + "</tbody></table><div class='dosBotones'><button class='btnRedondeado' onclick='vEveAlumno("
            + tdoc + "," + doc + ")'>Regresar</button><button class='btnRedondeado' onclick='eAluEve("
            + tdoc + "," + doc + ")'>Aceptar</button></div>"
        });
    });
}
function eAluEve(tdoc, doc){
    let text = "";
    document.getElementsByName("checkAluEve").forEach(elem => {
        if(elem.checked){
            text += elem.value + ",";
        }
    })
    if(text != ""){
        location.href="/elimEvento/" + tdoc + "/" + doc + "/" + text.substring(0,(text.length - 1));
    }
}
function vMatriAlu(tdoc,doc){
    fetch("/vMatriAlu/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<div><p>Fecha: " + data['fecha'][i]
                + "</p><p>Tipo: " + data['tipo'][i] + "</p></div>"
            }
            cont.innerHTML = text
            + "<button class='btnRedondeado unBoton' onclick=detalleAlumno("
            + tdoc + "," + doc + ")>Regresar</button>"
        });
    });
}