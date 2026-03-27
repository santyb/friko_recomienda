"""
recipe_generator.py — Generador de recetas.

Estrategia:
1. Buscar en la base de recetas reales (JSON) una que coincida con el producto.
2. Si no hay match, generar una receta estructurada con plantillas colombianas.
3. Si hay API de Claude disponible, usarla para generar recetas dinámicas.

La función principal `obtener_receta()` unifica ambos caminos.
"""

import random
import re
import os
from typing import Dict, List, Optional

# ──────────────────────────────────────────────
#  Intentar importar la API de Anthropic
# ──────────────────────────────────────────────
CLAUDE_AVAILABLE = False
try:
    import anthropic
    ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    if ANTHROPIC_KEY:
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        CLAUDE_AVAILABLE = True
except ImportError:
    pass


# ──────────────────────────────────────────────
#  Mapeo producto → keywords de búsqueda en recetas
# ──────────────────────────────────────────────
PRODUCT_RECIPE_MAP = {
    "Chuzos de contramuslo": ["chuzo"],
    "Mini chuzos": ["chuzo", "mini"],
    "Alitas BBQ": ["alitas"],
    "Alitas picantes": ["alitas", "picante"],
    "Nuggets de pollo": ["nugget"],
    "Bombones BBQ": ["bombón", "bombones", "apanado"],
    "Chorizo de pollo": ["chorizo"],
    "Filete de pechuga": ["pechuga", "filete"],
    "Lomitos de pechuga": ["lomito", "pechuga"],
    "Hamburguesa de salmón": ["hamburguesa", "salmón"],
    "Brochetas de langostino": ["langostino", "brocheta"],
    "Medallones de pescado": ["medallón", "pescado"],
    "Dedos de merluza": ["merluza", "dedo"],
    "Filete de salmón premium": ["salmón", "filete"],
    "Camarón tití": ["camarón"],
}


def buscar_receta_real(producto: str, recetas: List[Dict]) -> Optional[Dict]:
    """
    Busca en la base de recetas reales una que coincida con el producto.
    Devuelve la mejor coincidencia o None.
    """
    keywords = PRODUCT_RECIPE_MAP.get(producto, [producto.lower().split()[0]])

    mejores = []
    for r in recetas:
        titulo_lower = r["titulo"].lower()
        matches = sum(1 for kw in keywords if kw.lower() in titulo_lower)
        if matches > 0:
            mejores.append((matches, r))

    if mejores:
        mejores.sort(key=lambda x: x[0], reverse=True)
        return mejores[0][1]

    return None


def generar_receta_ia(
    producto: str,
    preparacion: str,
    num_personas: int,
    ocasion: str,
) -> Dict:
    """
    Genera receta usando Claude API si está disponible.
    Si no, usa el generador de plantillas.
    """
    if CLAUDE_AVAILABLE:
        return _generar_con_claude(producto, preparacion, num_personas, ocasion)
    return _generar_plantilla(producto, preparacion, num_personas, ocasion)


