from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify, session
from flask_uploads import IMAGES, UploadSet, configure_uploads
from models import *
from shutil import rmtree
import os
import pathlib
import pymysql
import shutil
import MySQLdb
import pytz
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="/home/Leo0997/BaseConReact/Templates")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(
    app.root_path, 'static/Imagenes')
app.config['UPLOADED_PHOTOS_ALLOW'] = set(
    ['png', 'jpg', 'jpeg', 'jfif', 'jpeg'])
app.config['SECRET_KEY'] = 'Taekwon-do_Enat'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
HOST = "Leo0997.mysql.pythonanywhere-services.com"
USUARIO = "Leo0997"
CONTRA = "matryoshka"
BASE= "Leo0997$BaseConReact"
# conn = pyodbc.connect(
#     'Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-TFA1LI9\SQLEXPRESS;Database=BaseEnat;UID=Leo;PWD=12345'
# ).cursor()


if __name__ == '__main__':
    app.run()

def conectarAll(query):
    conn = pymysql.connect(host=HOST, user=USUARIO, passwd=CONTRA, db=BASE).cursor()
    conn.execute(query)
    resu = conn.fetchall()
    conn.close()
    return resu

def conectarOne(query):
    conn = pymysql.connect(host=HOST, user=USUARIO, passwd=CONTRA, db=BASE).cursor()
    conn.execute(query)
    resu = conn.fetchone()
    conn.close()
    return resu

@app.route("/gimPagina")
def gimPagina():
    gim = conectarAll("select * from gimnasio")
    dicGim = {
        'id': [], 'nombre': [], 'direc': [], 'face': [], 'insta': [], 'ubi': [],
        'whats': [], 'logo': [], 'lim': 0, 'instru': [], 'horario': []
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
        for nom, ape in conectarAll(
            "select u.nombre, u.apellido "
            "from gimnasio g, usuario u, enseñaen ee "
            "where ee.idgim=g.id and ee.tdoc=u.tdoc and ee.doc=u.documento and g.id='" +
                str(id) + "'"
        ):
            instru += f'{nom} {ape} '
        dicGim['instru'].append(instru[:-1])
        for eIni, eFin, hIni, hFin, dia in conectarAll(
            "select h.edadini, h.edadfin, h.horaini, h.horafin, d.tipo "
            "from horario h, dia d "
            "where h.idgim='" + str(id) + "' and h.dia=d.id"
        ):
            hora.append(
                f'<p>{dia} de {eIni} a {eFin} años: {hIni} a {hFin} Hs</p>,')
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
    return conectarOne(
        "select isnull(convert(varchar,min(e.fecha),3),'') "
        "from evento e "
        "where e.tipo='" + str(tipo) + "' and e.fecha >= getdate()"
    )[0]


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
    return conectarAll(
        "select i.direccion, 1 "
        "from imagen i, ("
        "select top 1 e.id as idEve "
        "from evento e "
        "where e.tipo='" + tipo + "' and e.fecha <= getdate() "
        "order by e.fecha DESC"
        ") as eve "
        "where i.idevento=eve.idEve"
    )


@app.route("/")
@app.route("/MainBase")
def main():
    if not session or 'tdoc' not in session:
        return redirect(url_for("login"))
    gim = conectarAll(
        "select 1 from gimnasio g, enseñaen ee "
        "where ee.tdoc=" + str(session['tdoc']) +
        " and ee.doc='" + session['doc']
        + "' and ee.idgim=g.id"
        )
    noti = conectarAll(
        "select n.id, n.texto "
        "from notificacion n, notifica nt "
        "where nt.tdoc=" + str(session['tdoc']) +
        " and nt.documento='" + session['doc']
        + "' and nt.idnoti=n.id "
        )
    return render_template(
        "Inicio.html", tdoc=session['tdoc'], doc=session['doc'],
        cargo=session['cargo'], gim=gim, noti=noti
    )


def tiempoSesion():
    tiempo = conectarOne(
        "select u.sesion from usuario u "
        "where u.tdoc=" + str(session['tdoc'])
        + " and u.documento='" + session['doc'] + "'"
        )
    if not tiempo:
        return redirect(url_for("logout"))
    if tiempo[0] + timedelta(hours=1) < datetime.now():
        return redirect(url_for("logout"))
    upTabla(
        "usuario", "sesion='" + str(datetime.now()) + "'",
        "tdoc=" + str(session['tdoc']) +
        " and documento='" + session['doc'] + "'"
    )


@app.route("/login", methods={"GET", "POST"})
def login():
    if request.method == 'POST':
        usu = conectarOne(
            "select u.tdoc, u.documento, u.cargo from usuario u where u.email='" +
            request.form.get("mail") + "' and u.contraseña='"
            + request.form.get("contra") + "'"
            )
        if usu:
            session['tdoc'] = usu[0]
            session['doc'] = usu[1]
            session['cargo'] = usu[2]
            upTabla(
                "usuario", "sesion='" + str(datetime.now()) + "'",
                "tdoc=" + str(session['tdoc']) +
                " and documento='" + session['doc'] + "'"
            )
            return redirect("/MainBase")
    return render_template("Login.html")


@app.route("/logout")
def logout():
    if session and session['tdoc']:
        session.pop("tdoc")
        session.pop("doc")
        session.pop("cargo")
    return redirect("/MainBase")


@app.route("/cambiarContra/<string:tdoc>/<string:doc>", methods={'GET', 'POST'})
def cambiarContra(tdoc, doc):
    # tiempoSesion()
    if request.method == 'POST':
        contra1 = request.form.get("contra_1")
        contra2 = request.form.get("contra_2")
        if contra1 and contra2 and contra1 == contra2:
            contraUsu = conectarOne(
                "select u.contraseña from usuario u "
                "where u.tdoc=" + tdoc + " and u.documento='" + doc + "'"
                )[0]
            if contra1 == contraUsu:
                return render_template(
                    "cambiarContra.html", msj="La nueva contraseña es igual a la anterior"
                )
            upTabla(
                "usuario", "contraseña='" + contra1 + "'",
                "tdoc=" + tdoc + " and documento=" + doc + ""
            )
            return redirect("/MainBase")
        return render_template(
            "cambiarContra.html", msj="Las contraseñas no coinciden"
        )
    return render_template("cambiarContra.html", msj="")

# Agregar


@app.route("/aUsuario", methods={'GET', 'POST'})
def aUsuraio():
    # tiempoSesion()
    cargo = conectarAll('select * from cargo')
    categoria = conectarAll("select * from categoria c where c.id > 10")
    tDoc = conectarAll("select * from tipodocumento")
    instructor = list(conectarAll(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo '
        'from usuario u, categoria c '
        'where u.cargo <> 1 and c.id = u.categoria'
    ))
    instructor.insert(0, ('', '', '', '', ''))
    cabeza = list(conectarAll(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo '
        'from usuario u, categoria c '
        'where u.cargo = 2 and c.id = u.categoria'
    ))
    cabeza.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        cUsuario = request.form.get("Cargo")
        tDocUsu = request.form.get("TipoDocumento")
        docUsu = request.form.get("Documento")
        insTabla(
            "usuario","nombre,apellido,categoria,cargo,contraseña,email,tdoc,documento",
            "'" + request.form.get("Nombre").capitalize() + "','" +
            request.form.get("Apellido").capitalize()
            + "'," + request.form.get("Categoria") + "," + cUsuario
            + ",'Taekwondo','" + request.form.get("Email") + "'," + tDocUsu
            + ",'" + docUsu + "'"
        )
        if int(cUsuario) == 2:
            insTabla(
                "cabeza", "tdoccabeza,doccabeza,tdoc,documento",
                tDocUsu + ",'" + docUsu + "'," + tDocUsu + ",'" + docUsu + "'"
            )
        elif int(cUsuario) == 3:
            insTabla(
                "instructor", "tdocinstru,docinstru,tdoc,documento",
                tDocUsu + ",'" + docUsu + "'," + tDocUsu + ",'" + docUsu + "'"
            )
            aInstruCab("Cabeza", "cabeza", "tdoccabeza",
                        "doccabeza", tDocUsu, docUsu)
            aInstruCab("Instructor", "instructor", "tdocinstru",
                        "docinstru", tDocUsu, docUsu)
        return redirect("/MainBase")
    return render_template(
        "/Agregar/AgregarUsuario.html", cargo=cargo,
        categoria=categoria, tDoc=tDoc, instructor=instructor,
        cabeza=cabeza
    )


def aInstruCab(busca, tabla, col1, col2, tDocUsu, docUsu):
    # tiempoSesion()
    dato = request.form.get(busca).split(",")
    if dato[0] and dato[1]:
        insTabla(
            tabla,col1 + "," + col2 + ",tdoc,documento",
            dato[0] + ",'" + dato[1] + "'," + tDocUsu + ",'" + docUsu + "'"
        )


@app.route("/aGimnasio", methods={'GET', 'POST'})
def aGimnasio():
    # tiempoSesion()
    if request.method == 'POST' and (instru := request.form.getlist("instru")):
        nomGim = request.form.get("Nombre").capitalize()
        direcGim = request.form.get("Direccion").capitalize()
        resu = conectarAll(
            "select 1 from gimnasio g where g.nombre='"
            + nomGim + "' and g.direccion='" + direcGim + "'"
        )
        if resu:
            return redirect("/MainBase")
        i = 1
        lim = conectarOne("select coalesce(max(g.id),1) from gimnasio g")[0]
        while i <= lim and conectarOne(
            "select 1 from gimnasio where id='" + str(i) + "'"
        ):
            i += 1
        nombre = "sin_foto.png"
        if request.files["Logo"]:
            nombre = photos.save(
                request.files["Logo"], nomGim.replace(" ", "")
            )
        insTabla(
            "gimnasio", "id,nombre,direccion,ubicacion,instagram,face,whats,logo",
            str(i) + ",'" + nomGim + "','" + direcGim + "','"
            + request.form.get("Ubicacion") + "','" +
            request.form.get("Instagram") + "','"
            + request.form.get("Contacto") + "','" +
            request.form.get("Facebook") + "','Imagenes"
            + url_for('obtener_nombre', filename=nombre)[8:] + "'"
        )
        for dato in instru:
            dato = dato.split(",")
            resu = conectarOne(
                "select 1 from enseñaen en "
                "where en.tdoc=" + dato[0] + " and en.doc='" + dato[1]
                + "' and en.idgim=" + str(i)
            )
            if not resu:
                insTabla(
                    "enseñaen", "tdoc,doc,idgim",
                    dato[0] + ",'" + dato[1] + "'," + str(i)
                )
                nomUsu = conectarOne(
                    "select u.apellido, u.nombre "
                    "from usuario u where u.tdoc=" +
                    dato[0] + " and u.documento='" + dato[1] + "'"
                )
                if not os.path.isdir(f'static/Imagenes/{nomGim.replace(" ","")}/{nomUsu[0]}{nomUsu[1]}'):
                    os.makedirs(
                        f'static/Imagenes/{nomGim.replace(" ","")}/{nomUsu[0]}{nomUsu[1]}'
                    )
            return redirect("/MainBase")
    return render_template("/Agregar/AgregarGimnasio.html")


@app.route("/selGimInstru")
def selGimInstru():
    # tiempoSesion()
    condiEx = ""
    if session['cargo'] == 2:
        condiEx = " and exists(select 1 from cabeza ca where ca.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and ca.tdoccabeza=" + str(session['tdoc'])
        condiEx += " and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    usuario = conectarAll(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo'
        ' from usuario u, categoria c'
        ' where u.cargo <> 1 and c.id = u.categoria' + condiEx
    )
    dic = {'value': [], 'text': [], 'lim': 0}
    for tdoc, doc, ape, nom, cate in usuario:
        dic['value'].append(f'{tdoc},{doc}')
        dic['text'].append(f'{ape} {nom} {cate}')
        dic['lim'] += 1
    return jsonify(dic)


