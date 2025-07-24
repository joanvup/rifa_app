# Rifa App 🎟️

Una aplicación web desarrollada en Python para gestionar y administrar rifas de forma sencilla e intuitiva. El proyecto está diseñado con un enfoque **mobile-first**, optimizado para una visualización perfecta en dispositivos móviles.

![Captura de Pantalla de la App](https-placeholder-for-your-image.png)

## ✨ Características Principales

-   **Gestión de Talonarios:** Crea y administra rifas con talonarios de 100 números (00-99).
-   **Visualización en Cuadrícula:** Cada talonario se presenta en una cuadrícula interactiva de 10x10 para una fácil navegación.
-   **Diseño Responsivo:** Interfaz adaptable y optimizada por defecto para formatos de pantalla móvil (9:16).
-   **Estado de Números por Color:** Un sistema de leyenda visual para identificar rápidamente el estado de cada número:
    -   🟩 **Disponible:** El número puede ser asignado.
    -   🟨 **Ocupado:** El número está reservado pero aún no ha sido pagado.
    -   🟥 **Pagado:** El número ha sido comprado y pagado.
-   **Asignación Interactiva:** Al hacer clic en un número, se despliega un menú de acciones rápidas: `Asignar`, `Asignar y Pagar`, `Pagar`, `Desasignar`.
-   **Control Financiero:** Visualiza en tiempo real el total **recaudado** y el monto **por recaudar** a medida que se pagan los números.
-   **Sistema de Premios Configurable:** Define el precio por boleta y los porcentajes de los premios.
-   **Cálculo Automático de Ganadores:** Introduce el número de 4 cifras de la lotería y la app calculará y mostrará automáticamente a los ganadores y el monto de su premio.

## 🎲 Lógica del Sorteo y Premios

La rifa se gana con base en un número de lotería de 4 dígitos. Los premios se distribuyen de la siguiente manera:

-   🏆 **Primer Premio:** Coincide con las **2 primeras cifras** del número ganador.
-   🥈 **Segundo Premio:** Coincide con las **2 cifras de en medio** del número ganador.
-   🥉 **Tercer Premio:** Coincide con las **2 últimas cifras** del número ganador.

**Ejemplo:**
-   **Número de Lotería Ganador:** `1234`
-   **Ganador 1er Premio:** Quien tenga el número `12`.
-   **Ganador 2do Premio:** Quien tenga el número `23`.
-   **Ganador 3er Premio:** Quien tenga el número `34`.

El **valor total de la rifa** se calcula como `(Precio de la Boleta) x 100`. Los porcentajes de los premios se aplican sobre este total y son configurables en el panel de administración.

## 🛠️ Tecnologías Utilizadas

-   **Backend:** Python (Puedes especificar el framework, por ejemplo: Flask, Django)
-   **Frontend:** HTML5, CSS3, JavaScript
-   **Base de Datos:** (Especifica la base de datos que usas, ej: SQLite, PostgreSQL)

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu entorno local.

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/joanvup/rifa_app.git
    cd rifa_app
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Para Linux/Mac
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación:**
    ```bash
    # Ejemplo para Flask
    python app.py

    # Ejemplo para flet
    flet run rifa_app.py
    ```
    La aplicación estará disponible en `http://127.0.0.1:5000` (o el puerto que hayas configurado).

## ⚙️ Configuración

Dentro de la aplicación, encontrarás una sección de **Configuraciones** donde podrás ajustar valores clave como:
-   Precio de la boleta.
-   Porcentaje del premio para las 2 primeras cifras.
-   Porcentaje del premio para las 2 cifras de en medio.
-   Porcentaje del premio para las 2 últimas cifras.

## 🤝 Cómo Contribuir

¡Las contribuciones son bienvenidas! Si deseas mejorar esta aplicación, sigue estos pasos:

1.  Haz un **Fork** de este repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y haz **Commit** (`git commit -m 'Añade nueva funcionalidad'`).
4.  Haz **Push** a tu rama (`git push origin feature/nueva-funcionalidad`).
5.  Abre un **Pull Request**.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---
**Desarrollado por joanvup** - @joanvup
