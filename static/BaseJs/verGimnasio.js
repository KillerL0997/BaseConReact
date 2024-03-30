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
    window.location.href = "/direcGimnasio/" + idGim;
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