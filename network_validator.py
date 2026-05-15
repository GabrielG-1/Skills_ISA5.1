import json
from typing import List, Dict

def validar_arquitectura_red(dispositivos: List[Dict[str, str]], subred: str = "192.168.0") -> Dict[str, Any]:
    """
    Verifica conflictos de IP y sugiere topología para Modbus TCP / Profinet.
    """
    topologia = []
    conflictos = []
    ips_ocupadas = set()

    for i, dev in enumerate(dispositivos):
        nombre = dev.get("nombre", f"Dispositivo_{i}")
        protocolo = dev.get("protocolo", "Profinet") # Default
        ip_sugerida = f"{subred}.{10 + i}"
        
        if ip_sugerida in ips_ocupadas:
            conflictos.append(f"Conflicto de IP en: {ip_sugerida}")
        
        ips_ocupadas.add(ip_sugerida)
        
        topologia.append({
            "dispositivo": nombre,
            "protocolo_principal": protocolo,
            "ip_asignada": ip_sugerida,
            "puerto_estandar": 502 if protocolo.lower() == "modbus" else 102
        })

    return {
        "configuracion_red_valida": len(conflictos) == 0,
        "mapa_de_red": topologia,
        "alertas": conflictos,
        "recomendacion_hardware_red": "Se requiere Switch Industrial No Administrable de al menos 5 puertos."
    }