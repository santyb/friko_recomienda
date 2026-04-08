# 🚀 Guía rápida — Codespaces

## Paso 1: Crear tu Codespace
1. Ve a [github.com/santyb/friko_recomienda](https://github.com/santyb/friko_recomienda)
2. Click en el botón verde **"Code"**
3. Pestaña **"Codespaces"** → **"Create codespace on main"**
4. Espera ~1 minuto mientras se configura todo automáticamente

## Paso 2: Configurar tu API Key
Cuando el Codespace se abra, GitHub te pedirá tu `ANTHROPIC_API_KEY`.
Pégala y listo. Si no la tienes aún, créala en: https://console.anthropic.com/settings/keys

> ⚠️ La app funciona sin API key (usa recetas de plantilla), pero con key genera recetas personalizadas con IA.

## Paso 3: Correr la app
En la terminal del Codespace, ejecuta:
```bash
streamlit run app.py
```
Se abrirá automáticamente una pestaña con la app en el puerto 8501.

## Hacer cambios
Simplemente edita los archivos en el editor, guarda, y Streamlit recargará automáticamente. Para guardar tus cambios en GitHub, usa la pestaña de Source Control (ícono de ramas) a la izquierda.
