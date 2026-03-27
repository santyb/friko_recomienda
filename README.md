# 🍗 Friko Recomienda — MVP

**Tu asistente culinario inteligente para descubrir el producto Friko ideal y la receta perfecta.**

---

## Descripción

Friko Recomienda es una plataforma web que ayuda al consumidor de productos Friko a:

- **Descubrir** el producto ideal según su ocasión, número de personas, tipo de preparación y región.
- **Recibir** una receta colombiana personalizada lista para preparar.
- **Explorar** el portafolio completo de la marca.

---

## Estructura del Proyecto

```
friko_recomienda/
├── app.py                  # Aplicación principal Streamlit
├── data_loader.py          # Carga de catálogo (Excel) y recetas (JSON)
├── engine.py               # Motor de recomendación basado en reglas
├── recipe_generator.py     # Generador de recetas (real + IA + plantillas)
├── requirements.txt        # Dependencias Python
├── .streamlit/
│   └── config.toml         # Tema y configuración de Streamlit
└── data/
    ├── BD_base.xlsx         # Catálogo de 75 productos (Friko + Antillana)
    └── recetas_friko.json   # 200 recetas de momentosfriko.com
```

---

## Instalación Local

### Requisitos previos
- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Clonar o copiar el proyecto
cd friko_recomienda

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Configurar API de Claude para recetas con IA
export ANTHROPIC_API_KEY="tu-clave-aqui"

# 5. Ejecutar
streamlit run app.py
```

La app estará disponible en `http://localhost:8501`

---

## Cómo Funciona

### Flujo del Usuario

```
Usuario → Formulario (ocasión + personas + preparación + región)
    → Motor de reglas (filtra y puntúa productos del catálogo)
        → Busca receta real en base de 200 recetas
            → Si no encuentra: genera receta con IA o plantilla colombiana
                → Muestra resultado: producto + receta + alternativas
```

### Motor de Recomendación

El motor puntúa cada producto en el catálogo según:

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| Región | Filtro | Solo muestra productos de la región seleccionada |
| Preparación | +30 | Si el tipo de preparación coincide |
| Categoría | +20 | Si la categoría es preferida para la ocasión |
| Porciones | +25 | Si la presentación cubre el número de personas |
| Bonus | ×1.3-2.0 | Productos rápidos para snack, premium para eventos |

### Generación de Recetas

Tres niveles de fallback:

1. **Receta real**: busca en las 200 recetas de momentosfriko.com por coincidencia de producto.
2. **Claude API**: si hay API key configurada, genera receta colombiana personalizada.
3. **Plantillas**: 10+ recetas colombianas pre-diseñadas como fallback local.

---

## Datos

### Catálogo (BD_base.xlsx)
- 75 productos (45 Friko + 30 Antillana)
- 6 regiones: Antioquia, Atlántico, Bogotá, Eje Cafetero, Norte de Santander, Santander
- 6 categorías: Pollo, Pollo Procesado, Carnes frías, Pescado, Pescado Procesado, Mariscos
- 11 tipos de preparación

### Recetas (recetas_friko.json)
- 200 recetas extraídas de momentosfriko.com
- Incluyen ingredientes, pasos, tiempos e imágenes

---

## Despliegue

### Opción 1: Streamlit Cloud (Gratis)

1. Subir el proyecto a un repositorio en GitHub.
2. Ir a [share.streamlit.io](https://share.streamlit.io).
3. Conectar el repositorio y seleccionar `app.py`.
4. (Opcional) Agregar `ANTHROPIC_API_KEY` en Settings > Secrets.
5. Deploy.

### Opción 2: Railway

1. Crear cuenta en [railway.app](https://railway.app).
2. Crear nuevo proyecto desde GitHub.
3. Agregar variable de entorno `ANTHROPIC_API_KEY` si se desea.
4. Railway detecta automáticamente el `requirements.txt`.
5. Configurar el comando de inicio: `streamlit run app.py --server.port $PORT`

### Opción 3: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## Evolución Futura

- [ ] Panel de administración del catálogo
- [ ] Dashboard de métricas de uso
- [ ] Personalización con historial del consumidor
- [ ] Migración a Next.js para experiencia móvil premium
- [ ] Integración con e-commerce

---

## Tecnologías

| Capa | Herramienta | Uso |
|------|-------------|-----|
| Frontend | Streamlit | Formulario + visualización de resultados |
| Backend | Python | Motor de reglas + lógica de negocio |
| IA | Claude API (Anthropic) | Generación de recetas personalizadas |
| Datos | Excel + JSON | Catálogo de productos + recetas base |
| Despliegue | Streamlit Cloud / Railway | Hosting gratuito o bajo costo |
