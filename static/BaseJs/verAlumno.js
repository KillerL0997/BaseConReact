botVerHabi();
var deta = document.getElementById("detaAlum");
let sel = document.getElementById("usuAlu");

function filtroAlumno() {
    document.getElementById("asignaUsuario").innerHTML = "Usuario";
    let tabla = document.getElementById("TablaAlumno");
    tabla.innerHTML = "";
    let nom = document.getElementById("Nombre").value;
    let ape = document.getElementById("Apellido").value;
    let cate = document.getElementById("Categoria").value;
    let usu = document.getElementById("usuAlu").value.split(",");
    let gim = document.getElementById("usuGim").value;
    let fdExamen = document.getElementById("fdExamen").value;
    let fhExamen = document.getElementById("fhExamen").value;
    let fdAATEE = (
        document.getElementById("fdAATEE")
    ) ? document.getElementById("fdAATEE").value : null;
    let fhAATEE = (
        document.getElementById("fhAATEE")
    ) ? document.getElementById("fhAATEE").value : null;
    let fdEnat = (
        document.getElementById("fdEnat")
    ) ? document.getElementById("fdEnat").value : null;
    let fhEnat = (
        document.getElementById("fhEnat")
    ) ? document.getElementById("fhEnat").value : null;
    fetch(
        "/filtroAlumno/" + ((nom) ? nom : "-") + "/" + ((ape) ? ape : "-") + "/"
        + cate + "/" + ((fdExamen) ? fdExamen : "-") + "/" + ((fhExamen) ? fhExamen : "-")
        + "/" + ((fdAATEE) ? fdAATEE : "-") + "/" + ((fhAATEE) ? fhAATEE : "-") + "/"
        + ((fdEnat) ? fdEnat : "-") + "/" + ((fhEnat) ? fhEnat : "-") + "/"
        + ((usu[0]) ? usu[0] : "-") + "/" + ((usu[1]) ? usu[1] : "-") + "/"
        + ((gim) ? gim : "-")
    ).then((response) => {
        response.json().then((data) => {
            document.getElementById("cantAlus").innerHTML = "Cantidad de alumnos encontrados: " + data['lim'];
            let lim = data['lim'];
            if(document.getElementById("fdEnat")){
                for (let i = 0; i < lim; i++) {
                    tabla.innerHTML += "<tr><td><input type='checkbox' name='checkAlu' value='"
                        + data['tdoc'][i] + "," + data['doc'][i] + "'></td><td>"
                        + data['fecha'][i] + "</td><td>" + data['nom'][i]
                        + "</td><td>" + data['ape'][i] + "</td><td>" + data['edad'][i] + " Años</td><td>"
                        + data['insNom'][i] + " " + data['insApe'][i] + "</td>"
                        + "<td>" + data['gimNom'][i] + "</td><td>" + data['cate'][i] + "</td><td>" + data['fAATEE'][i]
                        + "</td><td>" + data['fEnat'][i]
                        + "</td><td><button class='btnRedondeado' onclick=location.href='/detalleAlumno/"
                        + data['tdoc'][i] + "/" + data['doc'][i] + "'>Ver</button></td></tr>"
                }
            } else {
                for (let i = 0; i < lim; i++) {
                    tabla.innerHTML += "<tr><td><input type='checkbox' name='checkAlu' value='"
                        + data['tdoc'][i] + "," + data['doc'][i] + "'></td><td>"
                        + data['fecha'][i] + "</td><td>" + data['nom'][i]
                        + "</td><td>" + data['ape'][i] + "</td><td>" + data['edad'][i] + " Años</td><td>"
                        + data['insNom'][i] + " " + data['insApe'][i] 
                        + "</td><td>" + data['gimNom'][i] + "</td><td>" + data['cate'][i] +
                        "</td><td><button class='btnRedondeado' onclick=location.href='/detalleAlumno/"
                        + data['tdoc'][i] + "/" + data['doc'][i] + "'>Ver</button></td></tr>"
                }
            }
        });
    });
}
function vDesaAlu() {
    limpiaFiltros();
    document.getElementById("asignaUsuario").innerHTML = "Asignar a:";
    let tabla = document.getElementById("TablaAlumno");
    tabla.innerHTML = "";
    document.getElementsByName("habiDesa").forEach(elem => {
        elem.style.display = "none";
    });
    document.getElementsByName("celhabiDesa").forEach(elem => {
        elem.style.display = "none";
    });
    document.getElementsByName("dasaHabi").forEach(elem => {
        elem.style.display = "block";
    });
    document.getElementsByName("celDesaHabi").forEach(elem => {
        elem.style.display = "table-cell";
    });
    document.getElementById("botFiltro").setAttribute("onclick", "filtroDesaAlu()");
    fetch("/vDesaAlu").then(response => {
        response.json().then(data => {
            let lim = data['lim'];
            for (let i = 0; i < lim; i++) {
                tabla.innerHTML += "<tr><td><input type='checkbox' name='checkAlu' value='"
                    + data['tdoc'][i] + "," + data['doc'][i] + "'></td><td>" + data['fecha'][i]
                    + "</td><td>" + data['nom'][i] + "</td><td>" + data['ape'][i] + "</td><td>"
                    + data['edad'][i] + " Años</td><td>" + data['cate'][i] + "</td></tr>";
            }
        });
    });
}
function botVerHabi() {
    document.getElementsByName("dasaHabi").forEach(elem => {
        elem.style.display = "none";
    });
    document.getElementsByName("celDesaHabi").forEach(elem => {
        elem.style.display = "none";
    });
    document.getElementsByName("habiDesa").forEach(elem => {
        elem.style.display = "block";
    });
    document.getElementsByName("celhabiDesa").forEach(elem => {
        elem.style.display = "table-cell";
    });
    document.getElementById("botFiltro").setAttribute("onclick", "filtroAlumno()");
    limpiaFiltros();
    filtroAlumno();
}
function limpiaFiltros() {
    document.getElementById("Categoria").value = "-";
    if (document.getElementById("fdAATEE")){
        document.getElementById("fdAATEE").value =
        document.getElementById("fhAATEE").value = "";
    }
    if (document.getElementById("fdEnat")){
        document.getElementById("fdEnat").value =
        document.getElementById("fhEnat").value = "";
    }
    if (document.getElementById("fdFetra")){
        document.getElementById("fdFetra").value =
        document.getElementById("fhFetra").value = "";
    }
    document.getElementById("Nombre").value =
        document.getElementById("usuAlu").value =
        document.getElementById("usuGim").value =
        document.getElementById("Apellido").value =
        document.getElementById("fdExamen").value =
        document.getElementById("fhExamen").value = "";
}
function aAluEven(tipo) {
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + ".";
        }
    });
    if (text) {
        location.href = "/aAluEven/" + tipo + "/" + text.substring(0, text.length - 1);
    }
}
function desaAlu() {
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + ".";
        }
    });
    if (text) {
        location.href = "/desaAlu/" + text.substring(0, text.length - 1);
    }
}
function filtroDesaAlu() {
    let tabla = document.getElementById("TablaAlumno");
    tabla.innerHTML = "";
    nom = document.getElementById("Nombre").value;
    ape = document.getElementById("Apellido").value;
    cate = document.getElementById("Categoria").value;
    fetch(
        "/filtroDesaAlu/" + ((nom) ? nom : "-") + "/" + ((ape) ? ape : "-")
        + "/" + cate
    ).then(response => {
        response.json().then(data => {
            let lim = data['lim'];
            for (let i = 0; i < lim; i++) {
                tabla.innerHTML += "<tr><td><input type='checkbox' name='checkAlu' value='"
                    + data['tdoc'][i] + "," + data['doc'][i] + "'></td><td>" + data['fecha'][i]
                    + "</td><td>" + data['ape'][i] + " " + data['nom'][i] + "</td><td>"
                    + data['cate'][i] + "</td></tr>";
            }
        });
    });
}
function habiAlu() {
    let selUsu = document.getElementById("usuAlu").value.split(",");
    let selGim = document.getElementById("usuGim").value;
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + "."
        }
    });
    if (selUsu && selGim && text) {
        location.href = "/habiAlu/" + selUsu[0] + "/" + selUsu[1] +
            "/" + selGim + "/" + text.substring(0, text.length - 1);
    }
}
function aluMatri(tipo) {
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + "."
        }
    });
    if (text) {
        location.href = "/aluMatri/" + tipo + "/" + text.substring(0, text.length - 1);
    }
}
function vFilEveAlu(tipo, tdoc, doc) {
    fetch("/vFilEveAlu/" + tipo + "/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let detaAlu = document.getElementById("detaAlu");
            if (tipo == 1) {
                detaAlu.innerHTML = "<h1>Examenes</h1>";
            }
            if (tipo == 2) {
                detaAlu.innerHTML = "<h1>Torneos</h1>";
            }
            if (tipo == 3) {
                detaAlu.innerHTML = "<h1>Eventos</h1>";
            }
            let text = "";
            for (let i = 0; i < data['lim']; i++) {
                text += "<tr><td>" + data['fecha'][i]
                    + "</td><td>" + data['tipo'][i] + "</td><td>"
                    + data['cate'][i] + "</td></tr>";
            }
            detaAlu.innerHTML += "<table><thead><th></th><th></th><th></th></thead><tbody>"
                + text + "</tbody></table>";
            let btnEditar = document.getElementById("btnEditarAlu");
            btnEditar.innerHTML = "Agregar";
            btnEditar.setAttribute(
                "onclick", "aPrevEve(" + tipo + "," + tdoc + "," + doc + ")"
            );
            let btnEvento = document.getElementById("btnEventoAlu");
            btnEvento.innerHTML = "Quitar";
            btnEvento.setAttribute(
                "onclick", "ePrevEven(" + tipo + "," + tdoc + "," + doc + ")"
            );
            btnEvento.style.display = "block";
            let btnMatri = document.getElementById("btnMatrialu");
            btnMatri.innerHTML = "";
            btnMatri.setAttribute("onclick", "");
            btnMatri.style.display = "none";
            document.getElementById("regresar").setAttribute(
                "onclick", "vEveAlumno('" + tdoc + "'," + doc + ")"
            );
        });
    });
}
function aPrevEve(tipo, tdoc, doc) {
    fetch("/aPrevEve/" + tipo + "/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let detaAlu = document.getElementById("detaAlu");
            if (tipo == 1) {
                detaAlu.innerHTML = "<h1>Agregar examen</h1>"
            }
            if (tipo == 2) {
                detaAlu.innerHTML = "<h1>Agregar torneo</h1>"
            }
            if (tipo == 3) {
                detaAlu.innerHTML = "<h1>Agregar evento</h1>"
            }
            let text = "";
            for (let i = 0; i < data['lim']; i++) {
                text += "<tr><td><input type='checkbox' name='checkAlu' value='" + data['id'][i]
                    + "'></td><td>Fecha: " + data['fecha'][i] + "</td></tr>";
            }
            detaAlu.innerHTML += "<table><thead><th></th><th></th></thead><tbody>" + text +
                "</tbody></table>";
            let btnEditar = document.getElementById("btnEditarAlu");
            btnEditar.innerHTML = "Aceptar";
            btnEditar.setAttribute(
                "onclick", "agregaEvento(" + tdoc + "," + doc + ")"
            );
            let btnEvento = document.getElementById("btnEventoAlu");
            btnEvento.innerHTML = "";
            btnEvento.setAttribute("onclick", "");
            btnEvento.style.display = "none";
            document.getElementById("regresar").setAttribute(
                "onclick", "vFilEveAlu(" + tipo + ",'" + tdoc + "'," + doc + ")"
            );
        });
    });
}
function agregaEvento(tdoc, doc) {
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + ",";
        }
    });
    if (text) {
        location.href = "/agregaEvento/" + tdoc + "/" + doc + "/" + text.substring(0, text.length - 1);
    }
}
function ePrevEven(tipo, tdoc, doc) {
    fetch("/ePrevEven/" + tipo + "/" + tdoc + "/" + doc).then(response => {
        response.json().then(data => {
            let detaAlu = document.getElementById("detaAlu");
            if (tipo == 1) {
                detaAlu.innerHTML = "<h1>Eliminar examen</h1>"
            }
            if (tipo == 2) {
                detaAlu.innerHTML = "<h1>Eliminar torneo</h1>"
            }
            if (tipo == 3) {
                detaAlu.innerHTML = "<h1>Eliminar evento</h1>"
            }
            let text = "";
            for (let i = 0; i < data['lim']; i++) {
                text += "<tr><td><input type='checkbox' name='checkAlu' value='" + data['id'][i]
                    + "'></td><td>Fecha: " + data['fecha'][i] + "</td></tr>";
            }
            detaAlu.innerHTML += "<table><thead><th></th><th></th></thead><tbody>" + text +
                "</tbody></table>";
            let btnEditar = document.getElementById("btnEditarAlu");
            btnEditar.innerHTML = "Aceptar";
            btnEditar.setAttribute(
                "onclick", "elimEvento(" + tdoc + "," + doc + ")"
            );
            let btnEvento = document.getElementById("btnEventoAlu");
            btnEvento.innerHTML = "";
            btnEvento.setAttribute("onclick", "");
            btnEvento.style.display = "none";
            document.getElementById("regresar").setAttribute(
                "onclick", "vFilEveAlu(" + tipo + ",'" + tdoc + "'," + doc + ")"
            );
        });
    });
}
function elimEvento(tdoc, doc) {
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + ",";
        }
    });
    if (text) {
        location.href = "/elimEvento/" + tdoc + "/" + doc + "/" + text.substring(0, text.length - 1);
    }
}
function elimAlu() {
    let text = "";
    document.getElementsByName("checkAlu").forEach(elem => {
        if (elem.checked) {
            text += elem.value + ".";
        }
    });
    if (text) {
        location.href = "/elimAlu/" + text.substring(0, text.length - 1);
    }
}