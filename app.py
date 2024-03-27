from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify, session
from flask_uploads import IMAGES, UploadSet, configure_uploads
from models import *
import os
import pyodbc
import shutil
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(
    app.root_path, 'static/Imagenes')
app.config['UPLOADED_PHOTOS_ALLOW'] = set(
    ['png', 'jpg', 'jpeg', 'jfif', 'jpeg'])
app.config['SECRET_KEY'] = 'Taekwon-do_Enat'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-TFA1LI9\SQLEXPRESS;Database=BaseEnat;UID=Leo;PWD=12345'
).cursor()

# @app.route("/")
# def index():
#     return app.send_static_file("index.html")

@app.route("/gimPagina")
def gimPagina():
    gim = conn.execute(
        "select * from gimnasio"
    ).fetchall()
    dicGim = {
        'id': [], 'nombre': [], 'direc': [], 'face': [], 'insta': [], 'ubi': [],
        'whats': [], 'logo': [], 'lim' : 0, 'instru': [], 'horario': []
    }
    for id, nom, dir, face, insta, ubi, whats, logo in gim:
        instru = ""
        hora = ""
        dicGim['id'].append(id)
        dicGim['nombre'].append(nom)
        dicGim['direc'].append(dir)
        dicGim['face'].append(face)
        dicGim['insta'].append(insta)
        dicGim['ubi'].append(ubi)
        dicGim['whats'].append(whats)
        dicGim['logo'].append('static/' + logo)
        dicGim['lim'] += 1
        for nom, ape in conn.execute(
            "select u.nombre, u.apellido "
            "from gimnasio g, usuario u, enseñaen ee "
            "where ee.idgim=g.id and ee.tdoc=u.tdoc and ee.doc=u.documento and g.id='" + str(id) + "'"  
        ).fetchall():
            instru += f'{nom} {ape} '
        dicGim['instru'].append(instru[:-1])
        for eIni, eFin, hIni, hFin, dia in conn.execute(
            "select h.edadini, h.edadfin, h.horaini, h.horafin, d.tipo "
            "from horario h, dia d "
            "where h.idgim='" + str(id) + "' and h.dia=d.id"
        ).fetchall():
            hora.append(f'<p>{dia} de {eIni} a {eFin} años: {hIni} a {hFin} Hs</p>,')
        dicGim['horario'].append(hora[:-1])
    return jsonify(dicGim)

@app.route("/fechaEvento")
def fechaEvento():
    resuExa = fechaEvento(1)
    resuTor = fechaEvento(2)
    resuEve = fechaEvento(3)
    fExamen = "Sin fecha de examen"
    fTorneo = "Sin fecha de torneo"
    fEvento = "Sin fecha de evento"
    if resuExa:
        fExamen = f'Proximo examen: {resuExa}'
    if resuTor:
        fTorneo = f'Proximo torneo: {resuTor}'
    if resuEve:
        fEvento = f'Proximo evento: {resuEve}'
    return jsonify({
        'fExamen': fExamen, 'fTorneo': fTorneo, 'fEvento': fEvento
    })

def fechaEvento(tipo):
    return conn.execute(
        "select isnull(convert(varchar,min(e.fecha),3),'') "
        "from evento e "
        "where e.tipo='" + str(tipo) + "' and e.fecha >= getdate()"
    ).fetchone()[0]

@app.route("/buscaFotos")
def buscaFotos():
    examen = buscaFotosEvento("1")
    torneo = buscaFotosEvento("2")
    evento = buscaFotosEvento("3")
    vecExa = []
    vecTor = []
    vecEve = []
    for direc, _ in examen:
        vecExa.append("static/" + direc)
    for direc, _ in torneo:
        vecTor.append("static/" + direc)
    for direc, _ in evento:
        vecEve.append("static/" + direc)
    return jsonify({
        'vecExa': vecExa, 'vecTor': vecTor, 'vecEve': vecEve
    })

def buscaFotosEvento(tipo):
    return conn.execute(
        "select i.direccion, 1 "
        "from imagen i, ("
            "select top 1 e.id as idEve "
            "from evento e "
            "where e.tipo='" + tipo + "' and e.fecha <= getdate() "
            "order by e.fecha DESC"
        ") as eve "
        "where i.idevento=eve.idEve"
    ).fetchall()

@app.route("/")
@app.route("/MainBase")
def main():
    if not session or 'tdoc' not in session:
        return redirect(url_for("login"))
    gim = conn.execute(
        "select 1 from gimnasio g, enseñaen ee "
        "where ee.tdoc=" + str(session['tdoc']) + " and ee.doc='" + session['doc']
        + "' and ee.idgim=g.id"
    ).fetchall()
    noti = conn.execute(
        "select n.id, n.texto "
        "from notificacion n, notifica nt "
        "where nt.tdoc=" + str(session['tdoc']) + " and nt.documento='" + session['doc']
        + "' and nt.idnoti=n.id "
    ).fetchall()
    return render_template(
        "Inicio.html", tdoc = session['tdoc'], doc = session['doc'],
        cargo = session['cargo'], gim = gim, noti = noti
    )

def tiempoSesion(): 
    tiempo = conn.execute(
        "select u.sesion from usuario u "
        "where u.tdoc=" + str(session['tdoc'])
        + " and u.documento='" + session['doc'] + "'"
    ).fetchone()[0]
    if tiempo and tiempo + timedelta(hours=1) < datetime.now():
        return redirect(url_for("logout")) 
    upTabla(
        "usuario","sesion=getdate()",
        "tdoc=" + str(session['tdoc']) + " and documento='" + session['doc'] + "'"
    )
    conn.commit()

@app.route("/login", methods={"GET", "POST"})
def login():
    if request.method == 'POST':
        usu = conn.execute(
            "select u.tdoc, u.documento, u.cargo from usuario u "
            "where u.email='" + request.form.get("mail") +"' and u.contraseña='"
            + request.form.get("contra") + "'"
        ).fetchone()
        if usu:
            session['tdoc'] = usu[0]
            session['doc'] = usu[1]
            session['cargo'] = usu[2]
            upTabla(
                "usuario","sesion=getdate()",
                "tdoc=" + str(session['tdoc']) + " and documento='" + session['doc'] + "'"
            )
            conn.commit()
            return redirect("/MainBase")
    return render_template("Login.html")

@app.route("/logout")
def logout():
    try:
        session.pop("tdoc")
        session.pop("doc")
        session.pop("cargo")
    finally:
        return redirect("/MainBase")

@app.route("/cambiarContra/<string:tdoc>/<string:doc>", methods={'GET','POST'})
def cambiarContra(tdoc,doc):
    tiempoSesion()
    if request.method == 'POST':
        contra1 = request.form.get("contra_1")
        contra2 = request.form.get("contra_2")
        if contra1 and contra2 and contra1 == contra2:
            contraUsu = conn.execute(
                "select u.contraseña from usuario u "
                "where u.tdoc=" + tdoc + " and u.documento='" + doc + "'"
            ).fetchone()[0]
            if contra1 == contraUsu:
                return render_template(
                    "cambiarContra.html", msj = "La nueva contraseña es igual a la anterior"
                )
            upTabla(
                "usuario","contraseña='" + contra1 + "'",
                "tdoc=" + tdoc + "and documento='" + doc + "'"
            )
            conn.commit()
            return redirect("/MainBase")
        return render_template(
                    "cambiarContra.html", msj = "Las contraseñas no coinciden"
                )
    return render_template("cambiarContra.html", msj = "")

# Agregar


@app.route("/aUsuario", methods={'GET', 'POST'})
def aUsuraio():
    tiempoSesion()
    cargo = conn.execute('select * from cargo').fetchall()
    categoria = conn.execute(
        "select * from categoria c where c.id > 10").fetchall()
    tDoc = conn.execute("select * from tipodocumento").fetchall()
    instructor = conn.execute(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo '
        'from usuario u, categoria c '
        'where u.cargo <> 1 and c.id = u.categoria'
    ).fetchall()
    instructor.insert(0, ('', '', '', '', ''))
    cabeza = conn.execute(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo '
        'from usuario u, categoria c '
        'where u.cargo = 2 and c.id = u.categoria'
    ).fetchall()
    cabeza.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        cUsuario = request.form.get("Cargo")
        tDocUsu = request.form.get("TipoDocumento")
        docUsu = request.form.get("Documento")
        conn.execute(
            "insert into usuario (nombre,apellido,categoria,cargo,contraseña,email,tdoc,documento) values('"
            + request.form.get("Nombre").capitalize() + "','" +
            request.form.get("Apellido").capitalize()
            + "'," + request.form.get("Categoria") + "," + cUsuario
            + ",'Taekwondo','" + request.form.get("Email") + "'," + tDocUsu
            + ",'" + docUsu + "')"
        )
        if int(cUsuario) == 2:
            insTabla(
                "cabeza","tdoccabeza,doccabeza,tdoc,documento",
                tDocUsu + ",'" + docUsu + "'," + tDocUsu + ",'" + docUsu + "'"
            )
        elif int(cUsuario) == 3:
            insTabla(
                "instructor","tdocinstru,docinstru,tdoc,documento",
                tDocUsu + ",'" + docUsu + "'," + tDocUsu + ",'" + docUsu + "'"
            )
            aInstruCab("Cabe", "cabeza", "tdoccabeza",
                       "doccabeza", tDocUsu, docUsu)
            aInstruCab("Instru", "instructor", "tdocinstru",
                       "docinstru", tDocUsu, docUsu)
        conn.commit()
        return redirect("/MainBase")
    return render_template(
        "/Agregar/AgregarUsuario.html", cargo=cargo,
        categoria=categoria, tDoc=tDoc, instructor=instructor,
        cabeza=cabeza
    )


def aInstruCab(busca, tabla, col1, col2, tDocUsu, docUsu):
    tiempoSesion()
    dato = request.form.get(busca).split(",")
    if dato[0] and dato[1]:
        conn.execute(
            "insert into " + tabla + " (" + col1 +
            "," + col2 + ",tdoc,documento) values ("
            + dato[0] + ",'" + dato[1] + "'," + tDocUsu + ",'" + docUsu + "')"
        )


@app.route("/aGimnasio", methods={'GET', 'POST'})
def aGimnasio():
    tiempoSesion()
    if request.method == 'POST' and request.files["Logo"] and (instru := request.form.getlist("instru")):
        nomGim = request.form.get("Nombre").capitalize()
        direcGim = request.form.get("Direccion").capitalize()
        if conn.execute(
            "select 1 from gimnasio g where g.nombre='"
            + nomGim + "' and g.direccion='" + direcGim + "'"
        ).fetchall():
            return redirect("/MainBase")
        i = 1
        lim = conn.execute(
            "select coalesce(max(g.id),1) from gimnasio g"
        ).fetchone()[0]
        while i <= lim and conn.execute(
            f'select 1 from gimnasio where id = {str(i)}'
        ).fetchone():
            i += 1
        nombre = ""
        nombre = photos.save(
            request.files["Logo"], nomGim.replace(" ", "")
        )
        conn.execute(
            "insert into gimnasio(id,nombre,direccion,ubicacion,instagram,face,whats,logo) values("
            + str(i) + ",'" + nomGim + "','" + direcGim + "','"
            + request.form.get("Ubicacion") + "','" +
            request.form.get("Instagram") + "','"
            + request.form.get("Contacto") + "','" +
            request.form.get("Facebook") + "','Imagenes"
            + url_for('obtener_nombre', filename=nombre)[8:] + "')"
            )
        for dato in instru:
            dato = dato.split(",")
            if not conn.execute(
                "select 1 from enseñaen en "
                "where en.tdoc=" + dato[0] + " and en.doc='" + dato[1]
                + "' and en.idgim=" + str(i)
            ).fetchone():
                conn.execute(
                    "insert into enseñaen(tdoc,doc,idgim) values("
                    + dato[0] + ",'" + dato[1] + "'," + str(i) + ")"
                    )
                conn.commit()
                nomUsu = conn.execute(
                    "select u.apellido, u.nombre "
                    "from usuario u where u.tdoc=" +
                    dato[0] + " and u.documento='" + dato[1] + "'"
                    ).fetchone()
                os.makedirs(
                    f'static/Imagenes/{nomGim.replace(" ","")}/{nomUsu[0]}{nomUsu[1]}'
                    )
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarGimnasio.html")

