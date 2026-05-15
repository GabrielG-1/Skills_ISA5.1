import json
from typing import List, Dict, Any

def generar_tabla_io(instrumentos: List[Dict[str, Any]], margen_reserva: float = 0.20) -> Dict[str, Any]:
    """
    Toma una lista de equipos básicos y genera la ingeniería de detalle de la tabla de I/O
    aplicando la norma ISA-5.1 y determinando los tipos de señales industriales.
    """
    # Diccionario de emparejamiento de ingeniería (Tipos de equipos -> Señales requeridas)
    MAPEO_INGENIERIA = {
        "bomba": [
            {"sufijo": "BBA", "descripcion": "Comando de Marcha/Parada", "tipo_senal": "DO"},
            {"sufijo": "FB", "descripcion": "Feedback de Estado (Run)", "tipo_senal": "DI"},
            {"sufijo": "FLT", "descripcion": "Falla de Proteccion (Termico)", "tipo_senal": "DI"}
        ],
        "bomba_vfd": [
            {"sufijo": "P", "descripcion": "Comando de Marcha/Parada", "tipo_senal": "DO"},
            {"sufijo": "FB", "descripcion": "Feedback de Estado (Run)", "tipo_senal": "DI"},
            {"sufijo": "HZ", "descripcion": "Consigna de Frecuencia (Velocidad)", "tipo_senal": "AO"},
            {"sufijo": "AI_HZ", "descripcion": "Lectura de Frecuencia Real", "tipo_senal": "AI"},
            {"sufijo": "FLT", "descripcion": "Falla General Variador", "tipo_senal": "DI"}
        ],
        "sensor_temperatura": [
            {"sufijo": "TT", "descripcion": "Transmisor de Temperatura (4-20mA)", "tipo_senal": "AI"}
        ],
        "sensor_presion": [
            {"sufijo": "PT", "descripcion": "Transmisor de Presion (4-20mA)", "tipo_senal": "AI"}
        ],
        "valvula_on_off": [
            {"sufijo": "YV", "descripcion": "Comando Apertura/Cierre Solenoide", "tipo_senal": "DO"},
            {"sufijo": "ZSC", "descripcion": "Sensor Final de Carrera - Cerrada", "tipo_senal": "DI"},
            {"sufijo": "ZSO", "descripcion": "Sensor Final de Carrera - Abierta", "tipo_senal": "DI"}
        ],
        "agitador": [
            {"sufijo": "AG", "descripcion": "Comando de Marcha Agitador", "tipo_senal": "DO"},
            {"sufijo": "FB", "descripcion": "Feedback de Estado Agitador", "tipo_senal": "DI"}
        ]
    }

    tabla_final_io = []
    conteos = {"DI": 0, "DO": 0, "AI": 0, "AO": 0}
    indices_tags = {}

    for inst in instrumentos:
        tipo = inst.get("tipo", "").lower()
        zona = inst.get("zona", "01") # Ej: Filtro, Macerador, etc.
        
        if tipo not in MAPEO_INGENIERIA:
            continue
            
        # Controlar el índice correlativo por tipo de instrumento en la zona
        if tipo not in indices_tags:
            indices_tags[tipo] = 1
        else:
            indices_tags[tipo] += 1
            
        correlativo = f"{indices_tags[tipo]:02d}"
        
        # Generar las señales asociadas a este equipo
        for senal in MAPEO_INGENIERIA[tipo]:
            # Construcción del Tag bajo norma ISA-5.1 simplificada (Ej: PIT-01, P-01_FB)
            if "_" in senal["sufijo"] or senal["sufijo"] in ["FB", "FLT", "HZ", "AI_HZ", "ZSC", "ZSO"]:
                # Es una señal subordinada a un equipo principal (ej: Bomba P-01)
                tag_principal = "P" if "bomba" in tipo else "AG" if tipo == "agitador" else "YV"
                tag_isa = f"{tag_principal}-{correlativo}_{senal['sufijo']}"
            else:
                # Es un instrumento directo (ej: PIT-01, TT-01)
                tag_isa = f"{senal['sufijo']}-{correlativo}"
            
            registro_io = {
                "tag": tag_isa,
                "zona": zona,
                "descripcion": f"{inst.get('nombre', 'Equipo')} - {senal['descripcion']}",
                "tipo_senal": senal["tipo_senal"],
                "direccion_sugerida": "" # Espacio para mapear al PLC posteriormente
            }
            
            tabla_final_io.append(registro_io)
            conteos[senal["tipo_senal"]] += 1

    # Calcular el dimensionamiento físico de hardware + Reserva Técnica
    resumen_hardware = {}
    for tipo_s, cantidad in conteos.items():
        cantidad_con_reserva = int(cantidad * (1 + margen_reserva)) + (1 if (cantidad * (1 + margen_reserva)) % 1 > 0 else 0)
        resumen_hardware[tipo_s] = {
            "canales_netos": cantidad,
            "canales_con_reserva": cantidad_con_reserva,
            "reserva_fisica_disponible": cantidad_con_reserva - cantidad
        }

    return {
        "status": "success",
        "tabla_io": tabla_final_io,
        "resumen_canales_hardware": resumen_hardware
    }

# Código de prueba local para verificar compatibilidad de datos
if __name__ == "__main__":
    # Datos de ejemplo que enviaría tu interfaz de Antigravity
    input_usuario = [
        {"nombre": "Bomba de Recirculación Filtro", "tipo": "bomba_vfd", "zona": "01"},
        {"nombre": "Transmisor de Presión Filtro", "tipo": "sensor_presion", "zona": "01"},
        {"nombre": "Agitador Macerador", "tipo": "agitador", "zona": "01"},
        {"nombre": "Válvula de Llenado", "tipo": "valvula_on_off", "zona": "02"}
    ]
    
    resultado = generar_tabla_io(input_usuario)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))