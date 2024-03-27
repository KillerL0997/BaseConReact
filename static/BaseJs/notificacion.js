check = document.getElementById("1");
checkDest = document.getElementsByName("Destino");
checkDest.forEach(elem => {
    elem.onchange = cambio;
});
function cambio(){
    if(check.disabled){
        check.disabled = false;
        check.checked = false;
    }
}
check.onchange = () => {
    if (check.checked){
        check.disabled = true;
        checkDest.forEach(elem => {
            elem.checked = true;
        });
    }
}