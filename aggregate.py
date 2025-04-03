import pandas as pd
from shapely.geometry import box

# Jaccard similarity for time (using timestamp set similarity)
def jaccard_time_similarity(cluster_a, cluster_b):
    times_a = set(event['time'] for event in cluster_a)
    times_b = set(event['time'] for event in cluster_b)
    intersection = times_a.intersection(times_b)
    union = times_a.union(times_b)
    return len(intersection) / len(union) if union else 0

# Jaccard similarity for coordinates (using latitude and longitude)
def jaccard_coordinate_similarity(cluster_a, cluster_b):
    coordinates_a = set((event['latitude'], event['longitude']) for event in cluster_a)
    coordinates_b = set((event['latitude'], event['longitude']) for event in cluster_b)
    intersection = coordinates_a.intersection(coordinates_b)
    union = coordinates_a.union(coordinates_b)
    return len(intersection) / len(union) if union else 0

# Function to merge clusters across days based on Jaccard similarity thresholds
def merge_across_days(all_days_clusters, time_threshold=0.7, coordinate_threshold=0.7):
    merged_clusters = []  

    for day_idx, day_clusters in enumerate(all_days_clusters):
        for cluster in day_clusters:
            is_merged = False
            for merged_cluster in merged_clusters:
                time_sim = jaccard_time_similarity(cluster, merged_cluster)
                coord_sim = jaccard_coordinate_similarity(cluster, merged_cluster)

                # Merge if both similarity conditions are met
                if time_sim >= time_threshold and coord_sim >= coordinate_threshold:
                    merged_cluster.extend(cluster)
                    is_merged = True
                    break
            
            # If not merged, add it as a new merged cluster
            if not is_merged:
                merged_clusters.append(cluster.copy())

    return merged_clusters

week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
all_days_clusters = []  

for day in week:
    data = f'data5Day/{day}/temp_result.csv'
    df = pd.read_csv(data)
    day_clusters = [group_df.to_dict('records') for _, group_df in df.groupby("cluster")]
    all_days_clusters.append(day_clusters) 

# Merge clusters across different days with specified similarity thresholds
merged_clusters_all_days = merge_across_days(all_days_clusters, time_threshold=0.7, coordinate_threshold=0.7)



timestamps = sorted(set(event['time'] for cluster in merged_clusters_all_days for event in cluster))

# Function to calculate bounding boxes of clusters at a given timestamp
def get_bounding_boxes_at_time(clusters, timestamp):
    bounding_boxes = []
    for cluster in clusters:
        # Filter events by the given timestamp
        events = [event for event in cluster if event['time'] == timestamp]
        if events:
            lats = [event['latitude'] for event in events]
            longs = [event['longitude'] for event in events]
            min_lat, max_lat = min(lats), max(lats)
            min_long, max_long = min(longs), max(longs)
            bounding_boxes.append(box(min_long, min_lat, max_long, max_lat))
    return bounding_boxes

# Function to calculate bounding boxes of clusters and its start and end time
def get_bounding_boxes(clusters):
    bounding_boxes = pd.DataFrame(columns=['box', 'minTime', 'maxTime'])
    for cluster in clusters:
        lats = [event['latitude'] for event in cluster]
        longs = [event['longitude'] for event in cluster]
        t=[event['time'] for event in cluster]
        min_time, max_time=min(t), max(t)
        min_lat, max_lat = min(lats), max(lats)
        min_long, max_long = min(longs), max(longs)
        new_row=pd.DataFrame([{'box': box(min_long,min_lat, max_long, max_lat), 'minTime':min_time, 'maxTime':max_time}])
        bounding_boxes=pd.concat([bounding_boxes,new_row])
    return bounding_boxes

for time in timestamps:
    boxes = get_bounding_boxes_at_time(merged_clusters_all_days, time)
    df_bounding_boxes = pd.DataFrame(boxes)
    df_bounding_boxes.to_csv('timeBox/bounding_boxes' + str(time) +'.csv', index=False)


minimum_bounding_box=get_bounding_boxes(merged_clusters_all_days)
minimum_bounding_box.to_csv('box/bounding_box' +'.csv', index=False)