@app.route("/selGimInstru")
def selGimInstru():
    tiempoSesion()
    condiEx = ""
    if session['cargo'] == 2: 
        condiEx = " and exists(select 1 from cabeza ca where ca.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and ca.tdoccabeza=" + str(session['tdoc'])
        condiEx += " and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    usuario = conn.execute(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo'
        ' from usuario u, categoria c'
        ' where u.cargo <> 1 and c.id = u.categoria' + condiEx
    ).fetchall()
    dic = {'value': [], 'text': [], 'lim': 0}
    for tdoc, doc, ape, nom, cate in usuario:
        dic['value'].append(f'{tdoc},{doc}')
        dic['text'].append(f'{ape} {nom} {cate}')
        dic['lim'] += 1
    return jsonify(dic)

@app.route("/aEvento", methods={'GET', 'POST'})
def aEvento():
    tiempoSesion()
    tipo = conn.execute('select * from tipoevento').fetchall()
    if request.method == 'POST':
        eFecha = request.form.get("Fecha")
        eTipo = request.form.get("Tipo")
        i = 1
        while conn.execute(
            "select 1 from evento e where e.id=" + str(i)
        ).fetchone():
            i += 1
        if not conn.execute(
            "select 1 from evento e where e.fecha='" + eFecha + "' and e.tipo=" + eTipo
        ).fetchone():
            conn.execute(
                "insert into evento (id,tipo,fecha,descripcion) values ("
                + str(i) + "," + eTipo + ",'"
                + eFecha + "','" + request.form.get("Descripcion") + "')"
            )
            conn.commit()
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarEvento.html", tipoEvento=tipo)


@app.route("/aAlumno", methods={'GET', 'POST'})
def aAlumno():
    tiempoSesion()
    categoria = conn.execute("select * from categoria").fetchall()
    tDoc = conn.execute("select * from tipodocumento").fetchall()
    condiEx = ""
    if session['cargo'] == 2: 
        condiEx = " and exists(select 1 from cabeza ca where ca.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and ca.tdoccabeza=" + str(session['tdoc'])
        condiEx += " and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    elif session['cargo'] == 3:
        condiEx = " and exists(select 1 from instructor i where i.docinstru='"
        condiEx += session['doc']
        condiEx += "' and i.tdocinstru=" + str(session['tdoc'])
        condiEx += " and i.tdoc=u.tdoc and i.documento=u.documento)"
    query = "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
    query += " from usuario u, categoria c, enseñaen ee"
    query += " where ee.tdoc = u.tdoc and ee.doc= u.documento and c.id = u.categoria" + condiEx
    usuario = conn.execute(
        query + " group by u.tdoc,u.documento,u.apellido,u.nombre,c.tipo "
    ).fetchall()
    usuario.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        instru = request.form.get("Instructor").split(",")
        idGim = request.form.get("Gimnasio")
        nomGim = conn.execute(
            "select g.nombre from gimnasio g where g.id=" + idGim
        ).fetchone()[0]
        nomUsu = conn.execute(
            "select u.apellido, u.nombre from usuario u "
            "where u.tdoc=" + instru[0] + " and u.documento=" + instru[1]
        ).fetchone()
        nombre = 'SinFoto.jpg'
        if request.files["Foto"]:
            nombre = photos.save(
                request.files["Foto"], f'{nomGim.replace(" ","")}/{nomUsu[0]}{nomUsu[1]}'
            )
        tdoc = request.form.get("TipoDocumento")
        doc = request.form.get("Documento")
        conn.execute(
            "insert into alumno("
            "nombre,apellido,tdoc,documento,categoria,nacionalidad,finscripcion,observaciones,"
            "email,localidad,fnac,libreta,foto,tdocinstru,docinstru,idgim"
            ") values('"
            + request.form.get("Nombre").capitalize() + "','" +
            request.form.get("Apellido").capitalize() + "'," + tdoc
            + ",'" + doc + "'," + request.form.get("Categoria") +
            ",'" + request.form.get("Nacionalidad").capitalize() + "','"
            + request.form.get("fInscripcion") + "','" +
            request.form.get("Observaciones") + "','"
            + request.form.get("Mail") + "','"
            + request.form.get("Localidad").capitalize() + "','"
            + request.form.get("fNacimiento") + "'," +
            request.form.get("Libreta") + ",'Imagenes"
            + url_for('obtener_nombre',
                      filename=nombre)[8:] + "'," + instru[0] + ",'" + instru[1]
            + "'," + idGim + ")"
        )
        contacto = request.form.getlist("Contacto")
        telefono = request.form.getlist("Telefono")
        for con, tel in zip(contacto, telefono):
            if con and tel:
                conn.execute(
                    "insert into telefono(telefono,contacto,tdoc,documento) values ('"
                    + tel + "','" + con + "'," + tdoc + ",'" + doc + "')"
                )
        conn.commit()
        return redirect("/MainBase")
    return render_template(
        "/Agregar/AgregarAlumno.html", categoria=categoria,
        tdoc=tDoc, usuario=usuario
    )


@app.route("/aNotificacion", methods={'GET', 'POST'})
def aNotificacion():
    tiempoSesion()
    usuario = conn.execute(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo, 0 "
        "from usuario u, categoria c "
        "where c.id = u.categoria"
    ).fetchall()
    usuario.insert(0, ('', '', 'Todos', '', '', 1))
    if request.method == 'POST':
        i = 1
        while conn.execute(
            "select 1 from notificacion n where n.id=" + str(i)
        ).fetchone():
            i += 1
        i = str(i)
        app.logger.debug(i)
        conn.execute(
            "insert into notificacion(id,texto) values(" + i + ",'"
            + request.form.get("Descripcion") + "')"
        )
        destino = request.form.getlist("Destino")
        for item in destino:
            dest = item.split(",")
            conn.execute(
                "insert into notifica(tdoc,documento,idnoti) values("
                + dest[0] + ",'" + dest[1] + "'," + i + ")"
            )
        conn.commit()
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarNotificacion.html", usuario=usuario)


@app.route("/aImagen", methods={'GET', 'POST'})
def aImagen():
    tiempoSesion()
    fEvento = conn.execute(
        "select max(e.fecha), e.tipo from evento e "
        "group by e.tipo"
    ).fetchall()
    evento = []
    for fecha, tipo in fEvento:
        evento.append((conn.execute(
            "select e.id from evento e where e.fecha='" +
            str(fecha) + "' and e.tipo=" + str(tipo)
        ).fetchone()[0], fecha, conn.execute(
            "select te.tipo from tipoevento te where te.id=" + str(tipo)
        ).fetchone()[0]))
    if request.method == 'POST' and request.files["Foto"]:
        idEve = request.form.get("Evento")
        direc = conn.execute(
            "select i.direccion from imagen i "
            "where i.idevento=" + idEve
        ).fetchall()
        for elim in direc:
            os.remove(f'static/{elim[0]}')
        conn.execute(
            "delete from imagen where idevento=" + idEve
        )
        tipo = conn.execute(
            "select te.tipo "
            "from evento e, tipoevento te "
            "where e.id=" + idEve + " and e.tipo=te.id"
        ).fetchone()[0]
        for i in request.files.getlist("Foto"):
            nombre = photos.save(
                i, f'Eventos/{tipo}'
            )
            conn.execute(
                "insert into imagen(idevento,direccion) values("
                + idEve + ",'Imagenes"
                + url_for('obtener_nombre', filename=nombre)[8:] + "')"
            )
        conn.commit()
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarImagen.html", evento=evento)

# Ver


@app.route("/vUsuario")
def vUsuario():
    tiempoSesion()
    return render_template("/Ver/VerUsuario.html")


@app.route("/verUsuario/<int:tUsuario>")
def verUsuario(tUsuario):
    tiempoSesion()
    usuario = conn.execute(
        "select u.nombre, u.apellido, c.tipo, u.tdoc, u.documento "
        "from usuario u, categoria c "
        "where u.cargo=" + str(tUsuario) + " and u.categoria=c.id"
    ).fetchall()
    dicUsu = {
        'nomUsu': [], 'apeUsu': [], 'cateUsu': [], 'lim': 0,
        'tdocUsu': [], 'docUsu': []
    }
    llenarDiccionarioUsuario(usuario, dicUsu)
    return jsonify(dicUsu)


@app.route("/verInstructores")
def verInstructores():
    tiempoSesion()
    usuario = conn.execute(
        "select u.nombre, u.apellido, c.tipo, u.tdoc, u.documento "
        "from usuario u, categoria c, enseñaen ee "
        "where u.tdoc=ee.tdoc and u.documento=ee.doc and u.categoria=c.id "
        "group by u.nombre, u.apellido, c.tipo, u.tdoc, u.documento"
    ).fetchall()
    dicUsu = {
        'nomUsu': [], 'apeUsu': [], 'cateUsu': [], 'lim': 0,
        'tdocUsu': [], 'docUsu': []
    }
    llenarDiccionarioUsuario(usuario, dicUsu)
    return jsonify(dicUsu)


@app.route("/verTodoUsuario")
def verTodoUsuario():
    tiempoSesion()
    usuario = conn.execute(
        "select u.nombre, u.apellido, c.tipo, u.tdoc, u.documento "
        "from usuario u, categoria c "
        "where u.categoria=c.id"
    ).fetchall()
    dicUsu = {
        'nomUsu': [], 'apeUsu': [], 'cateUsu': [], 'lim': 0,
        'tdocUsu': [], 'docUsu': []
    }
    llenarDiccionarioUsuario(usuario, dicUsu)
    return jsonify(dicUsu)


def llenarDiccionarioUsuario(recorrer, dicUsu):
    for elem1, elem2, elem3, elem4, elem5 in recorrer:
        dicUsu['nomUsu'].append(elem1)
        dicUsu['apeUsu'].append(elem2)
        dicUsu['cateUsu'].append(elem3)
        dicUsu['tdocUsu'].append(elem4)
        dicUsu['docUsu'].append(elem5)
        dicUsu['lim'] += 1