@app.route("/aEvento", methods={'GET', 'POST'})
def aEvento():
    # tiempoSesion()
    tipo = conectarAll("select * from tipoevento")
    if request.method == 'POST':
        eFecha = request.form.get("Fecha")
        eTipo = request.form.get("Tipo")
        i = 1
        while conectarOne("select 1 from evento e where e.id='" + str(i) + "'"):
            i += 1
        if not conectarOne("select 1 from evento e where e.fecha='" + eFecha + "' and e.tipo=" + eTipo):
            insTabla(
                "evento", "id,tipo,fecha,descripcion",
                str(i) + "," + eTipo + ",'" + eFecha + "','"
                + request.form.get("Descripcion") + "'"
            )
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarEvento.html", tipoEvento=tipo)


@app.route("/aAlumno/<string:msj>", methods={'GET', 'POST'})
def aAlumno(msj):
    # tiempoSesion()
    categoria =  conectarAll("select * from categoria")
    tDoc = conectarAll("select * from tipodocumento")
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
    usuario = list(conectarAll(query + " group by u.tdoc,u.documento,u.apellido,u.nombre,c.tipo "))
    if request.method == 'POST':
        if not request.form.get("Instructor"):
            return redirect('/aAlumno/No se introdujo el instructor')
        if not request.form.get("Gimnasio"):
            return redirect('/aAlumno/No se introdujo el gimnasio')
        if not request.form.get("Nombre"):
            return redirect('/aAlumno/No se introdujo el nombre del alumno')
        if not request.form.get("Apellido"):
            return redirect('/aAlumno/No se introdujo el apellido del alumno')
        if not request.form.get("Documento"):
            return redirect('/aAlumno/No se introdujo el documento del alumno')
        if not request.form.get("fNacimiento"):
            return redirect('/aAlumno/No se introdujo fecha de nacimiento del alumno')
        if not request.form.get("fInscripcion"):
            return redirect('/aAlumno/No se introdujo fecha de inscripcion a la escuela')
        tdoc = request.form.get("TipoDocumento")
        doc = request.form.get("Documento").replace(".","")
        aluExt = conectarOne(
                "select a.apellido, a.nombre, u.nombre, u.apellido, g.nombre from alumno a, usuario u, gimnasio g "
                "where a.documento='" + doc + "' and a.tdoc=" + tdoc + " and a.docinstru=u.documento and a.tdocinstru=u.tdoc and a.idgim=g.id"
             )
        if aluExt:
            return redirect(
                    "/aAlumno/El documento " + doc + " ya fue registrado al alumno " + aluExt[0] + " " + aluExt[1]
                    + " del instructor " + aluExt[2] + " " + aluExt[3] + " y gimnasio " + aluExt[4]
                )
        instru = request.form.get("Instructor").split(",")
        idGim = request.form.get("Gimnasio")
        nomGim = conectarOne("select g.nombre from gimnasio g where g.id=" + idGim)[0]
        nomUsu = conectarOne(
            "select u.apellido, u.nombre from usuario u "
            "where u.tdoc=" + instru[0] + " and u.documento=" + instru[1]
        )
        nombre = 'sin_foto.png'
        if request.files["Foto"]:
            nombre = photos.save(
                request.files["Foto"], f'{nomGim.replace(" ","")}/{nomUsu[0]}{nomUsu[1]}'
            )
        msj = "Se registro al alumno: Nombre: "+ request.form.get("Nombre").capitalize()
        msj += ". Apellido: "+ request.form.get("Apellido").capitalize()
        msj += ". Instructor: " + nomUsu[0]
        msj +=" " + nomUsu[1]
        msj += ". Gimnasio: " + nomGim
        insTabla(
            "alumno", "nombre,apellido,tdoc,documento,categoria,nacionalidad,"
            + "finscripcion,observaciones,email,localidad,fnac,libreta,foto,"
            + "tdocinstru,docinstru,idgim",
            "'" + request.form.get("Nombre").capitalize() + "','" +
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
            + "'," + idGim
        )
        contacto = request.form.getlist("Contacto")
        telefono = request.form.getlist("Telefono")
        for con, tel in zip(contacto, telefono):
            if con and tel:
                insTabla(
                    "telefono", "telefono,contacto,tdoc,documento",
                    "'" + tel + "','" + con + "'," + tdoc + ",'" + doc + "'"
                )
        if request.form.get("Libreta") == "0":
            i = 1
            while conectarOne("select 1 from notificacion n where n.id=" + str(i)):
                i += 1
            insTabla(
                "notificacion", "id,texto",
                str(i) + ",'Se ha registrado al alumno " + request.form.get("Apellido").capitalize()
                + " " + request.form.get("Nombre").capitalize() + " (Sin libreta)'"
                )
            for tdoc, doc in conectarAll("select u.tdoc, u.documento from usuario u where u.cargo=1"):
                insTabla(
                    "notifica", "tdoc,documento,idnoti",
                    str(tdoc) + ",'" + doc + "'," + str(i)
                    )
        return redirect('/aAlumno/' + msj)
        # return render_template("/Agregar/AgregarAlumno.html",
        #     categoria=categoria,tdoc=tDoc,
        #     usuario=usuario, msj="Se registro al alumno:\nNombre: "
        #     + request.form.get("Nombre").capitalize() + "\nApellido: " + request.form.get("Apellido").capitalize()
        #     + "\nInstructor: " + nomUsu[0] + " " + nomUsu[1] + "\nGimnasio: " + nomGim
        # )
    return render_template("/Agregar/AgregarAlumno.html", categoria=categoria,tdoc=tDoc, usuario=usuario, msj=' ' if msj=='-' else msj)


@app.route("/aNotificacion", methods={'GET', 'POST'})
def aNotificacion():
    # tiempoSesion()
    usuario = list(conectarAll(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo, 0 "
        "from usuario u, categoria c "
        "where c.id = u.categoria"
    ))
    usuario.insert(0, ('', '', 'Todos', '', '', 1))
    if request.method == 'POST':
        i = 1
        while conectarOne(
            "select 1 from notificacion n where n.id=" + str(i)
        ):
            i += 1
        i = str(i)
        insTabla(
            "notificacion", "id,texto",
            i + ",'" + request.form.get("Descripcion") + "'"
        )
        destino = request.form.getlist("Destino")
        for item in destino:
            dest = item.split(",")
            insTabla(
                "notifica", "tdoc,documento,idnoti",
                dest[0] + ",'" + dest[1] + "'," + i
            )
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarNotificacion.html", usuario=usuario)


@app.route("/aImagen", methods={'GET', 'POST'})
def aImagen():
    # tiempoSesion()
    fEvento = conectarAll(
        "select max(e.fecha), e.tipo from evento e "
        "group by e.tipo"
    )
    evento = []
    for fecha, tipo in fEvento:
        idEve = conectarOne(
            "select e.id from evento e where e.fecha='" +
            str(fecha) + "' and e.tipo=" + str(tipo)
        )[0]
        tipoEve = conectarOne("select te.tipo from tipoevento te where te.id=" + str(tipo))[0]
        evento.append((idEve, fecha, tipoEve))
    if request.method == 'POST' and request.files["Foto"]:
        idEve = request.form.get("Evento")
        direc = conectarAll(
            "select i.direccion, 1 from imagen i, evento e, tipoevento te "
            "where i.idevento=e.id and e.tipo=te.id and e.tipo = ( "
                "select eve.tipo from evento eve where eve.id='" + idEve + "' "
            ")"
        )
        for elim, _ in direc:
            os.remove(f'static/{elim}')
        delTabla("imagen","idevento=" + idEve)
        tipo = conectarOne(
            "select te.tipo "
            "from evento e, tipoevento te "
            "where e.id=" + idEve + " and e.tipo=te.id"
        )[0].replace(" ","")
        for i in request.files.getlist("Foto"):
            nombre = photos.save(
                i, f'Eventos/{tipo}'
            )
            insTabla(
                "imagen", "idevento,direccion",
                idEve + ",'Imagenes" + url_for('obtener_nombre', filename=nombre)[8:] + "'"
            )
        return redirect("/MainBase")
    return render_template("/Agregar/AgregarImagen.html", evento=evento)

# Ver


@app.route("/vUsuario")
def vUsuario():
    # tiempoSesion()
    return render_template("/Ver/VerUsuario.html")


@app.route("/verUsuario/<int:tUsuario>")
def verUsuario(tUsuario):
    # tiempoSesion()
    usuario = conectarAll(
        "select u.nombre, u.apellido, c.tipo, u.tdoc, u.documento "
        "from usuario u, categoria c "
        "where u.cargo=" + str(tUsuario) + " and u.categoria=c.id"
    )
    dicUsu = {
        'nomUsu': [], 'apeUsu': [], 'cateUsu': [], 'lim': 0,
        'tdocUsu': [], 'docUsu': []
    }
    llenarDiccionarioUsuario(usuario, dicUsu)
    return jsonify(dicUsu)


@app.route("/verInstructores")
def verInstructores():
    # tiempoSesion()
    usuario = conectarAll(
        "select u.nombre, u.apellido, c.tipo, u.tdoc, u.documento "
        "from usuario u, categoria c, enseñaen ee "
        "where u.tdoc=ee.tdoc and u.documento=ee.doc and u.categoria=c.id "
        "group by u.nombre, u.apellido, c.tipo, u.tdoc, u.documento"
    )
    dicUsu = {
        'nomUsu': [], 'apeUsu': [], 'cateUsu': [], 'lim': 0,
        'tdocUsu': [], 'docUsu': []
    }
    llenarDiccionarioUsuario(usuario, dicUsu)
    return jsonify(dicUsu)


@app.route("/verTodoUsuario")
def verTodoUsuario():
    # tiempoSesion()
    usuario = conectarAll(
        "select u.nombre, u.apellido, c.tipo, u.tdoc, u.documento "
        "from usuario u, categoria c "
        "where u.categoria=c.id"
    )
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
    # tiempoSesion()
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
    usuario = list(conectarAll(
        "select u.tdoc, u.documento, u.nombre, u.apellido, c.tipo"
        " from usuario u, " + condiEx + ", categoria c"
        " where u.documento=uee.doc and u.tdoc=uee.tdoc and c.id=u.categoria"
    ))
    usuario.insert(0, ('', '', '', '', ''))
    return render_template("/Ver/VerGimnasio.html", usuario=usuario)


@app.route("/verGimnasio/<int:tdoc>/<string:doc>")
def verGimnasio(tdoc, doc):
    # tiempoSesion()
    gimnasio = conectarAll(
        "select g.id, g.nombre, g.direccion "
        "from gimnasio g, enseñaen ee "
        "where ee.tdoc=" +
        str(tdoc) + " and ee.doc='" + doc + "' and ee.idgim=g.id"
    )
    dicGim = {
        'id': [], 'nom': [], 'direc': [], 'lim': 0,
        'onclick': 'desaGim', 'valBot': 'Deshabilitar',
        'verElim': "Ver", 'func': "detalleGimnasio"
    }
    llenarDiccionarioGimnasio(gimnasio, dicGim)
    return jsonify(dicGim)


