instru = document.getElementById("Instru");
instru.onchange = cambiaSelGim;
cambiaSelGim();
verMensaje();
function verMensaje(){
    msj = document.getElementById("msj");
    if(msj.value != " ") {
        window.alert(msj.value);
    }
}
function cambiaSelGim(){
    gim = document.getElementById("Gim");
    gim.innerHTML = "";
    if(instru.value != ","){
        valInstru = instru.value.split(",");
        fetch("/cambioGim/" + valInstru[0] + "/" + valInstru[1]).then((response) => {
            response.json().then((data) => {
                for(let i = 0; i < data['cant']; i++){
                    gim.innerHTML += "<option value='" + data['idGim'][i] + "'>"
                    + data['nomGim'][i] + " " + data['direGim'][i] + "</option>";
                }
            });
        });
    }
}
function agregarTelefono(){
    lugar = document.getElementById("ContactoAlumno");
    cant = document.getElementsByName("Contacto").length;
    div = document.createElement("div");
    div.setAttribute("id","cAlumno-" + cant);
    div.setAttribute("name","cAlumno");
    div.setAttribute("class","contactoAlu");
    div.innerHTML += "<label for='Contacto'>Contacto</label><input type='text' name='Contacto'>";
    div.innerHTML += "<label for='Telefono'>Telefono</label><input type='text' name='Telefono'>";
    div.innerHTML += "<button class='btnRedondeado' type='button' name='elimTel' onclick='eliminarTelefono(" + cant +")'>Eliminar</button>";
    lugar.appendChild(div);
}
function eliminarTelefono(pos){
    cont = document.getElementById("ContactoAlumno");
    remo = document.getElementById("cAlumno-" + pos);
    cont.removeChild(remo);
    reco = document.getElementsByName("cAlumno");
    let i = 0;
    reco.forEach(element => {
        element.setAttribute("id","cAlumno-" + i);
        i++;
    });
    i = 0;
    reco = document.getElementsByName("elimTel");
    reco.forEach(element => {
        element.setAttribute("onclick","eliminarTelefono(" + i +")");
        i++;
    });
}