@app.route("/vGimnasio")
def vGimnasio():
    tiempoSesion()
    condiEx = "(select ee.doc, ee.tdoc from enseñaen ee group by ee.doc, ee.tdoc) uee"
    if session['cargo'] == 2:
        condiEx = "(select ee.tdoc, ee.doc from enseñaen ee, cabeza c, usuario u where c.tdoccabeza="
        condiEx += str(session['tdoc']) + " and c.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and c.documento=u.documento and c.tdoc=u.tdoc and ee.tdoc=u.tdoc and ee.doc=u.documento "
        condiEx += "GROUP by ee.tdoc, ee.doc) as uee"
    elif session['cargo'] == 3:
        condiEx = "(select ee.tdoc, ee.doc from enseñaen ee, instructor i, usuario u where i.tdocinstru="
        condiEx += str(session['tdoc']) + " and i.docinstru='"
        condiEx += session['doc']
        condiEx += "' and i.documento=u.documento and i.tdoc=u.tdoc and ee.tdoc=u.tdoc and ee.doc=u.documento "
        condiEx += "GROUP by ee.tdoc, ee.doc) as uee"
    usuario = conn.execute(
        "select u.tdoc, u.documento, u.nombre, u.apellido, c.tipo"
        " from usuario u, " + condiEx + ", categoria c"
        " where u.documento=uee.doc and u.tdoc=uee.tdoc and c.id=u.categoria" 
    ).fetchall()
    usuario.insert(0, ('', '', '', '', ''))
    return render_template(
        "/Ver/VerGimnasio.html", usuario=usuario
    )


@app.route("/verGimnasio/<int:tdoc>/<string:doc>")
def verGimnasio(tdoc, doc):
    tiempoSesion()
    gimnasio = conn.execute(
        "select g.id, g.nombre, g.direccion "
        "from gimnasio g, enseñaen ee "
        "where ee.tdoc=" +
        str(tdoc) + " and ee.doc='" + doc + "' and ee.idgim=g.id"
    ).fetchall()
    dicGim = {
        'id': [], 'nom': [], 'direc': [], 'lim': 0,
        'onclick': 'desaGim', 'valBot': 'Deshabilitar',
        'verElim': "Ver", 'func': "detalleGimnasio"
    }
    llenarDiccionarioGimnasio(gimnasio, dicGim)
    return jsonify(dicGim)


@app.route("/verTodoGimnasio")
def verTodoGimnasio():
    tiempoSesion()
    query = "(select ee.idgim from enseñaen ee group by ee.idgim) as tee"
    if session['cargo'] == 2:
        query = "(select ee.idgim from enseñaen ee, cabeza c, usuario u where c.tdoccabeza=" 
        query += str(session['tdoc'])
        query +=" and c.doccabeza='" + session['doc'] 
        query += "' and c.tdoc=u.tdoc and c.documento=u.documento "
        query += "and u.tdoc=ee.tdoc and u.documento=ee.doc "
        query += "GROUP BY ee.idgim) as tee"
    elif session['cargo'] == 3:
        query = "(select ee.idgim from enseñaen ee, instructor i, usuario u where i.tdocinstru=" 
        query += str(session['tdoc'])
        query +=" and i.docinstru='" + session['doc'] 
        query += "' and i.tdoc=u.tdoc and i.documento=u.documento "
        query += "and u.tdoc=ee.tdoc and u.documento=ee.doc "
        query += "GROUP BY ee.idgim) as tee"
    gimnasio = conn.execute(
        "select g.id, g.nombre, g.direccion from " + query
        + ", gimnasio g where tee.idgim=g.id"
    ).fetchall()
    dicGim = {
        'id': [], 'nom': [], 'direc': [], 'lim': 0,
        'onclick': 'desaGim', 'valBot': 'Deshabilitar',
        'verElim': "Ver", 'func': "detalleGimnasio"
    }
    llenarDiccionarioGimnasio(gimnasio, dicGim)
    return jsonify(dicGim)


@app.route("/verDesaHabi/<int:valor>")
def verDesaHabi(valor):
    tiempoSesion()
    gimnasio = []
    dicGim = {
        'id': [], 'nom': [], 'direc': [], 'lim': 0,
        'onclick': '', 'valBot': '',
        'verElim': "Ver", 'func': "detalleGimnasio"
    }
    if valor == 0:
        gimnasio = conn.execute(
            "select g.id, g.nombre, g.direccion "
            "from gimnasio g "
            "where not exists ("
                "select 1 from enseñaen ee "
                "where ee.idgim=g.id"
            ")"
        ).fetchall()
        dicGim['onclick'] = "habiGim"
        dicGim['valBot'] = "Habilitar"
        dicGim['verElim'] = "Eliminar"
        dicGim['func'] = "elimGim"
    else:
        gimnasio = conn.execute(
            "select g.id, g.nombre, g.direccion "
            "from (select ee.idgim from enseñaen ee group by ee.idgim) as tee, gimnasio g "
            "where tee.idgim=g.id"
        ).fetchall()
        dicGim['onclick'] = "desaGim"
        dicGim['valBot'] = "Deshabilitar"
    llenarDiccionarioGimnasio(gimnasio, dicGim)
    return jsonify(dicGim)


def llenarDiccionarioGimnasio(recorrer, dicGim):
    for idGim, nomGim, direcGim in recorrer:
        dicGim['id'].append(idGim)
        dicGim['nom'].append(nomGim)
        dicGim['direc'].append(direcGim)
        dicGim['lim'] += 1


@app.route("/vEvento")
def vEvento():
    tiempoSesion()
    tEvento = conn.execute(
        "select te.id, te.tipo "
        "from tipoevento te"
    ).fetchall()
    tEvento.insert(0, ('', ''))
    return render_template("/Ver/VerEvento.html", tEvento=tEvento)


@app.route("/verEvento/<int:tipo>/<string:fDesde>/<string:fHasta>")
def verEvento(tipo, fDesde, fHasta):
    tiempoSesion()
    query = "select e.id , convert(varchar,e.fecha,3), te.tipo from evento e, tipoevento te where e.tipo=te.id "
    if tipo != 0:
        query += "and e.tipo=" + str(tipo) + " "
    if fDesde != "-":
        query += "and e.fecha >= '" + fDesde + "' "
    if fHasta != "-":
        query += "and e.fecha <= '" + fHasta + "' "
    query += "order by e.fecha desc "
    evento = conn.execute(query).fetchall()
    dicEvento = {'id': [], 'fecha': [], 'tipo': [], 'lim': 0}
    llenarDiccionarioEvento(evento, dicEvento)
    return jsonify(dicEvento)


def llenarDiccionarioEvento(recorrer, dicEven):
    for id, fecha, tipo in recorrer:
        dicEven['id'].append(id)
        dicEven['fecha'].append(fecha)
        dicEven['tipo'].append(tipo)
        dicEven['lim'] += 1


@app.route("/vAlumno")
def vAlumno():
    tiempoSesion()
    categoria = conn.execute(
        "select c.id, c.tipo from categoria c where c.id < 14"
    ).fetchall()
    categoria.insert(0, ("-", ""))
    exaCap = conn.execute(
        "select convert(varchar,min(e.fecha),3) from evento e "
        "where e.tipo=1 and e.fecha >=GETDATE()"
    ).fetchone()[0]
    exaProv = conn.execute(
        "select convert(varchar,min(e.fecha),3) from evento e "
        "where e.tipo=4 and e.fecha >=GETDATE()"
    ).fetchone()[0]
    tor = conn.execute(
        "select convert(varchar,min(e.fecha),3) from evento e "
        "where e.tipo=2 and e.fecha >=GETDATE()"
    ).fetchone()[0]
    otro = conn.execute(
        "select convert(varchar,min(e.fecha),3) from evento e "
        "where e.tipo=3 and e.fecha >=GETDATE()"
    ).fetchone()[0]
    condiGim = ""
    condiEx = ""
    if session['cargo'] == 2:
        condiEx += " and exists(select 1 from cabeza ca where ca.tdoccabeza="
        condiEx += str(session['tdoc']) 
        condiEx += " and ca.doccabeza='" + session['doc']
        condiEx += "' and ca.tdoc=u.tdoc and ca.documento=u.documento)"
        condiGim += "select g.id, g.nombre "
        condiGim += "from gimnasio g, cabeza c, usuario u, enseñaen ee "
        condiGim += "where c.tdoccabeza='" 
        condiGim += str(session['tdoc']) 
        condiGim += "' and c.doccabeza=" + session['doc']
        condiGim += " and c.tdoc=u.tdoc and c.documento=u.documento "
        condiGim += "and u.tdoc=ee.tdoc and u.documento=ee.doc"
        condiGim += " and ee.idgim=g.id group by g.id, g.nombre"
    elif session['cargo'] == 3:
        condiEx += " and exists(select 1 from instructor ca where ca.tdocinstru="
        condiEx += str(session['tdoc']) 
        condiEx += " and ca.docinstru='" + session['doc']
        condiEx += "' and ca.tdoc=u.tdoc and ca.documento=u.documento)"
        condiGim += "select g.id, g.nombre "
        condiGim += "from gimnasio g, instructor i, usuario u, enseñaen ee "
        condiGim += "where i.tdocinstru='" 
        condiGim += str(session['tdoc']) 
        condiGim += "' and i.docinstru=" + session['doc']
        condiGim += " and i.tdoc=u.tdoc and i.documento=u.documento "
        condiGim += "and u.tdoc=ee.tdoc and u.documento=ee.doc"
        condiGim += " and ee.idgim=g.id group by g.id, g.nombre"
    elif session['cargo'] == 1:
        condiGim += "select g.id, g.nombre from gimnasio g"
    usuario = conn.execute(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
        " from usuario u, categoria c"
        " where u.cargo <> 1 and u.categoria=c.id" + condiEx
    ).fetchall()
    usuario.insert(0,("","","","",""))
    gimnasio = conn.execute(condiGim).fetchall()
    gimnasio.insert(0,("",""))
    return render_template(
        "/Ver/VerAlumno.html", categoria=categoria,
        exaCap = exaCap, exaProv =exaProv, tor = tor, otro = otro, usuario=usuario,
        gimnasio = gimnasio, cargo = True if session['cargo'] == 1 else False
    )


