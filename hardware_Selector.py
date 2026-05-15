import json
from typing import Dict, Any

def cotizar_hardware_automatizacion(resumen_canales: Dict[str, Any], moneda: str = "USD") -> Dict[str, Any]:
    """
    Sugiere controladores y módulos de expansión basados en la cantidad de I/O necesarias.
    """
    # Precios referenciales estimados (Mercado Industrial 2026)
    PRECIOS = {
        "PLC_BASIC": 450,    # Ej: S7-1200 CPU 1214C
        "MOD_DI_8": 120,     # Módulo 8 Entradas Digitales
        "MOD_DO_8": 140,     # Módulo 8 Salidas Digitales
        "MOD_AI_4": 210,     # Módulo 4 Entradas Analógicas
        "MOD_AO_2": 230      # Módulo 2 Salidas Analógicas
    }

    canales = resumen_canales
    configuracion = []
    costo_total = 0

    # Lógica de selección básica
    # 1. CPU Base (asumimos que incluye algunas I/O)
    configuracion.append({"item": "CPU Principal (Controlador)", "costo": PRECIOS["PLC_BASIC"]})
    costo_total += PRECIOS["PLC_BASIC"]

    # 2. Cálculo de módulos adicionales basados en la reserva técnica
    # Digitales
    if canales.get("DI", {}).get("canales_con_reserva", 0) > 14: # La CPU trae ~14
        num_mods = (canales["DI"]["canales_con_reserva"] - 14) // 8 + 1
        configuracion.append({"item": f"Módulo Expansión DI (x{num_mods})", "costo": PRECIOS["MOD_DI_8"] * num_mods})
        costo_total += PRECIOS["MOD_DI_8"] * num_mods

    # Analógicas (Las CPUs básicas suelen traer solo 2 AI de 0-10V, para 4-20mA se requiere módulo)
    if canales.get("AI", {}).get("canales_con_reserva", 0) > 0:
        num_mods = canales["AI"]["canales_con_reserva"] // 4 + 1
        configuracion.append({"item": f"Módulo Expansión AI (x{num_mods})", "costo": PRECIOS["MOD_AI_4"] * num_mods})
        costo_total += PRECIOS["MOD_AI_4"] * num_mods

    return {
        "presupuesto_estimado": f"{costo_total} {moneda}",
        "lista_materiales_provisoria": configuracion,
        "nota": "Los precios son referenciales. No incluye gabinete, fuentes ni protecciones eléctricas."
    }