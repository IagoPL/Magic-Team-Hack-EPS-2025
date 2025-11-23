"""
Motor de justificación
Genera explicaciones automáticas sobre por qué un barrio es recomendado para un cliente
"""
from typing import Dict, List
from src.utils import load_json


class JustificationEngine:
    """Genera explicaciones justificadas para las recomendaciones"""
    
    def __init__(self):
        self.clients = load_json('config/clients.json')
        
        # Templates de explicaciones en catalán
        self.templates = {
            "top_reason": "{metric_description} ({metric_value}) fa que {neighborhood} sigui ideal per a {client_name}.",
            "reason_list": "Les 3 raons principals per triar {neighborhood} són: {reasons}",
            "metric_comparison": "Amb un {metric_name} de {value}, {neighborhood} supera la mitjana d'altres barris."
        }
        
        # Descripciones amigables de las métricas
        self.metric_descriptions = {
            "density_parks": "alta densitat de parcs",
            "ratio_local_businesses": "elevat percentatge de negocis locals",
            "community_organizations": "forta presència d'organitzacions comunitàries",
            "dog_friendly_parks": "parcs adaptats per a gossos",
            "median_income": "elevats ingressos mitjans",
            "low_crime_rate": "baixa taxa de criminalitat",
            "elite_schools": "presència de col·legis d'elit",
            "high_rent_price": "alta qualitat residencial",
            "accessibility_score": "excel·lent accessibilitat",
            "quietness_score": "entorn tranquil i silenciós",
            "internet_coverage": "bon cobertura d'internet d'alta velocitat",
            "low_population_density": "baixa densitat de població",
            "low_rent_price": "preus de lloguer accessibles",
            "cultural_diversity": "alta diversitat cultural",
            "proximity_nature": "proximitat a zones naturals",
            "community_density": "forta densitat comunitària",
            "public_transport_coverage": "excel·lent cobertura de transport públic",
            "high_population_density": "alta densitat de població",
            "large_neighborhood": "barri extens",
            "activity_centers": "proximitat a centres d'activitat",
            "cultural_venues": "alta densitat de llocs culturals",
            "restaurant_density": "alta densitat de restaurants",
            "walkability_score": "excel·lent walkability",
            "public_transport_access": "bon accés al transport públic"
        }
    
    def get_justification(self, neighborhood_data: Dict, client_id: str) -> Dict[str, str]:
        """
        Genera justificación para un barrio recomendado
        
        Args:
            neighborhood_data: Datos del barrio con score y métricas
            client_id: ID del cliente
        
        Returns:
            Diccionario con:
            - summary: Resumen breve
            - top_3_reasons: Lista de las 3 razones principales
            - detailed_explanation: Explicación más detallada
        """
        if client_id not in self.clients:
            raise ValueError(f"Cliente {client_id} no encontrado")
        
        client_config = self.clients[client_id]
        client_name = client_config['name'].split(' - ')[0]  # Solo el nombre
        weights = client_config['weights']
        neighborhood_name = neighborhood_data.get('name', 'Aquest barri')
        score = neighborhood_data.get('score', 0.0)
        
        # Identificar las top 3 métricas que más contribuyen al score
        metric_contributions = []
        for metric, weight in weights.items():
            metric_value = neighborhood_data.get(metric, 0.0)
            contribution = metric_value * weight
            metric_contributions.append({
                'metric': metric,
                'value': metric_value,
                'weight': weight,
                'contribution': contribution
            })
        
        # Ordenar por contribución
        metric_contributions.sort(key=lambda x: x['contribution'], reverse=True)
        top_3 = metric_contributions[:3]
        
        # Generar razones
        reasons = []
        for i, metric_info in enumerate(top_3):
            metric = metric_info['metric']
            metric_desc = self.metric_descriptions.get(metric, metric)
            metric_value = metric_info['value']
            
            # Formatear valor para mostrar
            if isinstance(metric_value, float):
                if metric_value < 0.01:
                    value_str = "molt baix"
                elif metric_value < 0.3:
                    value_str = "baix"
                elif metric_value < 0.7:
                    value_str = "mitjà"
                else:
                    value_str = "alt"
            else:
                value_str = str(metric_value)
            
            reason = f"{metric_desc.capitalize()} ({value_str})"
            reasons.append(reason)
        
        # Generar resumen
        summary = f"{neighborhood_name} és una excel·lent opció per a {client_name} amb un score de {score:.2%}."
        
        # Generar lista de razones
        reasons_text = ", ".join(reasons[:-1]) + f" i {reasons[-1]}" if len(reasons) > 1 else reasons[0]
        top_3_text = f"Les 3 raons principals per triar {neighborhood_name} són: {reasons_text}."
        
        # Generar explicación detallada
        detailed = f"{summary}\n\n{top_3_text}\n\n"
        detailed += f"Amb un score total de {score:.2%}, {neighborhood_name} satisfà les necessitats específiques de {client_name}: {client_config['description']}"
        
        return {
            'summary': summary,
            'top_3_reasons': reasons,
            'detailed_explanation': detailed,
            'score': score
        }