@app.route("/verTodoGimnasio")
def verTodoGimnasio():
    # tiempoSesion()
    query = "(select ee.idgim from enseñaen ee group by ee.idgim) as tee"
    if session['cargo'] == 2:
        query = "(select ee.idgim from enseñaen ee, cabeza c, usuario u where c.tdoccabeza="
        query += str(session['tdoc'])
        query += " and c.doccabeza='" + session['doc']
        query += "' and c.tdoc=u.tdoc and c.documento=u.documento "
        query += "and u.tdoc=ee.tdoc and u.documento=ee.doc "
        query += "GROUP BY ee.idgim) as tee"
    elif session['cargo'] == 3:
        query = "(select ee.idgim from enseñaen ee, instructor i, usuario u where i.tdocinstru="
        query += str(session['tdoc'])
        query += " and i.docinstru='" + session['doc']
        query += "' and i.tdoc=u.tdoc and i.documento=u.documento "
        query += "and u.tdoc=ee.tdoc and u.documento=ee.doc "
        query += "GROUP BY ee.idgim) as tee"
    gimnasio = conectarAll(
        "select g.id, g.nombre, g.direccion from " + query
        + ", gimnasio g where tee.idgim=g.id"
        )
    dicGim = {
        'id': [], 'nom': [], 'direc': [], 'lim': 0,
        'onclick': 'desaGim', 'valBot': 'Deshabilitar',
        'verElim': "Ver", 'func': "detalleGimnasio"
    }
    llenarDiccionarioGimnasio(gimnasio, dicGim)
    return jsonify(dicGim)

@app.route("/direcGimnasio/<int:idGim>")
def direcGimnasio(idGim):
    # tiempoSesion()
    return render_template("Detalles/DetalleGimnasio.html", idGim=idGim)

@app.route("/dGimnasio/<int:idGim>")
def dGimnasio(idGim):
    # tiempoSesion()
    gim = conectarOne(
        "select * from gimnasio g "
        "where g.id=" + str(idGim)
    )
    return jsonify({
        'nom': gim[1], 'direc': gim[2], 'ubi': gim[3], 'insta': gim[4],
        'face': gim[6], 'whats': gim[5], 'logo': "/static/" + gim[7]
    })

@app.route("/verDesaHabi/<int:valor>")
def verDesaHabi(valor):
    # tiempoSesion()
    gimnasio = []
    dicGim = {
        'id': [], 'nom': [], 'direc': [], 'lim': 0,
        'onclick': '', 'valBot': '',
        'verElim': "Ver", 'func': "detalleGimnasio"
    }
    if valor == 0:
        gimnasio = conectarAll(
            "select g.id, g.nombre, g.direccion "
            "from gimnasio g "
            "where not exists ("
            "select 1 from enseñaen ee "
            "where ee.idgim=g.id"
            ")"
        )
        dicGim['onclick'] = "habiGim"
        dicGim['valBot'] = "Habilitar"
        dicGim['verElim'] = "Eliminar"
        dicGim['func'] = "elimGim"
    else:
        gimnasio = conectarAll(
            "select g.id, g.nombre, g.direccion "
            "from (select ee.idgim from enseñaen ee group by ee.idgim) as tee, gimnasio g "
            "where tee.idgim=g.id"
        )
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
    # tiempoSesion()
    tEvento = list(conectarAll(
        "select te.id, te.tipo "
        "from tipoevento te"
    ))
    tEvento.insert(0, ('', ''))
    return render_template("/Ver/VerEvento.html", tEvento=tEvento)


@app.route("/verEvento/<int:tipo>/<string:fDesde>/<string:fHasta>")
def verEvento(tipo, fDesde, fHasta):
    # tiempoSesion()
    query = "select e.id, e.fecha, te.tipo from evento e, tipoevento te where e.tipo=te.id "
    if tipo != 0:
        query += "and e.tipo=" + str(tipo) + " "
    if fDesde != "-":
        query += "and e.fecha >= '" + fDesde + "' "
    if fHasta != "-":
        query += "and e.fecha <= '" + fHasta + "' "
    query += "order by e.fecha desc "
    evento = conectarAll(query)
    dicEvento = {'id': [], 'fecha': [], 'tipo': [], 'lim': 0}
    llenarDiccionarioEvento(evento, dicEvento)
    return jsonify(dicEvento)


def llenarDiccionarioEvento(recorrer, dicEven):
    for id, fecha, tipo in recorrer:
        dicEven['id'].append(id)
        dicEven['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.year}')
        dicEven['tipo'].append(tipo)
        dicEven['lim'] += 1


@app.route("/vAlumno")
def vAlumno():
    # tiempoSesion()
    categoria = list(conectarAll("select c.id, c.tipo from categoria c where c.id < 14"))
    categoria.insert(0, ("-", ""))
    exaCap = conectarOne(
        "select min(e.fecha) from evento e where e.tipo=1 and e.fecha >='" + str(datetime.now()) + "'"
    )[0]
    if exaCap:
        exaCap = f'{exaCap.day}/{exaCap.month}/{exaCap.year}'
    exaProv = conectarOne(
        "select min(e.fecha) from evento e where e.tipo=4 and e.fecha >='" + str(datetime.now()) + "'"
    )[0]
    if exaProv:
        exaProv = f'{exaProv.day}/{exaProv.month}/{exaProv.year}'
    tor = conectarOne(
        "select min(e.fecha) from evento e where e.tipo=2 and e.fecha >='" + str(datetime.now()) + "'"
    )[0]
    if tor:
        tor = f'{tor.day}/{tor.month}/{tor.year}'
    otro = conectarOne(
        "select min(e.fecha) from evento e where e.tipo=3 and e.fecha >='" + str(datetime.now()) + "'"
    )[0]
    if otro:
        otro = f'{otro.day}/{otro.month}/{otro.year}'
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
    usuario = list(conectarAll(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
        " from usuario u, categoria c"
        " where u.cargo <> 1 and u.categoria=c.id" + condiEx
    ))
    usuario.insert(0, ("", "", "", "", ""))
    gimnasio = list(conectarAll(condiGim))
    gimnasio.insert(0, ("", ""))
    return render_template(
        "/Ver/VerAlumno.html", categoria=categoria,
        exaCap=exaCap, exaProv=exaProv, tor=tor, otro=otro, usuario=usuario,
        gimnasio=gimnasio, cargo=True if session['cargo'] == 1 else False
    )


@app.route(
    "/filtroAlumno/<string:nom>/<string:ape>/<string:cate>"
    "/<string:fdExamen>/<string:fhExamen>/<string:fdAATEE>"
    "/<string:fhAATEE>/<string:fdEnat>/<string:fhEnat>"
    "/<string:tdocUsu>/<string:docUsu>/<string:idGim>"
)
def filtroAlumno(
    nom, ape, cate, fdExamen, fhExamen,
    fdAATEE, fhAATEE, fdEnat, fhEnat,
    tdocUsu, docUsu, idGim
):
    # tiempoSesion()
    query = "SELECT alucate.tdoc, alucate.documento, alucate.nombre, alucate.apellido, alucate.edad, alucate.libreta,"
    query += " alucate.tipo, alucate.insNombre, alucate.insApellido, alucate.gimNombre,"
    query += " pEvento.fecha as fEvento, aatee.fecha as fAATEE, enat.fecha as fEnat "
    query += "from (SELECT a.tdoc, a.documento, a.nombre, a.apellido, c.tipo,"
    query += " a.fnac as edad, a.libreta, "
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
        query += str(session['tdoc']) + " and c.doccabeza='"
        query += session['doc'] + \
            "' and u.tdoc=c.tdoc and u.documento=c.documento"
        query += " and a.tdocinstru=u.tdoc and a.docinstru=u.documento) and "
    elif session['cargo'] == 3:
        query += "exists (select 1 from usuario u, instructor i where i.tdocinstru= "
        query += str(session['tdoc']) + " and i.docinstru='"
        query += session['doc'] + \
            "' and u.tdoc=i.tdoc and u.documento=i.documento"
        query += " and a.tdocinstru=u.tdoc and a.docinstru=u.documento) and "
    query += "u.tdoc=ee.tdoc and u.documento=ee.doc and ee.idgim=g.id and a.tdocinstru=u.tdoc and a.docinstru=u.documento and a.idgim = g.id and a.categoria=c.id and "
    query += "not exists (select 1 from aludesa ad where ad.tdocalu=a.tdoc and ad.docalu=a.documento)) as alucate "
    if fdExamen != "-" or fhExamen != "-":
        query += "JOIN (select max(e.fecha) as fecha, p.tdoc, p.doc from evento e, participa p WHERE (e.tipo=1 or e.tipo=4) "
        if fdExamen != "-" and fhExamen != "-":
            query += "and e.fecha between '" + fdExamen + "' and '" + fhExamen + "' "
        elif fdExamen != "-":
            query += "and e.fecha >= '" + fdExamen + "' "
        else:
            query += "and e.fecha <= '" + fhExamen + "' "
    else:
        query += "LEFT JOIN (select max(e.fecha) as fecha, p.tdoc, p.doc from evento e, participa p WHERE (e.tipo=1 or e.tipo=4) "
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
        query += "JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=2 "
        if fdEnat != "-" and fhEnat != "-":
            query += "and m.fecha between '" + fdEnat + "' and '" + fhEnat + "' "
        elif fdEnat != "-":
            query += "and m.fecha >= '" + fdEnat + "' "
        else:
            query += "and m.fecha <= '" + fhEnat + "' "
    else:
        query += "LEFT JOIN (select m.tdoc, m.doc, max(m.fecha) as fecha from matricula m, tipomatri tm WHERE tm.id=2 "
    query += "and m.tipo=tm.id group by m.tdoc, m.doc) AS enat on enat.tdoc=alucate.tdoc AND enat.doc=alucate.documento "
    query += "order by alucate.apellido, alucate.nombre"
    alumno = conectarAll(query)
    dicAlu = {
        'tdoc': [], 'doc': [], 'nom': [], 'ape': [], 'cate': [], 'fecha': [],
        'fAATEE': [], 'fEnat': [], 'lim': 0, 'insNom': [],
        'insApe': [], 'gimNom': [], 'edad': [], 'libreta': []
    }
    hoy = datetime.now()
    for tDocAlu, docAlu, nomAlu, apeAlu, fnac, libreta , cateAlu, insNom, insApe, gimNom, feAlu, faAlu, fEnatAlu in alumno:
        dicAlu["tdoc"].append(tDocAlu)
        dicAlu["doc"].append(docAlu)
        dicAlu["nom"].append(nomAlu)
        dicAlu["ape"].append(apeAlu)
        dicAlu["cate"].append(cateAlu)
        if feAlu:
            dicAlu["fecha"].append(f'{feAlu.day}/{feAlu.month}/{feAlu.year}')
        else:
            dicAlu["fecha"].append("---")
        if faAlu:
            dicAlu["fAATEE"].append(f'{faAlu.day}/{faAlu.month}/{faAlu.year}')
        else:
                dicAlu["fAATEE"].append("---")
        if fEnatAlu:
            dicAlu["fEnat"].append(f'{fEnatAlu.day}/{fEnatAlu.month}/{fEnatAlu.year}')
        else:
            dicAlu["fEnat"].append("---")
        dicAlu["insNom"].append(insNom)
        dicAlu["insApe"].append(insApe)
        dicAlu["gimNom"].append(gimNom)
        dicAlu["libreta"].append(libreta)
        edad = hoy.year - fnac.year
        edad += 1 if (fnac.month < hoy.month) or (fnac.month == hoy.month and fnac.day >= hoy.day) else 0
        dicAlu['edad'].append(edad)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)