@app.route(
        "/filtroAlumno/<string:nom>/<string:ape>/<string:cate>"
        "/<string:fdExamen>/<string:fhExamen>/<string:fdAATEE>"
        "/<string:fhAATEE>/<string:fdEnat>/<string:fhEnat>"
        "/<string:fdFetra>/<string:fhFetra>/<string:tdocUsu>"
        "/<string:docUsu>/<string:idGim>"
)
def filtroAlumno(
    nom, ape, cate, fdExamen, fhExamen,
    fdAATEE, fhAATEE, fdEnat, fhEnat, fdFetra, fhFetra,
    tdocUsu, docUsu, idGim
):
    tiempoSesion()
    query = "SELECT alucate.tdoc, alucate.documento, alucate.nombre, alucate.apellido, alucate.edad,"
    query += " alucate.tipo, alucate.insNombre, alucate.insApellido, alucate.gimNombre,"
    query += " ISNULL(CONVERT(varchar,pEvento.fecha,3),'--') as fEvento"
    query += ", ISNULL(CONVERT(varchar,aatee.fecha,3),'--') as fAATEE,"
    query += " ISNULL(CONVERT(varchar,enat.fecha,3),'--') as fEnat,"
    query += " ISNULL(CONVERT(varchar,fetra.fecha,3),'--') as fFetra "
    query += "from (SELECT a.tdoc, a.documento, a.nombre, a.apellido, c.tipo,"
    query += " floor((cast(convert(varchar(8),getdate(),112) as int) - "
    query += "cast(convert(varchar(8),a.fnac,112) as int)) / 10000) as edad,"
    query += " u.nombre as insNombre, u.apellido as insApellido, g.nombre as gimNombre"
    query += " FROM alumno a, categoria c, usuario u, gimnasio g, enseñaen ee where "
    if nom != "-":
        query += "a.nombre like'%" + nom + "%' and "
    if ape != "-":
        query += "a.apellido like'%" + ape + "%' and "
    if cate != "-":
        query += "a.categoria=" + cate + " and "
    if tdocUsu != "-" or docUsu != "-" or idGim != "-":
        if tdocUsu != "-":
            query += "a.tdocinstru=" + tdocUsu + " and "
        if docUsu != "-":
            query += "a.docinstru=" + docUsu + " and "
        if idGim != "-":
            query += "a.idgim=" + idGim + " and "
    elif session['cargo'] == 2:
        query += "exists (select 1 from usuario u, cabeza c where c.tdoccabeza= " 
        query += str(session['tdoc']) +" and c.doccabeza='" 
        query += session['doc'] + "' and u.tdoc=c.tdoc and u.documento=c.documento"
        query += " and a.tdocinstru=u.tdoc and a.docinstru=u.documento) and "
    elif session['cargo'] == 3:
        query += "exists (select 1 from usuario u, instructor i where i.tdocinstru= " 
        query += str(session['tdoc']) +" and i.docinstru='" 
        query += session['doc'] + "' and u.tdoc=i.tdoc and u.documento=i.documento"
        query += " and a.tdocinstru=u.tdoc and a.docinstru=u.documento) and "
    query += "u.tdoc=ee.tdoc and u.documento=ee.doc and ee.idgim=g.id and a.tdocinstru=u.tdoc and a.docinstru=u.documento and a.idgim = g.id and a.categoria=c.id and "
    query += "not exists (select 1 from aludesa ad where ad.tdocalu=a.tdoc and ad.docalu=a.documento)) as alucate "
    if fdExamen != "-" or fhExamen != "-":
        query += "JOIN (select max(e.fecha) as fecha, p.tdoc, p.doc from evento e, participa p WHERE e.tipo=1 "
        if fdExamen != "-" and fhExamen != "-":
            query += "and e.fecha between '" + fdExamen + "' and '" + fhExamen + "' "
        elif fdExamen != "-":
            query += "and e.fecha >= '" + fdExamen + "' "
        else:
            query += "and e.fecha <= '" + fhExamen + "' "
    else:
        query += "LEFT JOIN (select max(e.fecha) as fecha, p.tdoc, p.doc from evento e, participa p WHERE e.tipo=1 "
    query += "and e.id=p.idevento group by p.tdoc, p.doc) as pEvento on pEvento.tdoc=alucate.tdoc AND pEvento.doc=alucate.documento "
    if fdAATEE != "-" or fhAATEE != "-":
        query += "JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=1 "
        if fdAATEE != "-" and fhAATEE != "-":
            query += "and m.fecha between '" + fdAATEE + "' and '" + fhAATEE + "' "
        elif fdAATEE != "-":
            query += "and m.fecha >= '" + fdAATEE + "' "
        else:
            query += "and m.fecha <= '" + fhAATEE + "' "
    else:
        query += "LEFT JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=1 "
    query += "and m.tipo=tm.id group by m.tdoc, m.doc) AS aatee on aatee.tdoc=alucate.tdoc AND aatee.doc=alucate.documento "
    if fdEnat != "-" or fhEnat != "-":
        query += "JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=1 "
        if fdEnat != "-" and fhEnat != "-":
            query += "and m.fecha between '" + fdAATEE + "' and '" + fhAATEE + "' "
        elif fdEnat != "-":
            query += "and m.fecha >= '" + fdAATEE + "' "
        else:
            query += "and m.fecha <= '" + fhAATEE + "' "
    else:
        query += "LEFT JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=2 "
    query += "and m.tipo=tm.id group by m.tdoc, m.doc) AS enat on enat.tdoc=alucate.tdoc AND enat.doc=alucate.documento "
    if fdFetra != "-" or fhFetra != "-":
        query += "JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=3 "
        if fdFetra != "-" and fhFetra != "-":
            query += "and m.fecha between '" + fdAATEE + "' and '" + fhAATEE + "' "
        elif fdFetra != "-":
            query += "and m.fecha >= '" + fdAATEE + "' "
        else:
            query += "and m.fecha <= '" + fhAATEE + "' "
    else:
        query += "LEFT JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=3 "
    query += "and m.tipo=tm.id group by m.tdoc, m.doc) AS fetra on fetra.tdoc=alucate.tdoc AND fetra.doc=alucate.documento "
    query += "order by alucate.apellido, alucate.nombre"
    alumno = conn.execute(query).fetchall()
    dicAlu = {
        'tdoc': [], 'doc': [], 'nom': [], 'ape': [], 'cate': [], 'fecha': [],
        'fAATEE': [], 'fEnat': [], 'fFetra': [], 'lim': 0, 'insNom': [],
        'insApe': [], 'gimNom': [], 'edad': []
    }
    for tDocAlu, docAlu, nomAlu, apeAlu, edad, cateAlu, insNom, insApe, gimNom, feAlu, faAlu, fEnatAlu, fFetraAlu in alumno:
        dicAlu["tdoc"].append(tDocAlu)
        dicAlu["doc"].append(docAlu)
        dicAlu["nom"].append(nomAlu)
        dicAlu["ape"].append(apeAlu)
        dicAlu["cate"].append(cateAlu)
        dicAlu["fecha"].append(feAlu)
        dicAlu["fAATEE"].append(faAlu)
        dicAlu["fEnat"].append(fEnatAlu)
        dicAlu["fFetra"].append(fFetraAlu)
        dicAlu["insNom"].append(insNom)
        dicAlu["insApe"].append(insApe)
        dicAlu["gimNom"].append(gimNom)
        dicAlu['edad'].append(edad)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)

@app.route("/vDesaAlu")
def vDesaAlu():
    tiempoSesion()
    alumno = conn.execute(
        "select a.tdoc, a.documento, a.apellido, a.nombre, c.tipo, convert(varchar,d.fecha,3), "
        "floor((cast(convert(varchar(8),getdate(),112) as int)"
        " - (cast(convert(varchar(8), a.fnac,112) as int)))/10000) as edad "
        "from alumno a, categoria c, aludesa d "
        "where a.categoria=c.id and a.tdoc=d.tdocalu and a.documento=d.docalu"
    ).fetchall()
    dicAlu = {
        'tdoc': [], 'doc': [], 'ape': [], 'nom': [], 'cate': [], 'fecha': [], 'lim': 0, 'edad': []
    }
    for tdoc, doc, ape, nom, cate, fecha, edad in alumno:
        dicAlu['tdoc'].append(tdoc)
        dicAlu['doc'].append(doc)
        dicAlu['ape'].append(ape)
        dicAlu['nom'].append(nom)
        dicAlu['cate'].append(cate)
        dicAlu['fecha'].append(fecha)
        dicAlu['edad'].append(edad)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)

@app.route("/filtroDesaAlu/<string:nom>/<string:ape>/<string:cate>")
def filtroDesaAlu(nom, ape, cate):
    tiempoSesion()
    query = "select a.tdoc, a.documento, a.apellido, a.nombre, c.tipo, convert(varchar,d.fecha,3) "
    query += "from alumno a, categoria c, aludesa d where "
    if nom != "-":
        query += "a.nombre like'%" + nom + "%' and " 
    if ape != "-":
        query += "a.apellido like'%" + ape + "%' and " 
    if cate != "-":
        query += "c.id=" + cate + " and " 
    query += "c.id=a.categoria and d.tdocalu=a.tdoc and a.documento=d.docalu"
    alumno = conn.execute(query).fetchall()
    dicAlu = {
        'tdoc': [], 'doc': [], 'ape': [], 'nom': [],
        'cate': [], 'fecha': [], 'lim': 0
    }
    for tdoc, doc, apealu, nomAlu, cate, fecha in alumno:
        dicAlu['tdoc'].append(tdoc)
        dicAlu['doc'].append(doc)
        dicAlu['ape'].append(apealu)
        dicAlu['nom'].append(nomAlu)
        dicAlu['cate'].append(cate)
        dicAlu['fecha'].append(fecha)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)


@app.route("/vImagen")
def vImagen():
    tiempoSesion()
    return render_template("/Ver/VerImagen.html")


@app.route("/filtrarImagen/<int:tipo>")
def filtrarImagen(tipo):
    tiempoSesion()
    dicEven = {'id': [], 'direc': [], 'lim': 0, 'tipo': ""}
    llenarDicImagen(dicEven, 'lim', tipo)
    dicEven['tipo'] = conn.execute(
        "select te.tipo from tipoevento te where te.id=" + str(tipo)
    ).fetchone()[0]
    return jsonify(dicEven)


@app.route("/vTodoImagen")
def vTodoImagen():
    tiempoSesion()
    dicEven = {'id': [], 'direc': [], 'limExa': 0, 'limTor': 0, 'limVar': 0}
    llenarDicImagen(dicEven, 'limExa', 1)
    llenarDicImagen(dicEven, 'limTor', 2)
    llenarDicImagen(dicEven, 'limVar', 3)
    return jsonify(dicEven)


def llenarDicImagen(dicEven, lim, tipo):
    recorre = conn.execute(
        "select i.* from imagen i, evento e "
        "where e.tipo =" + str(tipo) + " and e.id=i.idevento"
    ).fetchall()
    for idImg, direc in recorre:
        dicEven['id'].append(idImg)
        dicEven['direc'].append(direc)
        dicEven[lim] += 1

# Detalles
@app.route("/detalleUsuario/<int:tdoc>/<string:doc>")
def detalleUsuario(tdoc, doc):
    tiempoSesion()
    usuario = conn.execute(
        "select u.nombre, u.apellido, c.tipo, ca.tipo, u.email, u.tdoc, u.documento "
        "from usuario u, categoria c, cargo ca "
        "where u.tdoc=" + str(tdoc) + " and u.documento=" + doc
        + " and u.categoria=c.id and u.cargo=ca.id"
    ).fetchone()
    return jsonify({
        'nomape': f'{usuario[0]} {usuario[1]}', 'cate': usuario[2], 'cargo': usuario[3],
        'mail': usuario[4], 'tdoc': usuario[5], 'doc': usuario[6]
    })

@app.route("/gUsuario/<int:tdoc>/<string:doc>")
def gUsuario(tdoc, doc):
    tiempoSesion()
    gimnasio = conn.execute(
        "select g.nombre, g.direccion from gimnasio g, enseñaen ee "
        "where ee.tdoc=" + str(tdoc) + " and ee.doc=" +
        doc + " and ee.idgim=g.id"
    ).fetchall()
    dicGim = {'nom': [], 'direc': [], 'lim': 0}
    for nom, dire in gimnasio:
        dicGim['nom'].append(nom)
        dicGim['direc'].append(dire)
        dicGim['lim'] += 1
    return jsonify(dicGim)

@app.route("/verContra/<int:tdoc>/<string:doc>")
def verContra(tdoc, doc):
    tiempoSesion()
    usuario = conn.execute(
        "select u.contraseña from usuario u "
        "where u.tdoc=" + str(tdoc) + " and u.documento=" + doc
    ).fetchone()
    return jsonify({'contra': usuario[0]})

@app.route("/detalleGimnasio/<int:idGim>")
def detalleGimnasio(idGim):
    tiempoSesion()
    gimnasio = conn.execute(
        "select g.id, g.nombre, g.direccion, g.logo"
        " from gimnasio g where g.id=" + str(idGim)
    ).fetchone()
    return jsonify({
        'id': gimnasio[0], 'nom': gimnasio[1], 'direc': gimnasio[2],
        'logo': "static/" + gimnasio[3]
    })


