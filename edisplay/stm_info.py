from typing import List, Dict
from pprint import pprint
from dataclasses import dataclass

import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime

from edisplay.secrets import get_config


OCCUPANCY_LEVELS = {
    0: "EMPTY",
    1: "MANY_SEATS_AVAILABLE", 
    2: "FEW_SEATS_AVAILABLE",
    3: "STANDING_ROOM_ONLY",
    4: "CRUSHED_STANDING_ROOM_ONLY",
    5: "FULL",
    6: "NOT_ACCEPTING_PASSENGERS"
}


STOPS = {
    '47E': '51930',
    '197E': '51822',
    '45N': '52022'
}


@dataclass
class ArrivalInfo:
    delta: int = -1
    delay: int = 0


@dataclass
class StopInfo:
    stop_name: str
    stop_id: str
    arrivals: List[ArrivalInfo]


class STMRealtimeAPI:
    BASE_URL = "https://api.stm.info/pub/od/gtfs-rt/ic/v2"
    
    def __init__(self):
        self.api_key = get_config('STM', 'Key')
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.api_key,
            'Accept': 'application/x-protobuf'
        })
    
    def _make_request(self, endpoint: str) -> bytes:
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Max 10 req/sec or 10,000 req/day")
            elif response.status_code == 400:
                raise Exception("Rate limit or quota exceeded")
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_vehicle_positions(self) -> List[Dict]:
        """
        Get real-time positions of all buses
        Includes bus occupancy levels
        
        Returns:
            List of vehicle position dictionaries
        """
        data = self._make_request("vehiclePositions")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)
        
        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicle = entity.vehicle
                
                vehicle_data = {
                    'vehicle_id': vehicle.vehicle.id if vehicle.HasField('vehicle') else None,
                    'trip_id': vehicle.trip.trip_id if vehicle.HasField('trip') else None,
                    'route_id': vehicle.trip.route_id if vehicle.HasField('trip') else None,
                    'latitude': vehicle.position.latitude if vehicle.HasField('position') else None,
                    'longitude': vehicle.position.longitude if vehicle.HasField('position') else None,
                    'bearing': vehicle.position.bearing if vehicle.HasField('position') else None,
                    'speed': vehicle.position.speed if vehicle.HasField('position') else None,
                    'timestamp': datetime.fromtimestamp(vehicle.timestamp) if vehicle.timestamp else None,
                    'current_stop_sequence': vehicle.current_stop_sequence if vehicle.current_stop_sequence else None,
                    'current_status': vehicle.current_status if vehicle.current_status else None,
                }
                
                # Add occupancy data (v2 feature)
                if vehicle.HasField('occupancy_status'):
                    vehicle_data['occupancy_status'] = vehicle.occupancy_status
                    vehicle_data['occupancy_level'] = OCCUPANCY_LEVELS.get(
                        vehicle.occupancy_status, 
                        "UNKNOWN"
                    )
                
                vehicles.append(vehicle_data)
        
        return vehicles
    
    def get_trip_updates(self) -> List[Dict]:
        """
        Get real-time trip updates with arrival/departure predictions
        
        Returns:
            List of trip update dictionaries
        """
        data = self._make_request("tripUpdates")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)
        
        updates = []
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                
                trip_data = {
                    'trip_id': trip_update.trip.trip_id if trip_update.HasField('trip') else None,
                    'route_id': trip_update.trip.route_id if trip_update.HasField('trip') else None,
                    'timestamp': datetime.fromtimestamp(trip_update.timestamp) if trip_update.timestamp else None,
                    'stop_time_updates': []
                }
                
                # Parse stop time updates
                for stu in trip_update.stop_time_update:
                    stop_update = {
                        'stop_id': stu.stop_id,
                        'stop_sequence': stu.stop_sequence,
                        'arrival_delay': stu.arrival.delay if stu.HasField('arrival') else None,
                        'arrival_time': datetime.fromtimestamp(stu.arrival.time) if stu.HasField('arrival') and stu.arrival.time else None,
                        'departure_delay': stu.departure.delay if stu.HasField('departure') else None,
                        'departure_time': datetime.fromtimestamp(stu.departure.time) if stu.HasField('departure') and stu.departure.time else None,
                    }
                    trip_data['stop_time_updates'].append(stop_update)
                
                updates.append(trip_data)
        
        return updates
    
    def get_service_alerts(self) -> List[Dict]:
        data = self._make_request("alerts")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)
        
        alerts = []
        for entity in feed.entity:
            if entity.HasField('alert'):
                alert = entity.alert
                
                alert_data = {
                    'id': entity.id,
                    'cause': alert.cause if alert.cause else None,
                    'effect': alert.effect if alert.effect else None,
                    'header_text': self._extract_translation(alert.header_text) if alert.HasField('header_text') else None,
                    'description_text': self._extract_translation(alert.description_text) if alert.HasField('description_text') else None,
                    'affected_routes': [],
                    'affected_stops': [],
                    'active_periods': []
                }
                
                # Extract affected entities
                for entity_selector in alert.informed_entity:
                    if entity_selector.HasField('route_id'):
                        alert_data['affected_routes'].append(entity_selector.route_id)
                    if entity_selector.HasField('stop_id'):
                        alert_data['affected_stops'].append(entity_selector.stop_id)
                
                # Extract active periods
                for period in alert.active_period:
                    active_period = {
                        'start': datetime.fromtimestamp(period.start) if period.start else None,
                        'end': datetime.fromtimestamp(period.end) if period.end else None
                    }
                    alert_data['active_periods'].append(active_period)
                
                alerts.append(alert_data)
        
        return alerts
    
    def _extract_translation(self, translated_string) -> str:
        """Extract text from TranslatedString (prefer French)"""
        if not translated_string.translation:
            return ""
        
        # Try to find French translation first
        for translation in translated_string.translation:
            if translation.language == 'fr':
                return translation.text
        
        # Fall back to first available
        return translated_string.translation[0].text if translated_string.translation else ""
    
    def get_vehicles_by_route(self, route_id: str) -> List[Dict]:
        """Get all vehicles currently on a specific route"""
        vehicles = self.get_vehicle_positions()
        return [v for v in vehicles if v.get('route_id') == route_id]
    
    def get_next_arrivals_at_stop(self, stop_id: str) -> List[Dict]:
        arrivals = []
        
        trip_updates = self.get_trip_updates()
        for trip in trip_updates:
            for stop_update in trip.get('stop_time_updates', []):
                if stop_update.get('stop_id') == stop_id:
                    arrivals.append({
                        'trip_id': trip['trip_id'],
                        'route_id': trip['route_id'],
                        'stop_id': stop_id,
                        'arrival_time': stop_update.get('arrival_time'),
                        'arrival_delay': stop_update.get('arrival_delay'),
                        'stop_sequence': stop_update.get('stop_sequence')
                    })

        arrivals.sort(key=lambda x: x['arrival_time'] if x['arrival_time'] else datetime.max)
        return arrivals
    
    def get_next_arrivals_at_stops(self, stops_id: List[str]) -> Dict:
        arrivals = {}
        
        trip_updates = self.get_trip_updates()
        for trip in trip_updates:
            for stop_update in trip.get('stop_time_updates', []):
                stop_id = stop_update.get('stop_id')
                if stop_id in stops_id:
                    arrivals.setdefault(stop_id, []).append({
                        'trip_id': trip['trip_id'],
                        'route_id': trip['route_id'],
                        'stop_id': stop_id,
                        'arrival_time': stop_update.get('arrival_time'),
                        'arrival_delay': stop_update.get('arrival_delay'),
                        'stop_sequence': stop_update.get('stop_sequence')
                    })

        for _, times in arrivals.items():
            times.sort(key=lambda x: x['arrival_time'] if x['arrival_time'] else datetime.max)
        return arrivals
    
    def get_arrivals_display(self, route, count):
        stop = STOPS.get(route)
        if stop is None:
            return 'Invalid Stop'
        
        arrivals = []
        arrivals = self.get_next_arrivals_at_stop(stop)
        for arrival in arrivals[:count]:
            if arrival_time := arrival.get('arrival_time'):
                delta = arrival_time - datetime.now()
                minutes = delta.total_seconds() // 60
                text += f' >> {minutes:.0f}'
                if arrival_delay := arrival.get('arrival_delay'):
                    minutes = arrival_delay // 60
                    text += f'+{minutes:.0f}'
            else:
                text += '?'
        return text
    
    def get_arrivals_display_multi(self, stops):
        stop_ids = [STOPS.get(stop) for stop in stops]
        if not all(stop_ids):
            return 'Invalid Stop'
        
        display = [StopInfo(stop, STOPS.get(stop), []) for stop in stops]
        arrivals = self.get_next_arrivals_at_stops(stop_ids)
        for stop_info in display:
            if arr := arrivals.get(stop_info.stop_id):
                for arrival_entry in arr:
                    if arrival_time := arrival_entry.get('arrival_time'):
                        arrival_info = ArrivalInfo()
                        delta = arrival_time - datetime.now()
                        arrival_info.delta = int(delta.total_seconds() // 60)
                        if arrival_delay := arrival_entry.get('arrival_delay'):
                            arrival_info.delay = int(arrival_delay // 60)
                        stop_info.arrivals.append(arrival_info)
        return display


if __name__ == "__main__":
    stm = STMRealtimeAPI()
    arrivals = stm.get_arrivals_display_multi(['47E', '197E', '45N'])
    pprint(arrivals[:2])
