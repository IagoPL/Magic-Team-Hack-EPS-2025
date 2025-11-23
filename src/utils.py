"""
Utilidades generales para el proyecto
"""
import json
import os
from typing import Dict, List, Any


def load_json(filepath: str) -> Dict | List:
    """Carga un archivo JSON y retorna su contenido"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict | List, filepath: str) -> None:
    """Guarda datos en un archivo JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normaliza un valor al rango [0, 1]
    Si min == max, retorna 0.5
    """
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def normalize_list(values: List[float]) -> List[float]:
    """
    Normaliza una lista de valores al rango [0, 1]
    """
    if not values:
        return []
    
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        return [0.5] * len(values)
    
    return [(v - min_val) / (max_val - min_val) for v in values]


def get_project_root() -> str:
    """Retorna la ruta raíz del proyecto"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_path(filename: str) -> str:
    """Retorna la ruta completa de un archivo en config/"""
    return os.path.join(get_project_root(), 'config', filename)


def get_data_path(filename: str, subfolder: str = 'cache') -> str:
    """Retorna la ruta completa de un archivo en data/"""
    return os.path.join(get_project_root(), 'data', subfolder, filename)

