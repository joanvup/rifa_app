from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from datetime import datetime
import os
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = 'supersecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rifas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Filtro personalizado para formatear números
def format_currency(value):
    try:
        return "{:,.0f}".format(value)
    except:
        return str(value)

# Añadir filtro al entorno Jinja
app.jinja_env.filters['currency'] = format_currency

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    precio_boleta = db.Column(db.Float, default=100.0)
    porcentaje_primeras = db.Column(db.Float, default=25.0)
    porcentaje_medio = db.Column(db.Float, default=10.0)
    porcentaje_ultimas = db.Column(db.Float, default=40.0)

class Talonario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sorteos = db.relationship('Sorteo', backref='talonario', lazy=True)

class Numero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    talonario_id = db.Column(db.Integer, db.ForeignKey('talonario.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default='disponible')
    nombre_persona = db.Column(db.String(100))

class Sorteo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    talonario_id = db.Column(db.Integer, db.ForeignKey('talonario.id'), nullable=False)
    numero_ganador = db.Column(db.String(4), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# Crear tablas y configuración inicial
with app.app_context():
    db.create_all()
    if not Configuracion.query.first():
        config = Configuracion()
        db.session.add(config)
        db.session.commit()

@app.route('/')
def index():
    talonarios = db.session.scalars(select(Talonario)).all()
    return render_template('index.html', talonarios=talonarios)

@app.route('/crear_talonario', methods=['POST'])
def crear_talonario():
    nuevo_talonario = Talonario(nombre=request.form['nombre'])
    db.session.add(nuevo_talonario)
    db.session.commit()
    
    for i in range(100):
        nuevo_numero = Numero(
            talonario_id=nuevo_talonario.id,
            numero=i,
            estado='disponible'
        )
        db.session.add(nuevo_numero)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/talonario/<int:talonario_id>')
def ver_talonario(talonario_id):
    talonario = db.session.get(Talonario, talonario_id)
    if not talonario:
        return "Talonario no encontrado", 404
        
    stmt = select(Numero).where(Numero.talonario_id == talonario_id).order_by(Numero.numero)
    numeros = db.session.scalars(stmt).all()
    
    config = Configuracion.query.first()
    
    total_esperado = 100 * config.precio_boleta
    numeros_pagados = sum(1 for n in numeros if n.estado == 'pagado')
    recaudado = numeros_pagados * config.precio_boleta
    por_recaudar = total_esperado - recaudado
    
    return render_template('talonario.html', 
                           talonario=talonario, 
                           numeros=numeros,
                           now=datetime.now(),
                           config=config,
                           total_esperado=total_esperado,
                           recaudado=recaudado,
                           por_recaudar=por_recaudar)

@app.route('/accion_numero/<int:numero_id>', methods=['POST'])
def accion_numero(numero_id):
    numero = db.session.get(Numero, numero_id)
    if not numero:
        return "Número no encontrado", 404
        
    accion = request.form.get('accion')
    
    if not accion:
        return "Acción no especificada", 400
    
    if accion == 'asignar':
        numero.estado = 'ocupado'
        numero.nombre_persona = request.form['nombre']
    elif accion == 'asignar_pagar':
        numero.estado = 'pagado'
        numero.nombre_persona = request.form['nombre']
    elif accion == 'pagar':
        if numero.estado == 'ocupado':
            numero.estado = 'pagado'
    elif accion == 'desasignar':
        numero.estado = 'disponible'
        numero.nombre_persona = None
    
    db.session.commit()
    return redirect(url_for('ver_talonario', talonario_id=numero.talonario_id))

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    config = Configuracion.query.first()
    if request.method == 'POST':
        config.precio_boleta = float(request.form['precio_boleta'])
        config.porcentaje_primeras = float(request.form['porcentaje_primeras'])
        config.porcentaje_medio = float(request.form['porcentaje_medio'])
        config.porcentaje_ultimas = float(request.form['porcentaje_ultimas'])
        db.session.commit()
        flash('Configuración actualizada correctamente', 'success')
        return redirect(url_for('configuracion'))
    
    return render_template('configuracion.html', config=config)

@app.route('/talonario/<int:talonario_id>/sorteo', methods=['GET', 'POST'])
def sorteo(talonario_id):
    talonario = db.session.get(Talonario, talonario_id)
    if not talonario:
        return "Talonario no encontrado", 404
        
    config = Configuracion.query.first()
    
    if request.method == 'POST':
        numero_ganador = request.form['numero_ganador']
        if len(numero_ganador) != 4 or not numero_ganador.isdigit():
            flash('Número ganador debe ser de 4 dígitos', 'danger')
            return redirect(url_for('sorteo', talonario_id=talonario_id))
        
        nuevo_sorteo = Sorteo(talonario_id=talonario_id, numero_ganador=numero_ganador)
        db.session.add(nuevo_sorteo)
        db.session.commit()
        
        return redirect(url_for('resultado_sorteo', sorteo_id=nuevo_sorteo.id))
    
    return render_template('sorteo_form.html', talonario=talonario)

@app.route('/sorteo/<int:sorteo_id>')
def resultado_sorteo(sorteo_id):
    sorteo = db.session.get(Sorteo, sorteo_id)
    if not sorteo:
        return "Sorteo no encontrado", 404
        
    talonario = sorteo.talonario
    config = Configuracion.query.first()
    
    total_esperado = 100 * config.precio_boleta
    premio_primeras = total_esperado * config.porcentaje_primeras / 100
    premio_medio = total_esperado * config.porcentaje_medio / 100
    premio_ultimas = total_esperado * config.porcentaje_ultimas / 100
    
    primeras = sorteo.numero_ganador[:2]
    medio = sorteo.numero_ganador[1:3]
    ultimas = sorteo.numero_ganador[2:]
    
    ganadores_primeras = Numero.query.filter(
        Numero.talonario_id == talonario.id,
        func.substr(func.format('%02d', Numero.numero), 1, 2) == primeras,
        Numero.estado == 'pagado'
    ).all()
    
    ganadores_medio = Numero.query.filter(
        Numero.talonario_id == talonario.id,
        func.substr(func.format('%02d', Numero.numero), 1, 2) == medio,
        Numero.estado == 'pagado'
    ).all()
    
    ganadores_ultimas = Numero.query.filter(
        Numero.talonario_id == talonario.id,
        func.substr(func.format('%02d', Numero.numero), 1, 2) == ultimas,
        Numero.estado == 'pagado'
    ).all()
    
    premios_persona = {}
    
    def agregar_premio(nombre, premio):
        if nombre in premios_persona:
            premios_persona[nombre] += premio
        else:
            premios_persona[nombre] = premio
    
    for g in ganadores_primeras:
        premio_individual = premio_primeras / len(ganadores_primeras) if ganadores_primeras else 0
        agregar_premio(g.nombre_persona, premio_individual)
    
    for g in ganadores_medio:
        premio_individual = premio_medio / len(ganadores_medio) if ganadores_medio else 0
        agregar_premio(g.nombre_persona, premio_individual)
    
    for g in ganadores_ultimas:
        premio_individual = premio_ultimas / len(ganadores_ultimas) if ganadores_ultimas else 0
        agregar_premio(g.nombre_persona, premio_individual)
    
    premios_persona = [{'nombre': k, 'premio': v} for k, v in premios_persona.items()]
    
    return render_template('resultado_sorteo.html',
                           sorteo=sorteo,
                           talonario=talonario,
                           primeras=primeras,
                           medio=medio,
                           ultimas=ultimas,
                           premio_primeras=premio_primeras,
                           premio_medio=premio_medio,
                           premio_ultimas=premio_ultimas,
                           ganadores_primeras=ganadores_primeras,
                           ganadores_medio=ganadores_medio,
                           ganadores_ultimas=ganadores_ultimas,
                           premios_persona=premios_persona,
                           config=config,
                           total_esperado=total_esperado)

if __name__ == '__main__':
    app.run(debug=True)