@app.route("/vAluGimnasio/<int:idGim>")
def vAluGimnasio(idGim):
    tiempoSesion()
    query = ""
    if session['cargo'] == 2:
        query = " and exists(select 1 from cabeza c, usuario u where c.tdoccabeza="
        query += str(session['tdoc']) + " and c.doccabeza='"
        query += session['doc']
        query += "' and c.tdoc=u.tdoc and c.documento=u.documento and u.tdoc=a.tdocinstru"
        query += " and u.documento=a.docinstru)"
    elif session['cargo'] == 3:
        query = " and exists(select 1 from instructor i, usuario u where i.tdocinstru="
        query += str(session['tdoc']) + " and i.docinstru='"
        query += session['doc']
        query += "' and i.tdoc=u.tdoc and i.documento=u.documento and u.tdoc=a.tdocinstru"
        query += " and u.documento=a.docinstru)"
    alumno = conn.execute(
        "select a.nombre, a.apellido, c.tipo"
        " from alumno a, categoria c where a.idgim=" + str(idGim)
        + " and a.categoria=c.id" + query 
    ).fetchall()
    dicAlu = {'nom': [], 'ape': [], 'cate': [], 'lim': 0}
    for nom, ape, cate in alumno:
        dicAlu['nom'].append(nom)
        dicAlu['ape'].append(ape)
        dicAlu['cate'].append(cate)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)


@app.route("/detalleEvento/<int:idEve>")
def detalleEvento(idEve):
    tiempoSesion()
    evento = conn.execute(
        "select e.id, convert(varchar,e.fecha,3), e.descripcion, te.tipo "
        "from evento e, tipoevento te "
        "where e.id=" + str(idEve) + " and e.tipo=te.id"
    ).fetchone()
    return jsonify({
        'id': evento[0], 'fecha': evento[1], 'desc': evento[2], 'tipo': evento[3],
        'editar': True if session['cargo'] == 1 else False
    })


@app.route("/vAluEvento/<int:idEve>")
def vAluEvento(idEve):
    tiempoSesion()
    condiEx = ""
    if session['cargo'] == 2:
        condiEx = " and exists (select 1 from cabeza c, usuario u where c.tdoccabeza="
        condiEx += str(session['tdoc']) + " and c.doccabeza='"
        condiEx += session['doc'] + "' and c.tdoc=u.tdoc and c.documento=u.documento"
        condiEx += " and a.tdocinstru=u.tdoc and a.docinstru=a.documento)"
    elif session['cargo'] == 3:
        condiEx = " and exists (select 1 from instructor i, usuario u where i.tdocinstru="
        condiEx += str(session['tdoc']) + " and i.docinstru='"
        condiEx += session['doc'] + "' and i.tdoc=u.tdoc and i.documento=u.documento"
        condiEx += " and a.tdocinstru=u.tdoc and a.docinstru=a.documento)"
    evento = conn.execute(
        "select a.nombre, a.apellido, c.tipo"
        " from alumno a, participa p, evento e, categoria c"
        + " where e.id=" + str(idEve) +
        " and e.id=p.idevento and p.tdoc=a.tdoc and p.doc=a.documento and p.categoria=c.id"
        + condiEx + " order by a.apellido, a.nombre"
    ).fetchall()
    dicAluEve = {'nom': [], 'ape': [], 'cate': [], 'lim': 0, 'idEve': idEve}
    for nom, ape, cate in evento:
        dicAluEve['nom'].append(nom)
        dicAluEve['ape'].append(ape)
        dicAluEve['cate'].append(cate)
        dicAluEve['lim'] += 1
    return jsonify(dicAluEve)


@app.route("/detalleAlumno/<int:tdoc>/<string:doc>")
def detalleAlumno(tdoc, doc):
    tiempoSesion()
    alumno = conn.execute(
        "select a.nombre, a.apellido, c.tipo, a.nacionalidad, convert(varchar,a.fnac,3), "
        "convert(varchar,a.finscripcion,3), a.observaciones, a.email, a.localidad, a.foto, "
        "u.nombre, u.apellido, g.nombre "
        "from alumno a, categoria c, usuario u, gimnasio g "
        "where a.documento=" + doc + " and a.tdoc=" + str(tdoc)
        + " and a.categoria=c.id and a.docinstru=u.documento and a.tdocinstru=u.tdoc and "
        "a.idgim=g.id"
    ).fetchone()
    return jsonify({
        'nom': alumno[0], 'ape': alumno[1], 'cate': alumno[2], 'nacio': alumno[3],
        'fnac': alumno[4], 'finsc': alumno[5], 'obs': alumno[6], 'mail': alumno[7],
        'loc': alumno[8], 'foto': "static/" + alumno[9], 'nominstru': alumno[10],
        'apeinstru': alumno[11], 'nomgim': alumno[12], 
        'matri': True if session['cargo'] == 1 else False
    })


@app.route("/vEveAlumno/<int:tdoc>/<string:doc>")
def vEveAlumno(tdoc, doc):
    tiempoSesion()
    evento = conn.execute(
        "select convert(varchar,e.fecha,3), te.tipo, c.tipo "
        "from evento e, participa p, tipoevento te, categoria c "
        "where p.tdoc=" + str(tdoc) + " and p.doc='" + doc + "' and "
        "p.categoria=c.id and p.idevento=e.id and e.tipo=te.id "
        "order by e.fecha"
    ).fetchall()
    dicEven = {'fecha': [], 'tipo': [], 'cate': [], 'lim': 0}
    for fecha, tipo, cate in evento:
        dicEven['fecha'].append(fecha)
        dicEven['tipo'].append(tipo)
        dicEven['cate'].append(cate)
        dicEven['lim'] += 1
    return jsonify(dicEven)


@app.route("/vMatriAlu/<int:tdoc>/<string:doc>")
def vMatriAlu(tdoc, doc):
    tiempoSesion()
    matricula = conn.execute(
        "select convert(varchar,m.fecha,3), tm.tipo "
        "from alumno a, matricula m, tipomatri tm "
        "where a.tdoc=" + str(tdoc) + " and a.documento=" + doc
        + " and a.tdoc=m.tdoc and  a.documento=m.doc and m.tipo=tm.id"
    ).fetchall()
    dicMatri = {'fecha': [], 'tipo': [], 'lim': 0}
    for fecha, tipo in matricula:
        dicMatri['fecha'].append(fecha)
        dicMatri['tipo'].append(tipo)
        dicMatri['lim'] += 1
    return jsonify(dicMatri)

# Editar
@app.route("/eUsuario/<int:tdoc>/<string:doc>/<string:retorno>", methods={'GET', 'POST'})
def eUsuario(tdoc, doc, retorno):
    tiempoSesion()
    cargo = conn.execute('select * from cargo').fetchall()
    categoria = conn.execute(
        "select * from categoria c where c.id > 10").fetchall()
    tDoc = conn.execute("select * from tipodocumento").fetchall()
    instructor = conn.execute(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo "
        "from usuario u, categoria c "
        "where u.cargo <> 1 and c.id = u.categoria "
        "and not (u.tdoc=" + str(tdoc) + " and u.documento='" + doc + "')"
    ).fetchall()
    instructor.insert(0, ('', '', '', '', ''))
    cabeza = conn.execute(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo '
        'from usuario u, categoria c '
        'where u.cargo = 2 and c.id = u.categoria'
    ).fetchall()
    cabeza.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        usuario = conn.execute(
            "select usu.nombre, usu.apellido, usu.categoria, usu.cargo, usu.email, usu.tdoc, usu.documento, "
            "isnull(convert(varchar,c.tdoccabeza),''), isnull(c.doccabeza,''), "
            "isnull(convert(varchar,i.tdocinstru),''), isnull(i.docinstru,'') "
            "from (select u.nombre, u.apellido, u.categoria, u.cargo, u.email, u.tdoc, u.documento "
            "from usuario u "
            "where u.tdoc=" + str(tdoc) +
            " and u.documento=" + doc + " ) as usu "
            "left join cabeza c "
            "on c.tdoc=usu.tdoc and c.documento=usu.documento "
            "left join instructor i "
            "on i.tdoc=usu.tdoc and i.documento=usu.documento"
        ).fetchone()
        query = ""
        tdoc = str(tdoc)
        if usuario[0] != (nom := request.form.get("Nombre").capitalize()):
            query += " nombre='" + nom + "',"
        if usuario[1] != (ape := request.form.get("Apellido").capitalize()):
            query += " apellido='" + ape + "',"
        if usuario[2] != (cate := request.form.get("Categoria")):
            query += " categoria=" + cate + ","
        if usuario[4] != (mail := request.form.get("Email")):
            query += " email='" + mail + "',"
        if usuario[3] != (cargo := request.form.get("Cargo")):
            query += " cargo=" + cargo + ","
            if cargo == 1:
                delTabla(
                    "cabeza", "tdoccabeza="+ tdoc + " and doccabeza='" + doc + "'"
                    )
                delTabla(
                    "instructor", "tdocinstru="+ tdoc + " and docinstru='" + doc + "'"
                    )
            elif cargo == 2:
                insTabla(
                    "cabeza","tdoccabeza,doccabeza,tdoc,documento",
                    tdoc + ",'" + doc + "'," + tdoc + ",'" + doc + "'"
                )
                if usuario[3] == 1:
                    insTabla(
                        "instructor","tdocinstru,docinstru,tdoc,documento",
                        tdoc + ",'" + doc + "'," + tdoc + ",'" + doc + "'"
                    )
            else:
                delTabla(
                    "cabeza", "tdoccabeza="+ tdoc + " and doccabeza='" + doc + "'"
                    )
                if usuario[3] == 1:
                    insTabla(
                        "instructor","tdocinstru,docinstru,tdoc,documento",
                        tdoc + ",'" + doc + "'," + tdoc + ",'" + doc + "'"
                        )
        if usuario[5] != (
            nTdoc := request.form.get("TipoDocumento")
            ) or usuario[6] != (
                nDoc := request.form.get("Documento")
                ):
            if usuario[5] != nTdoc and usuario[6] != nDoc:
                query += " tdoc=" + nTdoc + " and documento='" + nDoc + "',"
                upInstruCabe(
                    "tdoc=" + nTdoc + " and documento='" + nDoc + "'",
                    "tdoc=" + usuario[5] + " and documento='" + usuario[6] + "'",
                    "tdoccabeza=" + nTdoc + " and doccabeza='" + nDoc + "'",
                    "tdoccabeza=" + usuario[5] + " and doccabeza='" + usuario[6] + "'",
                    "tdoc=" + nTdoc + " and documento='" + nDoc + "'",
                    "tdoc=" + usuario[5] + " and documento='" + usuario[6] + "'",
                    "tdocinstru=" + nTdoc + " and docinstru='" + nDoc + "'",
                    "tdocinstru=" + usuario[5] + " and docinstru='" + usuario[6] + "'"
                )
            elif usuario[5] != nTdoc:
                query += " tdoc=" + nTdoc + "',"
                upInstruCabe(
                    "tdoc=" + nTdoc,
                    "tdoc=" + usuario[5] + " and documento='" + usuario[6] + "'",
                    "tdoccabeza=" + nTdoc,
                    "tdoccabeza=" + usuario[5] + " and doccabeza='" + usuario[6] + "'",
                    "tdoc=" + nTdoc,
                    "tdoc=" + usuario[5] + " and documento='" + usuario[6] + "'",
                    "tdocinstru=" + nTdoc,
                    "tdocinstru=" + usuario[5] + " and docinstru='" + usuario[6] + "'"
                )
            elif usuario[6] != nDoc:
                query += " documento='" + nDoc + "',"
                upInstruCabe(
                    "documento='" + nDoc + "'",
                    "tdoc=" + usuario[5] + "documento='" + usuario[6] + "'",
                    "doccabeza='" + nDoc + "'",
                    "tdoccabeza=" + usuario[5] + " and doccabeza='" + usuario[6] + "'",
                    "documento='" + nDoc + "'",
                    "tdoc=" + usuario[5] + " and documento='" + usuario[6] + "'",
                    "docinstru='" + nDoc + "'",
                    "tdocinstru=" + usuario[5] + " and docinstru='" + usuario[6] + "'"
                )
        if query:
            upTabla("usuario", query[:-1] ,"tdoc=" + str(tdoc) + " and documento='" + doc + "'")
        conn.commit()
        return redirect("/MainBase")
    return render_template(
        "/Editar/EditarUsuario.html", cargo=cargo, categoria=categoria,
        tDoc=tDoc, instructor=instructor, cabeza=cabeza, tdoc=tdoc, doc=doc, retorno=retorno
    )

