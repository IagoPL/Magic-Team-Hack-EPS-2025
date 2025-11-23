import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
from src.utils import load_json, get_data_path, get_metric_display_name, get_metric_description, get_metric_display_name, get_metric_description
from src.recommendation_engine import RecommendationEngine
from src.justification_engine import JustificationEngine
from src.client_manager import ClientManager

# Configuración de la página
st.set_page_config(
    page_title="El Joc de Barris - HackEPS 2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar motores y gestor de clientes
@st.cache_resource
def load_engines():
    """Carga los motores de recomendación y justificación"""
    return RecommendationEngine(), JustificationEngine()

recommendation_engine, justification_engine = load_engines()

# Inicializar client manager
client_manager = ClientManager()

# Sidebar - Selector de cliente (disponible en ambos tabs)
st.sidebar.title("Navegació")

    # Tabs para separar funcionalidades
tab1, tab2 = st.tabs(["Recomanacions", "Gestionar Clients"])

# Cargar clientes para el sidebar
clients_config = client_manager.get_all_clients()

with tab1:
    st.sidebar.markdown("---")
    st.sidebar.title("Selecciona un Client")
    
    client_options = {cid: info['name'] for cid, info in clients_config.items()}
    
    selected_client_id = st.sidebar.selectbox(
        "Client:",
        options=list(client_options.keys()),
        format_func=lambda x: client_options[x],
        help="Tria un client per veure les seves recomanacions personalitzades"
    )
    
    # Mostrar información del cliente seleccionado
    if selected_client_id in clients_config:
        selected_client = clients_config[selected_client_id]
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{selected_client['name']}**")
        st.sidebar.markdown(f"_{selected_client['description']}_")
        
        # Mostrar métricas del cliente con nombres legibles
        if 'weights' in selected_client:
            st.sidebar.markdown("---")
            st.sidebar.markdown("**Mètriques:**")
            for metric, weight in list(selected_client['weights'].items())[:3]:
                st.sidebar.markdown(f"- {get_metric_display_name(metric)}: {weight:.0%}")
    else:
        st.sidebar.error("Client no trobat")
        st.stop()
    
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
                st.warning("No s'han trobat dades processades. Executa primer `python src/data_collector.py` i després `python src/data_processor.py`. S'estan utilitzant dades d'exemple per ara.")
                return load_example_data()
        except Exception as e:
            st.error(f"Error en carregar les dades: {e}")
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
        st.header(f"Top 5 Recomanacions per a {selected_client['name'].split(' - ')[0]}")

        # Crear columnas para mostrar recomendaciones
        cols = st.columns(5)

        for i, rec in enumerate(recommendations):
            with cols[i]:
                score = rec.get('score', 0)
                st.markdown(f"**{rec['name']}**")
                st.markdown(f"### {score:.0%}")
                st.caption(f"Score: {score:.2f}")

        st.markdown("---")

        # Mapa interactivo
        st.header("Mapa de Recomanacions")

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
        st.header("Justificacions Detallades")

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
        st.header("Comparativa de Mètriques")

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
                    row[get_metric_display_name(metric)] = rec.get(metric, 0)
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
                st.plotly_chart(fig, width='stretch')

    else:
        st.error("No s'han pogut carregar les dades. Si us plau, executa primer `python src/data_collector.py` i després `python src/data_processor.py`")

with tab2:
    st.header("Gestionar Clients")
    st.markdown("Afegeix o edita clients per personalitzar les recomanacions de barris.")
    
    # Lista de métricas disponibles
    available_metrics = [
        'density_parks', 'ratio_local_businesses', 'community_organizations', 'dog_friendly_parks',
        'median_income', 'low_crime_rate', 'elite_schools', 'high_rent_price',
        'accessibility_score', 'quietness_score', 'internet_coverage', 'low_population_density',
        'low_rent_price', 'cultural_diversity', 'proximity_nature', 'community_density',
        'public_transport_coverage', 'high_population_density', 'large_neighborhood', 'activity_centers',
        'cultural_venues', 'restaurant_density', 'walkability_score', 'public_transport_access'
    ]
    
    # Opciones: Agregar o Editar
    action = st.radio("Acció:", ["Afegir nou client", "Editar client existent"], horizontal=True)
    
    if action == "Afegir nou client":
        st.subheader("Afegir Nou Client")
        
        with st.form("add_client_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_client_name = st.text_input("Nom del client:", 
                                                help="Nom complet del client (l'ID es generarà automàticament)")
            
            new_client_description = st.text_area("Descripció:", 
                                                  help="Descripció de les necessitats i preferències del client")
            
            # Seleccionar métricas a usar
            st.markdown("### Pas 1: Selecciona les Mètriques")
            
            # Crear opciones con nombres legibles para el selector
            metric_options = {get_metric_display_name(m): m for m in available_metrics}
            metric_options_reverse = {m: get_metric_display_name(m) for m in available_metrics}
            
            selected_metric_display = st.multiselect(
                "Selecciona les mètriques que usarà aquest client (mínim 3):",
                options=list(metric_options.keys()),
                help="Selecciona un mínim de 3 mètriques per a aquest client"
            )
            
            # Convertir nombres legibles de vuelta a keys
            selected_metrics = [metric_options[display] for display in selected_metric_display if display in metric_options]
            
            # Variables para pesos y validación
            weights = {}
            total_weight = 0.0
            is_valid = False
            
            # Solo mostrar pesos si hay métricas seleccionadas (mínimo 3)
            if len(selected_metrics) >= 3:
                st.markdown("### Pas 2: Assigna Importància a les Mètriques")
                st.markdown("**Important:** Els pesos han de sumar exactament 1.0")
                
                # Calcular valor inicial equitativo
                initial_weight = 1.0 / len(selected_metrics)
                
                # Mostrar métricas con sliders
                st.markdown("**Utilitza els deslitzadors per ajustar la importància de cada mètrica:**")
                
                for i, metric in enumerate(selected_metrics):
                    display_name = get_metric_display_name(metric)
                    description = get_metric_description(metric)
                    
                    # Usar session_state para persistir valores
                    if f"weight_{metric}" not in st.session_state:
                        st.session_state[f"weight_{metric}"] = initial_weight
                    
                    # Mostrar en formato de tarjeta visual
                    with st.container():
                        col1, col2, col3 = st.columns([3, 5, 2])
                        
                        with col1:
                            st.markdown(f"**{display_name}**")
                            st.caption(description)
                        
                        with col2:
                            # Slider visual con mejor formato
                            weight = st.slider(
                                display_name,
                                min_value=0.0,
                                max_value=1.0,
                                value=float(st.session_state[f"weight_{metric}"]),
                                step=0.01,
                                format="%.2f",
                                key=f"slider_{metric}",
                                help=f"Importància: {float(st.session_state[f'weight_{metric}'])*100:.0f}%"
                            )
                            # Actualizar session_state
                            st.session_state[f"weight_{metric}"] = weight
                        
                        with col3:
                            # Mostrar valor porcentual grande y claro
                            percent_value = weight * 100
                            st.markdown(f"### {percent_value:.0f}%")
                        
                        weights[metric] = weight
                        st.markdown("---")
                
                # Recalcular total después de leer todos los pesos
                total_weight = sum(weights.values())
                
                # Mostrar suma de pesos de forma prominente
                col_sum1, col_sum2 = st.columns([2, 1])
                with col_sum1:
                    is_valid = abs(total_weight - 1.0) < 0.01
                    if is_valid:
                        st.success(f"**Suma de pesos: {total_weight:.2f}** (vàlid - pots continuar)")
                    else:
                        diff = abs(total_weight - 1.0)
                        st.error(f"**Suma de pesos: {total_weight:.2f}** (falten {diff:.2f} per arribar a 1.0)")
                
                with col_sum2:
                    # Barra de progreso visual
                    progress_value = min(total_weight, 1.0)
                    st.progress(progress_value)
                    st.caption(f"Progrés: {progress_value*100:.0f}%")
            elif len(selected_metrics) > 0:
                st.warning(f"Selecciona un mínim de 3 mètriques. Actualment has seleccionat {len(selected_metrics)}.")
            else:
                st.info("Selecciona almenys 3 mètriques per continuar.")
            
            # Generar ID automáticamente desde el nombre
            auto_id = ""
            if new_client_name:
                import re
                # Convertir a minúsculas y reemplazar espacios por guiones bajos
                auto_id = re.sub(r'[^a-z0-9_]+', '_', new_client_name.lower().strip())
                # Eliminar guiones bajos múltiples
                auto_id = re.sub(r'_+', '_', auto_id)
                # Eliminar guiones bajos al inicio y final
                auto_id = auto_id.strip('_')
                
                if auto_id and len(selected_metrics) >= 3:
                    st.info(f"**ID auto-generat:** `{auto_id}`")
            
            # Botón de envío siempre presente (requerido por Streamlit)
            submitted = st.form_submit_button("Afegir Client", use_container_width=True, type="primary")
            
            if submitted:
                # Validaciones
                if not new_client_name or not new_client_description:
                    st.error("Si us plau, completa tots els camps requerits (nom i descripció).")
                elif len(selected_metrics) < 3:
                    st.error(f"Selecciona un mínim de 3 mètriques. Actualment has seleccionat {len(selected_metrics)}.")
                elif not is_valid:
                    st.error(f"Els pesos han de sumar exactament 1.0. Actualment sumen {total_weight:.2f}.")
                elif not auto_id:
                    st.error("No s'ha pogut generar un ID vàlid des del nom. Utilitza un nom amb lletres o nombres.")
                elif auto_id in client_manager.get_client_list():
                    st.error(f"El client amb ID '{auto_id}' ja existeix. Utilitza 'Editar client existent' per modificar-lo.")
                else:
                    try:
                        client_data = {
                            'name': new_client_name,
                            'description': new_client_description,
                            'weights': weights,
                            'preferences': {}
                        }
                        client_manager.add_client(auto_id, client_data)
                        # Recargar clientes en los motores
                        recommendation_engine.reload_clients()
                        justification_engine.reload_clients()
                        st.success(f"Client '{new_client_name}' (ID: {auto_id}) afegit exitosament!")
                        # Limpiar cache y recargar
                        st.cache_resource.clear()
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error en afegir el client: {e}")
    
    else:  # Editar cliente existente
        st.subheader("Editar Client Existent")
        
        clients_config = client_manager.get_all_clients()
        client_list = list(clients_config.keys())
        
        if not client_list:
            st.error("No hi ha clients per editar.")
        else:
            edit_client_id = st.selectbox(
                "Selecciona el client a editar:",
                options=client_list,
                format_func=lambda x: clients_config[x]['name']
            )
            
            if edit_client_id:
                edit_client = clients_config[edit_client_id]
                
                with st.form("edit_client_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_client_name = st.text_input("Nom del client:", 
                                                        value=edit_client.get('name', ''))
                    
                    edit_client_description = st.text_area("Descripció:", 
                                                          value=edit_client.get('description', ''))
                    
                    st.markdown("### Ajusta la Importància de les Mètriques")
                    
                    # Mostrar métricas actuales con nombres legibles
                    current_weights = edit_client.get('weights', {})
                    current_metrics = list(current_weights.keys())
                    
                    if current_metrics:
                        metric_display_names = [get_metric_display_name(m) for m in current_metrics]
                        st.markdown(f"**Mètriques actuals:** {', '.join(metric_display_names)}")
                        
                        # Permitir cambiar pesos con sliders
                        new_weights = {}
                        st.markdown("**Utilitza els deslitzadors per ajustar la importància de cada mètrica:**")
                        
                        for i, metric in enumerate(current_metrics):
                            display_name = get_metric_display_name(metric)
                            description = get_metric_description(metric)
                            
                            # Usar session_state para persistir valores
                            if f"edit_weight_{metric}" not in st.session_state:
                                st.session_state[f"edit_weight_{metric}"] = current_weights[metric]
                            
                            # Mostrar en formato de tarjeta visual
                            with st.container():
                                col1, col2, col3 = st.columns([3, 5, 2])
                                
                                with col1:
                                    st.markdown(f"**{display_name}**")
                                    st.caption(description)
                                
                                with col2:
                                    # Slider visual con mejor formato
                                    weight = st.slider(
                                        display_name,
                                        min_value=0.0,
                                        max_value=1.0,
                                        value=float(st.session_state[f"edit_weight_{metric}"]),
                                        step=0.01,
                                        format="%.2f",
                                        key=f"edit_slider_{metric}",
                                        help=f"Importància: {float(st.session_state[f'edit_weight_{metric}'])*100:.0f}%"
                                    )
                                    # Actualizar session_state
                                    st.session_state[f"edit_weight_{metric}"] = weight
                                
                                with col3:
                                    # Mostrar valor porcentual grande y claro
                                    percent_value = weight * 100
                                    st.markdown(f"### {percent_value:.0f}%")
                                
                                new_weights[metric] = weight
                                st.markdown("---")
                        
                        # Recalcular total después de leer todos los pesos
                        total_weight = sum(new_weights.values())
                        
                        # Mostrar suma de pesos de forma prominente
                        col_sum1, col_sum2 = st.columns([2, 1])
                        with col_sum1:
                            is_valid = abs(total_weight - 1.0) < 0.01
                            if is_valid:
                                st.success(f"**Suma de pesos: {total_weight:.2f}** (vàlid - pots continuar)")
                            else:
                                diff = abs(total_weight - 1.0)
                                st.error(f"**Suma de pesos: {total_weight:.2f}** (falten {diff:.2f} per arribar a 1.0)")
                        
                        with col_sum2:
                            # Barra de progreso visual
                            progress_value = min(total_weight, 1.0)
                            st.progress(progress_value)
                            st.caption(f"Progrés: {progress_value*100:.0f}%")
                    else:
                        st.warning("Aquest client no té mètriques assignades.")
                        new_weights = {}
                        total_weight = 0.0
                        is_valid = False
                    
                    submitted = st.form_submit_button("Guardar Canvis", use_container_width=True, type="primary")
                    
                    if submitted:
                        if not edit_client_name or not edit_client_description:
                            st.error("Si us plau, completa tots els camps requerits.")
                        elif not is_valid:
                            st.error(f"Els pesos han de sumar exactament 1.0. Actualment sumen {total_weight:.2f}.")
                        else:
                            try:
                                update_data = {
                                    'name': edit_client_name,
                                    'description': edit_client_description,
                                    'weights': new_weights
                                }
                                client_manager.update_client(edit_client_id, update_data)
                                # Recargar clientes en los motores
                                recommendation_engine.reload_clients()
                                justification_engine.reload_clients()
                                st.success(f"Client '{edit_client_name}' actualitzat exitosament!")
                                # Limpiar cache y recargar
                                st.cache_resource.clear()
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error en actualitzar el client: {e}")


