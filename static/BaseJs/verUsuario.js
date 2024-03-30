var contDeta = document.getElementById("detalles");
verTodoUsuario();
function verUsuario(tipoUsu) {
    filtrarUsuario("/verUsuario/" + tipoUsu);
}
function verInstructores() {
    filtrarUsuario("/verInstructores");
}
function verTodoUsuario() {
    filtrarUsuario("/verTodoUsuario");
}
function filtrarUsuario(url) {
    fetch(url).then((response) => {
        response.json().then((data) => {
            tCuerpo = document.getElementById("TablaUsuario");
            tCuerpo.innerHTML = "";
            for (let i = 0; i < data['lim']; i++) {
                tCuerpo.innerHTML += "<tr><td>" + data['nomUsu'][i]
                    + "</td><td>" + data['apeUsu'][i] + "</td><td>" +
                    data['cateUsu'][i] + "</td><td><button class='btnRedondeado' onclick=location.href='/detalleUsuario/"
                    + data['tdocUsu'][i] + "/" + data['docUsu'][i]
                    + "'>Ver</button></td><td><button class='btnRedondeado' onclick='elimUsuario("
                    + data['tdocUsu'][i] + "," + data['docUsu'][i] 
                    + ")'>Eliminar</button></td></tr>";
            }
        });
    });
}
function elimUsuario(tdoc, doc){
    document.location.href = "/elimUsuario/" + tdoc + "/" + doc;
}