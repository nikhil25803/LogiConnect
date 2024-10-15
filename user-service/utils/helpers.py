import math


class LogisticsCalculations:
    """
    Initializing this with fuel rates per km
    """

    def __init__(self):
        self.FUEL_RATES = {"Petrol": 100, "Diesel": 90, "Electric": 60}

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
        return earth_radius_km * central_angle

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

        total_distance = distance_vehicle_to_pickup + distance_pickup_to_drop

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
