verEvento();
var deta = document.getElementById("detalles");
function verEvento() {
    let tipo = document.getElementById("tipoEvento");
    let fDesde = document.getElementById("fDesde");
    let fHasta = document.getElementById("fHasta");
    filtarEvento(
        "/verEvento/" + (((tipo.value) ? tipo.value : 0)) + "/" +
        ((fDesde.value) ? fDesde.value : "-") + "/" +
        ((fHasta.value) ? fHasta.value : "-")
    );
}
function filtarEvento(url) {
    tabla = document.getElementById("TablaEvento");
    tabla.innerHTML = "";
    fetch(url).then((response) => {
        response.json().then((data) => {
            for (let i = 0; i < data['lim']; i++) {
                tabla.innerHTML += "<tr><td>"
                    + data['fecha'][i] + "</td><td>"
                    + data['tipo'][i] +
                    "</td><td><button class='btnRedondeado' onclick=location.href='/detalleEvento/"
                    + data['id'][i] + "'>Ver</button></td></tr>";
            }
        });
    });
}