@app.route("/vDesaAlu")
def vDesaAlu():
    # tiempoSesion()
    alumno = conectarAll(
        "select a.tdoc, a.documento, a.apellido, a.nombre, c.tipo, d.fecha, "
        " a.fnac "
        "from alumno a, categoria c, aludesa d "
        "where a.categoria=c.id and a.tdoc=d.tdocalu and a.documento=d.docalu"
        " order by a.apellido, a.nombre"
    )
    dicAlu = {
        'tdoc': [], 'doc': [], 'ape': [], 'nom': [], 'cate': [], 'fecha': [], 'lim': 0, 'edad': []
    }
    hoy = datetime.now()
    for tdoc, doc, ape, nom, cate, fecha, fnac in alumno:
        dicAlu['tdoc'].append(tdoc)
        dicAlu['doc'].append(doc)
        dicAlu['ape'].append(ape)
        dicAlu['nom'].append(nom)
        dicAlu['cate'].append(cate)
        if fecha:
            dicAlu['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.year}')
        else:
            dicAlu['fecha'].append("---")
        edad = hoy.year - fnac.year
        edad += 1 if (fnac.month < hoy.month) or (fnac.month == hoy.month and fnac.day >= hoy.day) else 0
        dicAlu['edad'].append(edad)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)


@app.route("/filtroDesaAlu/<string:nom>/<string:ape>/<string:cate>")
def filtroDesaAlu(nom, ape, cate):
    # tiempoSesion()
    query = "select a.tdoc, a.documento, a.apellido, a.nombre, c.tipo, d.fecha, a.fnac "
    query += "from alumno a, categoria c, aludesa d where "
    if nom != "-":
        query += "a.nombre like'%" + nom + "%' and "
    if ape != "-":
        query += "a.apellido like'%" + ape + "%' and "
    if cate != "-":
        query += "c.id=" + cate + " and "
    query += "c.id=a.categoria and d.tdocalu=a.tdoc and a.documento=d.docalu order by a.apellido, a.nombre"
    alumno = conectarAll(query)
    dicAlu = {
        'tdoc': [], 'doc': [], 'ape': [], 'nom': [],
        'cate': [], 'fecha': [], 'lim': 0, 'edad': []
    }
    hoy = datetime.now()
    for tdoc, doc, apealu, nomAlu, cate, fecha, fnac in alumno:
        dicAlu['tdoc'].append(tdoc)
        dicAlu['doc'].append(doc)
        dicAlu['ape'].append(apealu)
        dicAlu['nom'].append(nomAlu)
        dicAlu['cate'].append(cate)
        dicAlu['fecha'].append(fecha)
        edad = hoy.year - fnac.year
        edad -= 1 if fnac.month <= hoy.month and fnac.day <= hoy.day else 0
        dicAlu['edad'].append(edad)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)


@app.route("/vImagen")
def vImagen():
    # tiempoSesion()
    return render_template("/Ver/VerImagen.html")


@app.route("/filtrarImagen/<int:tipo>")
def filtrarImagen(tipo):
    # tiempoSesion()
    dicEven = {'id': [], 'direc': [], 'lim': 0, 'tipo': ""}
    llenarDicImagen(dicEven, 'lim', tipo)
    dicEven['tipo'] = conectarOne(
        "select te.tipo from tipoevento te where te.id=" + str(tipo)
    )[0]
    return jsonify(dicEven)


@app.route("/vTodoImagen")
def vTodoImagen():
    # tiempoSesion()
    dicEven = {'id': [], 'direc': [], 'limExaCap': 0, 'limTor': 0, 'limVar': 0, 'limExaProb': 0}
    llenarDicImagen(dicEven, 'limExaCap', 1)
    llenarDicImagen(dicEven, 'limTor', 2)
    llenarDicImagen(dicEven, 'limVar', 3)
    llenarDicImagen(dicEven, 'limExaProb', 4)
    return jsonify(dicEven)


def llenarDicImagen(dicEven, lim, tipo):
    recorre = conectarAll(
        "select i.* from imagen i, evento e "
        "where e.tipo =" + str(tipo) + " and e.id=i.idevento"
    )
    for idImg, direc in recorre:
        dicEven['id'].append(idImg)
        dicEven['direc'].append(direc)
        dicEven[lim] += 1

# Detalles


@app.route("/detalleUsuario/<int:tdoc>/<string:doc>")
def detalleUsuario(tdoc, doc):
    # tiempoSesion()
    return render_template("/Detalles/DetalleUsuario.html", tdoc=tdoc, doc=doc)


@app.route("/dUsuario/<int:tdoc>/<string:doc>")
def dUsuario(tdoc, doc):
    # tiempoSesion()
    usuario = conectarOne(
        "select usu.nombre, usu.apellido, usu.categoria, usu.cargo, usu.email, td.tipo, usu.documento, "
        "cabe.apellido, cabe.nombre, instru.apellido, instru.nombre "
        "from tipodocumento td, ("
            "select u.nombre, u.apellido, c.tipo as categoria, ca.tipo as cargo, u.email, u.tdoc, u.documento "
            "from usuario u, categoria c, cargo ca "
            "where u.tdoc=" + str(tdoc) + " and u.documento='" + doc
            + "' and u.categoria=c.id and ca.id=u.cargo"
        ") as usu "
        "left join( "
            "select u.apellido, u.nombre, " + str(tdoc) + " as tdoc, '" + doc
            + "' as doc from usuario u, cabeza c "
            "where c.doccabeza=u.documento and c.tdoccabeza=u.tdoc "
            "and c.doccabeza<>c.documento and c.tdoccabeza=c.tdoc "
            "and c.tdoc=" + str(tdoc) + " and c.documento='" + doc + "' "
        ") as cabe "
        "on cabe.tdoc=usu.tdoc and cabe.doc=usu.documento "
        "left join( "
            "select u.apellido, u.nombre, " + str(tdoc) + " as tdoc, '" + doc
            + "' as doc from usuario u, instructor i "
            "where i.docinstru=u.documento and i.tdocinstru=u.tdoc "
            "and i.docinstru<>i.documento and i.tdocinstru=i.tdoc "
            "and i.tdoc=" + str(tdoc) + " and i.documento='" + doc + "' "
        ") as instru "
        "on instru.tdoc=usu.tdoc and instru.doc=usu.documento "
        "WHERE td.id=usu.tdoc"
    )
    return jsonify({
        'nom': usuario[0], 'ape': usuario[1], 'cate': usuario[2], 'cargo': usuario[3],
        'mail': usuario[4], 'tdoc': usuario[5], 'doc': usuario[6],
        'cabeza': f'{usuario[7]} {usuario[8]}', 'instructor': f'{usuario[9]} {usuario[10]}'
    })


@app.route("/gUsuario/<int:tdoc>/<string:doc>")
def gUsuario(tdoc, doc):
    # tiempoSesion()
    gimnasio = conectarAll(
        "select g.nombre, g.direccion from gimnasio g, enseñaen ee "
        "where ee.tdoc=" + str(tdoc) + " and ee.doc=" +
         doc + " and ee.idgim=g.id"
    )
    dicGim = {'nom': [], 'direc': [], 'lim': 0}
    for nom, dire in gimnasio:
        dicGim['nom'].append(nom)
        dicGim['direc'].append(dire)
        dicGim['lim'] += 1
    return jsonify(dicGim)


@app.route("/verContra/<int:tdoc>/<string:doc>")
def verContra(tdoc, doc):
    # tiempoSesion()
    usuario = conectarOne(
        "select u.contraseña from usuario u "
        "where u.tdoc=" + str(tdoc) + " and u.documento=" + doc
    )[0]
    return jsonify({'contra': usuario})

@app.route("/detalleGimnasio/<int:idGim>")
def detalleGimnasio(idGim):
    # tiempoSesion()
    gimnasio = conectarOne(
        "select g.id, g.nombre, g.direccion, g.logo"
        " from gimnasio g where g.id=" + str(idGim)
    )
    return jsonify({
        'id': gimnasio[0], 'nom': gimnasio[1], 'direc': gimnasio[2],
        'logo': "/static/" + gimnasio[3]
    })


@app.route("/vAluGimnasio/<int:idGim>")
def vAluGimnasio(idGim):
    # tiempoSesion()
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
    alumno = conectarAll(
        "select a.nombre, a.apellido, c.tipo"
        " from alumno a, categoria c where a.idgim=" + str(idGim)
        + " and a.categoria=c.id" + query
    )
    dicAlu = {'nom': [], 'ape': [], 'cate': [], 'lim': 0}
    for nom, ape, cate in alumno:
        dicAlu['nom'].append(nom)
        dicAlu['ape'].append(ape)
        dicAlu['cate'].append(cate)
        dicAlu['lim'] += 1
    return jsonify(dicAlu)


@app.route("/detalleEvento/<int:idEve>")
def detalleEvento(idEve):
    # tiempoSesion()
    evento = conectarOne(
        "select e.id, 1 from evento e "
        "where e.id=" + str(idEve)
    )
    return render_template(
        "Detalles/DetalleEvento.html", idEve=evento[0]
    )

@app.route("/dEvento/<int:idEve>")
def dEvento(idEve):
    # tiempoSesion()
    evento = conectarOne(
        "select e.id, e.fecha, e.descripcion, te.tipo "
        "from evento e, tipoevento te "
        "where e.id=" + str(idEve) + " and e.tipo=te.id"
    )
    return jsonify({
        'idEve': evento[0], 'fecha': f'{evento[1].day}/{evento[1].month}/{evento[1].year}' if evento[1] else "---",
        'desc': evento[2], 'tipo': evento[3],
        'cargo': True if session['cargo'] == 1 else False
    })


@app.route("/vAluEvento/<int:idEve>")
def vAluEvento(idEve):
    # tiempoSesion()
    condiEx = ""
    if session['cargo'] == 2:
        condiEx = " and exists (select 1 from cabeza c, usuario u where c.tdoccabeza="
        condiEx += str(session['tdoc']) + " and c.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and c.tdoc=u.tdoc and c.documento=u.documento"
        condiEx += " and a.tdocinstru=u.tdoc and a.docinstru=u.documento)"
    elif session['cargo'] == 3:
        condiEx = " and exists (select 1 from instructor i, usuario u where i.tdocinstru="
        condiEx += str(session['tdoc']) + " and i.docinstru='"
        condiEx += session['doc']
        condiEx += "' and i.tdoc=u.tdoc and i.documento=u.documento"
        condiEx += " and a.tdocinstru=u.tdoc and a.docinstru=u.documento)"
    evento = conectarAll(
        "select a.nombre, a.apellido, c.tipo"
        " from alumno a, participa p, evento e, categoria c"
        + " where e.id=" + str(idEve) +
        " and e.id=p.idevento and p.tdoc=a.tdoc and p.doc=a.documento and p.categoria=c.id"
        + condiEx + " order by a.apellido, a.nombre"
    )
    dicAluEve = {'nom': [], 'ape': [], 'cate': [], 'lim': 0, 'idEve': idEve}
    for nom, ape, cate in evento:
        dicAluEve['nom'].append(nom)
        dicAluEve['ape'].append(ape)
        dicAluEve['cate'].append(cate)
        dicAluEve['lim'] += 1
    return jsonify(dicAluEve)


