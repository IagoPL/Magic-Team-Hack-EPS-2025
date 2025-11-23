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


def get_metric_display_name(metric_key: str) -> str:
    """
    Retorna el nombre legible de una métrica en catalán
    """
    metric_names = {
        # Daenerys
        'density_parks': 'Densitat de Parcs',
        'ratio_local_businesses': 'Percentatge de Negocis Locals',
        'community_organizations': 'Organitzacions Comunitàries',
        'dog_friendly_parks': 'Parcs Adaptats per a Gossos',
        
        # Cersei
        'median_income': 'Ingressos Mitjans',
        'low_crime_rate': 'Baixa Taxa de Criminalitat',
        'elite_schools': 'Presència de Col·legis d\'Elit',
        'high_rent_price': 'Alta Qualitat Residencial',
        
        # Bran
        'accessibility_score': 'Accessibilitat',
        'quietness_score': 'Tranquilitat i Silenci',
        'internet_coverage': 'Cobertura d\'Internet d\'Alta Velocitat',
        'low_population_density': 'Baixa Densitat de Població',
        
        # Jon Snow
        'low_rent_price': 'Preus de Lloguer Accessibles',
        'cultural_diversity': 'Diversitat Cultural',
        'proximity_nature': 'Proximitat a Zones Naturals',
        'community_density': 'Densitat Comunitària',
        
        # Arya
        'public_transport_coverage': 'Cobertura de Transport Públic',
        'high_population_density': 'Alta Densitat de Població',
        'large_neighborhood': 'Barri Extens',
        'activity_centers': 'Centres d\'Activitat',
        
        # Tyrion
        'cultural_venues': 'Llocs Culturals',
        'restaurant_density': 'Densitat de Restaurants',
        'walkability_score': 'Walkability (Caminabilitat)',
        'public_transport_access': 'Accés al Transport Públic'
    }
    
    return metric_names.get(metric_key, metric_key.replace('_', ' ').title())


def get_metric_description(metric_key: str) -> str:
    """
    Retorna una descripción breve de la métrica en catalán
    """
    descriptions = {
        'density_parks': 'Nombre de parcs per àrea',
        'ratio_local_businesses': 'Percentatge de negocis locals vs cadena',
        'community_organizations': 'Presència d\'organitzacions comunitàries',
        'dog_friendly_parks': 'Parcs amb facilitats per a gossos',
        'median_income': 'Ingressos medians del barri',
        'low_crime_rate': 'Baixa incidència criminal',
        'elite_schools': 'Presència de col·legis prestigiosos',
        'high_rent_price': 'Zona residencial d\'alta qualitat',
        'accessibility_score': 'Facilitat d\'accés i mobilitat',
        'quietness_score': 'Nivell de soroll ambiental',
        'internet_coverage': 'Cobertura de fibra òptica i internet ràpid',
        'low_population_density': 'Menys població per unitat d\'àrea',
        'low_rent_price': 'Preus de lloguer assequibles',
        'cultural_diversity': 'Diversitat ètnica i cultural',
        'proximity_nature': 'Accés a zones verdes i naturals',
        'community_density': 'Fortaliment de l\'espai comunitari',
        'public_transport_coverage': 'Cobertura de metro, bus, etc.',
        'high_population_density': 'Alta densitat de població',
        'large_neighborhood': 'Barri amb gran extensió territorial',
        'activity_centers': 'Proximitat a centres comercials i socials',
        'cultural_venues': 'Museus, teatre, galeries d\'art',
        'restaurant_density': 'Nombre de restaurants per àrea',
        'walkability_score': 'Facilitat per caminar a peu',
        'public_transport_access': 'Facilitat d\'accés al transport públic'
    }
    
    return descriptions.get(metric_key, 'Mètrica de qualitat del barri')

