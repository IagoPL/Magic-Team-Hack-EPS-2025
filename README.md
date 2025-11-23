# El Joc de Barris - HackEPS 2025

Motor de recomendación de barrios de Los Angeles basado en las necesidades específicas de diferentes clientes inspirados en personajes de *Game of Thrones*.

## Descripción

Este proyecto forma parte del reto propuesto por **restb.ai** para HackEPS 2025. Consiste en crear un sistema inteligente que recomienda barrios de Los Angeles a diferentes clientes según sus necesidades personales, estilo de vida y preferencias.

## Características

- Motor de recomendación basado en scoring ponderado
- 6 clientes predefinidos con necesidades específicas
- Sistema de justificación automática de recomendaciones
- Visualización interactiva con mapas (Folium)
- Integración con APIs: U.S. Census Bureau y OpenStreetMap
- Gráficos comparativos de métricas

## Instalación

### Requisitos

- Python 3.8+
- pip

### Pasos

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Recopilar datos (opcional pero recomendado):**
```bash
python src/data_collector.py
python src/data_processor.py
```

4. **Ejecutar la aplicación:**
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## Estructura del Proyecto

```
hackeps2025/
├── app.py                          # Aplicación principal Streamlit
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
│
├── config/
│   ├── clients.json               # Configuración de los 6 clientes
│   └── neighborhoods.json         # Lista de barrios de LA con coordenadas
│
├── data/
│   ├── cache/                     # Datos descargados de APIs (cache)
│   └── raw/                       # Datos sin procesar
│
├── src/
│   ├── data_collector.py          # Script para descargar datos de APIs
│   ├── data_processor.py          # Procesamiento y normalización de datos
│   ├── recommendation_engine.py   # Motor de scoring y ranking
│   ├── justification_engine.py    # Motor de explicaciones
│   └── utils.py                   # Utilidades generales
│
└── docs/
    └── technical_doc.md          # Documentación técnica (si existe)
```

## Los 6 Clientes

1. **Daenerys** - L'Emprenedora Ètica
   - Comunidad fuerte, negocios locales, consciencia social

2. **Cersei** - La Reina Corporativa
   - Lujo, seguretat, exclusivitat, col·legis d'elit

3. **Bran** - L'Analista Total
   - Accessibilitat, silenci, fibra òptica, entorn tranquil

4. **Jon Snow** - El Guardià de la Comunitat
   - Pressupost ajustat, barris autèntics, natura propera

5. **Arya** - La Nòmada Urbana
   - Anonimat, llibertat, zones denses, transport públic 24/7

6. **Tyrion** - L'Estratega Urbà
   - Centre cultural, gastronomía, walkability

## APIs Utilizadas

- **U.S. Census Bureau API**: Datos demográficos, ingresos, población
- **Overpass API (OpenStreetMap)**: Parques, restaurantes, transporte, amenidades

## Cómo Funciona

1. **Recopilación de datos**: Se descargan datos de las APIs y se guardan en cache local
2. **Procesamiento**: Los datos se normalizan y se calculan métricas específicas por cliente
3. **Scoring**: Cada barrio recibe un score ponderado según las necesidades del cliente
4. **Recomendación**: Se ordenan los barrios por score y se muestran los top 5
5. **Justificación**: Se generan explicaciones automáticas de por qué cada barrio es recomendado

## Uso

1. Abre la aplicación con `streamlit run app.py`
2. Selecciona un cliente en el sidebar
3. Visualiza las top 5 recomendaciones en el mapa
4. Lee las justificaciones detalladas
5. Explora los gráficos comparativos

## API Keys

**Nota importante**: Para usar el U.S. Census Bureau API con límites más altos, puedes obtener una API key gratuita en: https://api.census.gov/data/key_signup.html

Actualiza la variable `census_api_key` en `src/data_collector.py`.

## Notas

- Los datos se cachean localmente para evitar múltiples llamadas a las APIs
- Si no hay datos procesados, la aplicación usará datos de ejemplo
- El sistema está preparado para agregar fácilmente un 7º cliente (cliente secreto del reto)

## Desarrollo

Para desarrollo local:

```bash
# Recopilar datos
python src/data_collector.py

# Procesar datos
python src/data_processor.py

# Ejecutar app
streamlit run app.py
```
