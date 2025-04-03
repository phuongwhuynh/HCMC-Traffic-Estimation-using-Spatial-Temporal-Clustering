import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from shapely import wkt
import geopandas as gpd
from shapely.geometry import Polygon

latitude = 10.781
longitude = 106.692
radius = 1800
filename='box/bounding_box.csv'
def reverse_coords(geometry):
    return Polygon([(lon, lat) for lat, lon in geometry.exterior.coords])

df = pd.read_csv(filename)
df["box"] = df["box"].apply(wkt.loads)
box=df["box"]
gdf = gpd.GeoDataFrame(box, geometry="box")
gdf.set_crs(epsg=4326, inplace=True)
gdf['box'] = gdf['box'].apply(reverse_coords)

location_point = (latitude, longitude)
G = ox.graph_from_point(location_point, dist=radius, network_type="all")

fig, ax = plt.subplots(figsize=(10, 10))
ox.plot_graph(G, ax=ax, bgcolor="white", node_size=1, edge_color="black", edge_linewidth=1.5, show=False, close=False)

def update_plot(index):
    ax.clear()
    
    ox.plot_graph(G, ax=ax, bgcolor="white", node_size=1, edge_color="black", edge_linewidth=1.5, show=False, close=False)
    row=gdf.iloc[index]
    gpd.GeoSeries(row).plot(ax=ax, color="none", edgecolor="red", linewidth=2)

    df_row=df.iloc[index]
    time_start=df_row['minTime']
    time_end=df_row['maxTime']
    hour_start=time_start // 60
    minute_start=time_start-hour_start*60

    hour_end=time_end // 60
    minute_end=time_end-hour_end*60

    if minute_start==0 and minute_end==0:
        ax.set_title(f"This congestion happens between {str(hour_start)}:00 and {str(hour_end)}:00")
    elif minute_start==0:
        ax.set_title(f"This congestion happens between {str(hour_start)}:00 and {str(hour_end)}:{str(minute_end)}")
    elif minute_end==0:
        ax.set_title(f"This congestion happens between {str(hour_start)}:{str(minute_start)} and {str(hour_end)}:00")
    else:
        ax.set_title(f"This congestion happens between {str(hour_start)}:{str(minute_start)} and {str(hour_end)}:{str(minute_end)}")
# Create the animation
ani = animation.FuncAnimation(fig, update_plot, frames=range(0, df.shape[0]), repeat=False)
ani.save('box/bounding_boxes_animation.gif', writer='pillow', fps=1)

plt.show()
