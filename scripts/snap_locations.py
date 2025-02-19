#!/usr/bin/env python3

import os
import psycopg2
import requests
from datetime import datetime

# TODO; Issue - for some reason, some points keep disappearing.

def get_db_connection():
    return psycopg2.connect(
        database='thea', # TODO; change these when i am  done testing
        user='postgres',
        password='',
        host='thea_postgres_db'  # service name from docker-compose
    )

def get_last_processed_timestamp(cursor):
    cursor.execute("""
        SELECT last_processed_timestamp 
        FROM api_processingmetadata 
        WHERE id = 1
    """)
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else datetime.min

def update_last_processed_timestamp(cursor, timestamp):
    current_time = datetime.now()
    cursor.execute("""
        INSERT INTO api_processingmetadata (id, last_processed_timestamp, created_at, updated_at)
        VALUES (1, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET last_processed_timestamp = %s,
            updated_at = %s
    """, (timestamp, current_time, current_time, timestamp, current_time))

def get_coarse_locations(cursor, last_timestamp):
    # when getting the coarse locations, i dont think it is a good idea to remove 
    # duplicate lat-long pairs. this is because the timestamp could be different for
    # each pair e.g. someone could have been in the same spot but on different days.
    # "De-duplicating" could mess up some things, simplest of which  that comes to 
    # mind is the date filters in case of snapped locations.
    cursor.execute("""
        SELECT id, latitude, longitude, timestamp
        FROM api_location
        WHERE timestamp > %s
        ORDER BY latitude, longitude, timestamp
        LIMIT 100  -- Process in batches to avoid overwhelming the system
    """, (last_timestamp,))
    return cursor.fetchall()

def snap_to_road(locations):
    valhalla_url = 'http://thea_valhalla:8002/trace_attributes'  # Use the  service name from docker-compose
    
    # Format locations for Valhalla and convert Decimal to float
    points = [{"lat": float(lat), "lon": float(lon)} for _, lat, lon, _ in locations]
    
    payload = {
        "shape": points,
        "costing": "auto",
        "shape_match": "map_snap",
        "filters": {"attributes": ["edge.way_id", "matched.point", "matched.type", "matched.edge_index"]},
    }
    
    try:
        response = requests.post(valhalla_url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Failed to snap locations: {e}")


def store_snapped_locations(cursor, original_locations, snapped_results):
    matched_points = snapped_results.get('matched_points', [])
    
    for original, matched in zip(original_locations, matched_points):
        orig_id, _, _, timestamp = original

        # print(f"Snapped location: ID={orig_id}, Lat={matched['lat']}, Lon={matched['lon']}, Time={timestamp}")
        
        cursor.execute("""
            INSERT INTO api_snappedlocation
            (original_location_id, snapped_latitude, snapped_longitude, id, created_at, modified_at)
            VALUES (%s, %s, %s, gen_random_uuid(), NOW(), NOW())
        """, (
            orig_id,
            matched['lat'],
            matched['lon'],
        ))

def main():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
             # Get last processed timestamp
            last_timestamp = get_last_processed_timestamp(cursor)

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Last processed timestamp: {last_timestamp}")
            
            # Get unprocessed locations
            locations = get_coarse_locations(cursor, last_timestamp)

            if locations:
                # Process locations through Valhalla
                snapped_results = snap_to_road(locations)
                
                # Store results
                store_snapped_locations(cursor, locations, snapped_results)
                
                # Update last processed timestamp
                latest_timestamp = max(loc[3] for loc in locations)
                update_last_processed_timestamp(cursor, latest_timestamp)
                
            conn.commit()

       
if __name__ == "__main__":
    main()
 