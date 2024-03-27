var tGimansio = document.getElementById("tableGimnsaio");
verTodoGimnasio();
var instru = document.getElementById("Instructor");
instru.onchange = cambioSelect;
var deta = document.getElementById("detalles");

function cambioSelect(){
    let usu = document.getElementById("Instructor").value;
    if (usu == ','){
        filtarGimnasio("/verTodoGimnasio");
    } else {
        instru = usu.split(",");
        filtarGimnasio("/verGimnasio/" + instru[0] + "/" + instru[1]);
    }
}
function verTodoGimnasio(){
    filtarGimnasio("/verTodoGimnasio");
    document.getElementById("vDeshabilitado").style.display = "block";
    document.getElementById("vHabilitado").style.display = "none";
    document.getElementById("Instructor").style.display = "block";
}
function verDesaHabi(valor){
    if (valor == 1){
        document.getElementById("vDeshabilitado").style.display = "block";
        document.getElementById("vHabilitado").style.display = "none";
        document.getElementById("Titulo").style.display = "block";
        instru.style.display = "block";
    } else {
        document.getElementById("vDeshabilitado").style.display = "none";
        document.getElementById("vHabilitado").style.display = "block";
        document.getElementById("Titulo").style.display = "none";
        instru.style.display = "none";
    }
    filtarGimnasio("/verDesaHabi/" + valor);
}
function filtarGimnasio(url){
    tGimansio.innerHTML = "";
    fetch(url).then((response) => {
        response.json().then((data) => {
            for(let i = 0; i < data['lim']; i++){
                tGimansio.innerHTML += "<tr><td>" + data['nom'][i] 
                +"</td><td>" + data['direc'][i] + "</td><td><button class='btnRedondeado' onclick=" + data['func'] + "("
                + data['id'][i] + ")>" + data['verElim'] + "</button></td><td><button class='btnRedondeado' onclick='" + data['onclick'] + "("
                + data['id'][i] + ")'>" + data['valBot'] + "</button></td></tr>";
            }
        });
    });
}
function detalleGimnasio(idGim){
    fetch("/detalleGimnasio/" + idGim).then((response) => {
        response.json().then((data) => {
            deta.style.display = "block";
            let detaGim = document.getElementById("detaGim");
            detaGim.innerHTML = "<div><img style='width:250px;' src='"
            + data['logo'] + "'></div><div><p>Nombre: " + data['nom']
            + "</p><p>Direccion: " + data['direc'] + "</p></div>";
            if (window.screen.width <= 768){
                detaGim.style.flexDirection = "column";
            } else {
                detaGim.style.flexDirection = "row-reverse";
            }
            let botEdi = document.getElementById("btnEditar");
            botEdi.setAttribute(
                "onclick","location.href='/eGimnasio/" + idGim + "'"
            );
            botEdi.style.display = "block";
            let botAlu = document.getElementById("btnAluGim");
            botAlu.setAttribute(
                "onclick","vAluGimnasio(" + idGim + ")"
            );
            botAlu.innerHTML = "ver Alumnos";
        });
    });
}
function vAluGimnasio(idGim){
    fetch("/vAluGimnasio/" + idGim).then((response) => {
        response.json().then((data) => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<tr><td>" + data['nom'][i]
                + "</td><td>" + data['ape'][i] + "</td><td>"
                + data['cate'][i] + "</td></tr>";
            }
            document.getElementById("btnEditar").style.display = "none";
            let bot = document.getElementById("btnAluGim");
            bot.innerHTML = "Regresar";
            bot.setAttribute("onclick","detalleGimnasio(" + idGim + ")");
            let detaGim = document.getElementById("detaGim");
            detaGim.innerHTML = "<h1>Alumnos</h1><table><thead><th></th><th></th><th></th></thead><tbody>"
            + text + "</tbody></table>";
            detaGim.style.flexDirection = "column";
        });
    });
}
function cerrar(){
    deta.style.display = "none";
}
function desaGim(idGim){
    location.href= '/desaGim/' + idGim;
}
function habiGim(idGim){
    location.href= '/eGimnasio/' + idGim; 
}
function elimGim(idGim){
    location.href= '/elimGimnasio/' + idGim;
}