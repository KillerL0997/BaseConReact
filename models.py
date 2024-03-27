from database import db

class Cargo(db.Model):
    __tablename__='cargo'
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.String(20), nullable=True)

class Categoria(db.Model):
    __tablename__='categoria'
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.String(20), nullable=True)

class TipoDoc(db.Model):
    __tablename__='tdoc'
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.String(10), nullable=True)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    nombre = db.Column(db.String(200), nullable= True)
    apellido = db.Column(db.String(200), nullable= True)
    categoria = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    email = db.Column(db.String(100))
    contraseña = db.Column(db.String(200))
    cargo = db.Column(db.Integer, db.ForeignKey('cargo.id'))
    tipoDoc = db.Column(db.Integer, db.ForeignKey('tipodoc.id'), primary_key= True)
    documento = db.Column(db.String(10), primary_key = True)
    tipoDocCabeza = db.Column(db.Integer, db.ForeignKey('usuario.tipoDoc'))
    docCabeza = db.Column(db.String(10), db.ForeignKey('usuario.documento'))
    tipoDocInstructor = db.Column(db.Integer, db.ForeignKey('usuario.tipoDoc'))
    docInstructor = db.Column(db.String(10), db.ForeignKey('usuario.documento'))

class Notificacion(db.Model):
    __tablename__= 'notificacion'
    id = db.Column(db.Integer, primary_key= True)
    texto = db.Column(db.Text, nullable = True)

class notifica(db.Model):
    __tablename__= 'notifica'
    tDoc = db.Column(db.Integer, db.ForeignKey('usuario.tipoDoc'), primary_key= True)
    doc = db.Column(db.String(10), db.ForeignKey('usuario.documento'), primary_key= True)
    idNoti = db.Column(db.Integer, db.ForeignKey('notificacion.id'), primary_key= True)

class Gimnasio(db.Model):
    __tablename__= 'gimnasio'
    id = db.Column(db.Integer, primary_key= True)
    nombre = db.Column(db.String(100), nullable= True)
    direccion = db.Column(db.String(100), nullable= True)
    habilitado = db.Column(db.Boolean)
    ubicacion = db.Column(db.String(300))
    instagram = db.Column(db.String(300))
    whats = db.Column(db.String(300))
    face = db.Column(db.String(300))
    logo = db.Column(db.String(300))

class Enseña(db.Model):
    __tablename__= 'enseña'
    tDoc = db.Column(db.Integer, db.ForeignKey('usuario.tipoDoc'), primary_key= True)
    doc = db.Column(db.String(10), db.ForeignKey('usuario.documento'), primary_key= True)
    idGim = db.Column(db.Integer, db.ForeignKey('gimnasio.id'), primary_key= True)

class Horario(db.Model):
    __tablename__= 'horario'
    tDoc = db.Column(db.Integer, db.ForeignKey('usuario.tipoDoc'), primary_key= True)
    doc = db.Column(db.String(10), db.ForeignKey('usuario.documento'), primary_key= True)
    idGim = db.Column(db.Integer, db.ForeignKey('gimnasio.id'), primary_key= True)
    edadIni = db.Column(db.Integer)
    edadFin = db.Column(db.Integer)
    horaIni = db.Column(db.Integer)
    horaFin = db.Column(db.Integer)

class Alumno(db.Model):
    __tablename__= 'alumno'
    nombre = db.Column(db.String(100), nullable= True)
    apellido = db.Column(db.String(100), nullable= True)
    tipoDoc = db.Column(db.Integer, db.ForeignKey('tipodoc.id'), primary_key= True)
    documento = db.Column(db.String(10), primary_key= True)
    categoria = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    nacionalidad = db.Column(db.String(50), nullable= True)   
    fIncripcion = db.Column(db.Date, nullable= True)
    observaciones = db.Column(db.Text)
    email = db.Column(db.String(100))
    localidad = db.Column(db.String(100), nullable= True)
    fNac = db.Column(db.Date, nullable= True)
    habilitado = db.Column(db.Boolean)
    fEvento = db.Column(db.Date)
    libreta = db.Column(db.String(20))
    foto = db.Column(db.String(500))
    tDocInstru = db.Column(db.Integer, db.ForeignKey('usuario.tipoDoc'))
    docInstru = db.Column(db.String(10), db.ForeignKey('usuario.documento'))
    idGim = db.Column(db.Integer, db.ForeignKey('gimnasio.id'))

class Telefono(db.Model):
    __tablename__= 'telefono'
    telefono = db.Column(db.String(20), primary_key= True)
    contacto = db.Column(db.String(50), primary_key= True)

class Llama(db.Model):
    telefono = db.Column(db.String(20), db.ForeignKey('telefono.telefono'), primary_key= True)
    contacto = db.Column(db.String(50), db.ForeignKey('telefono.contacto'), primary_key= True)
    tipoDoc = db.Column(db.Integer, db.ForeignKey('alumno.tipoDoc'), primary_key= True)
    documento = db.Column(db.String(10), db.ForeignKey('alumno.documento'), primary_key= True)

class Matricula(db.Model):
    __tablename__= 'matricula'
    tDoc = db.Column(db.Integer, db.ForeignKey('alumno.tipoDoc'), primary_key= True)
    doc = db.Column(db.String(10), db.ForeignKey('alumno.documento'), primary_key= True)
    fecha = db.Column(db.Date)
    idTipo = db.Column(db.Integer, db.ForeignKey('tipomatri.id'), primary_key= True)

class TipoMatri(db.Model):
    __tablename__= 'tipomatri'
    id = db.Column(db.Integer, primary_key= True)
    tipo = db.Column(db.String(10))

class Evento(db.Model):
    __tablename__= 'evento'
    id = db.Column(db.Integer, primary_key= True)
    tipoEvento = db.Column(db.Integer, db.ForeignKey('tipoevento.id'), primary_key= True)
    fecha = db.Column(db.Date, nullable= True)
    descripcion = db.Column(db.String(500), nullable= True)

class TipoEvento(db.Model):
    __tablename__= 'tipoevento'
    id = db.Column(db.Integer, primary_key= True)
    tipo = db.Column(db.String(10))

class Participa(db.Model):
    __tablename__= 'participa'
    tDoc = db.Column(db.Integer, db.ForeignKey('alumno.tipoDoc'), primary_key= True)
    doc = db.Column(db.String(10), db.ForeignKey('alumno.documento'), primary_key= True)
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), primary_key= True)

class Imagen(db.Model):
    __tablename__= 'imagen'
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), primary_key= True)
    direccion = db.Column(db.String(500), primary_key= True)