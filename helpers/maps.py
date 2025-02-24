import json
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
from typing import Optional


def get_geojson() -> dict:
    data = {}

    script_dir = os.path.dirname(os.path.realpath(__file__))
    geojson_dir = os.path.join(script_dir, '../data/geojson/provincias')
    locations_file = os.path.join(script_dir, '../data/locations/provincias.json')

    for file in glob.glob(os.path.join(geojson_dir, '*.geojson')):
        key = os.path.basename(file).removesuffix(".geojson")
        data[key] = {}
        with open(file, encoding="utf-8") as f:
            data[key]['geojson'] = json.load(f)

    with open(locations_file) as f:
        loc_data = json.load(f)

    for key, value in loc_data.items():
        data[key].update(value)
        for feature in data[key]['geojson']['features']:
            feature.setdefault('properties', {})
            feature['properties'].update(value)
            feature['properties']['provincia_id'] = key


    return data


def add_region(ax: plt.Axes, geodata, alpha: float = 0, color: Optional[str] = None):
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
                ax.plot(lons + (lons[0],), lats + (lats[0],), transform=ccrs.PlateCarree(), color='black',
                        linewidth=.5)
                ax.fill(lons, lats, transform=ccrs.PlateCarree(), color=color, alpha=alpha, linewidth=0)


# noinspection PydanticTypeChecker,PyTypeChecker
def spain_outline():
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

    inset_ax = fig.add_axes((0.68, 0.15, 0.2, 0.2), projection=ccrs.PlateCarree())
    inset_ax.set_extent([-19, -12, 27, 30], crs=ccrs.PlateCarree())

    for key, val in data.items():
        geojson = val['geojson']
        if key not in ['35', '38']:
            add_region(ax, geojson)
        else:
            add_region(inset_ax, geojson)

    return fig, ax, inset_ax


def add_area(provincia_id, ax, inset_ax, handles, alpha: float = 0.5, color: str = 'blue'):
    with open(f'../data/locations/provincias.json') as f:
        name = json.load(f)[provincia_id]['nombre']

    if any(handle.get_label() == name for handle in handles):
        return

    with open(f"../data/geojson/provincias/{provincia_id}.geojson") as f:
        geojson = json.load(f)

    if provincia_id in ['35', '38']:  # Islas Canarias
        add_region(inset_ax, geojson, alpha=alpha, color=color)
    else:
        add_region(ax, geojson, alpha=alpha, color=color)

    handles.append(mpatches.Patch(label=name, color=color))
