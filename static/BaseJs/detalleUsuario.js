var cont = document.getElementById("contenedor");
detalleUsuario(parseInt(document.getElementById("tdoc").value),document.getElementById("doc").value);
function detalleUsuario(tdoc,doc){
    fetch("/dUsuario/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let text = "";
            if (data['cabeza'] != "None None"){
                text += "<p>Cabeza de Grupo: " + data['cabeza'] + "</p>";
            } else {
                text += "<p>Sin cabeza de grupo</p>";
            }
            if (data['instructor'] != "None None"){
                text += "<p>Instructor: " + data['instructor'] + "</p>";
            } else {
                text += "<p>Sin instructor</p>";
            }
            cont.innerHTML = "<div class='detalle'><p>Nombre: " + data['nom'] +
            "</p><p>Apellido: " + data['ape'] + "</p><p>Categoria: " + data['cate']
            + "</p><p>Cargo: " + data['cargo'] + "</p><p>Email: " + data['mail']
            + "</p><p>" + data['tdoc'] + ": " + data['doc'] + "</p>" + text +
            "</div><div class='cuatroBotones'><button class='btnRedondeado' onclick=location.href='/eUsuario/"
            + tdoc +"/" + doc + "/vUsuario'>Editar</button><button class='btnRedondeado' onclick='gimsUsuario("
            + tdoc + "," + doc +")'>Ver gimnasios</button><button class='btnRedondeado' onclick='verContra("
            + tdoc + "," + doc + ")'>Ver contraseña</button><button class='btnRedondeado' onclick=location.href='/vUsuario'>Regresar</button></div>"
        });
    });
}
function gimsUsuario(tdoc,doc){
    fetch("/gUsuario/" + tdoc + "/" + doc).then( response => {
        response.json().then(data => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<div><p>Nombre: " + data['nom'][i]
                + "</p><p>Direccion: " + data['direc'][i] + "</p></div>"
            }
            cont.innerHTML = text + "<button class='btnRedondeado unBoton' onclick='detalleUsuario("
            + tdoc + "," + doc + ")'>Regresar</button>";
        });
    });
}
function verContra(tdoc,doc){
    fetch("/verContra/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            alert("Contraseña: " + data['contra']);
        });
    });
}