@app.route("/detalleAlumno/<int:tdoc>/<string:doc>")
def detalleAlumno(tdoc, doc):
    # tiempoSesion()
    alumno = conectarOne(
        "select a.tdoc, a.documento from alumno a "
        "where a.tdoc=" + str(tdoc) + " and a.documento='" + doc + "'"
    )
    return render_template("Detalles/DetalleAlumno.html", tdoc=alumno[0], doc=alumno[1])

@app.route("/dAlumno/<int:tdoc>/<string:doc>")
def dAlumno(tdoc, doc):
    # tiempoSesion()
    alumno = conectarOne(
        "select a.nombre, a.apellido, c.tipo, a.nacionalidad, a.fnac, "
        "a.finscripcion, a.observaciones, a.email, a.localidad, a.foto, "
        "u.nombre, u.apellido, g.nombre, td.tipo, a.documento "
        "from alumno a, categoria c, usuario u, gimnasio g, tipodocumento td "
        "where td.id=a.tdoc and a.documento=" + doc + " and a.tdoc=" + str(tdoc)
        + " and a.categoria=c.id and a.docinstru=u.documento and a.tdocinstru=u.tdoc and "
        "a.idgim=g.id"
    )
    return jsonify({
        'nom': alumno[0], 'ape': alumno[1], 'cate': alumno[2], 'nacio': alumno[3],
        'fnac': f'{alumno[4].day}/{alumno[4].month}/{alumno[4].year}',
        'finsc': f'{alumno[5].day}/{alumno[5].month}/{alumno[5].year}', 'obs': alumno[6], 'mail': alumno[7],
        'loc': alumno[8], 'foto': "/static/" + alumno[9], 'nominstru': alumno[10],
        'apeinstru': alumno[11], 'nomgim': alumno[12], 'tdoc': alumno[13], 'doc': alumno[14],
        'matri': True if session['cargo'] == 1 else False
    })


@app.route("/vEveAlumno/<int:tdoc>/<string:doc>")
def vEveAlumno(tdoc, doc):
    # tiempoSesion()
    evento = conectarAll(
        "select e.fecha, te.tipo, c.tipo "
        "from evento e, participa p, tipoevento te, categoria c "
        "where p.tdoc=" + str(tdoc) + " and p.doc='" + doc + "' and "
        "p.categoria=c.id and p.idevento=e.id and e.tipo=te.id "
        "order by e.fecha"
    )
    dicEven = {'fecha': [], 'tipo': [], 'cate': [], 'lim': 0}
    for fecha, tipo, cate in evento:
        dicEven['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.day}')
        dicEven['tipo'].append(tipo)
        dicEven['cate'].append(cate)
        dicEven['lim'] += 1
    return jsonify(dicEven)


@app.route("/vMatriAlu/<int:tdoc>/<string:doc>")
def vMatriAlu(tdoc, doc):
    # tiempoSesion()
    matricula = conectarAll(
        "select m.fecha, tm.tipo "
        "from alumno a, matricula m, tipomatri tm "
        "where a.tdoc=" + str(tdoc) + " and a.documento=" + doc
        + " and a.tdoc=m.tdoc and  a.documento=m.doc and m.tipo=tm.id"
    )
    dicMatri = {'fecha': [], 'tipo': [], 'lim': 0}
    for fecha, tipo in matricula:
        dicMatri['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.year}')
        dicMatri['tipo'].append(tipo)
        dicMatri['lim'] += 1
    return jsonify(dicMatri)

# Editar


@app.route("/eUsuario/<int:tdoc>/<string:doc>/<string:retorno>", methods={'GET', 'POST'})
def eUsuario(tdoc, doc, retorno):
    # tiempoSesion()
    cargo = conectarAll('select * from cargo')
    categoria = conectarAll("select * from categoria c where c.id > 10")
    tDoc = conectarAll("select * from tipodocumento")
    instructor = list(conectarAll(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo "
        "from usuario u, categoria c "
        "where u.cargo <> 1 and c.id = u.categoria "
        "and not (u.tdoc=" + str(tdoc) + " and u.documento='" + doc + "')"
    ))
    instructor.insert(0, ('', '', '', '', ''))
    cabeza = list(conectarAll(
        'select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo '
        'from usuario u, categoria c '
        'where u.cargo = 2 and c.id = u.categoria'
    ))
    cabeza.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        usuario = conectarOne(
            "select usu.nombre, usu.apellido, usu.categoria, usu.cargo, usu.email, usu.tdoc, usu.documento, "
            "cabe.tdoccabeza, cabe.doccabeza, "
            "instru.tdocinstru, instru.docinstru "
            "from (select u.nombre, u.apellido, u.categoria, u.cargo, u.email, u.tdoc, u.documento "
            "from usuario u "
            "where u.tdoc=" + str(tdoc) +
            " and u.documento=" + doc + " ) as usu "
            "left join ("
            "select c.* from cabeza c "
            "where c.tdoc=c.tdoccabeza and c.doccabeza<>c.documento "
            "and c.documento='" + doc + "' and c.tdoc=" + str(tdoc) +
            ") as cabe "
            "on cabe.tdoc=usu.tdoc and cabe.documento=usu.documento "
            "left join ("
            "select i.* from instructor i "
            "where i.tdoc=i.tdocinstru and i.docinstru<>i.documento "
            "and i.documento='" + doc + "' and i.tdoc=" + str(tdoc) +
            ") as instru "
            "on instru.tdoc=usu.tdoc and instru.documento=usu.documento"
        )
        query = ""
        tdoc = str(tdoc)
        if usuario[0] != (nom := request.form.get("Nombre").capitalize()):
            query += " nombre='" + nom + "',"
        if usuario[1] != (ape := request.form.get("Apellido").capitalize()):
            query += " apellido='" + ape + "',"
        if usuario[2] != (cate := int(request.form.get("Categoria"))):
            query += " categoria=" + str(cate) + ","
        if usuario[4] != (mail := request.form.get("Email")):
            query += " email='" + mail + "',"
        if request.form.get("Cabeza") and f'{usuario[7]},{usuario[8]}' != request.form.get("Cabeza"):
            dato = request.form.get("Cabeza").split(",")
            upTabla(
                "cabeza", "tdoccabeza=" + dato[0] + ", doccabeza=" + dato[1],
                "tdoc=" + str(usuario[5]) + " and documento='" + usuario[6]
                + "' and tdoccabeza=tdoc and doccabeza<>documento"
            )
        if request.form.get("Instructor") and  f'{usuario[9]},{usuario[10]}' != request.form.get("Instructor"):
            dato = request.form.get("Instructor").split(",")
            upTabla(
                "instructor", "tdocinstru=" +
                dato[0] + ", docinstru=" + dato[1],
                "tdoc=" + str(usuario[5]) + " and documento='" + usuario[6]
                + "' and tdoc=tdocinstru and docinstru<>documento"
            )
        if usuario[3] != (cargo := int(request.form.get("Cargo"))):
            query += " cargo=" + str(cargo) + ","
            if cargo == 1:
                delTabla(
                    "cabeza", "tdoccabeza=" + tdoc + " and doccabeza='" + doc + "'"
                )
                delTabla(
                    "instructor", "tdocinstru=" + tdoc + " and docinstru='" + doc + "'"
                )
            elif cargo == 2:
                insTabla(
                    "cabeza", "tdoccabeza,doccabeza,tdoc,documento",
                    tdoc + ",'" + doc + "'," + tdoc + ",'" + doc + "'"
                )
                if usuario[3] == 1:
                    insTabla(
                        "instructor", "tdocinstru,docinstru,tdoc,documento",
                        tdoc + ",'" + doc + "'," + tdoc + ",'" + doc + "'"
                    )
            else:
                delTabla(
                    "cabeza", "tdoccabeza=" + tdoc + " and doccabeza='" + doc + "'"
                )
                if usuario[3] == 1:
                    insTabla(
                        "instructor", "tdocinstru,docinstru,tdoc,documento",
                        tdoc + ",'" + doc + "'," + tdoc + ",'" + doc + "'"
                    )
        if usuario[5] != int(request.form.get("TipoDocumento")
                             ) or usuario[6] != request.form.get("Documento"):
            nTdoc = request.form.get("TipoDocumento")
            nDoc = request.form.get("Documento")
            if usuario[5] != nTdoc and usuario[6] != nDoc:
                query += " tdoc=" + nTdoc + " and documento='" + nDoc + "',"
                upInstruCabe(
                    "tdoc=" + nTdoc + " and documento='" + nDoc + "'",
                    "tdoc=" + str(usuario[5]) +
                    " and documento='" + usuario[6] + "'",
                    "tdoccabeza=" + nTdoc + " and doccabeza='" + nDoc + "'",
                    "tdoccabeza=" +
                    str(usuario[5]) + " and doccabeza='" + usuario[6] + "'",
                    "tdoc=" + nTdoc + " and documento='" + nDoc + "'",
                    "tdoc=" + str(usuario[5]) +
                    " and documento='" + usuario[6] + "'",
                    "tdocinstru=" + nTdoc + " and docinstru='" + nDoc + "'",
                    "tdocinstru=" +
                    str(usuario[5]) + " and docinstru='" + usuario[6] + "'"
                )
            elif usuario[5] != nTdoc:
                query += " tdoc=" + nTdoc + ","
                upInstruCabe(
                    "tdoc=" + nTdoc,
                    "tdoc=" + str(usuario[5]) +
                    " and documento='" + usuario[6] + "'",
                    "tdoccabeza=" + nTdoc,
                    "tdoccabeza=" +
                    str(usuario[5]) + " and doccabeza='" + usuario[6] + "'",
                    "tdoc=" + nTdoc,
                    "tdoc=" + str(usuario[5]) +
                    " and documento='" + usuario[6] + "'",
                    "tdocinstru=" + nTdoc,
                    "tdocinstru=" +
                    str(usuario[5]) + " and docinstru='" + usuario[6] + "'"
                )
            elif usuario[6] != nDoc:
                query += " documento='" + nDoc + "',"
                upInstruCabe(
                    "documento='" + nDoc + "'",
                    "tdoc=" + str(usuario[5]) +
                    "documento='" + usuario[6] + "'",
                    "doccabeza='" + nDoc + "'",
                    "tdoccabeza=" +
                    str(usuario[5]) + " and doccabeza='" + usuario[6] + "'",
                    "documento='" + nDoc + "'",
                    "tdoc=" + str(usuario[5]) +
                    " and documento='" + usuario[6] + "'",
                    "docinstru='" + nDoc + "'",
                    "tdocinstru=" +
                    str(usuario[5]) + " and docinstru='" + usuario[6] + "'"
                )
        if query:
            upTabla("usuario", query[:-1], "tdoc=" +
                    str(tdoc) + " and documento='" + doc + "'")
        return redirect("/MainBase")
    return render_template(
        "/Editar/EditarUsuario.html", cargo=cargo, categoria=categoria,
        tDoc=tDoc, instructor=instructor, cabeza=cabeza, tdoc=tdoc, doc=doc, retorno=retorno
    )


