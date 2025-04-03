import pandas as pd
from st_dbscan import ST_DBSCAN
week= ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
for day in week:
    df = pd.read_csv(f"data5Day/{day}/traffic_status.csv")

    def time_to_minutes(time_str):
        time_part = time_str.split(" ")[1]  
        hours, minutes, seconds = map(int, time_part.split(":"))  # Split into hours, minutes, and seconds
        if hours==1:
            hours=13
        total_minutes = hours * 60 + minutes 
        return total_minutes

    df['time'] = df['time'].apply(time_to_minutes)

    df.drop(["segmentId","polyline._id","polyline.type", "source", "los", "street.type"], axis=1, inplace=True)
    for col in [
        "polyline.coordinates.0.0", 
        "polyline.coordinates.0.1", 
        "polyline.coordinates.1.0", 
        "polyline.coordinates.1.1"
    ]:
        df[col] = df[col].str.replace(",", "").astype(str)

    def format_coordinates(row):
        # Format for 0.0 and 0.1
        coord0_0 = float(f"{row['polyline.coordinates.0.0'][:3]}.{row['polyline.coordinates.0.0'][3:]}") 
        coord1_0 = float(f"{row['polyline.coordinates.1.0'][:3]}.{row['polyline.coordinates.1.0'][3:]}") 
        # Format for 1.0 and 1.1
        coord0_1 = float(f"{row['polyline.coordinates.0.1'][:2]}.{row['polyline.coordinates.0.1'][2:]}") 
        coord1_1 = float(f"{row['polyline.coordinates.1.1'][:2]}.{row['polyline.coordinates.1.1'][2:]}") 
        
        return pd.Series([coord0_0, coord0_1, coord1_0, coord1_1])



    df[["latitude_0", "longitude_0", "latitude_1", "longitude_1"]] = df.apply(format_coordinates, axis=1)
    df.drop(["polyline.coordinates.0.0","polyline.coordinates.0.1","polyline.coordinates.1.0", "polyline.coordinates.1.1"], axis=1, inplace=True)

    df["latitude"]=(df["latitude_0"]+df["latitude_1"])/2
    df["longitude"]=(df["longitude_0"]+df["longitude_1"])/2

    extracted_data = df[[
        "time", 
        "latitude", 
        "longitude", 
        "velocity", 
        "street.name"
    ]]

    filtered_data = extracted_data[extracted_data["velocity"] <= 15][["time", "latitude", "longitude"]].copy()
    # Perform clustering
    st_dbscan = ST_DBSCAN(eps1=0.0005, eps2=5, min_samples=10)
    st_dbscan.fit(filtered_data)

    filtered_data['cluster'] = st_dbscan.labels
    filtered_data = filtered_data[filtered_data['cluster'] != -1]

    # Merge cluster labels with the original extracted_data
    filtered_data = filtered_data.merge(extracted_data[['time', 'latitude', 'longitude', 'velocity', 'street.name']],
                                        on=['time', 'latitude', 'longitude'],
                                        how='left')


    filtered_data.to_csv(f"data5Day/{day}/temp_result.csv")
