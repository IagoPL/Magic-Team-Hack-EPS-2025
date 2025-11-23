"""
Aplicación principal Streamlit - El Joc de Barris
Motor de recomendación de barrios de Los Angeles
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
from src.utils import load_json, get_data_path
from src.recommendation_engine import RecommendationEngine
from src.justification_engine import JustificationEngine

# Configuración de la página
st.set_page_config(
    page_title="El Joc de Barris - HackEPS 2025",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏰 El Joc de Barris")
st.markdown("### Motor de Recomanació de Barris per a Los Angeles")
st.markdown("---")

# Inicializar motores
@st.cache_resource
def load_engines():
    """Carga los motores de recomendación y justificación"""
    return RecommendationEngine(), JustificationEngine()

recommendation_engine, justification_engine = load_engines()

# Sidebar - Selector de cliente
st.sidebar.title("👤 Selecciona un Client")

clients_config = load_json('config/clients.json')
client_options = {cid: info['name'] for cid, info in clients_config.items()}

selected_client_id = st.sidebar.selectbox(
    "Client:",
    options=list(client_options.keys()),
    format_func=lambda x: client_options[x]
)

# Mostrar información del cliente seleccionado
selected_client = clients_config[selected_client_id]
st.sidebar.markdown("---")
st.sidebar.markdown(f"**{selected_client['name']}**")
st.sidebar.markdown(f"_{selected_client['description']}_")

# Cargar datos procesados
@st.cache_data
def load_processed_data():
    """Carga los datos procesados de barrios"""
    import json
    import os
    
    try:
        data_path = get_data_path('processed_neighborhood_data.json')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Datos de ejemplo si no hay datos procesados
            st.warning("⚠️ No se encontraron datos procesados. Ejecuta primero `python src/data_collector.py` y luego `python src/data_processor.py`. Usando datos de ejemplo por ahora.")
            return load_example_data()
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return load_example_data()

def load_example_data():
    """Carga datos de ejemplo para demo con métricas básicas"""
    import random
    neighborhoods = load_json('config/neighborhoods.json')['neighborhoods']
    example_data = []
    
    # Valores variados para que las recomendaciones tengan sentido
    for i, nb in enumerate(neighborhoods):
        # Crear valores variados según posición (para diversidad)
        base_score = (i % 5) / 4.0  # Ciclo entre 0 y 1
        
        example_data.append({
            'name': nb['name'],
            'lat': nb['lat'],
            'lon': nb['lon'],
            'zipcode': nb.get('zipcode', ''),
            # Daenerys
            'density_parks': 0.3 + base_score * 0.4,
            'ratio_local_businesses': 0.5 + random.uniform(-0.2, 0.2),
            'community_organizations': 0.4 + base_score * 0.3,
            'dog_friendly_parks': 0.3 + base_score * 0.4,
            # Cersei
            'median_income': base_score * 0.8 + 0.2,
            'low_crime_rate': base_score * 0.8 + 0.2,
            'elite_schools': base_score * 0.7 + 0.3,
            'high_rent_price': base_score * 0.8 + 0.2,
            # Bran
            'accessibility_score': 0.6 + random.uniform(-0.1, 0.2),
            'quietness_score': 1.0 - base_score * 0.6,
            'internet_coverage': base_score * 0.7 + 0.3,
            'low_population_density': 1.0 - base_score * 0.6,
            # Jon Snow
            'low_rent_price': 1.0 - base_score * 0.6,
            'cultural_diversity': 0.5 + random.uniform(-0.1, 0.2),
            'proximity_nature': 0.3 + base_score * 0.4,
            'community_density': 0.4 + base_score * 0.4,
            # Arya
            'public_transport_coverage': base_score * 0.7 + 0.3,
            'high_population_density': base_score * 0.8,
            'large_neighborhood': 0.6 if i % 2 == 0 else 0.8,
            'activity_centers': base_score * 0.7 + 0.3,
            # Tyrion
            'cultural_venues': 0.4 + base_score * 0.4,
            'restaurant_density': 0.5 + base_score * 0.4,
            'walkability_score': 0.5 + base_score * 0.4,
            'public_transport_access': base_score * 0.7 + 0.3,
        })
    
    return example_data

neighborhoods_data = load_processed_data()

if neighborhoods_data:
    # Obtener recomendaciones
    recommendations = recommendation_engine.get_recommendations(
        neighborhoods_data,
        selected_client_id,
        top_n=5
    )
    
    # Mostrar top recomendaciones
    st.header(f"🏆 Top 5 Recomanacions per a {selected_client['name'].split(' - ')[0]}")
    
    # Crear columnas para mostrar recomendaciones
    cols = st.columns(5)
    
    for i, rec in enumerate(recommendations):
        with cols[i]:
            score = rec.get('score', 0)
            st.metric(
                label=rec['name'],
                value=f"{score:.0%}",
                delta=f"Score: {score:.2f}"
            )
    
    st.markdown("---")
    
    # Mapa interactivo
    st.header("🗺️ Mapa de Recomanacions")
    
    # Crear mapa centrado en LA
    m = folium.Map(
        location=[34.0522, -118.2437],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Agregar marcadores para cada recomendación
    for i, rec in enumerate(recommendations, 1):
        name = rec['name']
        lat = rec.get('lat', 34.0522)
        lon = rec.get('lon', -118.2437)
        score = rec.get('score', 0)
        
        # Color según posición (verde = mejor, rojo = peor)
        colors = ['darkgreen', 'green', 'orange', 'lightred', 'red']
        color = colors[min(i-1, len(colors)-1)]
        
        folium.Marker(
            [lat, lon],
            popup=f"<b>{name}</b><br>Score: {score:.2%}",
            tooltip=f"#{i} {name}",
            icon=folium.Icon(color=color, icon='home', prefix='fa')
        ).add_to(m)
    
    # Mostrar mapa
    map_data = st_folium(m, width=1200, height=500)
    
    st.markdown("---")
    
    # Justificaciones detalladas
    st.header("📝 Justificacions Detallades")
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"#{i} - {rec['name']} (Score: {rec.get('score', 0):.2%})"):
            justification = justification_engine.get_justification(rec, selected_client_id)
            
            st.markdown(f"**{justification['summary']}**")
            st.markdown("\n**Raons principals:**")
            for reason in justification['top_3_reasons']:
                st.markdown(f"- {reason}")
            st.markdown(f"\n{justification['detailed_explanation']}")
    
    # Gráfico comparativo
    st.markdown("---")
    st.header("📊 Comparativa de Mètriques")
    
    # Preparar datos para gráfico
    df_recs = pd.DataFrame(recommendations)
    
    if not df_recs.empty:
        # Seleccionar métricas relevantes para el cliente
        client_weights = selected_client['weights']
        metrics_to_show = list(client_weights.keys())[:4]  # Top 4 métricas
        
        # Crear gráfico de barras
        chart_data = []
        for rec in recommendations:
            row = {'Barri': rec['name']}
            for metric in metrics_to_show:
                row[metric.replace('_', ' ').title()] = rec.get(metric, 0)
            chart_data.append(row)
        
        df_chart = pd.DataFrame(chart_data)
        
        if not df_chart.empty:
            fig = px.bar(
                df_chart,
                x='Barri',
                y=[col for col in df_chart.columns if col != 'Barri'],
                title=f"Mètriques principals per a {selected_client['name'].split(' - ')[0]}",
                barmode='group'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
else:
    st.error("❌ No se pudieron cargar los datos. Por favor, ejecuta primero data_collector.py y data_processor.py")

# Footer
st.markdown("---")
st.markdown("### 📚 Informació del Projecte")
st.markdown("""
**El Joc de Barris** - Motor de recomanació de barris per a Los Angeles basat en les necessitats específiques de cada client.

Desenvolupat per a **HackEPS 2025** - Repte de *restb.ai*
""")

