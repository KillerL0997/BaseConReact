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
                    data['cateUsu'][i] + "</td><td><button class='btnRedondeado' onclick='detalleUsuario("
                    + data['tdocUsu'][i] + "," + data['docUsu'][i]
                    + ")'>Ver</button></td><td><button class='btnRedondeado' onclick='elimUsuario("
                    + data['tdocUsu'][i] + "," + data['docUsu'][i] 
                    + ")'>Eliminar</button></td></tr>";
            }
        });
    });
}
function elimUsuario(tdoc, doc){
    document.location.href = "/elimUsuario/" + tdoc + "/" + doc;
}
function detalleUsuario(tdoc, doc) {
    fetch("/detalleUsuario/" + tdoc + "/" + doc).then((response) => {
        response.json().then((data) => {
            contDeta.style.display = "block";
            tdoc = data['tdoc'];
            doc = data['doc'];
            let detaUsu = document.getElementById("detaUsu");
            detaUsu.innerHTML = "<h2>Usuario: " + data['nomape'] +
            "</h2><p>Categoria: " + data['cate'] + "</p><p>Cargo: "
            + data['cargo'] + "</p><p>Email: " + data['mail'] + "</p>";
            document.getElementById("btnEditar").setAttribute(
                "onclick","location.href='/eUsuario/" + tdoc + "/" + doc + "/vUsuario'"
            );
            let bot = document.getElementById("btnGimUsu");
            bot.setAttribute(
                "onclick","gUsuario('" + tdoc + "'," + doc + ")"
            );
            bot.innerHTML = "Ver gimnasios";
            document.getElementById("contraUsu").setAttribute(
                "onclick","verContra('" + tdoc + "'," + doc + ")"
            );
        });
    });
}
function gUsuario(tdoc, doc) {
    fetch("/gUsuario/" + tdoc + "/" + doc).then((response) => {
        response.json().then((data) => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<p>" + data['nom'][i] + ": "
                + data['direc'][i] + "</p>";
            }
            let detaUsu = document.getElementById("detaUsu");
            detaUsu.innerHTML = text;
            let bot = document.getElementById("btnGimUsu");
            bot.innerHTML = "Regresar";
            bot.setAttribute("onclick","detalleUsuario(" + tdoc + "," + doc + ")");
        });
    });
}
function verContra(tdoc, doc) {
    fetch("/verContra/" + tdoc + "/" + doc).then((response) => {
        response.json().then((data) => {
            alert("Contraseña: " + data['contra']);
        });
    });
}
function cerrar(){
    contDeta.style.display = "none";
}