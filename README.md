# 🎟️ Rifa App

**Rifa App** es una aplicación web desarrollada en Python para la administración y control de rifas con talonarios de 100 números. Está diseñada para ser totalmente responsiva y adaptada a dispositivos móviles (formato 9:16), facilitando su uso desde smartphones, tablets o computadores.

## 🌐 Enlace al repositorio

🔗 [https://github.com/joanvup/rifa_app](https://github.com/joanvup/rifa_app)

---

## 🧩 Características principales

- 📱 **Diseño responsivo**: Adaptado automáticamente a pantallas de celular (9:16).
- 🧮 **Talonario de 100 números**: Presentado visualmente como una cuadrícula de 10x10.
- 🎨 **Leyenda por colores**:
  - **Disponible**: Número libre para asignar.
  - **Ocupado**: Ya asignado a una persona.
  - **Pagado**: Número comprado y confirmado.
- 👤 **Datos del comprador**: Cada número ocupado o pagado muestra el nombre del comprador.
- 🚫 **Control de asignación**: Un número ya ocupado o pagado no puede ser reasignado.
- 📋 **Opciones al hacer clic sobre un número**:
  - Asignar
  - Asignar y pagar
  - Pagar
  - Desasignar
- 💰 **Configuración de premios**:
  - Número ganador de la rifa: número de 4 cifras.
  - Premios calculados con base en coincidencias:
    - **Primeras 2 cifras**: 25% del total.
    - **2 cifras del medio**: 10% del total.
    - **Últimas 2 cifras**: 40% del total.
  - El **total** se calcula como: `precio_boleta × 100`.
- 🏆 **Detección automática de ganadores**: Al ingresar el número de la lotería, la app identifica y muestra:
  - Los números ganadores.
  - Los participantes ganadores.
  - El monto a pagar a cada uno (sumado si tiene más de un número ganador).
- 📈 **Indicadores financieros en tiempo real**:
  - Acumulado recaudado.
  - Monto por recaudar.

---

## ⚙️ Configuraciones disponibles

Desde la interfaz de configuración, el administrador puede definir:

- Precio de cada boleta.
- Porcentajes de premio para:
  - Primeras 2 cifras.
  - 2 cifras del medio.
  - Últimas 2 cifras.

---

## 📦 Tecnologías utilizadas

- 🐍 Python
- 🌐 Flask / Flet (dependiendo de la versión del frontend)
- HTML / CSS / JavaScript
- Bootstrap u otra librería responsiva (si aplica)

---
## 📸 Vista previa


## 🤝 Contribuciones
Las contribuciones, ideas o mejoras son bienvenidas. Puedes abrir un issue o enviar un pull request.

## 🧑‍💻 Autor
Joan Fuentes
🔗 @joanvup

## 📄 Licencia
Este proyecto está bajo la licencia MIT.

## 🚀 Cómo ejecutar la aplicación

```bash
# Clona el repositorio
git clone https://github.com/joanvup/rifa_app.git
cd rifa_app

# (Opcional) Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt

# Ejecuta la app
python main.py
