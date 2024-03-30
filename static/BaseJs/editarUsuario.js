const vecId = [
    "Nombre","Apellido","Categoria",
    "Cargo","Email","TipoDocumento",
    "Documento","Cabe","Instru"
];
const vecPos = [
    'nom', 'ape', 'cate', 'cargo', 'mail',
    'tdoc', 'doc', 'cabeza', 'instructor'
]
let carga = document.getElementById("busca").value.split(",");
cargarUsuario(carga[0],carga[1]);
function cargarUsuario(tdoc,doc){
    fetch("/cargarUsuario/" + tdoc + "/" + doc).then((response) => {
        response.json().then((data) => {
            let lim = vecId.length;
            for(let i = 0; i < lim; i++){
                document.getElementById(vecId[i]).value = data[vecPos[i]];
            }
        });
    });
}