const alu = document.getElementById("hidden").value.split(",");
const vBusca = [
    "Nombre", "Apellido", "TipoDocumento", "Documento",
    "Categoria", "Nacionalidad", "fInscripcion", "Observaciones",
    "Mail", "Localidad", "fNacimiento", "Instru", "Gim"
];
const vVals = [
    'nom', 'ape', 'tdoc', 'doc','cate', 'nacio', 'fIns', 'ibs',
    'mail', 'loc', 'fnac','instru', 'idgim'
];
cargarAlumno(alu[0],alu[1]);
function cargarAlumno(tdoc,doc){
    fetch("/cargarAlumno/" + tdoc + "/" + doc + "").then( response => {
        response.json().then( data => {
            for(let i = 0; i < vBusca.length; i++){
                document.getElementById(vBusca[i]).value = data[vVals[i]];
            }
            cont = document.getElementById("ContactoAlumno")
            cant = document.getElementsByName("Contacto").length;
            for(let i = 0; i < data['limTel']; i++, cant++){
                div = document.createElement("div");
                div.setAttribute("id","cAlumno-" + cant);
                div.setAttribute("name","cAlumno");
                text = "<div><label for='Contacto'>Contacto</label><input type='text' value='"
                + data['cont'][i]
                + "' name='Contacto'></div><div><label for='Telefono'>Telefono</label><input type='text' value='"
                + data['tel'][i]
                + "' name='Telefono'></div><button class='btnRedondeado' type='button' name='elimTel' onclick='eliminarTelefono("
                + cant +")'>Eliminar</button>";
                div.innerHTML = text;
                cont.appendChild(div);
            }
        });
    });
}