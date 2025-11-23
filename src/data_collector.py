"""
Script para descargar y procesar datos de APIs externas
APIs: U.S. Census Bureau, Overpass (OpenStreetMap)
"""
import requests
import json
import time
from typing import Dict, List
from src.utils import load_json, save_json, get_data_path


class DataCollector:
    """Recolecta datos de diferentes APIs y los guarda en cache"""
    
    def __init__(self):
        self.neighborhoods = load_json('config/neighborhoods.json')['neighborhoods']
        # API Key del Census (puede ser 'demo' para pruebas, pero mejor obtener una real)
        self.census_api_key = "demo"  # TODO: Reemplazar con tu API key real
    
    def collect_census_data(self) -> Dict:
        """
        Descarga datos del U.S. Census Bureau para los barrios de LA
        Datos: ingresos, población, edad, densidad
        """
        print("Recopilando datos del Census Bureau...")
        
        # Endpoint del Census API
        base_url = "https://api.census.gov/data/2021/acs/acs5"
        
        # Variables que queremos obtener
        variables = {
            "B19013_001E": "median_household_income",  # Ingresos medianos
            "B01003_001E": "total_population",  # Población total
            "B08301_021E": "public_transport_commuters",  # Usuarios de transporte público
            "B08301_001E": "total_commuters"  # Total de commuters
        }
        
        census_data = {}
        
        for nb in self.neighborhoods:
            zipcode = nb['zipcode']
            print(f"  Procesando {nb['name']} (ZIP: {zipcode})...")
            
            try:
                # El Census API usa códigos de tracto, pero podemos buscar por ZIP
                # Nota: Esto es simplificado. En producción, necesitarías mapear ZIPs a tractos
                params = {
                    "get": ",".join(variables.keys()),
                    "for": f"zip code tabulation area:{zipcode}",
                    "key": self.census_api_key
                }
                
                response = requests.get(base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1:  # Si hay datos (header + data)
                        values = data[1]
                        nb_data = {}
                        for i, var in enumerate(variables.keys()):
                            nb_data[variables[var]] = int(values[i]) if values[i] else 0
                        
                        census_data[nb['name']] = nb_data
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Error obteniendo datos para {nb['name']}: {e}")
                census_data[nb['name']] = {}
        
        # Guardar en cache
        save_json(census_data, get_data_path('census_data.json'))
        print(f"Datos del Census guardados en cache ({len(census_data)} barrios)")
        
        return census_data
    
    def collect_osm_data(self) -> Dict:
        """
        Descarga datos de OpenStreetMap usando Overpass API
        Datos: parques, restaurantes, transporte, amenidades
        """
        print("Recopilando datos de OpenStreetMap (Overpass API)...")
        
        overpass_url = "https://overpass-api.de/api/interpreter"
        osm_data = {}
        
        for nb in self.neighborhoods:
            name = nb['name']
            lat = nb['lat']
            lon = nb['lon']
            
            print(f"  Procesando {name}...")
            
            # Radio de búsqueda en km (convertido a grados, aprox)
            radius = 0.01  # ~1km
            
            # Query Overpass para obtener amenidades dentro del radio
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="restaurant"](around:500,{lat},{lon});
              node["amenity"="park"](around:500,{lat},{lon});
              node["leisure"="park"](around:500,{lat},{lon});
              node["public_transport"="station"](around:500,{lat},{lon});
              node["amenity"="school"](around:500,{lat},{lon});
              node["amenity"="cafe"](around:500,{lat},{lon});
            );
            out count;
            """
            
            try:
                response = requests.post(overpass_url, data={'data': query}, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get('elements', [])
                    
                    # Contar por tipo
                    counts = {
                        'restaurants': 0,
                        'parks': 0,
                        'public_transport': 0,
                        'schools': 0,
                        'cafes': 0
                    }
                    
                    for element in elements:
                        tags = element.get('tags', {})
                        amenity = tags.get('amenity', '')
                        leisure = tags.get('leisure', '')
                        public_transport = tags.get('public_transport', '')
                        
                        if amenity == 'restaurant':
                            counts['restaurants'] += 1
                        elif amenity == 'park' or leisure == 'park':
                            counts['parks'] += 1
                        elif public_transport == 'station' or amenity == 'bus_station':
                            counts['public_transport'] += 1
                        elif amenity == 'school':
                            counts['schools'] += 1
                        elif amenity == 'cafe':
                            counts['cafes'] += 1
                    
                    osm_data[name] = counts
                else:
                    print(f"    Error HTTP {response.status_code} para {name}")
                    osm_data[name] = {}
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"    Error obteniendo datos OSM para {name}: {e}")
                osm_data[name] = {}
        
        # Guardar en cache
        save_json(osm_data, get_data_path('osm_data.json'))
        print(f"Datos de OSM guardados en cache ({len(osm_data)} barrios)")
        
        return osm_data
    
    def merge_neighborhood_data(self) -> List[Dict]:
        """
        Combina todos los datos recopilados en un formato unificado
        """
        print("Combinando datos de todas las fuentes...")
        
        census_data = load_json(get_data_path('census_data.json')) if self._file_exists(get_data_path('census_data.json')) else {}
        osm_data = load_json(get_data_path('osm_data.json')) if self._file_exists(get_data_path('osm_data.json')) else {}
        
        merged_data = []
        
        for nb in self.neighborhoods:
            name = nb['name']
            
            # Inicializar datos del barrio
            nb_data = {
                'name': name,
                'lat': nb['lat'],
                'lon': nb['lon'],
                'zipcode': nb['zipcode']
            }
            
            # Agregar datos del Census
            if name in census_data:
                census = census_data[name]
                nb_data.update({
                    'median_income': census.get('median_household_income', 0),
                    'total_population': census.get('total_population', 0),
                    'public_transport_commuters': census.get('public_transport_commuters', 0),
                    'total_commuters': census.get('total_commuters', 1)
                })
                
                # Calcular métricas derivadas
                pop_density = nb_data['total_population'] / 1.0  # Simplificado (necesitarías área)
                nb_data['population_density'] = pop_density
                
                # Ratio de transporte público
                transport_ratio = nb_data['public_transport_commuters'] / max(nb_data['total_commuters'], 1)
                nb_data['public_transport_coverage'] = transport_ratio
            else:
                # Valores por defecto si no hay datos
                nb_data.update({
                    'median_income': 50000,
                    'total_population': 10000,
                    'population_density': 2000,
                    'public_transport_coverage': 0.2
                })
            
            # Agregar datos de OSM
            if name in osm_data:
                osm = osm_data[name]
                nb_data.update({
                    'restaurant_count': osm.get('restaurants', 0),
                    'park_count': osm.get('parks', 0),
                    'public_transport_stations': osm.get('public_transport', 0),
                    'school_count': osm.get('schools', 0),
                    'cafe_count': osm.get('cafes', 0)
                })
            else:
                # Valores por defecto
                nb_data.update({
                    'restaurant_count': 10,
                    'park_count': 2,
                    'public_transport_stations': 3,
                    'school_count': 2,
                    'cafe_count': 5
                })
            
            merged_data.append(nb_data)
        
        # Guardar datos combinados
        save_json(merged_data, get_data_path('merged_neighborhood_data.json'))
        print(f"Datos combinados guardados ({len(merged_data)} barrios)")
        
        return merged_data
    
    def _file_exists(self, filepath: str) -> bool:
        """Verifica si un archivo existe"""
        import os
        return os.path.exists(filepath)
    
    def collect_all(self):
        """Recopila todos los datos"""
        print("=== INICIANDO RECOPILACIÓN DE DATOS ===\n")
        
        # Recopilar datos
        self.collect_census_data()
        self.collect_osm_data()
        
        # Combinar
        merged = self.merge_neighborhood_data()
        
        print("\n=== RECOPILACIÓN COMPLETADA ===")
        return merged


if __name__ == "__main__":
    collector = DataCollector()
    collector.collect_all()