def upInstruCabe(valN1, condi1, valN2, condi2, valN3, condi3, valN4, condi4):
    upTabla("cabeza", valN1, condi1)
    upTabla("cabeza", valN2, condi2)
    upTabla("instructor", valN3, condi3)
    upTabla("instructor", valN4, condi4)


@app.route("/cargarUsuario/<int:tdoc>/<string:doc>")
def cargarUsuario(tdoc, doc):
    # tiempoSesion()
    usuario = conectarOne(
        "select usu.nombre, usu.apellido, usu.categoria, usu.cargo, usu.email, usu.tdoc, usu.documento, "
        "cabe.tdoccabeza, cabe.doccabeza, instru.tdocinstru, instru.docinstru "
        "from (select u.nombre, u.apellido, u.categoria, u.cargo, u.email, u.tdoc, u.documento "
        "from usuario u "
        "where u.tdoc=" + str(tdoc) + " and u.documento=" + doc + " ) as usu "
        "left join ("
        "select c.* from cabeza c "
        "where c.tdoc=c.tdoccabeza and c.doccabeza<>c.documento "
        "and c.documento='" + doc + "' and c.tdoc=" + str(tdoc) +
        ") as cabe "
        "on cabe.tdoc=usu.tdoc and cabe.documento=usu.documento "
        "left join ("
        "select i.* from instructor i "
        "where i.tdoc=i.tdocinstru and i.docinstru<>i.documento "
        "and i.documento='" + doc + "' and i.tdoc=" + str(tdoc) +
        ") as instru "
        "on instru.tdoc=usu.tdoc and instru.documento=usu.documento"
        )
    return jsonify({
        'nom': usuario[0], 'ape': usuario[1], 'cate': usuario[2],
        'cargo': usuario[3], 'mail': usuario[4], 'tdoc': usuario[5],
        'doc': usuario[6], 'cabeza': f'{usuario[7]},{usuario[8]}' if usuario[7] and usuario[8] else None,
        'instructor': f'{usuario[9]},{usuario[10]}' if usuario[9] and usuario[10] else None
    })


@app.route("/eGimnasio/<int:idGim>", methods={'GET', 'POST'})
def eGimnasio(idGim):
    # tiempoSesion()
    if request.method == 'POST':
        query = ""
        gim = conectarOne(
            "select g.nombre, g.direccion, "
            "g.ubicacion, g.instagram, g.face, g.whats, g.logo "
            "from gimnasio g where g.id=" + str(idGim)
        )
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
            os.remove("static/" + gim[6])
        if query:
            upTabla("gimnasio", query[:-1],"id=" + str(idGim))
        delTabla("enseñaen","idgim=" + str(idGim))
        instru = request.form.getlist("instru")
        query = ""
        for dato in instru:
            dato = dato.split(",")
            query += "(u.tdoc=" + dato[0] + \
                " and u.documento='" + dato[1] + "') or "
            if not conectarOne(
                "select 1 from enseñaen ee "
                "where ee.tdoc=" + dato[0] + " and ee.doc='" + dato[1]
                + "' and ee.idgim=" + str(idGim)
                ):
                insTabla(
                    "enseñaen", "tdoc,doc,idgim",
                    dato[0] + ",'" + dato[1] + "'," + str(idGim)
                )
        aludesa = conectarAll(
            "SELECT a.tdoc, a.documento from alumno a "
            "where not exists(select 1 from usuario u where (" + query[:-4]
            + ") and u.tdoc=a.tdocinstru and u.documento=a.docinstru) and a.idgim=" +
            str(idGim)
        )
        for tdocAlu, docAlu in aludesa:
            upTabla(
                "alumno", "tdocinstru=null, docinstru=null, idgim=null",
                "tdoc=" + str(tdocAlu) + " and documento='" + docAlu + "'"
            )
            insTabla("aludesa", "tdocalu,docalu,fecha", str(
                tdocAlu) + ",'" + docAlu + "','" + str(datetime.today()) + "'")
        delTabla("horario", "idgim=" + str(idGim))
        for edadIni, edadFin, horaIni, horaFin, usu, dia in zip(
            request.form.getlist("edadIni"), request.form.getlist("edadFin"),
            request.form.getlist("horaIni"), request.form.getlist("horaFin"),
            request.form.getlist("Hora"), request.form.getlist("diaClase")
        ):
            if int(edadIni) < int(edadFin) and horaIni < horaFin and not conectarOne(
                "select 1 from horario h "
                "where h.tdoc=" + usu[0] + " and h.doc='" + usu[1] +
                "' and h.idgim=" + str(idGim) + " and h.edadini=" + edadIni +
                " and h.dia=" + dia
            ):
                usu = usu.split(",")
                insTabla(
                    "horario", "tdoc,doc,idgim,edadini,edadfin,horaini,horafin,dia",
                    usu[0] + ",'" + usu[1] + "'," + str(idGim) + "," + edadIni +
                    "," + edadFin + ",'" + horaIni + "','" + horaFin + "'," + dia
                )
        return redirect("/vGimnasio")
    return render_template("/Editar/EditarGimnasio.html", idGim=idGim)


@app.route("/cargarGimnasio/<int:idGim>")
def cargarGimnasio(idGim):
    # tiempoSesion()
    usuario = conectarAll(
        "select u.tdoc, u.documento "
        "from usuario u, enseñaen en, categoria c "
        "where en.idgim=" + str(idGim) +
        " and en.tdoc=u.tdoc and en.doc=u.documento and u.categoria=c.id"
    )
    condiEx = ""
    if session['cargo'] == 2:
        condiEx += " and exists(select 1 from cabeza ca where ca.tdoccabeza="
        condiEx += str(session['tdoc'])
        condiEx += " and ca.doccabeza='" + session['doc']
        condiEx += "' and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    usuGen = list(conectarAll(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
        " from usuario u, categoria c"
        " where u.cargo <> 1 and u.categoria=c.id" + condiEx
    ))
    if session['cargo'] != 1:
        resu = conectarOne(
            "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
            " from usuario u, categoria c"
            " where u.tdoc=" + str(session['tdoc']) + " and u.documento='"
            + session['doc'] + "' and u.categoria=c.id"
        )
        usuGen.insert(0, resu)
    gim = conectarOne(
        "select g.nombre, g.direccion, "
        "g.ubicacion, g.instagram, g.face, g.whats "
        "from gimnasio g where g.id="
        + str(idGim)
    )
    hora = conectarAll(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo, "
        "h.edadini, h.edadfin, h.horaini, h.horafin, h.dia "
        "from usuario u, horario h, categoria c "
        "where idgim=" + str(idGim) +
        " and h.tdoc=u.tdoc and h.doc=u.documento and u.categoria=c.id "
        "order by u.apellido, u.nombre"
    )
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
    # tiempoSesion()
    aGimUsuHora = conectarAll(
        "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo "
        "from usuario u, enseñaen ee, categoria c "
        "where ee.idgim=" + str(idGim) +
        " and ee.tdoc=u.tdoc and ee.doc=u.documento and u.categoria=c.id"
    )
    dicHora = {'value': [], 'text': [], 'lim': 0}
    for tdoc, doc, ape, nom, cate in aGimUsuHora:
        dicHora['value'].append(f'{tdoc},{doc}')
        dicHora['text'].append(f'{ape} {nom} {cate}')
        dicHora['lim'] += 1
    return jsonify(dicHora)


@app.route("/eEvento/<int:idEve>", methods={'GET', 'POST'})
def eEvento(idEve):
    # tiempoSesion()
    tipo = conectarAll('select * from tipoevento')
    if request.method == 'POST':
        evento = conectarOne(
            "select e.fecha, e.tipo, e.descripcion "
            "from evento e "
            "where e.id=" + str(idEve)
        )
        query = ""
        if evento[0] != (fecha := request.form.get("Fecha")):
            query += " fecha='" + fecha + "',"
        if evento[1] != (tipo := request.form.get("Tipo")):
            query += " Tipo='" + tipo + "',"
        if evento[2] != (desc := request.form.get("Descripcion")):
            query += " Descripcion='" + desc + "',"
        if query:
            upTabla("evento", query[:-1], "id=" + str(idEve))
        return redirect("/MainBase")
    return render_template("/Editar/EditarEvento.html", tipoEvento=tipo, idEve=idEve)


@app.route("/cargarEvento/<int:idEve>")
def cargarEvento(idEve):
    # tiempoSesion()
    evento = conectarOne(
        "select e.fecha, e.tipo, e.descripcion "
        "from evento e "
        "where e.id=" + str(idEve)
    )
    return jsonify({
        'fecha': f'{evento[0].strftime("%Y")}-{evento[0].strftime("%m")}-{evento[0].strftime("%d")}', 'tipo': evento[1], 'desc': evento[2]
    })


