"""
data_loader.py — Carga y normalización de datos del catálogo Friko y recetas.
"""

import json
import os
import re
import pandas as pd
from typing import List, Dict, Optional

# ──────────────────────────────────────────────
#  Rutas por defecto
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "BD_base.xlsx")
RECIPES_PATH = os.path.join(BASE_DIR, "data", "recetas_friko.json")


# ──────────────────────────────────────────────
#  Mapeo de preparación → categorías simplificadas
# ──────────────────────────────────────────────
PREP_MAP = {
    "Parrilla / Sartén": ["Parrilla", "Sartén"],
    "Sartén / Airfryer": ["Sartén", "Airfryer"],
    "Horno / Airfryer": ["Horno", "Airfryer"],
    "Sartén / Horno": ["Sartén", "Horno"],
    "Sartén / Plancha": ["Sartén", "Plancha"],
    "Sartén / Wok": ["Sartén", "Wok"],
    "Sartén / Salteado": ["Sartén", "Salteado"],
    "Sartén / Parrilla": ["Sartén", "Parrilla"],
    "Plancha / Horno": ["Plancha", "Horno"],
    "Horno / Sartén": ["Horno", "Sartén"],
    "Parrilla": ["Parrilla"],
}


def load_catalog(path: str = CATALOG_PATH) -> pd.DataFrame:
    """Lee el catálogo de productos desde el archivo Excel."""
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]

    # Normalizar columnas clave
    df["Región"] = df["Región"].str.strip()
    df["Tipo_Preparación"] = df["Tipo_Preparación"].str.strip()
    df["Producto"] = df["Producto"].str.strip()
    df["Marca"] = df["Marca"].str.strip()

    # Extraer porciones estimadas del campo Presentación
    df["porciones_min"], df["porciones_max"] = zip(
        *df["Presentación"].apply(_estimate_servings)
    )

    # Expandir tipos de preparación a lista
    df["prep_list"] = df["Tipo_Preparación"].map(
        lambda x: PREP_MAP.get(x, [x])
    )

    return df


def _estimate_servings(presentacion: str) -> tuple:
    """
    Estima rango de porciones a partir de la presentación.
    Ejemplo: '10 und / 1.900 g' → (4, 10)
             '900 g' → (2, 4)
    """
    presentacion = str(presentacion)

    # Si tiene unidades, usar como referencia
    und_match = re.search(r"(\d+)\s*und", presentacion)
    if und_match:
        und = int(und_match.group(1))
        return (max(1, und // 3), und)

    # Si solo tiene gramos
    g_match = re.search(r"([\d.,]+)\s*g", presentacion.replace(".", ""))
    if g_match:
        grams = int(g_match.group(1).replace(",", "").replace(".", ""))
        # ~250g por porción como referencia
        portions = max(1, grams // 250)
        return (max(1, portions // 2), portions + 1)

    return (2, 6)  # Fallback


def load_recipes(path: str = RECIPES_PATH) -> List[Dict]:
    """Lee las recetas desde el archivo JSON."""
    with open(path, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    # Normalizar campos vacíos
    for r in recipes:
        r["tiempo"] = r.get("tiempo", "").strip() or "30 minutos"
        r["porciones"] = r.get("porciones", "").strip() or "4 porciones"
        r["ingredientes"] = r.get("ingredientes", [])
        r["pasos"] = r.get("pasos", [])
        r["imagen"] = r.get("imagen", "")
        r["titulo"] = r.get("titulo", "").strip()
        # Extraer keywords para matching
        r["_keywords"] = _extract_keywords(r["titulo"])

    return recipes


def _extract_keywords(titulo: str) -> List[str]:
    """Extrae palabras clave del título de la receta para matching."""
    titulo_lower = titulo.lower()
    keywords = []
    product_terms = {
        "pechuga": ["pechuga", "filete"],
        "alitas": ["alitas", "ala"],
        "nuggets": ["nugget", "nuggets"],
        "chuzos": ["chuzo", "chuzos", "brocheta"],
        "chorizo": ["chorizo"],
        "lomitos": ["lomito", "lomitos"],
        "bombones": ["bombón", "bombones"],
        "hamburguesa": ["hamburguesa"],
        "salmón": ["salmón", "salmon"],
        "camarón": ["camarón", "camaron"],
        "merluza": ["merluza"],
        "langostino": ["langostino"],
        "medallones": ["medallón", "medallones"],
    }
    for product, terms in product_terms.items():
        for t in terms:
            if t in titulo_lower:
                keywords.append(product)
                break
    return keywords


def get_unique_regions(df: pd.DataFrame) -> List[str]:
    """Devuelve regiones únicas ordenadas."""
    return sorted(df["Región"].unique().tolist())


def get_unique_preparations(df: pd.DataFrame) -> List[str]:
    """Devuelve tipos de preparación simplificados únicos."""
    all_preps = set()
    for preps in df["prep_list"]:
        all_preps.update(preps)
    return sorted(all_preps)


def get_unique_categories(df: pd.DataFrame) -> List[str]:
    """Devuelve categorías únicas."""
    return sorted(df["Categoría"].unique().tolist())
