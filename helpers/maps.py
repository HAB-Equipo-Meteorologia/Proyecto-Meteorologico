import json
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
from typing import Optional


def get_geojson(_type: str) -> dict:
    data = {}

    for file in glob.glob(f"../data/geojson/{_type}/*.geojson"):
        key = os.path.basename(file).removesuffix(".geojson")
        data[key] = {}
        with open(file, encoding="utf-8") as f:
            data[key]['geojson'] = json.load(f)

    with open(f'../data/locations/{_type}.json') as f:
        loc_data = json.load(f)

    for key, value in loc_data.items():
        data[key].update(value)

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
def spain_outline(_type):
    data = get_geojson(_type)
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


def add_area(_type, _id, ax, inset_ax, handles, alpha: float = 0.5, color: str = 'blue'):
    with open(f'../data/locations/{_type}.json') as f:
        name = json.load(f)[_id]['nombre']

    if any(handle.get_label() == name for handle in handles):
        return

    with open(f"../data/geojson/{_type}/{_id}.geojson") as f:
        geojson = json.load(f)

    if _type == 'provincias' and _id in ['35', '38'] or _type == 'comunidades' and _id in ['5']:  # Islas Canarias
        add_region(inset_ax, geojson, alpha=alpha, color=color)
    else:
        add_region(ax, geojson, alpha=alpha, color=color)

    handles.append(mpatches.Patch(label=name, color=color))
