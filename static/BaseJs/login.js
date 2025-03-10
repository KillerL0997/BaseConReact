var contra = document.getElementsByName("contra")[0];
var check = document.getElementById("checkContra");

function mostrarContra(){
    if (check.innerHTML == "visibility_off"){
        contra.type = "";
        check.innerHTML = "visibility";
    } else {
        contra.type = "password";
        check.innerHTML = "visibility_off";
    }
}