def upInstruCabe(valN1,condi1,valN2,condi2,valN3,condi3,valN4,condi4):
    upTabla("cabeza",valN1,condi1) 
    upTabla("cabeza",valN2,condi2) 
    upTabla("instructor",valN3,condi3) 
    upTabla("instructor",valN4,condi4) 

@app.route("/cargarUsuario/<int:tdoc>/<string:doc>")
def cargarUsuario(tdoc, doc):
    tiempoSesion()
    usuario = conn.execute(
        "select usu.nombre, usu.apellido, usu.categoria, usu.cargo, usu.email, usu.tdoc, usu.documento, "
        "isnull(convert(varchar,c.tdoccabeza),''), isnull(c.doccabeza,''), "
        "isnull(convert(varchar,i.tdocinstru),''), isnull(i.docinstru,'') "
        "from (select u.nombre, u.apellido, u.categoria, u.cargo, u.email, u.tdoc, u.documento "
        "from usuario u "
        "where u.tdoc=" + str(tdoc) + " and u.documento=" + doc + " ) as usu "
        "left join cabeza c "
        "on c.tdoc=usu.tdoc and c.documento=usu.documento "
        "left join instructor i "
        "on i.tdoc=usu.tdoc and i.documento=usu.documento"
    ).fetchone()
    return jsonify({
        'nom': usuario[0], 'ape': usuario[1], 'cate': usuario[2],
        'cargo': usuario[3], 'mail': usuario[4], 'tdoc': usuario[5],
        'doc': usuario[6], 'cabeza': f'{usuario[7]},{usuario[8]}',
        'instructor': f'{usuario[9]},{usuario[10]}'
    })

@app.route("/eGimnasio/<int:idGim>", methods={'GET', 'POST'})
def eGimnasio(idGim):
    tiempoSesion()
    if request.method == 'POST':
        query = ""
        gim = conn.execute(
            "select g.nombre, g.direccion, "
            "g.ubicacion, g.instagram, g.face, g.whats, g.logo "
            "from gimnasio g where g.id=" + str(idGim)
        ).fetchone()
        nomGim = gim[0]
        if gim[0] != (nom := request.form.get("Nombre")):
            query += " nombre='" + nom + "',"
            nomGim = nom
        if gim[1] != (direc := request.form.get("Direccion")):
            query += " direccion='" + direc + "',"
        if gim[2] != (ubi := request.form.get("Ubicacion")):
            query += " ubicacion='" + ubi + "',"
        if gim[3] != (insta := request.form.get("Instagram")):
            query += " instagram='" + insta + "',"
        if gim[4] != (face := request.form.get("Facebook")):
            query += " face='" + face + "',"
        if gim[5] != (whats := request.form.get("Contacto")):
            query += " whats='" + whats + "',"
        if request.files['Logo']:
            nombre = ""
            nombre = photos.save(
                request.files["Logo"], nomGim.replace(" ", "")
            )
            nombre = url_for('obtener_nombre', filename=nombre)[8:]
            query += " logo='Imagenes" + nombre + "',"
            os.remove("Static/" + gim[6])
        if query:
            conn.execute(
                "update gimnasio set " + query[:-1] + " where id=" + str(idGim)
            )
            conn.commit()
        conn.execute(
            "delete from enseñaen where idgim=" + str(idGim)
        )
        instru = request.form.getlist("instru")
        query = ""
        for dato in instru:
            dato = dato.split(",")
            query += "(u.tdoc=" + dato[0] + " and u.documento='" + dato[1] + "') or "
            if not conn.execute(
                "select 1 from enseñaen ee "
                "where ee.tdoc=" + dato[0] + " and ee.doc='" + dato[1]
                + "' and ee.idgim=" + str(idGim)
            ).fetchone():
                insTabla(
                    "enseñaen", "tdoc,doc,idgim",
                    dato[0] + ",'" + dato[1] + "'," + str(idGim)
                    )
        aludesa = conn.execute(
            "SELECT a.tdoc, a.documento from alumno a "
            "where not exists(select 1 from usuario u where (" + query[:-4]
            + ") and u.tdoc=a.tdocinstru and u.documento=a.docinstru) and a.idgim=" + str(idGim)
        ).fetchall()
        for tdocAlu, docAlu in aludesa:
            upTabla(
                "alumno","tdocinstru=null, docinstru=null, idgim=null",
                "tdoc=" + str(tdocAlu) + " and documento='" + docAlu + "'"
            )
            insTabla("aludesa","tdocalu,docalu,fecha", str(tdocAlu) + ",'" + docAlu + "',getdate()")
        conn.commit()
        delTabla("horario","idgim=" + str(idGim))
        for edadIni, edadFin, horaIni, horaFin, usu, dia in zip(
            request.form.getlist("edadIni"), request.form.getlist("edadFin"),
            request.form.getlist("horaIni"), request.form.getlist("horaFin"),
            request.form.getlist("Hora"), request.form.getlist("diaClase")
        ):
            if int(edadIni) < int(edadFin) and horaIni < horaFin and not conn.execute(
                        "select 1 from horario h "
                        "where h.tdoc=" + usu[0] + " and h.doc='" + usu[1] +
                        "' and h.idgim=" + str(idGim) + " and h.edadini=" + edadIni +
                        " and h.dia=" + dia
                    ).fetchone():
                usu = usu.split(",")
                insTabla(
                    "horario", "tdoc,doc,idgim,edadini,edadfin,horaini,horafin,dia",
                    usu[0] + ",'" + usu[1] + "'," + str(idGim) + "," + edadIni +
                    "," + edadFin + ",'" + horaIni + "','" + horaFin + "'," + dia
                )
        conn.commit()
        conn.execute(
            "delete horario where not exists(select 1 from usuario u where ("
            + query[:-4] + ") and u.tdoc=horario.tdoc and u.documento=horario.doc and horario.idgim=" + str(idGim) + ")"
        )
        conn.commit()
        return redirect("/vGimnasio")
    return render_template("/Editar/EditarGimnasio.html", idGim=idGim)

@app.route("/cargarGimnasio/<int:idGim>")
def cargarGimnasio(idGim):
    tiempoSesion()
    conaux = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-TFA1LI9\SQLEXPRESS;Database=BaseEnat;UID=Leo;PWD=12345'
        ).cursor()
    usuario = conaux.execute(
        "select u.tdoc, u.documento "
        "from usuario u, enseñaen en, categoria c "
        "where en.idgim=" + str(idGim) +
        " and en.tdoc=u.tdoc and en.doc=u.documento and u.categoria=c.id" 
    ).fetchall()
    condiEx = ""
    if session['cargo'] == 2:
        condiEx += " and exists(select 1 from cabeza ca where ca.tdoccabeza="
        condiEx += str(session['tdoc']) 
        condiEx += " and ca.doccabeza='" + session['doc']
        condiEx += "' and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    usuGen = conn.execute(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
        " from usuario u, categoria c"
        " where u.cargo <> 1 and u.categoria=c.id" + condiEx
    ).fetchall()
    if session['cargo'] != 1:
        usuGen.insert(0,conn.execute(
            "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
            " from usuario u, categoria c"
            " where u.tdoc=" + str(session['tdoc']) + " and u.documento='"
            + session['doc'] + "' and u.categoria=c.id"
        ).fetchone())
    gim = conn.execute(
        "select g.nombre, g.direccion, "
        "g.ubicacion, g.instagram, g.face, g.whats "
        "from gimnasio g where g.id="
        + str(idGim)
    ).fetchone()
    hora = conn.execute(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo, "
        "h.edadini, h.edadfin, h.horaini, h.horafin, h.dia "
        "from usuario u, horario h, categoria c "
        "where idgim=" + str(idGim) +
        " and h.tdoc=u.tdoc and h.doc=u.documento and u.categoria=c.id "
        "order by u.apellido, u.nombre"
    ).fetchall()
    dicGim = {
        'nom': gim[0], 'direc': gim[1], 'ubi': gim[2],
        'insta': gim[3], 'face': gim[4], 'whats': gim[5],
        'valHora': [], 'textHora': [], 'edadIni': [],
        'edadFin': [], 'horaIni': [], 'horaFin': [], 'dia': [], 'limHora': 0,
        'valGen': [], 'usuGen': [], 'limGen': 0, 'valAct': [], 'limAct': 0
    }
    for tdoc, doc, ape, nom, cate in usuGen:
        dicGim['valGen'].append(f'{tdoc},{doc}')
        dicGim['usuGen'].append(f'{ape} {nom} {cate}')
        dicGim['limGen'] += 1
    for tdoc, doc in usuario:
        dicGim['valAct'].append(f'{tdoc},{doc}')
        dicGim['limAct'] += 1
    conaux.close()
    for tdoc, doc, ape, nom, cate, eIni, eFin, hIni, hFin, dia in hora:
        dicGim['valHora'].append(f'{tdoc},{doc}')
        dicGim['textHora'].append(f'{ape} {nom} {cate}')
        dicGim['edadIni'].append(eIni)
        dicGim['edadFin'].append(eFin)
        dicGim['horaIni'].append(hIni)
        dicGim['horaFin'].append(hFin)
        dicGim['dia'].append(dia)
        dicGim['limHora'] += 1
    return jsonify(dicGim)

@app.route("/aHoraGim/<int:idGim>")
def aHoraGim(idGim):
    tiempoSesion()
    aGimUsuHora = conn.execute(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo "
        "from usuario u, enseñaen ee, categoria c "
        "where ee.idgim=" + str(idGim) +
        " and ee.tdoc=u.tdoc and ee.doc=u.documento and u.categoria=c.id"
    ).fetchall()
    dicHora = {'value': [], 'text': [], 'lim': 0}
    for tdoc, doc, ape, nom, cate in aGimUsuHora:
        dicHora['value'].append(f'{tdoc},{doc}')
        dicHora['text'].append(f'{ape} {nom} {cate}')
        dicHora['lim'] += 1
    return jsonify(dicHora)

