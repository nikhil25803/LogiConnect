import os
import math
from dotenv import load_dotenv
import googlemaps

load_dotenv()


class LogisticsCalculations:
    """
    Initializing this with fuel rates per km
    """

    def __init__(self):
        self.FUEL_RATES = {"Petrol": 100, "Diesel": 90, "Electric": 60}
        self.API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
        self.gmaps = googlemaps.Client(key=self.API_KEY)

    def calculate_estimated_distance(
        self, from_latitude, from_longitude, to_latitude, to_longitude
    ):
        """
        Calculates the Haversine distance between two points.
        """
        from_latitude, from_longitude, to_latitude, to_longitude = map(
            math.radians, [from_latitude, from_longitude, to_latitude, to_longitude]
        )

        delta_latitude = to_latitude - from_latitude
        delta_longitude = to_longitude - from_longitude

        haversine_formula = (
            math.sin(delta_latitude / 2) ** 2
            + math.cos(from_latitude)
            * math.cos(to_latitude)
            * math.sin(delta_longitude / 2) ** 2
        )
        central_angle = 2 * math.atan2(
            math.sqrt(haversine_formula), math.sqrt(1 - haversine_formula)
        )

        earth_radius_km = 6371
        return round((earth_radius_km * central_angle), 2)

    def calculate_estimated_price(
        self,
        vehicle_lat,
        vehicle_lon,
        pickup_lat,
        pickup_lon,
        drop_lat,
        drop_lon,
        fuel_type,
    ):
        """
        - Calculate vehicel distance from pickup point
        - Calculate distance from pickup to drop location
        - Multiply total distance with fuel rate
        - 28% GST (assumption)
        - 15% Platform fees (assumption)
        """

        distance_vehicle_to_pickup = self.calculate_estimated_distance(
            vehicle_lat, vehicle_lon, pickup_lat, pickup_lon
        )
        distance_pickup_to_drop = self.calculate_estimated_distance(
            pickup_lat, pickup_lon, drop_lat, drop_lon
        )

        total_distance = (distance_vehicle_to_pickup + distance_pickup_to_drop) / 100

        fuel_rate = self.FUEL_RATES.get(fuel_type, 10)
        base_price = total_distance * fuel_rate

        gst = base_price * 0.28
        platform_fee = base_price * 0.15

        total_price = base_price + gst + platform_fee

        return {
            "total_distance_km": round(total_distance, 2),
            "base_price": round(base_price, 2),
            "gst": round(gst, 2),
            "platform_fee": round(platform_fee, 2),
            "total_price": round(total_price, 2),
        }

    def geocode_address(self, address: str):
        try:
            geocode_result = self.gmaps.geocode(address)
            coordinates = geocode_result[0]["geometry"]["location"]
            return [coordinates["lat"], coordinates["lng"]]
        except Exception:
            return None

    def calculate_distance_time_price(
        self, vehicle_lat, vehicle_lng, origin_address, destination_address, fuel_type
    ):
        try:
            origin_coordinates = self.geocode_address(origin_address)
            destination_coordinates = self.geocode_address(destination_address)

            origin_vehicle_distance_matrix = self.gmaps.distance_matrix(
                (vehicle_lat, vehicle_lng), tuple(origin_coordinates), mode="driving"
            )

            origin_to_vehicle_distance = origin_vehicle_distance_matrix["rows"][0][
                "elements"
            ][0]["distance"]
            origin_to_vehicle_distance_in_km = (
                int(origin_to_vehicle_distance["value"]) // 1000
            )

            origin_to_vehicle_duration = origin_vehicle_distance_matrix["rows"][0][
                "elements"
            ][0]["duration"]
            origin_to_vehicle_duration_in_hr = (
                int(origin_to_vehicle_duration["value"]) // 60
            ) // 60

            origin_destination_distance_matrix = self.gmaps.distance_matrix(
                tuple(origin_coordinates),
                tuple(destination_coordinates),
                mode="driving",
            )

            origin_to_destination_distance = origin_destination_distance_matrix["rows"][
                0
            ]["elements"][0]["distance"]
            origin_to_destination_distance_in_km = (
                int(origin_to_destination_distance["value"]) // 1000
            )

            origin_to_destination_duration = origin_destination_distance_matrix["rows"][
                0
            ]["elements"][0]["duration"]
            origin_to_destination_duration_in_hr = (
                int(origin_to_destination_duration["value"]) // 60
            ) // 60

            total_distance_covered = (
                origin_to_destination_distance_in_km + origin_to_vehicle_distance_in_km
            )
            total_time_required = (
                origin_to_destination_duration_in_hr + origin_to_vehicle_duration_in_hr
            )

            fuel_rate = self.FUEL_RATES.get(fuel_type, 10)
            base_price = total_distance_covered * fuel_rate
            gst = base_price * 0.28
            platform_fee = base_price * 0.15
            total_price = base_price + gst + platform_fee

            results = {
                "total_distance_km": total_distance_covered,
                "base_price": round(base_price, 2),
                "gst": round(gst, 2),
                "platform_fee": round(platform_fee, 2),
                "total_price": round(total_price, 2),
                "estimated_delivery_time": total_time_required,
                "pickup_coordinates": origin_coordinates,
                "drop_coordinates": destination_coordinates,
            }

            return results
        except Exception:
            return None
