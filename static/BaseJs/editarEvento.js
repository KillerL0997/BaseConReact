const bVals = ["Fecha","Tipo","Descripcion"];
const bDic = ["fecha","tipo","desc"];
cargarEvento(document.getElementById("hidden").value);
function cargarEvento(idEve){
    fetch("/cargarEvento/" + idEve).then(response => {
        response.json().then(data => {
            for(let i = 0; i < bVals.length; i++){
                console.log(data[bDic[i]]);
                document.getElementById(bVals[i]).value = data[bDic[i]];
            }
        });
    });
}