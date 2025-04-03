import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from shapely import wkt
import geopandas as gpd
from shapely.geometry import Polygon

interval = 5
start = 420
end = 535
latitude = 10.781
longitude = 106.692
radius = 1800

def reverse_coords(geometry):
    return Polygon([(lon, lat) for lat, lon in geometry.exterior.coords])

location_point = (latitude, longitude)
G = ox.graph_from_point(location_point, dist=radius, network_type="all")

fig, ax = plt.subplots(figsize=(10, 10))
ox.plot_graph(G, ax=ax, bgcolor="white", node_size=1, edge_color="black", edge_linewidth=1.5,show=False, close=False)


# Function to update the plot for each frame
def update_plot(time):
    ax.clear()
    
    ox.plot_graph(G, ax=ax, bgcolor="white", node_size=1, edge_color="black", edge_linewidth=1.5, show=False, close=False)
    filename = f'timeBox/bounding_boxes{time}.csv'
    df = pd.read_csv(filename)
    df = df.rename(columns={"0": "geometry"})
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry")
    gdf.set_crs(epsg=4326, inplace=True)
    
    gdf['geometry'] = gdf['geometry'].apply(reverse_coords)
    
    gdf.plot(ax=ax, color="none", edgecolor="red", linewidth=2)
    hour=time // 60
    minute=time-hour*60

    if minute==0:
        ax.set_title(f"Traffic congestion at Time {str(hour)}:00")
    elif minute==5:
        ax.set_title(f"Traffic congestion at Time {str(hour)}:05")
    else:
        ax.set_title(f"Traffic congestion at Time {str(hour)}:{str(minute)}")

# Create the animation
ani = animation.FuncAnimation(fig, update_plot, frames=range(start, end + interval, interval), repeat=False)
ani.save('timeBox/bounding_boxes_animation.gif', writer='pillow', fps=1)

plt.show()
