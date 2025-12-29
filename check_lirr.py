#!/usr/bin/env python3
import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime, timezone

def get_next_grand_central_train():
    # Fetch the GTFS-realtime feed
    url = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/lirr%2Fgtfs-lirr'
    response = requests.get(url)

    # Parse the Protocol Buffer data
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    # Look for trips heading to Grand Central
    now = datetime.now(timezone.utc).timestamp()
    upcoming_trains = []

    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip = entity.trip_update

            # Check each stop time update
            for stop_update in trip.stop_time_update:
                if stop_update.HasField('arrival'):
                    arrival_time = stop_update.arrival.time
                    stop_id = stop_update.stop_id

                    # Filter for Grand Central (stop_id "1" is GCT in LIRR)
                    if stop_id == "1" and arrival_time > now:
                        upcoming_trains.append({
                            'trip_id': trip.trip.trip_id,
                            'route_id': trip.trip.route_id if trip.trip.HasField('route_id') else 'N/A',
                            'stop_id': stop_id,
                            'arrival_time': arrival_time,
                            'arrival_dt': datetime.fromtimestamp(arrival_time, tz=timezone.utc)
                        })

    # Sort by arrival time
    upcoming_trains.sort(key=lambda x: x['arrival_time'])

    if upcoming_trains:
        print("🚂 Next trains to Grand Central:\n")
        for i, train in enumerate(upcoming_trains[:5]):
            local_time = train['arrival_dt'].astimezone()
            time_str = local_time.strftime('%I:%M %p')
            minutes_away = int((train['arrival_time'] - now) / 60)
            print(f"{i+1}. Trip {train['trip_id']}")
            print(f"   Arrives: {time_str} (in {minutes_away} minutes)")
            print()
    else:
        print("No upcoming trains found to Grand Central")

if __name__ == '__main__':
    get_next_grand_central_train()
