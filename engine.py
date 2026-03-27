"""
engine.py — Motor de recomendación basado en reglas.

Lógica: puntuar cada producto del catálogo según qué tan bien se ajusta
a los criterios del usuario (región, preparación, ocasión, personas).
Devolver los N mejores.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple

# ──────────────────────────────────────────────
#  Configuración de ocasiones
# ──────────────────────────────────────────────
OCASION_CONFIG = {
    "Comida cotidiana en casa": {
        "max_personas": 6,
        "categorias_preferidas": ["Pollo", "Pollo Procesado", "Carnes frias"],
        "peso_rapido": 1.5,  # Bonus para productos rápidos
    },
    "Reunión familiar": {
        "max_personas": 20,
        "categorias_preferidas": ["Pollo", "Pollo Procesado", "Carnes frias", "Mariscos"],
        "peso_cantidad": 1.5,  # Bonus para presentaciones grandes
    },
    "Evento o celebración": {
        "max_personas": 50,
        "categorias_preferidas": ["Pollo", "Mariscos", "Pescado", "Pescado Procesado"],
        "peso_premium": 1.3,  # Bonus para productos premium
    },
    "Comida rápida / snack": {
        "max_personas": 4,
        "categorias_preferidas": ["Pollo Procesado", "Pescado Procesado"],
        "peso_rapido": 2.0,
    },
    "Comida para niños": {
        "max_personas": 10,
        "categorias_preferidas": ["Pollo Procesado"],
        "peso_rapido": 1.5,
    },
}

OCASIONES = list(OCASION_CONFIG.keys())

# Productos considerados "rápidos" (listos en <20 min)
PRODUCTOS_RAPIDOS = {"Nuggets de pollo", "Bombones BBQ", "Dedos de merluza", "Mini chuzos"}

# Productos considerados "premium"
PRODUCTOS_PREMIUM = {
    "Filete de salmón premium", "Brochetas de langostino",
    "Camarón tití", "Filete de pechuga",
}


def recomendar(
    df: pd.DataFrame,
    region: str,
    preparacion: str,
    ocasion: str,
    num_personas: int,
    top_n: int = 3,
) -> List[Dict]:
    """
    Motor de recomendación principal.

    Puntúa cada producto y devuelve los top_n mejores como lista de dicts.
    """
    config = OCASION_CONFIG.get(ocasion, OCASION_CONFIG["Comida cotidiana en casa"])

    resultados = []

    for _, row in df.iterrows():
        score = 0.0

        # ── 1. FILTRO DE REGIÓN (obligatorio) ──
        if row["Región"] != region:
            continue

        # ── 2. MATCH DE PREPARACIÓN (+30 pts si coincide) ──
        prep_list = row["prep_list"]
        if preparacion in prep_list:
            score += 30
        else:
            score += 5  # Producto válido pero con preparación distinta

        # ── 3. MATCH DE CATEGORÍA POR OCASIÓN (+20 pts) ──
        cats_preferidas = config.get("categorias_preferidas", [])
        if row["Categoría"] in cats_preferidas:
            score += 20
        else:
            score += 5

        # ── 4. RANGO DE PORCIONES vs PERSONAS (+25 pts) ──
        p_min = row["porciones_min"]
        p_max = row["porciones_max"]

        if p_min <= num_personas <= p_max:
            score += 25  # Encaja perfecto
        elif num_personas <= p_max * 1.5:
            score += 15  # Razonablemente cerca
        elif num_personas > p_max * 2:
            score += 5   # Necesitaría múltiples paquetes
        else:
            score += 10

        # ── 5. BONUS POR OCASIÓN ──
        if config.get("peso_rapido") and row["Producto"] in PRODUCTOS_RAPIDOS:
            score *= config["peso_rapido"]

        if config.get("peso_premium") and row["Producto"] in PRODUCTOS_PREMIUM:
            score *= config["peso_premium"]

        if config.get("peso_cantidad"):
            # Bonus para presentaciones grandes
            if p_max >= 8:
                score *= config["peso_cantidad"]

        resultados.append({
            "sku": row["SKU"],
            "marca": row["Marca"],
            "producto": row["Producto"],
            "descripcion": row["Descripción"],
            "presentacion": row["Presentación"],
            "categoria": row["Categoría"],
            "region": row["Región"],
            "tipo_preparacion": row["Tipo_Preparación"],
            "porciones_min": p_min,
            "porciones_max": p_max,
            "score": round(score, 1),
        })

    # Ordenar por score descendente y deduplicar por nombre de producto
    resultados.sort(key=lambda x: x["score"], reverse=True)

    # Deduplicar: quedarse con el mejor score por producto
    seen = set()
    deduped = []
    for r in resultados:
        if r["producto"] not in seen:
            seen.add(r["producto"])
            deduped.append(r)

    return deduped[:top_n]


def calcular_cantidad_paquetes(producto: Dict, num_personas: int) -> str:
    """Sugiere cuántos paquetes comprar."""
    p_max = producto["porciones_max"]
    if p_max <= 0:
        return "1 paquete"
    paquetes = max(1, -(-num_personas // p_max))  # Ceil division
    if paquetes == 1:
        return "1 paquete"
    return f"{paquetes} paquetes"


def get_ocasiones() -> List[str]:
    """Lista de ocasiones disponibles."""
    return OCASIONES