@app.route("/eEvento/<int:idEve>", methods={'GET', 'POST'})
def eEvento(idEve):
    tiempoSesion()
    tipo = conn.execute('select * from tipoevento').fetchall()
    if request.method == 'POST':
        evento = conn.execute(
            "select convert(varchar,e.fecha,23), e.tipo, e.descripcion "
            "from evento e "
            "where e.id=" + str(idEve)
        ).fetchone()
        query = ""
        if evento[0] != (fecha := request.form.get("Fecha")):
            query += " fecha='" + fecha + "',"
        if evento[1] != (tipo := request.form.get("Tipo")):
            query += " Tipo='" + tipo + "',"
        if evento[2] != (desc := request.form.get("Descripcion")):
            query += " Descripcion='" + desc + "',"
        if query:
            upTabla("evento",query[:-1],"id=" + str(idEve))
            conn.commit()
        return redirect("/MainBase")
    return render_template("/Editar/EditarEvento.html", tipoEvento=tipo, idEve = idEve)

@app.route("/cargarEvento/<int:idEve>")
def cargarEvento(idEve):
    tiempoSesion()
    evento = conn.execute(
        "select convert(varchar,e.fecha,23), e.tipo, e.descripcion "
        "from evento e "
        "where e.id=" + str(idEve)
    ).fetchone()
    return jsonify({
        'fecha': evento[0], 'tipo': evento[1], 'desc': evento[2]
    })

@app.route("/eAlumno/<int:tdoc>/<string:doc>", methods={'GET', 'POST'})
def eAlumno(tdoc,doc):
    tiempoSesion()
    categoria = conn.execute("select * from categoria").fetchall()
    tDoc = conn.execute("select * from tipodocumento").fetchall()
    condiEx = ""
    if session['cargo'] == 2: 
        condiEx = " and exists(select 1 from cabeza ca where ca.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and ca.tdoccabeza=" + str(session['tdoc'])
        condiEx += " and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    query = "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
    query += " from usuario u, categoria c, enseñaen ee"
    query += " where ee.tdoc = u.tdoc and ee.doc= u.documento and c.id = u.categoria" + condiEx
    usuario = conn.execute(
        query + " group by u.tdoc,u.documento,u.apellido,u.nombre,c.tipo "
    ).fetchall()
    if session['cargo'] != 1:
        usuario.insert(0,conn.execute(
            "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
            " from usuario u, categoria c"
            " where u.tdoc=" + str(session['tdoc']) + " and u.documento='"
            + session['doc'] + "' and c.id = u.categoria"
        ).fetchone())
    usuario.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        alumno = conn.execute(
            "select a.nombre, a.apellido, a.tdoc, a.documento, a.categoria, a.nacionalidad"
            ", convert(varchar,a.finscripcion,23), a.observaciones, a.email, a.localidad"
            ", convert(varchar,a.fnac,23), a.libreta, a.foto"
            ", a.tdocinstru, a.docinstru, a.idgim "
            "from alumno a where a.tdoc=" + str(tdoc)
            + " and a.documento='" + doc + "'"
        ).fetchone()
        query = ""
        if alumno[0] != (nom := request.form.get("Nombre")):
            query += " nombre='" + nom + "',"
        if alumno[1] != (ape := request.form.get("Apellido")):
            query += " apellido='" + ape + "',"
        if alumno[2] != (tDocAlu := int(request.form.get("TipoDocumento"))):
            query += " tdoc=" + tDocAlu + ","
        if alumno[3] != (docAlu := request.form.get("Documento")):
            query += " documento='" + docAlu + "',"
        if alumno[4] != (cate := int(request.form.get("Categoria"))):
            if cate >= conn.execute(
                "select count(*) + 1 from participa pe, evento e "
                "where pe.tdoc=" + str(alumno[2]) + " and pe.doc='" + alumno[3]
                + "' and e.tipo=1 and pe.idevento=e.id"
            ).fetchone()[0]:
                reParti(
                    iter(
                        conn.execute(
                            "select e.id, e.tipo "
                            "from evento e, participa pe "
                            "where pe.tdoc=" + str(alumno[2]) + " and pe.doc='"
                            + alumno[3] + "' and pe.idevento=e.id "
                            "order by e.fecha desc"
                        ).fetchall()
                    ),str(alumno[2]),alumno[3],cate
                )
        if alumno[5] != (nac := request.form.get("Nacionalidad")):
            query += " nacionalidad='" + nac + "',"
        if alumno[6] != (fNac := request.form.get("fInscripcion")):
            query += " finscripcion='" + fNac + "',"
        if alumno[7] != (obs := request.form.get("Observaciones")):
            query += " observaciones='" + obs + "',"
        if alumno[8] != (mail := request.form.get("Mail")):
            query += " email='" + mail + "',"
        if alumno[9] != (loc := request.form.get("Localidad")):
            query += " localidad='" + loc + "',"
        if alumno[10] != (fnac := request.form.get("fNacimiento")):
            query += " fnac='" + fnac + "',"
        libre = request.form.get("Libreta")
        if libre and alumno[11] != libre:
            query += " libreta=" + libre + ","
        instru = request.form.get("Instru")
        idGim = request.form.get("Gim")
        if request.files["Foto"] or instru or idGim:
            usu = []
            nomGim = []
            if instru:
                instru = instru.split(",")
                usu = conn.execute(
                    "select u.apellido, u.nombre "
                    "from usuario u where u.tdoc=" + str(instru[0])
                    + " and u.documento='" + instru[1] + "'"
                    ).fetchone()
                if alumno[13] != instru[0]:
                    query += " tdocinstru=" + str(instru[0]) + ","
                if alumno[14] != instru[1]:
                    query += " docinstru='" + instru[1] + "',"
            else:
                usu = conn.execute(
                    "select u.apellido, u.nombre "
                    "from usuario u where u.tdoc=" + str(alumno[13])
                    + " and u.documento='" + alumno[14] + "'"
                    ).fetchone()
            if idGim:
                if alumno[15] != idGim:
                    query += " idgim=" + idGim + ","
                nomGim = conn.execute(
                    "select g.nombre "
                    "from gimnasio g where g.id=" + str(idGim)
                ).fetchone()[0]
            else:
                nomGim = conn.execute(
                    "select g.nombre "
                    "from gimnasio g where g.id=" + str(alumno[15])
                ).fetchone()[0]
            nombre = 'SinFoto.jpg'
            if request.files["Foto"]:
                if alumno[12] != "Imagenes/SinFoto.jpg":
                    os.remove("Static/" + alumno[12])
                nombre = photos.save(
                    request.files["Foto"], f'{nomGim.replace(" ","")}/{usu[0]}{usu[1]}'
                )
                query += " foto='Imagenes" + url_for('obtener_nombre', filename=nombre)[8:] + "',"
        if query:
            upTabla("alumno",query[:-1],"tdoc=" + str(tdoc) + " and documento='" + doc + "'")
            conn.commit()
        tele = request.form.getlist("Telefono")
        conta = request.form.getlist("Contacto")
        delTabla("telefono","tdoc=" + str(tdoc) + " and documento='" + doc + "'")
        for tel, cont in zip(tele,conta):
            if tel and cont:
                insTabla(
                    "telefono","tdoc,documento,telefono,contacto",
                    "" + str(tdoc) + ",'" + doc + "','" + tel + "','" + cont + "'"
                )
        conn.commit()
        return redirect("/vAlumno")
    return render_template(
        "/Editar/EditarAlumno.html", categoria=categoria, tDoc=tDoc,
        usuario=usuario, doc=doc, tdoc=tdoc
    )

@app.route("/cargarAlumno/<int:tdoc>/<string:doc>")
def cargarAlumno(tdoc, doc):
    tiempoSesion()
    alumno = conn.execute(
        "select a.nombre, a.apellido, a.tdoc, a.documento, a.categoria, a.nacionalidad"
        ", convert(varchar,a.finscripcion,23), a.observaciones, a.email, a.localidad"
        ", convert(varchar,a.fnac,23)"
        ", a.tdocinstru, a.docinstru, a.idgim "
        "from alumno a where a.tdoc=" + str(tdoc)
        + " and a.documento='" + doc + "'"
    ).fetchone()
    telefono = conn.execute(
        "select t.telefono, t.contacto "
        "from telefono t "
        "where t.tdoc=" + str(tdoc) + " and t.documento='" + doc + "'"
    ).fetchall()
    dicAlu = {
        'nom': alumno[0], 'ape': alumno[1], 'tdoc': alumno[2], 'doc': alumno[3],
        'cate': alumno[4], 'nacio': alumno[5], 'fIns': alumno[6], 'ibs': alumno[7],
        'mail': alumno[8], 'loc': alumno[9], 'fnac': alumno[10],
        'instru': f'{alumno[11]},{alumno[12]}', 'idgim': alumno[13], 'tel': [], 'cont': [],
        'limTel': 0
    }
    for tel, cont in telefono:
        dicAlu['tel'].append(tel)
        dicAlu['cont'].append(cont)
        dicAlu['limTel'] += 1
    return jsonify(dicAlu)

# Funciones boton

@app.route("/elimUsuario/<int:tdoc>/<string:doc>")
def elimUsuario(tdoc, doc):
    tiempoSesion()
    delTabla("cabeza","tdoc=" + str(tdoc) + " and documento='" + doc + "'")
    delTabla("instructor","tdoc=" + str(tdoc) + " and documento='" + doc + "'")
    conn.commit()
    return redirect("/vUsuario")

@app.route("/desaGim/<int:idGim>")
def desaGim(idGim):
    tiempoSesion()
    alu = []
    if session['cargo'] != 3:
        delTabla("enseñaen","idgim=" + str(idGim))
        delTabla("horario","idgim=" + str(idGim))
        alu = conn.execute(
            "select a.tdoc, a.documento from alumno a "
            "where a.idgim=" + str(idGim)
        ).fetchall()
        upTabla(
            "alumno","idgim=null, tdocinstru=null, docinstru= null",
            "idgim=" + str(idGim)
            )
    else:
        delTabla(
            "enseñaen","idgim=" + str(idGim) + " and tdoc="
            + str(session['tdoc']) + " and doc='" + session['doc'] + "'"
            )
        delTabla(
            "horario","idgim=" + str(idGim) + " and tdoc=" 
            + str(session['tdoc']) + " and doc='" + session['doc'] + "'"
            )
        alu = conn.execute(
            "select a.tdoc, t.documento from alumno a "
            "where a.idgim=" + str(idGim) + " and a.tdocinstru=" + str(session['tdoc'])
            + " and a.docinstru='" + session['doc'] + "'"
        ).fetchall()
        upTabla(
            "alumno","idgim=null, tdocinstru=null, docinstru= null",
            "idgim=" + str(idGim) + " and tdocinstru=" + str(session['tdoc'])
            + " and docinstru='" + session['doc'] + "'"
                )
    for tdoc, doc in alu:
        insTabla("aludesa","tdocalu,docalu,fecha", str(tdoc) + ",'" + doc + "',getdate()")
    conn.commit()
    return redirect("/vGimnasio")

@app.route("/elimGimnasio/<int:idGim>")
def elimGimnasio(idGim):
    tiempoSesion()
    logo = conn.execute(
        "select g.logo from gimnasio g where g.id=" + str(idGim)
    ).fetchone()[0]
    os.remove("Static/" + logo)
    shutil.rmtree("Static/" + logo[:logo.rfind("/")])
    delTabla("gimnasio","id=" + str(idGim))
    conn.commit()
    return redirect("/vGimnasio")

