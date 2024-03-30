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
                + "<button class='btnRedondeado' onclick=location.href'/eAlumno/"
                + tdoc + "/" + doc + "'>Editar</button>"
                + "<button class='btnRedondeado' onclick=location.href='/vAlumno'>Regresar</button>"
                + "<button class='btnRedondeado' onclick=vEveAlumno("
                + tdoc + "," + doc + ")>Eventos</button></div>";
            }
            cont.innerHTML = "<div class='contConFoto'><div><p>Nombre: " + data['nom']
            + "</p><p>Apellido: " + data['ape'] + "</p><p>Categoria: " + data['cate']
            + "</p><p>Nacionalidad: " + data['nacio'] + "</p><p>Fecha de nacimiento: "
            + data['fnac'] + "</p><p>Fecha de inscripcion: " + data['finsc']
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
            + "<button class='btnRedondeado unBoton' onclick=detalleAlumno("
            + tdoc + "," + doc + ")>Regresar</button>" 
        });
    });
}
function vMatriAlu(tdoc,doc){
    fetch("/vMatriAlu/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<div><p>Fecha: " + data['fecha']
                + "</p><p>Tipo: " + data['tipo'] + "</p></div>"
            }
            cont.innerHTML = text
            + "<button class='btnRedondeado unBoton' onclick=detalleAlumno("
            + tdoc + "," + doc + ")>Regresar</button>"
        });
    });
}