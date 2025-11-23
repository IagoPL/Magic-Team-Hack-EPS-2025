"""
Procesa y transforma los datos recopilados en métricas normalizadas
para el motor de recomendación
"""
from typing import Dict, List
from src.utils import load_json, save_json, get_data_path, normalize_list


class DataProcessor:
    """Procesa datos raw y los convierte en métricas para el motor de recomendación"""

    def process_for_recommendation(self) -> List[Dict]:
        """
        Procesa los datos combinados y calcula las métricas necesarias
        para cada barrio según las necesidades de los clientes
        """
        # Cargar datos combinados
        merged_data = load_json(get_data_path('merged_neighborhood_data.json'))

        if not merged_data:
            raise FileNotFoundError("No se encontraron datos combinados. Ejecuta data_collector.py primero.")

        processed_data = []

        # Extraer todos los valores para normalización
        all_values = {
            'median_income': [],
            'population_density': [],
            'park_count': [],
            'restaurant_count': [],
            'public_transport_coverage': [],
            'public_transport_stations': [],
            'school_count': []
        }

        for nb in merged_data:
            for key in all_values.keys():
                if key in nb:
                    all_values[key].append(nb[key])

        # Normalizar cada métrica
        normalized_ranges = {}
        for metric, values in all_values.items():
            if values:
                normalized_ranges[metric] = {
                    'min': min(values),
                    'max': max(values),
                    'normalized': normalize_list(values)
                }

        # Procesar cada barrio
        for i, nb in enumerate(merged_data):
            processed_nb = {
                'name': nb['name'],
                'lat': nb['lat'],
                'lon': nb['lon'],
                'zipcode': nb.get('zipcode', '')
            }

            # Calcular métricas para cada cliente

            # Métricas generales (normalizadas 0-1)
            income_norm = normalized_ranges['median_income']['normalized'][i] if i < len(normalized_ranges['median_income']['normalized']) else 0.5
            pop_density_norm = normalized_ranges['population_density']['normalized'][i] if i < len(normalized_ranges['population_density']['normalized']) else 0.5
            parks_norm = normalized_ranges['park_count']['normalized'][i] if i < len(normalized_ranges['park_count']['normalized']) else 0.5
            restaurants_norm = normalized_ranges['restaurant_count']['normalized'][i] if i < len(normalized_ranges['restaurant_count']['normalized']) else 0.5
            transport_norm = normalized_ranges['public_transport_coverage']['normalized'][i] if i < len(normalized_ranges['public_transport_coverage']['normalized']) else 0.5
            transport_stations_norm = normalized_ranges['public_transport_stations']['normalized'][i] if i < len(normalized_ranges['public_transport_stations']['normalized']) else 0.5

            # Mapear a métricas específicas de clientes

            # Daenerys
            processed_nb['density_parks'] = parks_norm
            processed_nb['ratio_local_businesses'] = 0.7  # Simplificado (necesitaría datos reales)
            processed_nb['community_organizations'] = parks_norm * 0.8  # Proxy
            processed_nb['dog_friendly_parks'] = parks_norm * 0.9  # Proxy

            # Cersei
            processed_nb['median_income'] = income_norm
            processed_nb['low_crime_rate'] = income_norm * 0.9  # Proxy (necesitaría datos reales de crimen)
            processed_nb['elite_schools'] = (normalized_ranges['school_count']['normalized'][i] if i < len(normalized_ranges['school_count']['normalized']) else 0.5) * income_norm
            processed_nb['high_rent_price'] = income_norm

            # Bran
            processed_nb['accessibility_score'] = 0.7  # Simplificado (necesitaría datos OSM de accesibilidad)
            processed_nb['quietness_score'] = 1.0 - pop_density_norm  # Menos densidad = más quieto
            processed_nb['internet_coverage'] = income_norm  # Proxy
            processed_nb['low_population_density'] = 1.0 - pop_density_norm

            # Jon Snow
            processed_nb['low_rent_price'] = 1.0 - income_norm  # Menos ingresos = rentas más bajas
            processed_nb['cultural_diversity'] = 0.6  # Simplificado
            processed_nb['proximity_nature'] = parks_norm
            processed_nb['community_density'] = pop_density_norm * 0.7  # Densidad media-alta

            # Arya
            processed_nb['public_transport_coverage'] = transport_norm
            processed_nb['high_population_density'] = pop_density_norm
            processed_nb['large_neighborhood'] = 0.8 if nb.get('total_population', 0) > 20000 else 0.4
            processed_nb['activity_centers'] = (restaurants_norm + transport_stations_norm) / 2

            # Tyrion
            processed_nb['cultural_venues'] = restaurants_norm * 0.6  # Proxy (necesitaría datos de museos, etc.)
            processed_nb['restaurant_density'] = restaurants_norm
            processed_nb['walkability_score'] = (restaurants_norm + transport_stations_norm + parks_norm) / 3
            processed_nb['public_transport_access'] = transport_norm

            processed_data.append(processed_nb)

        # Guardar datos procesados
        save_json(processed_data, get_data_path('processed_neighborhood_data.json'))
        print(f"Datos procesados guardados ({len(processed_data)} barrios)")

        return processed_data


if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_for_recommendation()

