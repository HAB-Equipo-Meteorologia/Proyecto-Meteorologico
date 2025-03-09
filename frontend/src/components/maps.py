from plotly.graph_objs import Figure
from helpers.lookups import estaciones
import plotly.graph_objects as go
import json


def estacion_map(fig: Figure, idema: int):
    lat = estaciones[idema]["latitud"]
    lon = estaciones[idema]["longitud"]
    name = estaciones[idema]["nombre"]
    prov_id = estaciones[idema]["provincia_id"]

    provincia_map(fig, prov_id, lat, lon)
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=10, color='red'),
        text=[name],
    ))


def provincia_map(fig: Figure, prov_id: int, lat: int, lon: int):
    with open(f'data/geojson/provincias/{prov_id}.geojson') as pf:
        geodata = json.load(pf)

    _area_map(fig, geodata, lat, lon)


def comunidad_map(fig: Figure, com_id: int, lat: int, lon: int):
    with open(f'data/geojson/comunidades/{com_id}.geojson') as cf:
        geodata = json.load(cf)

    _area_map(fig, geodata, lat, lon)


def _area_map(fig: Figure, geodata, lat, lon):
    fig.data = []

    for feature in geodata["features"]:
        coords = feature["geometry"]["coordinates"]
        geom_type = feature["geometry"]["type"]

        if geom_type == "Polygon":
            polygons = [coords]
        elif geom_type == "MultiPolygon":
            polygons = coords
        else:
            continue

        for polygon in polygons:
            for ring in polygon:
                lons, lats = zip(*ring)

                lons += (lons[0],)
                lats += (lats[0],)

                fig.add_trace(go.Scattermapbox(
                    lon=lons,
                    lat=lats,
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba(51, 136, 255, 0.5)",
                    line=dict(color="#3388ff", width=2),
                ))
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=6,
            center={"lat": lat, "lon": lon},
        ),
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=False
    )