@app.route("/eAlumno/<int:tdoc>/<string:doc>", methods={'GET', 'POST'})
def eAlumno(tdoc, doc):
    # tiempoSesion()
    categoria = conectarAll("select * from categoria")
    tDoc = conectarAll("select * from tipodocumento")
    condiEx = ""
    if session['cargo'] == 2:
        condiEx = " and exists(select 1 from cabeza ca where ca.doccabeza='"
        condiEx += session['doc']
        condiEx += "' and ca.tdoccabeza=" + str(session['tdoc'])
        condiEx += " and ca.tdoc=u.tdoc and ca.documento=u.documento)"
    if session['cargo'] == 3:
        condiEx = " and exists(select 1 from instructor ia where ia.docinstru='"
        condiEx += session['doc']
        condiEx += "' and ia.tdocinstru=" + str(session['tdoc'])
        condiEx += " and ia.tdoc=u.tdoc and ia.documento=u.documento)"
    query = "select u.tdoc, u.documento, u.apellido, u.nombre, c.tipo"
    query += " from usuario u, categoria c, enseñaen ee"
    query += " where ee.tdoc = u.tdoc and ee.doc= u.documento and c.id = u.categoria" + condiEx
    usuario = list(conectarAll(query + " group by u.tdoc,u.documento,u.apellido,u.nombre,c.tipo "))
    usuario.insert(0, ('', '', '', '', ''))
    if request.method == 'POST':
        alumno = conectarOne(
            "select a.nombre, a.apellido, a.tdoc, a.documento, a.categoria, a.nacionalidad"
            ", a.finscripcion, a.observaciones, a.email, a.localidad, a.fnac, a.libreta, a.foto"
            ", a.tdocinstru, a.docinstru, a.idgim "
            "from alumno a where a.tdoc=" + str(tdoc)
            + " and a.documento='" + doc + "'"
        )
        query = ""
        if alumno[0] != (nom := request.form.get("Nombre")):
            query += " nombre='" + nom + "',"
        if alumno[1] != (ape := request.form.get("Apellido")):
            query += " apellido='" + ape + "',"
        if alumno[2] != (tDocAlu := int(request.form.get("TipoDocumento"))):
            query += " tdoc=" + str(tDocAlu) + ","
        if alumno[3] != (docAlu := request.form.get("Documento")):
            query += " documento='" + docAlu + "',"
        if alumno[4] != (cate := int(request.form.get("Categoria"))):
            resu = conectarOne(
                "select count(*) + 1 from participa pe, evento e "
                "where pe.tdoc=" + str(alumno[2]) + " and pe.doc='" + alumno[3]
                + "' and e.tipo=1 and pe.idevento=e.id"
            )[0]
            if cate >= resu:
                reParti(
                    iter(conectarAll(
                        "select e.id, e.tipo "
                        "from evento e, participa pe "
                        "where pe.tdoc=" + str(alumno[2]) + " and pe.doc='"
                        + alumno[3] + "' and pe.idevento=e.id "
                        "order by e.fecha desc"
                    )), str(alumno[2]), alumno[3], cate
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
                usu = conectarOne(
                    "select u.apellido, u.nombre "
                    "from usuario u where u.tdoc=" + str(instru[0])
                    + " and u.documento='" + instru[1] + "'"
                )
                if alumno[13] != instru[0]:
                    query += " tdocinstru=" + str(instru[0]) + ","
                if alumno[14] != instru[1]:
                    query += " docinstru='" + instru[1] + "',"
            else:
                usu = conectarOne(
                    "select u.apellido, u.nombre "
                    "from usuario u where u.tdoc=" + str(alumno[13])
                    + " and u.documento='" + alumno[14] + "'"
                )
            if idGim:
                if alumno[15] != idGim:
                    query += " idgim=" + idGim + ","
                nomGim = conectarOne(
                    "select g.nombre "
                    "from gimnasio g where g.id=" + str(idGim)
                )[0]
            else:
                nomGim = conectarOne(
                    "select g.nombre "
                    "from gimnasio g where g.id=" + str(alumno[15])
                )[0]
            nombre = 'sin_foto.png'
            if request.files["Foto"]:
                if alumno[12] != "Imagenes/sin_foto.png":
                    os.remove("static/" + alumno[12])
                nombre = photos.save(
                    request.files["Foto"], f'{nomGim.replace(" ","")}/{usu[0]}{usu[1]}'
                )
                query += " foto='Imagenes" + \
                    url_for('obtener_nombre', filename=nombre)[8:] + "',"
        if query:
            upTabla("alumno", query[:-1], "tdoc=" +
                    str(tdoc) + " and documento='" + doc + "'")
        tele = request.form.getlist("Telefono")
        conta = request.form.getlist("Contacto")
        delTabla("telefono", "tdoc=" + str(tdoc) +
                " and documento='" + doc + "'")
        for tel, cont in zip(tele, conta):
            if tel and cont and not conectarOne(
                    "select 1 from telefono where tdoc=" + str(tdoc) + " and documento='" + doc
                    + "' and telefono='" + tel + "'"
                ):
                insTabla(
                    "telefono", "tdoc,documento,telefono,contacto",
                    "" + str(tdoc) + ",'" + doc + "','" +
                    tel + "','" + cont + "'"
                )
        return redirect("/vAlumno")
    return render_template(
        "/Editar/EditarAlumno.html", categoria=categoria, tDoc=tDoc,
        usuario=usuario, doc=doc, tdoc=tdoc
    )


@app.route("/cargarAlumno/<int:tdoc>/<string:doc>")
def cargarAlumno(tdoc, doc):
    # tiempoSesion()
    alumno = conectarOne(
        "select a.nombre, a.apellido, a.tdoc, a.documento, a.categoria, a.nacionalidad"
        ", a.finscripcion, a.observaciones, a.email, a.localidad"
        ", a.fnac, a.tdocinstru, a.docinstru, a.idgim "
        "from alumno a where a.tdoc=" + str(tdoc)
        + " and a.documento='" + doc + "'"
    )
    telefono = conectarAll(
        "select t.telefono, t.contacto "
        "from telefono t "
        "where t.tdoc=" + str(tdoc) + " and t.documento='" + doc + "'"
    )
    dicAlu = {
        'nom': alumno[0], 'ape': alumno[1], 'tdoc': alumno[2], 'doc': alumno[3],
        'cate': alumno[4], 'nacio': alumno[5],
        'fIns': f'{alumno[6].strftime("%Y")}-{alumno[6].strftime("%m")}-{alumno[6].strftime("%d")}', 'ibs': alumno[7],
        'mail': alumno[8], 'loc': alumno[9], 'fnac': f'{alumno[10].strftime("%Y")}-{alumno[10].strftime("%m")}-{alumno[10].strftime("%d")}',
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
    # tiempoSesion()
    delTabla("cabeza", "tdoc=" + str(tdoc) + " and documento='" + doc + "'")
    delTabla("instructor", "tdoc=" + str(tdoc) +
             " and documento='" + doc + "'")
    delTabla("notifica", "tdoc=" + str(tdoc) + " and documento='" + doc + "'")
    notis = conectarAll("select n.id, 1 from notificacion n")
    for idNoti, _ in notis:
        resu = conectarOne(
            "select 1 from notifica n where n.idnoti='" + str(idNoti) + "'"
        )
        if not resu:
            delTabla("notificacion", "id='" + str(idNoti) + "'")
    delTabla("enseñaen", "tdoc=" + str(tdoc) + " and doc='" + doc + "'")
    delTabla("horario", "tdoc=" + str(tdoc) + " and doc='" + doc + "'")
    upTabla(
        "alumno", "tdocinstru=NULL, docinstru=NULL, idgim=NULL",
        "tdocinstru=" + str(tdoc) + " and docinstru='" + doc + "'"
    )
    delTabla("usuario", "tdoc=" + str(tdoc) + " and documento='" + doc + "'")
    return redirect("/vUsuario")


@app.route("/desaGim/<int:idGim>")
def desaGim(idGim):
    # tiempoSesion()
    alu = []
    if session['cargo'] != 3:
        delTabla("enseñaen", "idgim=" + str(idGim))
        delTabla("horario", "idgim=" + str(idGim))
        alu = conectarAll(
            "select a.tdoc, a.documento from alumno a "
            "where a.idgim=" + str(idGim)
        )
        upTabla(
             "alumno", "idgim=null, tdocinstru=null, docinstru= null",
            "idgim=" + str(idGim)
        )
    else:
        delTabla(
            "enseñaen", "idgim=" + str(idGim) + " and tdoc="
            + str(session['tdoc']) + " and doc='" + session['doc'] + "'"
        )
        delTabla(
            "horario", "idgim=" + str(idGim) + " and tdoc="
            + str(session['tdoc']) + " and doc='" + session['doc'] + "'"
        )
        alu = conectarAll(
            "select a.tdoc, t.documento from alumno a "
            "where a.idgim=" + str(idGim) +
            " and a.tdocinstru=" + str(session['tdoc'])
            + " and a.docinstru='" + session['doc'] + "'"
        )
        upTabla(
            "alumno", "idgim=null, tdocinstru=null, docinstru= null",
            "idgim=" + str(idGim) + " and tdocinstru=" + str(session['tdoc'])
            + " and docinstru='" + session['doc'] + "'"
        )
    if not os.path.isdir(pathlib.Path("BaseConReact/static/Imagenes/Deshabilitados").absolute()):
        os.mkdir(pathlib.Path("BaseConReact/static/Imagenes/Deshabilitados").absolute())
    for tdoc, doc in alu:
        foto = conectarOne(
            "select a.foto from alumno a where a.tdoc=" + tdoc + " and a.documento='" + doc + "'"
        )[0]
        if foto != "Imagenes/sin_foto.png":
            shutil.move(
                pathlib.Path("BaseConReact/static/" + foto).absolute(),
                pathlib.Path("BaseConReact/static/Imagenes/Deshabilitados/" + foto[foto.rfind("/"):]).absolute()
            )
            upTabla(
                "alumno", "foto='Imagenes/Deshabilitados" + foto[foto.rfind("/"):] + "'",
                "tdoc=" + tdoc + " and documento=" + doc + ""
            )
        insTabla("aludesa", "tdocalu,docalu,fecha",
                str(tdoc) + ",'" + doc + "','" + str(datetime.today()) + "'")
    return redirect("/vGimnasio")


@app.route("/elimGimnasio/<int:idGim>")
def elimGimnasio(idGim):
    # tiempoSesion()
    logo = conectarOne(
        "select g.logo from gimnasio g where g.id=" + str(idGim)
    )[0]
    shutil.rmtree(os.path.dirname(pathlib.Path("BaseConReact/static/" + logo).absolute()))
    delTabla("gimnasio", "id=" + str(idGim))
    return redirect("/vGimnasio")


@app.route("/aAluEven/<int:tipo>/<string:cadAlu>")
def aAluEven(tipo, cadAlu):
    # tiempoSesion()
    cadAlu = cadAlu.split(".")
    idEve = conectarOne(
        "select e.id "
        "from evento e, ("
        "select min(e.fecha) as minFecha "
        "from evento e where e.tipo=" +
        str(tipo) + " and e.fecha >= '" + str(datetime.today()) + "'"
        ") as ef "
        "where e.fecha = ef.minFecha and e.tipo=" + str(tipo)
    )[0]
    for elem in cadAlu:
        elem = elem.split(",")
        if not conectarOne(
            "select 1 from participa p "
            "where p.tdoc=" + elem[0] + " and p.doc='" +
            elem[1] + "' and p.idevento=" + str(idEve)
        ):
            cate = conectarOne(
                "select a.categoria from alumno a where a.tdoc="
                + elem[0] + " and a.documento='" + elem[1] + "'"
            )[0]
            if tipo == 1:
                cate = cate + 1
                upTabla(
                    "alumno", "categoria=" + str(cate),
                    "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
                )
            insTabla(
                "participa", "tdoc,doc,idevento,categoria",
                elem[0] + ",'" + elem[1] + "'," + str(idEve) + "," + str(cate)
            )
    return redirect("/vAlumno")


@app.route("/desaAlu/<string:cadAlu>")
def desaAlu(cadAlu):
    # tiempoSesion()
    cadAlu = cadAlu.split(".")
    if not os.path.isdir(pathlib.Path("BaseConReact/static/Imagenes/Deshabilitados").absolute()):
        os.mkdir(pathlib.Path("BaseConReact/static/Imagenes/Deshabilitados").absolute())
    for elem in cadAlu:
        elem = elem.split(",")
        upTabla(
            "alumno", "tdocinstru=null, docinstru=null, idgim=null",
            "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
        )
        insTabla("aludesa", "tdocalu,docalu,fecha",
                elem[0] + ",'" + elem[1] + "','" + str(datetime.today()) + "'")
        foto = conectarOne(
            "select a.foto from alumno a where a.tdoc=" + elem[0] + " and a.documento='" + elem[1] + "'"
        )[0]
        if foto != "Imagenes/sin_foto.png":
            shutil.move(
                pathlib.Path("BaseConReact/static/" + foto).absolute(),
                pathlib.Path("BaseConReact/static/Imagenes/Deshabilitados/" + foto[foto.rfind("/"):]).absolute()
            )
            upTabla(
                "alumno", "foto='Imagenes/Deshabilitados" + foto[foto.rfind("/"):] + "'",
                "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
            )
    return redirect("/vAlumno")


@app.route("/habiAlu/<string:tdocUsu>/<string:docUsu>/<string:idGim>/<string:cadAlu>")
def habiAlu(tdocUsu, docUsu, idGim, cadAlu):
    # tiempoSesion()
    cadAlu = cadAlu.split(".")
    if conectarOne(
        "select 1 from enseñaen en where en.tdoc="
        + tdocUsu + " and en.doc='" + docUsu + "' and en.idgim=" + idGim
    ):
        usu = conectarOne(
            "select u.apellido, u.nombre from usuario u where u.tdoc="
            +  tdocUsu + " and u.documento='" + docUsu + "'"
        )
        gim = conectarOne(
            "select g.nombre from gimnasio g where g.id=" + idGim
        )[0]
        for elem in cadAlu:
            elem = elem.split(",")
            foto = conectarOne(
                "select a.foto from alumno a where a.tdoc=" + elem[0] + " and a.documento='" + elem[1] + "'"
            )[0]
            if foto != "Imagenes/sin_foto.png":
                if not os.path.isdir(f'static/Imagenes/{gim.replace(" ","")}/{usu[0]}{usu[1]}'):
                    os.makedirs(
                        f'static/Imagenes/{gim.replace(" ","")}/{usu[0]}{usu[1]}'
                    )
                shutil.move(
                    pathlib.Path("BaseConReact/static/" + foto).absolute(),
                    pathlib.Path(f'BaseConReact/static/Imagenes/{gim.replace(" ","")}/{usu[0]}{usu[1]}/{foto[foto.rfind("/"):]}').absolute()
                )
                upTabla(
                    "alumno",
                    "foto='Imagenes/" + gim.replace(" ","") + "/"
                    + usu[0] + usu[1] + "/" + foto[foto.rfind("/"):] + "'",
                    "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
                )
            upTabla(
                "alumno", "tdocinstru=" + tdocUsu + ", docinstru='" + docUsu + "', idgim=" + idGim,
                "tdoc=" + elem[0] + " and documento='" + elem[1] + "'"
            )
            delTabla("aludesa", "tdocalu=" +
                    elem[0] + " and docalu='" + elem[1] + "'")
    return redirect("/vAlumno")


@app.route("/aluMatri/<int:tipo>/<string:cadAlu>")
def aluMatri(tipo, cadAlu):
    # tiempoSesion()
    cadAlu = cadAlu.split(".")
    tipo = str(tipo)
    for elem in cadAlu:
        elem = elem.split(",")
        resu = conectarOne(
            "select 1 from matricula m "
            "where m.tdoc=" + elem[0] + " and m.doc='" + elem[1] + "' and "
            "m.tipo=" + tipo + " and YEAR(m.fecha) = " + str(datetime.today().year) + ""
        )
        if not resu:
            insTabla(
                "matricula", "tdoc,doc,fecha,tipo",
                elem[0] + ",'" + elem[1] +
                "','" + str(datetime.now().date())
                + "'," + tipo
            )
    return redirect("/vAlumno")

@app.route("/aluLibre/<string:cadAlu>")
def aluLibre(cadAlu):
    cadAlu = cadAlu.split(".")
    for elem in cadAlu:
        elem = elem.split(",")
        upTabla("alumno", "libreta=1", "tdoc=" + elem[0] + " and documento='" + elem[1] + "'")
    return redirect("/vAlumno")


@app.route("/vFilEveAlu/<string:tipo>/<string:tdoc>/<string:doc>")
def vFilEveAlu(tipo, tdoc, doc):
    # tiempoSesion()
    aluEve = conectarAll(
        "select e.fecha, te.tipo, c.tipo "
        "from evento e, participa p, categoria c, tipoevento te "
        "where p.tdoc=" + tdoc + " and p.doc='" + doc + "' and e.tipo=" + tipo
        + " and p.idevento=e.id and p.categoria=c.id and e.tipo=te.id "
        "order by e.fecha"
    )
    dicEve = {'fecha': [], 'tipo': [], 'cate': [], 'lim': 0}
    for fecha, tipo, cate in aluEve:
        dicEve['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.day}')
        dicEve['tipo'].append(tipo)
        dicEve['cate'].append(cate)
        dicEve['lim'] += 1
    return jsonify(dicEve)


@app.route("/aPrevEve/<string:tdoc>/<string:doc>")
def aPrevEve(tdoc, doc):
    # tiempoSesion()
    evento = conectarAll(
        "select e.id, e.fecha, te.tipo "
        "from evento e, tipoevento te "
        "where e.tipo=te.id and e.fecha <= '" + str(datetime.now()) + "' and not exists("
        "select 1 from participa p "
        "where p.tdoc=" + tdoc + " and p.doc=" + doc + " and p.idevento=e.id "
        ") order by e.fecha"
    )
    dicEve = {'id': [], 'fecha': [], 'lim': 0, 'tipo': []}
    for id, fecha, tipo in evento:
        dicEve['id'].append(id)
        dicEve['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.year}')
        dicEve['tipo'].append(tipo)
        dicEve['lim'] += 1
    return jsonify(dicEve)


@app.route("/agregaEvento/<string:tdoc>/<string:doc>/<string:cadEve>")
def agregaEvento(tdoc, doc, cadEve):
    # tiempoSesion()
    eveReg = conectarAll(
        "select e.id, e.tipo, e.fecha "
        "from evento e "
        "where e.id in (" + cadEve + ") or exists ("
        "select 1 from participa p "
        "where p.tdoc=" + tdoc + " and p.doc='" + doc + "' and p.idevento=e.id"
        ") order by e.fecha desc"
    )
    cate = conectarOne(
        "select a.categoria + ("
        "select count(*) from evento e "
        "where e.id in(" + cadEve + ") and (e.tipo=1 or e.tipo=4)"
        ") "
        "from alumno a "
        "where a.tdoc=" + tdoc + " and a.documento='" + doc + "'"
    )[0]
    reParti(iter(eveReg), tdoc, doc, cate)
    return redirect("/vAlumno")


@app.route("/ePrevEven/<string:tdoc>/<string:doc>")
def ePrevEven(tdoc, doc):
    # tiempoSesion()
    even = conectarAll(
        "select e.id, e.fecha, te.tipo "
        "from evento e, tipoevento te, participa p "
        "where p.tdoc=" + tdoc + " and p.doc='" + doc + "'"
        " and e.tipo=te.id and p.idevento=e.id"
    )
    dicEve = {'id': [], 'fecha': [], 'lim': 0, 'tipo': []}
    for id, fecha, tipo in even:
        dicEve['id'].append(id)
        dicEve['fecha'].append(f'{fecha.day}/{fecha.month}/{fecha.year}')
        dicEve['tipo'].append(tipo)
        dicEve['lim'] += 1
    return jsonify(dicEve)


@app.route("/elimEvento/<string:tdoc>/<string:doc>/<string:cadEve>")
def elimEvento(tdoc, doc, cadEve):
    # tiempoSesion()
    eveReg = conectarAll(
        "select e.id, e.tipo "
        "from evento e "
        "where e.id not in (" + cadEve + ") and exists ("
        "select 1 from participa p "
        "where p.tdoc=" + tdoc + " and p.doc='" + doc + "' and p.idevento=e.id"
        ") order by e.fecha desc"
    )
    cate = conectarOne(
        "select a.categoria - ("
        "select count(*) from evento e "
        "where e.id in(" + cadEve + ") and (e.tipo=1 or e.tipo=4)"
        ") "
        "from alumno a "
        "where a.tdoc=" + tdoc + " and a.documento='" + doc + "'"
    )[0]
    reParti(iter(eveReg), tdoc, doc, cate)
    return redirect("/vAlumno")


def reParti(itera, tdoc, doc, cate):
    eveIdTipo = next(itera, None)
    delTabla("participa", "tdoc=" + tdoc + " and doc='" + doc + "'")
    upTabla(
        "alumno", "categoria=" + str(cate),
        "tdoc=" + tdoc + " and documento='" + doc + "'"
    )
    while eveIdTipo:
        while eveIdTipo and eveIdTipo[1] == 1:
            eveIdTipo = insparti(tdoc, doc, str(eveIdTipo[0]), cate, itera)
            cate -= 1
        while eveIdTipo and eveIdTipo[1] != 1:
            eveIdTipo = insparti(tdoc, doc, str(eveIdTipo[0]), cate, itera)


def insparti(tdoc, doc, idEve, cate, reco):
    insTabla(
        "participa", "tdoc,doc,idevento,categoria",
        tdoc + ",'" + doc + "'," + idEve + "," + str(cate)
    )
    return next(reco, None)


@app.route("/eImagen/<string:idImagen>/<string:direc>")
def eImagen(idImagen, direc):
    # tiempoSesion()
    direc = direc.replace("ƒ", "/")
    delTabla("imagen", "idevento=" + idImagen +
             " and direccion='" + direc + "'")
    os.remove("static/" + direc)
    return redirect("/vImagen")


@app.route("/eNotificacion/<string:idNoti>")
def eNotificacion(idNoti):
    # tiempoSesion()
    delTabla(
        "notifica", "idnoti=" + idNoti + " and tdoc="
        + str(session['tdoc']) + " and documento='" + session['doc'] + "'"
    )
    resu = conectarOne(
        "select 1 from notifica n "
        "where n.idnoti=" + idNoti
    )
    if not resu:
        delTabla("notificacion", "id=" + idNoti)
    return redirect("/MainBase")


@app.route("/elimAlu/<string:cadAlu>")
def elimAlu(cadAlu):
    # tiempoSesion()
    cadAlu = cadAlu.split(".")
    for dato in cadAlu:
        dato = dato.split(",")
        foto = conectarOne(
            "select a.foto from alumno a "
            "where a.tdoc=" + dato[0] + " and a.documento='" + dato[1] + "'"
        )[0]
        if foto != "Imagenes/sin_foto.png":
            os.remove(pathlib.Path("BaseConReact/static/" + foto).absolute())
        delTabla("aludesa", "tdocalu=" +
                 dato[0] + " and docalu='" + dato[1] + "'")
        delTabla("participa", "tdoc=" + dato[0] + " and doc='" + dato[1] + "'")
        delTabla("matricula", "tdoc=" + dato[0] + " and doc='" + dato[1] + "'")
        delTabla("telefono", "tdoc=" +
                 dato[0] + " and documento='" + dato[1] + "'")
        delTabla("alumno", "tdoc=" + dato[0] +
                 " and documento='" + dato[1] + "'")
    return redirect("/vAlumno")

# Funciones tipicas


@app.route("/uploads/<filename>")
def obtener_nombre(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route("/cambioGim/<string:tDocUsu>/<string:docUsu>")
def cambioGim(tDocUsu, docUsu):
    gim = conectarAll(
        "select g.id, g.nombre, g.direccion "
        "from gimnasio g, enseñaen ee "
        "where g.id = ee.idgim and ee.tdoc=" + tDocUsu + " and ee.doc=" + docUsu
    )
    dicGim = {'idGim': [], 'nomGim': [], 'direGim': [], 'cant': len(gim)}
    for idgim, nomgim, direcgim in gim:
        dicGim['idGim'].append(idgim)
        dicGim['nomGim'].append(nomgim)
        dicGim['direGim'].append(direcgim)
    return jsonify(dicGim)


def upTabla(tabla, cambio, condi):
    conn = pymysql.connect(host=HOST, user=USUARIO, passwd=CONTRA, db=BASE)
    con = conn.cursor()
    con.execute(
        "update " + tabla + " set " + cambio + " where " + condi
    )
    conn.commit()
    conn.close()

def delTabla(tabla, condi):
    conn = pymysql.connect(host=HOST, user=USUARIO, passwd=CONTRA, db=BASE)
    con = conn.cursor()
    con.execute(
        "delete from " + tabla + " where " + condi
    )
    conn.commit()
    conn.close()

def insTabla(tabla, valTabla, valInser):
    conn = pymysql.connect(host=HOST, user=USUARIO, passwd=CONTRA, db=BASE)
    con = conn.cursor()
    con.execute(
        "insert into " + tabla + " (" + valTabla + ") values(" + valInser + ")"
    )
    conn.commit()
    conn.close()