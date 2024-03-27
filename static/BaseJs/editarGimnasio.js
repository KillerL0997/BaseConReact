var cont = document.getElementById("Instructor");
var hora = document.getElementById("Horarios");
var valSelUsu = [];
const valGim = document.getElementById("hidden").value;
const bVals = [
    "Nombre","Direccion","Ubicacion",
    "Instagram","Conta","Facebook"
];
const dVals = [
    'nom', 'direc', 'ubi',
    'insta', 'face', 'whats'
];
const vecDias= [
    "Lunes", "Martes", "Miercoles", "Jueves",
    "Viernes", "Sabado", "Domingo"
];
const vecNums = [1,2,3,4,5,6,7];
cargarGimnasio();
function cargarGimnasio(){ 
    fetch("/cargarGimnasio/" + valGim).then( response => {
        response.json().then( data => {
            for(let i = 0; i < bVals.length; i++){
                document.getElementById(bVals[i]).value = data[dVals[i]];
            }
            let selec = "";
            for(let i = 0; i < data['limAct']; i++){
                let text = preparaText(data['limGen'],data['valGen'],data['usuGen']);
                selec += "<div name='contIsntru' id='contIsntru-" + i +
                "'><select name='instru'>" + text +
                "</select><button type='button' class='btnRedondeado' name='elimUsuGim' id='elimUsuGim' onclick='eUsuGim("
                + i + ")'>Eliminar</button></div>";
            }
            cont.innerHTML += selec;
            selUsu = document.getElementsByName("instru");
            for(let i = 0; i < data['limAct']; i++){
                selUsu[i].value = data['valAct'][i];
            }
            hora = document.getElementById("Horarios");
            let opcEdad = preparaOpc(3,70);
            let text = preparaText(data['limHora'],data['valHora'],data['textHora']);
            let sel = preparaText(vecDias.length,vecNums,vecDias);
            for(let i = 0; i < data['limHora']; i++){
                hora.innerHTML += "<div name='contHora' id='contHora-" + i
                + "'><select class='Hora' name='Hora'>" + text + "</select><section><h4>Edades</h4><div>" +
                "<label>Desde:</label><select name='edadIni'>" + opcEdad
                + "</select><label>Hasta:</label><select name='edadFin'>" + opcEdad +
                "</select></div></section><section><h4>Horario</h4><div><label>Desde:</label>" + 
                "<input type='time' name='horaIni'><label>Hasta:</label><input type='time' name='horaFin'></div>" 
                + "</section><section id='diaClase'><h4>Dia de clases</h4><select name='diaClase'>"
                + sel + "</select></section><button class='btnRedondeado' type='button' name='elimHora' onclick='eHoraGim("
                + i + ")'>Eliminar</button></div>";
            }
            let valHora = document.getElementsByName("Hora");
            let valEdadIni = document.getElementsByName("edadIni");
            let valEdadFin = document.getElementsByName("edadFin");
            let valHoraIni = document.getElementsByName("horaIni");
            let valHoraFin = document.getElementsByName("horaFin");
            let selDia = document.getElementsByName("diaClase");
            for(let i = 0; i < data['limHora']; i++){
                valHora[i].value = data['valHora'][i];
                valEdadIni[i].value = data['edadIni'][i];
                valEdadFin[i].value = data['edadFin'][i];
                valHoraIni[i].value = data['horaIni'][i];
                valHoraFin[i].value = data['horaFin'][i];
                selDia[i].value = data['dia'][i];
            }
        });
    });
}
function aUsuGim(){
    fetch("/selGimInstru").then((response) => {
        response.json().then((data) => {
            let text = preparaText(data['lim'],data['value'],data['text']);
            let val = document.getElementsByName("instru").length;
            let div = document.createElement("div");
            div.setAttribute("name","contIsntru");
            div.setAttribute("id","contIsntru-" + val);
            div.innerHTML += "<select name='instru'>" + text
            + "</select><button type='button' class='btnRedondeado' name='elimUsuGim' id='elimUsuGim' onclick='eUsuGim("
            + val + ")'>Eliminar</button>";
            cont.appendChild(div);
        });
    });
}
function eUsuGim(pos){
    let del = document.getElementById("contIsntru-" + pos);
    cont.removeChild(del);
    preparaSel(document.getElementsByName("contIsntru"),"id","contIsntru-",0);
    preparaSel(document.getElementsByName("elimUsuGim"),"id","elimUsuGim-",0);
    preparaBot(document.getElementsByName("elimUsuGim"),"onclick","eUsuGim",0);
}
function aHoraGim(){
    fetch("/aHoraGim/" + valGim).then( response => {
        response.json().then( data => {
            let pos = document.getElementsByName("contHora").length;
            let text = preparaText(data['lim'],data['value'],data['text']);
            let opcEdad = preparaOpc(3,70);
            let sel = preparaText(vecDias.length,vecNums,vecDias);
            let div = document.createElement("div");
            div.setAttribute("name","contHora");
            div.setAttribute("id","contHora-" + pos);
            div.innerHTML += "<select class='Hora' name='Hora'>" + text +
            "</select><section><h4>Edades</h4><div>" +
            "<label>Desde:</label><select name='edadIni'>" + opcEdad
            + "</select><label>Hasta:</label><select name='edadFin'>" + opcEdad +
            "</select></div></section><section><h4>Horario</h4><div><label>Desde:</label>"
            + "<input type='time' name='horaIni'><label>Hasta:</label>"
            + "<input type='time' name='horaFin'></div></section><section id='diaClase'>" 
            + "<h4>Dia de clases</h4><select name='diaClase'>" + sel
            + "</select></section><button type='button' class='btnRedondeado' name='elimHora' onclick='eHoraGim("
            + pos + ")'>Eliminar</button>";
            hora.appendChild(div);
        });
    });
}
function eHoraGim(pos){
    remo = document.getElementById("contHora-" + pos);
    hora.removeChild(remo);
    preparaSel(document.getElementsByName("contHora"),"id","contHora-",0);
    preparaBot(document.getElementsByName("elimHora"),"onclick","eHoraGim",0);
}
function preparaOpc(ini, fin){
    opc = "";
    for(let i = ini; i <= fin; i++){
        opc += "<option value=" + i + ">" + i + "</option>";
    }
    return opc;
}
function preparaText(lim,value,conte){
    let text = "";
    for(let i = 0; i < lim; i++){
        text += "<option value=" + value[i] + ">" + conte[i] + "</option>";
    }
    return text;
}
function preparaSel(reco,atri,val,pos){
    reco.forEach( elem => {
        elem.setAttribute(atri,val + pos);
        pos++;
    });
}
function preparaBot(reco,atri,func,pos){
    reco.forEach( elem => {
        elem.setAttribute(atri,func + "(" + pos + ")");
        pos++;
    });
}