"""
app.py — Friko Recomienda: MVP completo con Streamlit.

Ejecutar: streamlit run app.py
"""

import streamlit as st
from data_loader import load_catalog, load_recipes, get_unique_regions, get_unique_preparations
from engine import recomendar, calcular_cantidad_paquetes, get_ocasiones
from recipe_generator import obtener_receta

# ══════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="Friko Recomienda",
    page_icon="🍗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════
#  CSS PERSONALIZADO — Identidad Friko
# ══════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Paleta Friko ── */
    :root {
        --friko-red: #C8102E;
        --friko-red-dark: #A50D22;
        --friko-yellow: #F2A900;
        --friko-yellow-light: #FFF3D6;
        --friko-dark: #1A1A2E;
        --friko-gray: #F7F7F7;
        --friko-white: #FFFFFF;
    }

    /* ── Ocultar menú de Streamlit ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Body ── */
    .stApp {
        background: linear-gradient(180deg, #FFF9EC 0%, #FFFFFF 30%);
    }

    /* ── Header hero ── */
    .hero-container {
        background: linear-gradient(135deg, #C8102E 0%, #8B0A1E 100%);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(200,16,46,0.2);
    }
    .hero-container h1 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.3rem !important;
        font-weight: 800 !important;
    }
    .hero-container p {
        color: #FFD6DD;
        font-size: 1rem;
        margin: 0;
    }
    .hero-emoji {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    /* ── Cards de producto ── */
    .product-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 2px solid #F2A900;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    .product-card h3 {
        color: #C8102E !important;
        font-size: 1.3rem !important;
        margin-bottom: 0.5rem !important;
    }
    .product-badge {
        display: inline-block;
        background: #C8102E;
        color: white;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .product-badge-alt {
        display: inline-block;
        background: #F2A900;
        color: #1A1A2E;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .score-bar {
        background: linear-gradient(90deg, #C8102E, #F2A900);
        height: 6px;
        border-radius: 3px;
        margin-top: 8px;
    }

    /* ── Receta ── */
    .recipe-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        border-left: 5px solid #F2A900;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .recipe-card h2 {
        color: #C8102E !important;
        font-size: 1.4rem !important;
    }
    .recipe-meta {
        display: flex;
        gap: 1rem;
        margin: 0.8rem 0;
        flex-wrap: wrap;
    }
    .recipe-meta-item {
        background: #FFF3D6;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #1A1A2E;
        font-weight: 600;
    }
    .recipe-step {
        background: #F7F7F7;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #C8102E;
    }
    .recipe-step strong {
        color: #C8102E;
    }
    .tip-box {
        background: #FFF3D6;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 4px solid #F2A900;
    }

    /* ── Botones ── */
    .stButton > button {
        background: linear-gradient(135deg, #C8102E 0%, #A50D22 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #A50D22 0%, #8B0A1E 100%) !important;
        box-shadow: 0 4px 15px rgba(200,16,46,0.3) !important;
    }

    /* ── Formulario ── */
    .form-section {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .form-section h3 {
        color: #1A1A2E !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.8rem !important;
    }

    /* ── Select y inputs ── */
    .stSelectbox > div > div {
        border-radius: 10px !important;
    }
    .stSlider > div > div > div {
        color: #C8102E !important;
    }

    /* ── Divider ── */
    .friko-divider {
        height: 3px;
        background: linear-gradient(90deg, #C8102E, #F2A900, #C8102E);
        border-radius: 2px;
        margin: 1.5rem 0;
    }

    /* ── Footer ── */
    .friko-footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
    }

    /* ── Alternativas ── */
    .alt-card {
        background: #F7F7F7;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #E0E0E0;
    }
    .alt-card h4 {
        color: #1A1A2E !important;
        margin-bottom: 0.3rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
#  CARGA DE DATOS (cacheada)
# ══════════════════════════════════════════════════
@st.cache_data
def cargar_datos():
    catalogo = load_catalog()
    recetas = load_recipes()
    regiones = get_unique_regions(catalogo)
    preparaciones = get_unique_preparations(catalogo)
    return catalogo, recetas, regiones, preparaciones


catalogo, recetas, regiones, preparaciones = cargar_datos()
ocasiones = get_ocasiones()


# ══════════════════════════════════════════════════
#  ESTADO DE LA APP
# ══════════════════════════════════════════════════
if "mostrar_resultado" not in st.session_state:
    st.session_state.mostrar_resultado = False
if "recomendaciones" not in st.session_state:
    st.session_state.recomendaciones = []
if "receta_actual" not in st.session_state:
    st.session_state.receta_actual = None
if "params" not in st.session_state:
    st.session_state.params = {}


# ══════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════
st.markdown("""
<div class="hero-container">
    <div class="hero-emoji">🍗</div>
    <h1>Friko Recomienda</h1>
    <p>Descubre el producto ideal y la receta perfecta para tu ocasión</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
#  FORMULARIO
# ══════════════════════════════════════════════════
if not st.session_state.mostrar_resultado:

    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Cuéntanos sobre tu ocasión")

    col1, col2 = st.columns(2)

    with col1:
        ocasion = st.selectbox(
            "¿Para qué ocasión?",
            options=ocasiones,
            index=0,
            help="Selecciona el tipo de ocasión para personalizar la recomendación",
        )

    with col2:
        region = st.selectbox(
            "¿En qué región estás?",
            options=regiones,
            index=0,
            help="Mostramos productos disponibles en tu zona",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### 👨‍🍳 Detalles de preparación")

    col3, col4 = st.columns(2)

    with col3:
        num_personas = st.slider(
            "¿Para cuántas personas?",
            min_value=1,
            max_value=30,
            value=4,
            step=1,
        )

    with col4:
        preparacion = st.selectbox(
            "¿Cómo prefieres preparar?",
            options=preparaciones,
            index=0,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Botón principal
    st.markdown("")
    if st.button("🔍  ¡Recomiéndame!", use_container_width=True):
        with st.spinner("Buscando el producto perfecto para ti..."):
            recs = recomendar(
                catalogo, region, preparacion, ocasion, num_personas, top_n=3
            )

            if recs:
                # Obtener receta para el producto principal
                producto_principal = recs[0]
                receta = obtener_receta(
                    producto_principal["producto"],
                    preparacion,
                    num_personas,
                    ocasion,
                    recetas,
                )

                st.session_state.recomendaciones = recs
                st.session_state.receta_actual = receta
                st.session_state.params = {
                    "ocasion": ocasion,
                    "region": region,
                    "personas": num_personas,
                    "preparacion": preparacion,
                }
                st.session_state.mostrar_resultado = True
                st.rerun()
            else:
                st.warning(
                    "😕 No encontramos productos para esa combinación. "
                    "Intenta cambiar la región o el tipo de preparación."
                )


# ══════════════════════════════════════════════════
#  RESULTADOS
# ══════════════════════════════════════════════════
else:
    recs = st.session_state.recomendaciones
    receta = st.session_state.receta_actual
    params = st.session_state.params
    principal = recs[0]

    # ── Resumen de búsqueda ──
    st.markdown(f"""
    <div style="background: #F7F7F7; border-radius:12px; padding:1rem; margin-bottom:1rem; text-align:center;">
        <span style="font-size:0.9rem; color:#666;">
            📍 {params['region']} · 👥 {params['personas']} personas ·
            🍳 {params['preparacion']} · 🎉 {params['ocasion']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Producto principal ──
    st.markdown(f"""
    <div class="product-card">
        <span class="product-badge">⭐ RECOMENDADO</span>
        <span class="product-badge-alt">{principal['marca']}</span>
        <span class="product-badge-alt">{principal['categoria']}</span>
        <h3>🍗 {principal['producto']}</h3>
        <p style="color:#555; margin:0.3rem 0;">{principal['descripcion']}</p>
        <p style="margin:0.3rem 0;">
            📦 <strong>Presentación:</strong> {principal['presentacion']}<br>
            🍳 <strong>Preparación:</strong> {principal['tipo_preparacion']}<br>
            👥 <strong>Sugerencia:</strong> Compra <strong>{calcular_cantidad_paquetes(principal, params['personas'])}</strong> para {params['personas']} personas
        </p>
        <div class="score-bar" style="width:{min(100, principal['score'])}%;"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Receta ──
    st.markdown('<div class="friko-divider"></div>', unsafe_allow_html=True)

    fuente = receta.get("fuente", "")
    fuente_label = ""
    if fuente == "momentosfriko.com":
        fuente_label = '<span class="product-badge-alt">📖 Receta de momentosfriko.com</span>'
    elif fuente == "generada":
        fuente_label = '<span class="product-badge">🤖 Receta generada por IA</span>'

    st.markdown(f"""
    <div class="recipe-card">
        {fuente_label}
        <h2>👨‍🍳 {receta['titulo']}</h2>
        <div class="recipe-meta">
            <span class="recipe-meta-item">⏱️ {receta.get('tiempo', '30 min')}</span>
            <span class="recipe-meta-item">👥 {receta.get('porciones', f"{params['personas']} personas")}</span>
            <span class="recipe-meta-item">📊 {receta.get('dificultad', 'Media')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Imagen de la receta (si existe)
    imagen = receta.get("imagen", "")
    if imagen:
        st.image(imagen, use_container_width=True)

    # Ingredientes
    st.markdown("#### 🥘 Ingredientes")
    ingredientes = receta.get("ingredientes", [])
    if ingredientes:
        ing_html = ""
        for ing in ingredientes:
            ing_html += f'<li style="padding:4px 0;">{ing}</li>'
        st.markdown(
            f'<ul style="background:#FFF9EC; border-radius:12px; padding:1rem 1rem 1rem 2rem;">{ing_html}</ul>',
            unsafe_allow_html=True,
        )

    # Pasos
    st.markdown("#### 📋 Preparación paso a paso")
    pasos = receta.get("pasos", [])
    for i, paso in enumerate(pasos, 1):
        st.markdown(
            f'<div class="recipe-step"><strong>Paso {i}:</strong> {paso}</div>',
            unsafe_allow_html=True,
        )

    # Tip
    tip = receta.get("tip", "")
    if tip:
        st.markdown(
            f'<div class="tip-box">💡 <strong>Tip del chef:</strong> {tip}</div>',
            unsafe_allow_html=True,
        )

    # Link a receta original
    url = receta.get("url", "")
    if url:
        st.markdown(
            f'<p style="text-align:center; margin-top:1rem;">'
            f'<a href="{url}" target="_blank" style="color:#C8102E; font-weight:600;">'
            f'🔗 Ver receta completa en momentosfriko.com</a></p>',
            unsafe_allow_html=True,
        )

    # ── Alternativas ──
    if len(recs) > 1:
        st.markdown('<div class="friko-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 💡 También te puede interesar")

        for alt in recs[1:]:
            st.markdown(f"""
            <div class="alt-card">
                <h4>🍗 {alt['producto']}</h4>
                <p style="margin:0; font-size:0.9rem; color:#555;">
                    {alt['descripcion']} · 📦 {alt['presentacion']} · 🍳 {alt['tipo_preparacion']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ── Botón volver ──
    st.markdown('<div class="friko-divider"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄  Nueva búsqueda", use_container_width=True):
            st.session_state.mostrar_resultado = False
            st.session_state.recomendaciones = []
            st.session_state.receta_actual = None
            st.session_state.params = {}
            st.rerun()

    with col_b:
        # Botón compartir (genera texto para copiar)
        share_text = (
            f"🍗 Friko me recomienda: {principal['producto']} "
            f"para {params['ocasion'].lower()} ({params['personas']} personas).\n"
            f"Receta: {receta['titulo']}\n"
            f"¡Prueba Friko Recomienda!"
        )
        st.text_area(
            "📤 Comparte tu recomendación:",
            value=share_text,
            height=80,
            label_visibility="visible",
        )


# ══════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════
st.markdown("""
<div class="friko-footer">
    <div class="friko-divider"></div>
    <p>🍗 <strong>Friko Recomienda</strong> — Tu asistente culinario inteligente</p>
    <p>Un producto de <a href="https://www.momentosfriko.com" target="_blank" style="color:#C8102E;">Momentos Friko</a></p>
</div>
""", unsafe_allow_html=True)
