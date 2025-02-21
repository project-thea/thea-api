#!/usr/bin/env python3

import os
import psycopg2
import requests
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(
        database=os.environ.get('POSTGRES_DATABASE'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host='thea_postgres_db'  # service name from docker-compose
    )

def get_last_processed_timestamp(cursor):
    cursor.execute("""
        SELECT last_processed_timestamp 
        FROM api_processingmetadata 
        WHERE id = 1
    """)
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else datetime(1970, 1, 1)

def update_last_processed_timestamp(cursor, timestamp):
    cursor.execute("""
        INSERT INTO api_processingmetadata (id, last_processed_timestamp, created_at, updated_at)
        VALUES (1, %s, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE 
        SET last_processed_timestamp = %s,
            updated_at = NOW()
    """, (timestamp, timestamp))

def get_coarse_locations(cursor, last_timestamp):
    cursor.execute("""
        SELECT id, latitude, longitude, created_at, timestamp
        FROM api_location
        WHERE created_at > %s -- use 'created_at' instead of 'timestamp' to avoid missing some locations
        ORDER BY created_at ASC
        LIMIT 100  -- Process in batches to avoid overwhelming the system
    """, (last_timestamp,))

    return cursor.fetchall()

def snap_to_road(locations):
    valhalla_url = 'http://thea_valhalla:8002/trace_attributes'  # Use the  service name from docker-compose
    
    # Format locations for Valhalla and convert Decimal to float
    points = [{"lat": float(lat), "lon": float(lon)} for _, lat, lon, _, _ in locations]
    
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
        orig_id, _, _, _, timestamp = original
        
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

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing {len(locations)} locations")

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
 