def _generar_con_claude(
    producto: str,
    preparacion: str,
    num_personas: int,
    ocasion: str,
) -> Dict:
    """Genera receta con Claude API."""
    prompt = f"""Eres un chef colombiano experto. Genera UNA receta usando el producto "{producto}" de la marca Friko.

Contexto:
- Ocasión: {ocasion}
- Número de personas: {num_personas}
- Tipo de preparación: {preparacion}
- Debe usar ingredientes colombianos típicos
- El producto Friko es el ingrediente principal

Responde EXACTAMENTE en este formato JSON (sin markdown, sin ```):
{{
  "titulo": "Nombre creativo de la receta",
  "tiempo": "X minutos",
  "dificultad": "Fácil/Media/Difícil",
  "ingredientes": ["cantidad ingrediente 1", "cantidad ingrediente 2", ...],
  "pasos": ["Paso 1: descripción", "Paso 2: descripción", ...],
  "tip": "Un consejo útil para esta receta"
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        import json
        text = response.content[0].text.strip()
        # Limpiar posibles backticks
        text = re.sub(r"```json?\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        return json.loads(text)
    except Exception as e:
        print(f"Error con Claude API: {e}")
        return _generar_plantilla(producto, preparacion, num_personas, ocasion)


# ──────────────────────────────────────────────
#  Plantillas de recetas colombianas por producto
# ──────────────────────────────────────────────
PLANTILLAS = {
    "Chuzos de contramuslo": {
        "titulo": "Chuzos Friko con ají de maracuyá y arepa",
        "tiempo": "35 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Chuzos de contramuslo Friko",
            "4 arepas blancas",
            "2 limones",
            "1 maracuyá maduro",
            "1 ají dulce picado fino",
            "2 cucharadas de miel",
            "Sal y pimienta al gusto",
            "1 cucharada de aceite vegetal",
            "Guacamole para acompañar",
        ],
        "pasos": [
            "Sacamos los Chuzos de contramuslo Friko del empaque y los dejamos atemperar 10 minutos.",
            "Preparamos el ají de maracuyá: mezclamos la pulpa del maracuyá con el ají dulce picado, la miel, el jugo de un limón, sal y pimienta.",
            "Calentamos la parrilla o sartén a fuego medio-alto con un poco de aceite.",
            "Cocinamos los chuzos siguiendo las instrucciones del empaque, aproximadamente 6-8 minutos por lado hasta dorar.",
            "En los últimos 2 minutos, ponemos las arepas en la parrilla para calentar.",
            "Servimos los chuzos sobre las arepas, bañamos con el ají de maracuyá y acompañamos con guacamole.",
        ],
        "tip": "Si quieres un toque ahumado, agrega unas gotas de humo líquido al ají de maracuyá.",
    },
    "Alitas BBQ": {
        "titulo": "Alitas BBQ Friko con papas criollas y hogao",
        "tiempo": "40 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Alitas BBQ Friko",
            "500g de papas criollas",
            "2 tomates maduros",
            "1 cebolla larga grande",
            "2 dientes de ajo",
            "1 cucharada de comino",
            "Cilantro fresco al gusto",
            "Aceite vegetal",
            "Sal al gusto",
        ],
        "pasos": [
            "Precalentamos el horno a 200°C o la airfryer a 180°C.",
            "Colocamos las Alitas BBQ Friko en una bandeja con papel aluminio y horneamos 25-30 minutos según instrucciones del empaque.",
            "Mientras tanto, cocinamos las papas criollas en agua con sal hasta que estén tiernas (15-20 minutos). Escurrimos.",
            "Para el hogao: picamos la cebolla larga y el tomate. En una sartén con aceite, sofreímos la cebolla y el ajo hasta que estén transparentes. Agregamos el tomate, el comino y sal. Cocinamos 10 minutos a fuego bajo.",
            "Servimos las alitas BBQ acompañadas de las papas criollas bañadas con el hogao y cilantro fresco.",
        ],
        "tip": "Para alitas extra crocantes en airfryer, voltéalas a mitad de cocción.",
    },
    "Nuggets de pollo": {
        "titulo": "Bowl de nuggets Friko con arroz de coco y ensalada tropical",
        "tiempo": "25 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Nuggets de pollo Friko",
            "2 tazas de arroz cocido",
            "1/2 taza de leche de coco",
            "1 mango maduro en cubos",
            "1 aguacate en láminas",
            "1/2 taza de maíz tierno",
            "Limón y cilantro para servir",
            "Sal al gusto",
        ],
        "pasos": [
            "Preparamos los Nuggets Friko en airfryer u horno siguiendo las instrucciones del empaque hasta que estén dorados y crocantes.",
            "Calentamos el arroz cocido con la leche de coco en una olla a fuego bajo, revolviendo hasta que absorba. Salamos al gusto.",
            "Armamos el bowl: colocamos el arroz de coco como base, los nuggets encima, y decoramos con mango, aguacate y maíz.",
            "Terminamos con un chorrito de limón y cilantro fresco picado.",
        ],
        "tip": "Los niños aman este bowl. Puedes agregar salsa de miel-mostaza como dipping.",
    },
    "Filete de pechuga": {
        "titulo": "Pechuga Friko a la plancha con patacones y suero costeño",
        "tiempo": "30 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Filete de pechuga Friko",
            "2 plátanos verdes para patacones",
            "1/2 taza de suero costeño",
            "2 limones",
            "1 diente de ajo machacado",
            "1 cucharadita de orégano",
            "Aceite para freír",
            "Sal y pimienta al gusto",
            "Ensalada fresca para acompañar",
        ],
        "pasos": [
            "Sazonamos los filetes de pechuga Friko con ajo machacado, jugo de limón, orégano, sal y pimienta. Dejamos marinar 10 minutos.",
            "Calentamos una plancha o sartén a fuego medio-alto con un poco de aceite. Cocinamos los filetes 5-6 minutos por cada lado hasta que estén dorados y jugosos.",
            "Para los patacones: pelamos los plátanos y cortamos en rodajas gruesas. Freímos hasta dorar, aplastamos con un plataconera y volvemos a freír hasta que estén crocantes.",
            "Servimos la pechuga con los patacones calientes, suero costeño por encima y ensalada fresca.",
        ],
        "tip": "No aplastes demasiado la pechuga al cocinar para que quede jugosa por dentro.",
    },
    "Chorizo de pollo": {
        "titulo": "Choripán colombiano con guacamole y encurtido",
        "tiempo": "25 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Chorizo de pollo Friko",
            "4 panes de baguette o pan francés",
            "2 aguacates maduros",
            "1 cebolla morada en julianas",
            "2 limones",
            "1 tomate en cubos",
            "Cilantro fresco",
            "Ají al gusto",
            "Sal al gusto",
        ],
        "pasos": [
            "Cocinamos los chorizos de pollo Friko en una parrilla o sartén a fuego medio, dándoles vuelta cada 3-4 minutos hasta que estén dorados por todos los lados.",
            "Preparamos el guacamole: machacamos los aguacates con limón, tomate picado, cilantro, sal y un toque de ají.",
            "Para el encurtido: dejamos la cebolla morada en jugo de limón con sal por al menos 10 minutos.",
            "Cortamos los panes a lo largo, tostamos ligeramente en la misma parrilla.",
            "Armamos el choripán: pan, guacamole generoso, chorizo y cebolla encurtida.",
        ],
        "tip": "Pincha los chorizos con un tenedor antes de cocinarlos para que liberen grasa y queden más crocantes.",
    },
    "Lomitos de pechuga": {
        "titulo": "Lomitos Friko salteados con vegetales al wok estilo colombiano",
        "tiempo": "25 minutos",
        "dificultad": "Media",
        "ingredientes_base": [
            "{pkg} Lomitos de pechuga Friko",
            "1 pimentón rojo en julianas",
            "1 cebolla cabezona en plumas",
            "1 zanahoria en bastones finos",
            "2 cucharadas de salsa de soya",
            "1 cucharada de miel de panela",
            "1 diente de ajo picado",
            "Arroz blanco para acompañar",
            "Aceite vegetal",
        ],
        "pasos": [
            "Cortamos los Lomitos de pechuga Friko en tiras medianas y sazonamos con sal, pimienta y un toque de salsa de soya.",
            "En un wok o sartén grande a fuego alto, calentamos aceite y sellamos los lomitos por 3-4 minutos hasta dorar. Retiramos y reservamos.",
            "En el mismo wok, salteamos el ajo, la zanahoria y la cebolla por 2 minutos. Agregamos el pimentón y cocinamos 2 minutos más.",
            "Regresamos el pollo al wok, añadimos la salsa de soya restante y la miel de panela. Salteamos todo junto por 2 minutos.",
            "Servimos sobre arroz blanco caliente.",
        ],
        "tip": "La clave del wok es fuego alto y movimiento constante. No sobrecargues la sartén.",
    },
    "Bombones BBQ": {
        "titulo": "Bombones BBQ Friko con yuca frita y ají de aguacate",
        "tiempo": "25 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Bombones BBQ Friko",
            "500g de yuca pelada",
            "1 aguacate maduro",
            "1 ají dulce",
            "1 limón",
            "Cilantro fresco",
            "Aceite para freír",
            "Sal al gusto",
        ],
        "pasos": [
            "Preparamos los Bombones BBQ Friko en sartén u horno siguiendo las instrucciones del empaque.",
            "Cocinamos la yuca en agua con sal hasta que esté tierna (20 min). Escurrimos y freímos en aceite caliente hasta dorar.",
            "Para el ají de aguacate: licuamos el aguacate con ají dulce, jugo de limón, cilantro y sal hasta obtener una salsa cremosa.",
            "Servimos los bombones con la yuca frita y el ají de aguacate para dipping.",
        ],
        "tip": "Si la yuca queda fibrosa en el centro, retira esa parte antes de freír.",
    },
    "Mini chuzos": {
        "titulo": "Mini chuzos Friko con guasacaca y arepitas",
        "tiempo": "20 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Mini chuzos Friko",
            "6 arepitas pequeñas",
            "1 aguacate",
            "1/2 pimentón verde",
            "Cilantro y perejil",
            "1 limón",
            "1 ají dulce",
            "Sal y pimienta",
            "Aceite vegetal",
        ],
        "pasos": [
            "Cocinamos los Mini chuzos Friko en sartén o airfryer siguiendo las instrucciones del empaque.",
            "Preparamos la guasacaca: licuamos aguacate, pimentón, cilantro, perejil, ají dulce, limón y sal.",
            "Calentamos las arepitas en sartén o en la misma airfryer.",
            "Servimos los mini chuzos sobre las arepitas con guasacaca generosa.",
        ],
        "tip": "Perfectos para picar en reuniones. Ponlos en un plato grande con palillos para que todos se sirvan.",
    },
    "Alitas picantes": {
        "titulo": "Alitas picantes Friko con blue cheese casero y apio",
        "tiempo": "35 minutos",
        "dificultad": "Fácil",
        "ingredientes_base": [
            "{pkg} Alitas picantes Friko",
            "1/2 taza de crema de leche",
            "100g de queso azul (o queso campesino)",
            "2 tallos de apio en bastones",
            "Zanahoria en bastones",
            "Sal y pimienta",
        ],
        "pasos": [
            "Cocinamos las Alitas picantes Friko en horno a 200°C o airfryer siguiendo las instrucciones del empaque.",
            "Para la salsa blue cheese: mezclamos la crema de leche con el queso desmenuzado, sal y pimienta. Si usamos queso campesino, agregamos un toque de vinagre.",
            "Servimos las alitas con los bastones de apio y zanahoria y la salsa blue cheese para dipping.",
        ],
        "tip": "Si el picante es mucho, la salsa de queso es tu mejor aliada para equilibrar.",
    },
}

# Plantilla genérica como último recurso
PLANTILLA_GENERICA = {
    "titulo": "{producto} Friko con arroz colombiano y ensalada",
    "tiempo": "30 minutos",
    "dificultad": "Fácil",
    "ingredientes_base": [
        "{pkg} {producto}",
        "2 tazas de arroz blanco",
        "1 tomate maduro",
        "1 cebolla cabezona",
        "1 aguacate",
        "Limón, cilantro y sal al gusto",
    ],
    "pasos": [
        "Preparamos el {producto} siguiendo las instrucciones del empaque.",
        "Cocinamos el arroz blanco con sal.",
        "Preparamos una ensalada fresca con tomate, cebolla en julianas y aguacate en láminas, aliñada con limón y cilantro.",
        "Servimos el {producto} con el arroz y la ensalada. ¡Buen provecho!",
    ],
    "tip": "Acompaña con un jugo de lulo o maracuyá bien frío.",
}


def _ajustar_cantidades(ingredientes: List[str], num_personas: int) -> List[str]:
    """Ajusta las cantidades de ingredientes según el número de personas (base = 4)."""
    factor = num_personas / 4.0
    ajustados = []
    for ing in ingredientes:
        ing = ing.replace("{pkg}", f"{max(1, round(factor))} paquete(s) de")
        ajustados.append(ing)
    return ajustados


def _generar_plantilla(
    producto: str,
    preparacion: str,
    num_personas: int,
    ocasion: str,
) -> Dict:
    """Genera receta desde plantillas locales."""
    plantilla = PLANTILLAS.get(producto, PLANTILLA_GENERICA)

    titulo = plantilla["titulo"].replace("{producto}", producto)
    ingredientes = _ajustar_cantidades(
        [i.replace("{producto}", producto) for i in plantilla["ingredientes_base"]],
        num_personas,
    )
    pasos = [p.replace("{producto}", producto) for p in plantilla["pasos"]]

    return {
        "titulo": titulo,
        "tiempo": plantilla["tiempo"],
        "dificultad": plantilla["dificultad"],
        "porciones": f"{num_personas} personas",
        "ingredientes": ingredientes,
        "pasos": pasos,
        "tip": plantilla.get("tip", ""),
        "fuente": "generada",
    }


def formatear_receta_real(receta: Dict, num_personas: int) -> Dict:
    """Formatea una receta real del JSON para presentación consistente."""
    return {
        "titulo": receta["titulo"],
        "tiempo": receta.get("tiempo", "30 minutos"),
        "dificultad": "Media",
        "porciones": receta.get("porciones", f"{num_personas} porciones"),
        "ingredientes": receta.get("ingredientes", []),
        "pasos": receta.get("pasos", []),
        "imagen": receta.get("imagen", ""),
        "url": receta.get("url", ""),
        "tip": "",
        "fuente": "momentosfriko.com",
    }


def obtener_receta(
    producto: str,
    preparacion: str,
    num_personas: int,
    ocasion: str,
    recetas_db: List[Dict],
) -> Dict:
    """
    Función principal: busca receta real, si no la encuentra genera una.
    """
    # 1. Buscar en base real
    receta_real = buscar_receta_real(producto, recetas_db)
    if receta_real:
        return formatear_receta_real(receta_real, num_personas)

    # 2. Generar con IA o plantilla
    return generar_receta_ia(producto, preparacion, num_personas, ocasion)
