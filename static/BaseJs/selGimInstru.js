var cont = document.getElementById("Instructor");
function aUsuGim(){
    fetch("/selGimInstru").then((response) => {
        response.json().then((data) => {
            let text = "";
            for(let i = 0; i < data['lim']; i++){
                text += "<option value='" + data['value'][i]
                + "'>" + data['text'][i] + "</option>";
            }
            let val = document.getElementsByName("instru").length;
            if (!val){
                val = 0;
            }
            cont.innerHTML += "<div name='contIsntru' id='contIsntru-" + val + "'><select name='instru'>" + text
            + "</select><button class='btnRedondeado' type='button' name='elimUsuGim' id='elimUsuGim' onclick='eUsuGim("
            + val + ")'>Eliminar</button></div>";
        });
    });
}
function eUsuGim(pos){
    let del = document.getElementById("contIsntru-" + pos);
    cont.removeChild(del);
    let reco = document.getElementsByName("contIsntru");
    let i = 0;
    reco.forEach(elem => {
        elem.setAttribute("id","contIsntru-" + i);
        i++;
    });
    reco = document.getElementsByName("elimUsuGim");
    i = 0;
    reco.forEach(elem => {
        elem.setAttribute("id","elimUsuGim-" + i);
        elem.setAttribute("onclick","eUsuGim(" + i + ")");
        i++;
    });
}