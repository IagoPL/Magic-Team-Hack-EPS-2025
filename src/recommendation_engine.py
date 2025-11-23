"""
Motor de recomendación de barrios
Implementa scoring ponderado para recomendar barrios según las necesidades de cada cliente
"""
from typing import Dict, List, Any
import pandas as pd
from src.utils import normalize_value, normalize_list, load_json


class RecommendationEngine:
    """Motor de recomendación que calcula scores para cada barrio según un cliente"""
    
    def __init__(self):
        self.neighborhoods = load_json('config/neighborhoods.json')['neighborhoods']
        self.clients = load_json('config/clients.json')
    
    def calculate_score(self, neighborhood_data: Dict, client_id: str) -> float:
        """
        Calcula el score ponderado para un barrio dado un cliente
        
        Args:
            neighborhood_data: Diccionario con las métricas del barrio
            client_id: ID del cliente (daenerys, cersei, etc.)
        
        Returns:
            Score total (0-1)
        """
        if client_id not in self.clients:
            raise ValueError(f"Cliente {client_id} no encontrado")
        
        client_config = self.clients[client_id]
        weights = client_config['weights']
        
        score = 0.0
        
        # Calcular score ponderado
        for metric, weight in weights.items():
            metric_value = neighborhood_data.get(metric, 0.0)
            
            # Si la métrica no existe, usar 0 (puede mejorarse normalizando todos los barrios primero)
            if metric_value is None:
                metric_value = 0.0
            
            score += metric_value * weight
        
        return min(max(score, 0.0), 1.0)  # Asegurar que esté entre 0 y 1
    
    def get_recommendations(self, neighborhoods_data: List[Dict], client_id: str, top_n: int = 5) -> List[Dict]:
        """
        Obtiene las top N recomendaciones para un cliente
        
        Args:
            neighborhoods_data: Lista de diccionarios con datos de cada barrio
            client_id: ID del cliente
            top_n: Número de recomendaciones a retornar
        
        Returns:
            Lista de barrios ordenados por score descendente, cada uno con su score
        """
        # Normalizar todas las métricas primero
        normalized_data = self._normalize_metrics(neighborhoods_data, client_id)
        
        # Calcular scores
        recommendations = []
        for nb_data in normalized_data:
            score = self.calculate_score(nb_data, client_id)
            recommendations.append({
                **nb_data,
                'score': score
            })
        
        # Ordenar por score descendente
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _normalize_metrics(self, neighborhoods_data: List[Dict], client_id: str) -> List[Dict]:
        """
        Normaliza todas las métricas de todos los barrios al rango [0, 1]
        Esto asegura que el scoring sea justo
        """
        if not neighborhoods_data:
            return []
        
        client_config = self.clients[client_id]
        weights = client_config['weights']
        
        # Obtener todas las métricas que usa este cliente
        metrics_to_normalize = list(weights.keys())
        
        # Extraer valores de cada métrica
        metric_values = {metric: [] for metric in metrics_to_normalize}
        
        for nb_data in neighborhoods_data:
            for metric in metrics_to_normalize:
                value = nb_data.get(metric, 0.0)
                if value is None:
                    value = 0.0
                metric_values[metric].append(value)
        
        # Normalizar cada métrica
        normalized_metrics = {}
        for metric, values in metric_values.items():
            normalized_metrics[metric] = normalize_list(values)
        
        # Aplicar normalización a cada barrio
        normalized_data = []
        for i, nb_data in enumerate(neighborhoods_data):
            normalized_nb = nb_data.copy()
            for metric in metrics_to_normalize:
                normalized_nb[metric] = normalized_metrics[metric][i]
            normalized_data.append(normalized_nb)
        
        return normalized_data

