import flet as ft
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session as SQLASession
from datetime import datetime
import os

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'rifas.db')}"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Configuracion(Base):
    __tablename__ = 'configuracion'
    id = Column(Integer, primary_key=True)
    precio_boleta = Column(Float, default=100.0)
    porcentaje_primeras = Column(Float, default=25.0)
    porcentaje_medio = Column(Float, default=10.0)
    porcentaje_ultimas = Column(Float, default=40.0)

class Talonario(Base):
    __tablename__ = 'talonario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)

class Numero(Base):
    __tablename__ = 'numero'
    id = Column(Integer, primary_key=True)
    talonario_id = Column(Integer, ForeignKey('talonario.id'), nullable=False)
    numero = Column(Integer, nullable=False)
    estado = Column(String(20), default='disponible')
    nombre_persona = Column(String(100))

class Sorteo(Base):
    __tablename__ = 'sorteo'
    id = Column(Integer, primary_key=True)
    talonario_id = Column(Integer, ForeignKey('talonario.id'), nullable=False)
    numero_ganador = Column(String(4), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

# Crear tablas si no existen
Base.metadata.create_all(engine)

# Filtro para formatear moneda
def format_currency(value):
    return "{:,.0f}".format(value)

def main(page: ft.Page):
    page.title = "Sistema de Rifas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 10
    
    # Colores para los estados
    COLORES = {
        'disponible': ft.Colors.GREEN_100,
        'ocupado': ft.Colors.AMBER_100,
        'pagado': ft.Colors.LIGHT_GREEN_200
    }
    
    # -------------------------
    # Funciones de navegación
    # -------------------------
    def go_home(e):
        page.views.clear()
        page.views.append(home_view())
        page.update()
    
    def go_talonario(e, talonario_id):
        page.views.append(talonario_view(talonario_id))
        page.update()
    
    def go_configuracion(e):
        page.views.append(configuracion_view())
        page.update()
    
    def go_sorteo_form(e, talonario_id):
        page.views.append(sorteo_form_view(talonario_id))
        page.update()
    
    def go_resultado_sorteo(e, sorteo_id):
        page.views.append(resultado_sorteo_view(sorteo_id))
        page.update()
    
    # -------------------------
    # Funciones de datos
    # -------------------------
    def crear_talonario(nombre):
        nuevo_talonario = Talonario(nombre=nombre)
        session.add(nuevo_talonario)
        session.commit()
        
        for i in range(100):
            nuevo_numero = Numero(
                talonario_id=nuevo_talonario.id,
                numero=i,
                estado='disponible'
            )
            session.add(nuevo_numero)
        session.commit()
    
    def accion_numero(numero_id, accion, nombre=None):
        numero = session.get(Numero, numero_id)
        if not numero:
            return
        
        if accion == 'asignar':
            numero.estado = 'ocupado'
            numero.nombre_persona = nombre
        elif accion == 'asignar_pagar':
            numero.estado = 'pagado'
            numero.nombre_persona = nombre
        elif accion == 'pagar':
            if numero.estado == 'ocupado':
                numero.estado = 'pagado'
        elif accion == 'desasignar':
            numero.estado = 'disponible'
            numero.nombre_persona = None
        
        session.commit()
        return numero.talonario_id
    
    def realizar_sorteo(talonario_id, numero_ganador):
        nuevo_sorteo = Sorteo(talonario_id=talonario_id, numero_ganador=numero_ganador)
        session.add(nuevo_sorteo)
        session.commit()
        return nuevo_sorteo.id
    
    def actualizar_configuracion(precio, p1, p2, p3):
        config = session.query(Configuracion).first()
        if not config:
            config = Configuracion()
            session.add(config)
        
        config.precio_boleta = precio
        config.porcentaje_primeras = p1
        config.porcentaje_medio = p2
        config.porcentaje_ultimas = p3
        session.commit()
    
    # -------------------------
    # Vistas
    # -------------------------
    def home_view():
        # Obtener talonarios
        talonarios = session.query(Talonario).all()
        
        # Formulario para crear talonario
        nombre_talonario = ft.Ref[ft.TextField]()
        
        def crear_talonario_click(e):
            if nombre_talonario.current.value:
                crear_talonario(nombre_talonario.current.value)
                nombre_talonario.current.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("Talonario creado!"))
                page.snack_bar.open = True
                page.views.clear()
                page.views.append(home_view())
                page.update()
        
        # Lista de talonarios
        talonario_list = ft.ListView(expand=True)
        for t in talonarios:
            talonario_list.controls.append(
                ft.ListTile(
                    title=ft.Text(t.nombre),
                    on_click=lambda e, id=t.id: go_talonario(e, id)
                )
            )
        
        if not talonarios:
            talonario_list.controls.append(
                ft.ListTile(title=ft.Text("No hay talonarios creados"))
            )
        
        return ft.View(
            "/",
            [
                ft.AppBar(title=ft.Text("Sistema de Rifas")),
                ft.Text("Crear Nuevo Talonario", weight=ft.FontWeight.BOLD),
                ft.TextField(ref=nombre_talonario, label="Nombre del talonario"),
                ft.ElevatedButton("Crear Talonario", on_click=crear_talonario_click),
                ft.Divider(),
                ft.Text("Talonarios Existentes", weight=ft.FontWeight.BOLD),
                talonario_list,
                ft.ElevatedButton("Configuración", on_click=go_configuracion)
            ]
        )
    
    def talonario_view(talonario_id):
        talonario = session.get(Talonario, talonario_id)
        if not talonario:
            return go_home(None)
        
        numeros = session.query(Numero).filter_by(talonario_id=talonario_id).order_by(Numero.numero).all()
        config = session.query(Configuracion).first()
        
        # Calcular totales
        total_esperado = 100 * config.precio_boleta if config else 0
        numeros_pagados = sum(1 for n in numeros if n.estado == 'pagado')
        recaudado = numeros_pagados * config.precio_boleta if config else 0
        por_recaudar = total_esperado - recaudado
        
        # Crear cuadrícula de números
        grid = ft.GridView(
            expand=True,
            runs_count=10,
            max_extent=80,
            child_aspect_ratio=1,
            spacing=5,
            run_spacing=5,
        )
        
        for n in numeros:
            estado = n.estado
            grid.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"{n.numero:02d}", weight=ft.FontWeight.BOLD, size=12),
                            ft.Text(n.nombre_persona or "", size=10, max_lines=2)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=COLORES[estado],
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=5,
                    padding=5,
                    on_click=lambda e, num_id=n.id: mostrar_acciones_numero(e, num_id, estado)
                )
            )
        
        # Leyenda de colores
        leyenda = ft.Row(
            [
                ft.Container(
                    width=20, height=20, bgcolor=COLORES['disponible'], 
                    border=ft.border.all(1, ft.Colors.GREY_400)
                ),
                ft.Text("Disponible"),
                ft.Container(
                    width=20, height=20, bgcolor=COLORES['ocupado'], 
                    border=ft.border.all(1, ft.Colors.GREY_400)
                ),
                ft.Text("Ocupado"),
                ft.Container(
                    width=20, height=20, bgcolor=COLORES['pagado'], 
                    border=ft.border.all(1, ft.Colors.GREY_400)
                ),
                ft.Text("Pagado"),
            ],
            spacing=10
        )
        
        return ft.View(
            f"/talonario/{talonario_id}",
            [
                ft.AppBar(
                    title=ft.Text(f"Talonario: {talonario.nombre}"),
                    leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.views.pop()),
                    actions=[
                        ft.IconButton(ft.Icons.CARD_GIFTCARD, 
                                     on_click=lambda e: go_sorteo_form(e, talonario_id)),
                        ft.IconButton(ft.Icons.HOME, on_click=go_home)
                    ]
                ),
                ft.Row(
                    [
                        ft.Text(f"Total: ${format_currency(total_esperado)}"),
                        ft.Text(f"Recaudado: ${format_currency(recaudado)}"),
                        ft.Text(f"Por recaudar: ${format_currency(por_recaudar)}"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND
                ),
                leyenda,
                ft.Divider(),
                grid
            ]
        )
    
    def configuracion_view():
        config = session.query(Configuracion).first()
        if not config:
            config = Configuracion()
            session.add(config)
            session.commit()
        
        precio = ft.Ref[ft.TextField]()
        p1 = ft.Ref[ft.TextField]()
        p2 = ft.Ref[ft.TextField]()
        p3 = ft.Ref[ft.TextField]()
        
        def guardar_config(e):
            try:
                actualizar_configuracion(
                    float(precio.current.value),
                    float(p1.current.value),
                    float(p2.current.value),
                    float(p3.current.value)
                )
                page.snack_bar = ft.SnackBar(ft.Text("Configuración actualizada!"))
                page.snack_bar.open = True
                page.update()
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Valores inválidos"))
                page.snack_bar.open = True
                page.update()
        
        return ft.View(
            "/configuracion",
            [
                ft.AppBar(
                    title=ft.Text("Configuración"),
                    leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.views.pop()),
                    actions=[ft.IconButton(ft.Icons.HOME, on_click=go_home)]
                ),
                ft.TextField(ref=precio, label="Precio por boleta", 
                            value=str(config.precio_boleta)),
                ft.TextField(ref=p1, label="% Primeras 2 cifras", 
                            value=str(config.porcentaje_primeras)),
                ft.TextField(ref=p2, label="% 2 cifras del medio", 
                            value=str(config.porcentaje_medio)),
                ft.TextField(ref=p3, label="% Últimas 2 cifras", 
                            value=str(config.porcentaje_ultimas)),
                ft.ElevatedButton("Guardar", on_click=guardar_config),
                ft.ElevatedButton("Volver al Inicio", on_click=go_home)
            ]
        )
    
    def sorteo_form_view(talonario_id):
        talonario = session.get(Talonario, talonario_id)
        if not talonario:
            return go_home(None)
        
        numero_ganador = ft.Ref[ft.TextField]()
        
        def realizar_sorteo_click(e):
            num = numero_ganador.current.value
            if len(num) == 4 and num.isdigit():
                sorteo_id = realizar_sorteo(talonario_id, num)
                go_resultado_sorteo(e, sorteo_id)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Número debe ser de 4 dígitos"))
                page.snack_bar.open = True
                page.update()
        
        return ft.View(
            f"/sorteo/{talonario_id}",
            [
                ft.AppBar(
                    title=ft.Text(f"Sorteo: {talonario.nombre}"),
                    leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.views.pop()),
                    actions=[ft.IconButton(ft.Icons.HOME, on_click=go_home)]
                ),
                ft.TextField(ref=numero_ganador, label="Número ganador (4 dígitos)"),
                ft.ElevatedButton("Realizar Sorteo", on_click=realizar_sorteo_click)
            ]
        )
    
    def resultado_sorteo_view(sorteo_id):
        sorteo = session.get(Sorteo, sorteo_id)
        if not sorteo:
            return go_home(None)
        
        talonario = session.get(Talonario, sorteo.talonario_id)
        config = session.query(Configuracion).first()
        
        # Calcular premios
        total_esperado = 100 * config.precio_boleta
        premio_primeras = total_esperado * config.porcentaje_primeras / 100
        premio_medio = total_esperado * config.porcentaje_medio / 100
        premio_ultimas = total_esperado * config.porcentaje_ultimas / 100
        
        primeras = sorteo.numero_ganador[:2]
        medio = sorteo.numero_ganador[1:3]
        ultimas = sorteo.numero_ganador[2:]
        
        # Buscar ganadores
        ganadores_primeras = session.query(Numero).filter(
            Numero.talonario_id == talonario.id,
            func.cast(Numero.numero, String).like(f"{primeras}%"),
            Numero.estado == 'pagado'
        ).all()
        
        ganadores_medio = session.query(Numero).filter(
            Numero.talonario_id == talonario.id,
            func.cast(Numero.numero, String).like(f"{medio}%"),
            Numero.estado == 'pagado'
        ).all()
        
        ganadores_ultimas = session.query(Numero).filter(
            Numero.talonario_id == talonario.id,
            func.cast(Numero.numero, String).like(f"{ultimas}%"),
            Numero.estado == 'pagado'
        ).all()
        
        # Agrupar premios por persona
        premios_persona = {}
        
        def agregar_premio(nombre, premio):
            if nombre:
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
        
        # Crear UI
        contenido = ft.ListView(expand=True)
        
        # Resumen
        contenido.controls.append(ft.Text("Resumen de Premios", size=20, weight=ft.FontWeight.BOLD))
        contenido.controls.append(ft.Text(f"Total Esperado: ${format_currency(total_esperado)}"))
        contenido.controls.append(ft.Text(f"Premio Primeras 2 Cifras ({primeras}): ${format_currency(premio_primeras)}"))
        contenido.controls.append(ft.Text(f"Premio 2 Cifras del Medio ({medio}): ${format_currency(premio_medio)}"))
        contenido.controls.append(ft.Text(f"Premio Últimas 2 Cifras ({ultimas}): ${format_currency(premio_ultimas)}"))
        contenido.controls.append(ft.Divider())
        
        # Ganadores por categoría
        contenido.controls.append(ft.Text("Ganadores por Categoría", size=20, weight=ft.FontWeight.BOLD))
        
        # Primeras
        contenido.controls.append(ft.Text(f"Primeras 2 Cifras ({primeras}):", size=16))
        if ganadores_primeras:
            for g in ganadores_primeras:
                premio_individual = premio_primeras / len(ganadores_primeras)
                contenido.controls.append(ft.Text(f"Número {g.numero:02d}: {g.nombre_persona} - ${format_currency(premio_individual)}"))
        else:
            contenido.controls.append(ft.Text("No hay ganadores"))
        contenido.controls.append(ft.Divider())
        
        # Medio
        contenido.controls.append(ft.Text(f"2 Cifras del Medio ({medio}):", size=16))
        if ganadores_medio:
            for g in ganadores_medio:
                premio_individual = premio_medio / len(ganadores_medio)
                contenido.controls.append(ft.Text(f"Número {g.numero:02d}: {g.nombre_persona} - ${format_currency(premio_individual)}"))
        else:
            contenido.controls.append(ft.Text("No hay ganadores"))
        contenido.controls.append(ft.Divider())
        
        # Últimas
        contenido.controls.append(ft.Text(f"Últimas 2 Cifras ({ultimas}):", size=16))
        if ganadores_ultimas:
            for g in ganadores_ultimas:
                premio_individual = premio_ultimas / len(ganadores_ultimas)
                contenido.controls.append(ft.Text(f"Número {g.numero:02d}: {g.nombre_persona} - ${format_currency(premio_individual)}"))
        else:
            contenido.controls.append(ft.Text("No hay ganadores"))
        contenido.controls.append(ft.Divider())
        
        # Premios por persona
        contenido.controls.append(ft.Text("Premios por Persona", size=20, weight=ft.FontWeight.BOLD))
        if premios_persona:
            for persona, premio in premios_persona.items():
                contenido.controls.append(ft.Text(f"{persona}: ${format_currency(premio)}"))
        else:
            contenido.controls.append(ft.Text("No hay ganadores"))
        
        return ft.View(
            f"/resultado/{sorteo_id}",
            [
                ft.AppBar(
                    title=ft.Text(f"Resultado Sorteo: {sorteo.numero_ganador}"),
                    leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.views.pop()),
                    actions=[ft.IconButton(ft.Icons.HOME, on_click=go_home)]
                ),
                contenido,
                ft.ElevatedButton("Volver al Talonario", 
                                 on_click=lambda e: go_talonario(e, talonario.id))
            ],
            scroll=ft.ScrollMode.AUTO
        )
    
    # -------------------------
    # Funciones auxiliares
    # -------------------------
    def mostrar_acciones_numero(e, numero_id, estado):
        numero = session.get(Numero, numero_id)
        if not numero:
            return
        
        nombre_input = ft.Ref[ft.TextField]()
        
        def ejecutar_accion(accion):
            nombre = nombre_input.current.value if nombre_input.current else None
            talonario_id = accion_numero(numero_id, accion, nombre)
            if talonario_id:
                page.views.pop()
                page.views.append(talonario_view(talonario_id))
                page.update()
        
        controles = [
            ft.Text(f"Acciones para número: {numero.numero:02d}", size=18, weight=ft.FontWeight.BOLD)
        ]
        
        if estado in ['disponible', 'ocupado']:
            controles.append(ft.TextField(ref=nombre_input, label="Nombre"))
        
        if estado == 'disponible':
            controles.append(ft.ElevatedButton("Asignar", on_click=lambda _: ejecutar_accion('asignar')))
            controles.append(ft.ElevatedButton("Asignar y Pagar", on_click=lambda _: ejecutar_accion('asignar_pagar')))
        elif estado == 'ocupado':
            controles.append(ft.ElevatedButton("Pagar", on_click=lambda _: ejecutar_accion('pagar')))
            controles.append(ft.ElevatedButton("Desasignar", on_click=lambda _: ejecutar_accion('desasignar')))
        elif estado == 'pagado':
            controles.append(ft.ElevatedButton("Desasignar", on_click=lambda _: ejecutar_accion('desasignar')))
        
        controles.append(ft.ElevatedButton("Cancelar", on_click=lambda _: page.views.pop()))
        
        page.views.append(
            ft.View(
                f"/accion/{numero_id}",
                [
                    ft.AppBar(
                        title=ft.Text("Acciones"),
                        leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.views.pop())
                    ),
                    ft.Column(controles, spacing=10)
                ]
            )
        )
        page.update()
    
    # -------------------------
    # Inicialización
    # -------------------------
    # Crear configuración inicial si no existe
    if not session.query(Configuracion).first():
        config = Configuracion()
        session.add(config)
        session.commit()
    
    # Mostrar vista inicial
    page.views.append(home_view())
    page.update()

ft.app(target=main, view=ft.AppView.WEB_BROWSER)