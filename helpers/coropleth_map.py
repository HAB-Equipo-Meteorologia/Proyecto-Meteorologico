import os
import json
import unidecode
import geopandas as gpd
import folium
import pandas as pd
from folium import GeoJsonTooltip

def unificar_geojson_provincias(geojson_dir: str) -> dict:
    geojson_provincias = {"type": "FeatureCollection", "features": []}

    for filename in os.listdir(geojson_dir):
        if filename.endswith(".geojson"):
            file_path = os.path.join(geojson_dir, filename)
            index_value = filename.replace(".geojson", "")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                if data.get("type") == "FeatureCollection":
                    for feature in data["features"]:
                        feature.setdefault("properties", {})["provincia_id"] = index_value

                        if "nombre_prov" not in feature["properties"]:
                            if "name" in feature["properties"]:
                                feature["properties"]["nombre_prov"] = unidecode.unidecode(feature["properties"]["name"].strip().lower())
                            else:
                                feature["properties"]["nombre_prov"] = "desconocido"

                    geojson_provincias["features"].extend(data["features"])

                elif data.get("type") == "Feature":
                    data.setdefault("properties", {})["provincia_id"] = index_value

                    if "nombre_prov" not in data["properties"]:
                        if "name" in data["properties"]:
                            data["properties"]["nombre_prov"] = unidecode.unidecode(data["properties"]["name"].strip().lower())
                        else:
                            data["properties"]["nombre_prov"] = "desconocido"

                    geojson_provincias["features"].append(data)

                else:
                    geojson_provincias["features"].append({
                        "type": "Feature",
                        "properties": {"provincia_id": index_value, "nombre_prov": "desconocido"},
                        "geometry": data
                    })

    print("Número total de features en el GeoJSON unificado:", len(geojson_provincias["features"]))

    return geojson_provincias

def merge_geojson_provincias(geojson_provincias: dict) -> dict:

    gdf = gpd.GeoDataFrame.from_features(geojson_provincias["features"])
    gdf["provincia_id"] = gdf["provincia_id"].astype(str)

    gdf_merged = gdf.dissolve(by="provincia_id", as_index=False)
    gdf_merged["nombre_prov"] = gdf.groupby("provincia_id")["nombre_prov"].first().values

    geojson_provincias_merged = gdf_merged.__geo_interface__

    print("Número de features después de fusionar:", len(geojson_provincias_merged["features"]))

    return geojson_provincias_merged

def crear_mapa_choropleth(
    geojson_data: dict,
    df: pd.DataFrame,
    id_col: str,
    value_col: str,
    legend_name: str,
    tooltip_field: list = None,
    tooltip_alias: list = None,

) -> folium.Map:

    fill_color = "RdYlBu_r"
    fill_opacity = 0.7
    line_opacity = 0.2
    center = [40.4168, -3.7038]
    zoom_start = 6


    df[id_col] = df[id_col].astype(str)
    nombre_dict = df.set_index(id_col)["nombre_prov"].to_dict()
    temp_dict = df.set_index(id_col)[value_col].to_dict()


    for feature in geojson_data["features"]:
        prov_id = str(feature["properties"].get(id_col))
        feature["properties"]["nombre_prov"] = nombre_dict.get(prov_id, "desconocido")
        
        valor = temp_dict.get(prov_id, None)
        if valor is not None and isinstance(valor, (int, float)):
            feature["properties"][value_col] = f"{valor:.2f}"
        else:
            feature["properties"][value_col] = "desconocido"

    if not tooltip_field:
        tooltip_field = ["nombre_prov", value_col]
    if not tooltip_alias:
        tooltip_alias = ["Provincia:", "Valor:"]

    mapa = folium.Map(location=center, zoom_start=zoom_start)

    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    bounds = gdf.total_bounds
    mapa.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])


    folium.Choropleth(
        geo_data=geojson_data,
        data=df,
        columns=[id_col, value_col],
        key_on=f"feature.properties.{id_col}",
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        line_opacity=line_opacity,
        legend_name=legend_name
    ).add_to(mapa)


    tooltip = GeoJsonTooltip(
        fields=tooltip_field,
        aliases=tooltip_alias,
        localize=True,
        style=(
            "background-color: white; "
            "color: #333333; "
            "font-family: Arial, sans-serif; "
            "font-size: 12px; "
            "border: 1px solid gray; "
            "border-radius: 3px; "
            "padding: 5px;"
        ),
        max_width=800
    )


    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0},
        tooltip=tooltip
    ).add_to(mapa)
    
    return mapa