@app.route("/aAluEven/<int:tipo>/<string:cadAlu>")
def aAluEven(tipo, cadAlu):
    tiempoSesion()
    cadAlu = cadAlu.split(".")
    idEve = conn.execute(
        "select e.id "
        "from evento e, ("
            "select min(e.fecha) as minFecha "
            "from evento e where e.tipo=" + str(tipo) + " and e.fecha >= getdate()"
        ") as ef "
        "where e.fecha = ef.minFecha and e.tipo=" + str(tipo)
    ).fetchone()[0]
    for elem in cadAlu:
        elem = elem.split(",")
        if not conn.execute(
            "select 1 from participa p "
            "where p.tdoc=" + elem[0] + " and p.doc='" + elem[1] + "' and p.idevento=" + str(idEve)
        ).fetchone():
            cate = conn.execute(
                "select a.categoria from alumno a where a.tdoc="
                + elem[0] + " and a.documento='" + elem[1] + "'"
            ).fetchone()[0]
            if tipo == 1:
                cate = cate + 1
                upTabla(
                    "alumno","categoria=" + str(cate),
                    "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
                )
            insTabla(
                "participa","tdoc,doc,idevento,categoria",
                elem[0] + ",'" + elem[1] + "'," + str(idEve) + "," + str(cate)
            )
    conn.commit()
    return redirect("/vAlumno")

@app.route("/desaAlu/<string:cadAlu>")
def desaAlu(cadAlu):
    tiempoSesion()
    cadAlu = cadAlu.split(".")
    for elem in cadAlu:
        elem = elem.split(",")
        upTabla(
            "alumno","tdocinstru=null, docinstru=null, idgim=null",
            "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
        )
        insTabla("aludesa","tdocalu,docalu,fecha",elem[0] + ",'" + elem[1] + "',getdate()")
    conn.commit()
    return redirect("/vAlumno")

@app.route("/habiAlu/<string:tdocUsu>/<string:docUsu>/<string:idGim>/<string:cadAlu>")
def habiAlu(tdocUsu, docUsu, idGim, cadAlu):
    tiempoSesion()
    cadAlu = cadAlu.split(".")
    for elem in cadAlu:
        elem = elem.split(",")
        upTabla(
            "alumno","tdocinstru=" + tdocUsu + ", docinstru='" + docUsu + "', idgim=" + idGim,
            "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
        )
        delTabla("aludesa","tdocalu=" + elem[0] + " and docalu='" + elem[1] + "'")
    conn.commit()
    return redirect("/vAlumno")

@app.route("/aluMatri/<int:tipo>/<string:cadAlu>")
def aluMatri(tipo, cadAlu):
    tiempoSesion()
    cadAlu = cadAlu.split(".")
    tipo = str(tipo)
    for elem in cadAlu:
        elem = elem.split(",")
        if not conn.execute(
            "select 1 from matricula m "
            "where m.tdoc=" + elem[0] + " and m.doc='" + elem[1] + "' and "
            "m.tipo=" + tipo + " and m.fecha = convert(varchar,getdate(),3)"
        ).fetchone():
            insTabla(
                "matricula","tdoc,doc,fecha,tipo",
                elem[0] + ",'" + elem[1] + "',convert(varchar,getdate(),3)," + tipo
            )
    conn.commit()
    return redirect("/vAlumno")

@app.route("/vFilEveAlu/<string:tipo>/<string:tdoc>/<string:doc>")
def vFilEveAlu(tipo,tdoc,doc):
    tiempoSesion()
    aluEve = conn.execute(
        "select convert(varchar,e.fecha,3), te.tipo, c.tipo "
        "from evento e, participa p, categoria c, tipoevento te "
        "where p.tdoc=" + tdoc + " and p.doc='" + doc + "' and e.tipo=" + tipo
        + " and p.idevento=e.id and p.categoria=c.id and e.tipo=te.id "
        "order by e.fecha"
    ).fetchall()
    dicEve = {'fecha': [], 'tipo': [], 'cate': [], 'lim': 0}
    for fecha, tipo, cate in aluEve:
        dicEve['fecha'].append(fecha)
        dicEve['tipo'].append(tipo)
        dicEve['cate'].append(cate)
        dicEve['lim'] += 1
    return jsonify(dicEve)

@app.route("/aPrevEve/<string:tipo>/<string:tdoc>/<string:doc>")
def aPrevEve(tipo, tdoc, doc):
    tiempoSesion()
    evento = conn.execute(
        "select e.id, convert(varchar,e.fecha,3) "
        "from evento e "
        "where e.tipo= " + tipo + " and e.fecha <= getdate() and not exists("
            "select 1 from participa p "
            "where p.tdoc=" + tdoc + " and p.doc=" + doc + " and p.idevento=e.id "
        ") order by e.fecha"
    ).fetchall()
    dicEve = {'id': [], 'fecha': [], 'lim': 0}
    for id, fecha in evento:
        dicEve['id'].append(id)
        dicEve['fecha'].append(fecha)
        dicEve['lim'] += 1
    return jsonify(dicEve)

@app.route("/agregaEvento/<string:tdoc>/<string:doc>/<string:cadEve>")
def agregaEvento(tdoc, doc, cadEve):
    tiempoSesion()
    eveReg = conn.execute(
        "select e.id, e.tipo, convert(varchar,e.fecha,3) "
        "from evento e "
        "where e.id in (" + cadEve + ") or exists ("
            "select 1 from participa p "
            "where p.tdoc=" + tdoc + " and p.doc='" + doc + "' and p.idevento=e.id"
        ") order by e.fecha desc" 
    ).fetchall()
    cate = conn.execute(
        "select a.categoria + ("
            "select count(*) from evento e "
            "where e.id in(" + cadEve + ") and e.tipo=1"
        ") "
        "from alumno a "
        "where a.tdoc=" + tdoc + " and a.documento='" + doc + "'"  
    ).fetchone()[0]
    reParti(iter(eveReg),tdoc,doc,cate)
    conn.commit()
    return redirect("/vAlumno")

@app.route("/ePrevEven/<string:tipo>/<string:tdoc>/<string:doc>")
def ePrevEven(tipo,tdoc,doc):
    tiempoSesion()
    even = conn.execute(
        "select e.id, convert(varchar,e.fecha,3) "
        "from evento e, tipoevento te, participa p "
        "where p.tdoc=" + tdoc + " and p.doc='" + doc + "'"
        " and e.tipo=" + tipo + " and e.tipo=te.id and p.idevento=e.id"
    ).fetchall()
    dicEve = {'id': [], 'fecha': [], 'lim': 0}
    for id, fecha in even:
        dicEve['id'].append(id)
        dicEve['fecha'].append(fecha)
        dicEve['lim'] += 1
    return jsonify(dicEve)

@app.route("/elimEvento/<string:tdoc>/<string:doc>/<string:cadEve>")
def elimEvento(tdoc,doc,cadEve):
    tiempoSesion()
    eveReg = conn.execute(
        "select e.id, e.tipo "
        "from evento e "
        "where e.id not in (" + cadEve + ") and exists ("
            "select 1 from participa p "
            "where p.tdoc=" + tdoc + " and p.doc='" + doc + "' and p.idevento=e.id"
        ") order by e.fecha desc" 
    ).fetchall()
    cate = conn.execute(
        "select a.categoria - ("
            "select count(*) from evento e "
            "where e.id in(" + cadEve + ") and e.tipo=1"
        ") "
        "from alumno a "
        "where a.tdoc=" + tdoc + " and a.documento='" + doc + "'"  
    ).fetchone()[0]
    reParti(iter(eveReg),tdoc,doc,cate)
    conn.commit()
    return redirect("/vAlumno")

def reParti(itera,tdoc,doc,cate):
    eveIdTipo = next(itera,None)
    delTabla("participa","tdoc=" + tdoc + " and doc='" + doc + "'")
    upTabla(
        "alumno","categoria=" + str(cate),
        "tdoc=" + tdoc + " and documento='" + doc + "'"
    )
    while eveIdTipo:
        while eveIdTipo and eveIdTipo[1] == 1:
            eveIdTipo = insparti(tdoc,doc,str(eveIdTipo[0]),cate,itera)
            cate -= 1
        while eveIdTipo and eveIdTipo[1] != 1:
            eveIdTipo = insparti(tdoc,doc,str(eveIdTipo[0]),cate,itera)

def insparti(tdoc,doc,idEve,cate,reco):
    insTabla(
        "participa","tdoc,doc,idevento,categoria",
        tdoc + ",'" + doc + "'," + idEve + "," + str(cate)
    )
    return next(reco,None)

@app.route("/eImagen/<string:idImagen>/<string:direc>")
def eImagen(idImagen,direc):
    tiempoSesion()
    direc = direc.replace("ƒ","/")
    delTabla("imagen","idevento=" + idImagen + " and direccion='" + direc + "'")
    os.remove("static/" + direc)
    conn.commit()
    return redirect("/vImagen")

@app.route("/eNotificacion/<string:idNoti>")
def eNotificacion(idNoti):
    tiempoSesion()
    delTabla(
        "notifica","idnoti=" + idNoti + " and tdoc="
        + str(session['tdoc']) + " and documento='" + session['doc'] + "'"
    )
    if not conn.execute(
        "select 1 from notifica n "
        "where n.idnoti=" + idNoti
    ).fetchone():
        delTabla("notidicacion","id=" + idNoti)
    conn.commit()
    return redirect("/MainBase")

@app.route("/elimAlu/<string:cadAlu>")
def elimAlu(cadAlu):
    tiempoSesion()
    cadAlu = cadAlu.split(".")
    for dato in cadAlu:
        dato = dato.split(",")
        delTabla("aludesa","tdocalu=" + dato[0] + " and docalu='" + dato[1] + "'")
        delTabla("participa","tdoc=" + dato[0] + " and doc='" + dato[1] + "'")
        delTabla("matricula","tdoc=" + dato[0] + " and doc='" + dato[1] + "'")
        delTabla("telefono","tdoc=" + dato[0] + " and documento='" + dato[1] + "'")
        foto = conn.execute(
            "select a.foto from alumno a "
            "where a.tdoc=" + dato[0] + " and a.documento='" + dato[1] + "'"
        ).fetchone()[0]
        if foto != "Imagenes/SinFoto.jpg":
            os.remove("static/" + foto)
        delTabla("alumno","tdoc=" + dato[0] + " and documento='" + dato[1] + "'")
    conn.commit()
    return redirect("/vAlumno")

# Funciones tipicas


@app.route("/uploads/<filename>")
def obtener_nombre(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route("/cambioGim/<string:tDocUsu>/<string:docUsu>")
def cambioGim(tDocUsu, docUsu):
    gim = conn.execute(
        "select g.id, g.nombre, g.direccion "
        "from gimnasio g, enseñaen ee "
        "where g.id = ee.idgim and ee.tdoc=" + tDocUsu + " and ee.doc=" + docUsu
    ).fetchall()
    dicGim = {'idGim': [], 'nomGim': [], 'direGim': [], 'cant': len(gim)}
    for idgim, nomgim, direcgim in gim:
        dicGim['idGim'].append(idgim)
        dicGim['nomGim'].append(nomgim)
        dicGim['direGim'].append(direcgim)
    return jsonify(dicGim)

def upTabla(tabla,cambio,condi):
    conn.execute(
        "update " + tabla + " set " + cambio + " where " + condi
    )

def delTabla(tabla,condi):
    conn.execute(
        "delete from " + tabla + " where " + condi
    )

def insTabla(tabla,valTabla,valInser):
    conn.execute(
        "insert into " + tabla + " (" + valTabla + ") values(" + valInser + ")"
    )