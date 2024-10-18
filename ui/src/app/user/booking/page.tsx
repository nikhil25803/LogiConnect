"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

export interface Vehicle {
  vehicle_id: string;
  registration_number: string;
  model_name: string;
  capacity_in_kg: number;
  current_latitude: number;
  current_longitude: number;
  fuel_type: string;
  distance_from_pickup: number;
  total_distance_km: number;
  base_price: number;
  gst: number;
  platform_fee: number;
  total_price: number;
}

export interface Driver {
  driver_id: string;
  name: string;
  mobile: string;
  email: string;
}

export default function UserBooking() {
  const router = useRouter();
  const [pickup, setPickup] = useState<string>("");
  const [drop, setDrop] = useState<string>("");
  const [capacity, setCapacity] = useState<number>(1500);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [driver, setDriver] = useState<Driver | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isBooking, setIsBooking] = useState<boolean>(false);

  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    const userId = localStorage.getItem("userid");

    if (!accessToken || !userId) {
      router.push("/login");
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    const accessToken = localStorage.getItem("access_token");
    const userId = localStorage.getItem("userid");

    try {
      // Fetch pickup coordinates
      const coordinatesResponse = await fetch(
        `http://localhost:3001/booking/coordinates?pickup_address=${encodeURIComponent(
          pickup
        )}&drop_address=${encodeURIComponent(drop)}&user_id=${userId}`,
        {
          method: "GET",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!coordinatesResponse.ok) {
        toast.error("Failed to fetch coordinates.");
        setIsLoading(false);
        return;
      }

      const coordinatesData = await coordinatesResponse.json();
      const { pickup_coordinates, drop_coordinates } = coordinatesData;

      // Fetch vehicle data with updated payload and user_id as a query parameter
      const vehicleResponse = await fetch(
        `http://localhost:3001/vehicle/search?user_id=${userId}`,
        {
          method: "POST",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            capacity_in_kg: capacity,
            pickup_latitude: pickup_coordinates[0],
            pickup_longitude: pickup_coordinates[1],
            drop_latitude: drop_coordinates[0],
            drop_longitude: drop_coordinates[1],
          }),
        }
      );

      if (!vehicleResponse.ok) {
        toast.error("Failed to fetch vehicle details.");
        setIsLoading(false);
        return;
      }

      const vehicleData: Vehicle[] = await vehicleResponse.json();
      setVehicles(vehicleData);
    } catch (error) {
      console.error("Error during booking:", error);
      toast.error("An error occurred during booking.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectVehicle = async (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle);
    setIsLoading(true);

    const accessToken = localStorage.getItem("access_token");
    const userId = localStorage.getItem("userid");

    try {
      // Fetch driver details
      const driverResponse = await fetch(
        `http://localhost:3001/vehicle/search/driver?vehicle_id=${vehicle.vehicle_id}&user_id=${userId}`,
        {
          method: "GET",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!driverResponse.ok) {
        toast.error("Failed to fetch driver details.");
        setIsLoading(false);
        return;
      }

      const driverData: Driver = await driverResponse.json();
      setDriver(driverData);
      setIsBooking(true); // Set booking flag to true
    } catch (error) {
      console.error("Error fetching driver details:", error);
      toast.error("An error occurred while fetching driver details.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmBooking = async () => {
    if (!selectedVehicle || !driver) return;

    const accessToken = localStorage.getItem("access_token");
    const userId = localStorage.getItem("userid");

    setIsLoading(true);

    try {
      const response = await fetch(
        `http://localhost:3001/booking/new?user_id=${userId}`,
        {
          method: "POST",
          headers: {
            accept: "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            user_id: userId,
            vehicle_id: selectedVehicle.vehicle_id,
            driver_id: driver.driver_id,
            pickup_location: pickup,
            drop_location: drop,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
        router.push("/user/profile");
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || "Failed to confirm booking.");
      }
    } catch (error) {
      console.error("Error confirming booking:", error);
      toast.error("An error occurred while confirming the booking.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="bg-backgroundPrimary w-full h-fit font-montserrat">
      <div className="max-w-[800px] w-full h-fit mx-auto p-5">
        {!isBooking ? (
          <form onSubmit={handleSubmit} className="mb-5">
            <div className="mb-4">
              <label
                htmlFor="pickup"
                className="block text-sm font-medium mb-2"
              >
                Pickup Location
              </label>
              <input
                type="text"
                id="pickup"
                value={pickup}
                onChange={(e) => setPickup(e.target.value)}
                required
                className="border rounded p-2 w-full"
              />
            </div>
            <div className="mb-4">
              <label htmlFor="drop" className="block text-sm font-medium mb-2">
                Drop Location
              </label>
              <input
                type="text"
                id="drop"
                value={drop}
                onChange={(e) => setDrop(e.target.value)}
                required
                className="border rounded p-2 w-full"
              />
            </div>
            <div className="mb-4">
              <label
                htmlFor="capacity"
                className="block text-sm font-medium mb-2"
              >
                Vehicle Capacity (in kg)
              </label>
              <input
                type="number"
                id="capacity"
                value={capacity}
                onChange={(e) => setCapacity(Number(e.target.value))}
                required
                className="border rounded p-2 w-full"
                min={0}
              />
            </div>
            <button
              type="submit"
              className="bg-textSecondary w-full text-white p-2 rounded"
              disabled={isLoading}
            >
              {isLoading ? "Loading..." : "Submit"}
            </button>
          </form>
        ) : (
          <div className="mt-5">
            <h2 className="text-xl font-semibold mb-2">Booking Summary</h2>
            {selectedVehicle && (
              <div className="border p-4 rounded bg-white shadow mb-4">
                <h3 className="font-semibold">Vehicle Details</h3>
                <p>
                  <strong>Model:</strong> {selectedVehicle.model_name}
                </p>
                <p>
                  <strong>Registration Number:</strong>{" "}
                  {selectedVehicle.registration_number}
                </p>
                <p>
                  <strong>Capacity:</strong> {selectedVehicle.capacity_in_kg} kg
                </p>
                <p>
                  <strong>Fuel Type:</strong> {selectedVehicle.fuel_type}
                </p>
                <p>
                  <strong>Distance from Pickup:</strong>{" "}
                  {selectedVehicle.distance_from_pickup.toFixed(2)} km
                </p>
                <p>
                  <strong>Total Distance:</strong>{" "}
                  {selectedVehicle.total_distance_km.toFixed(2)} km
                </p>
                <p>
                  <strong>Total Price:</strong> Rs.{" "}
                  {selectedVehicle.total_price.toFixed(2)}
                </p>
              </div>
            )}
            {driver && (
              <div className="border p-4 rounded bg-white shadow">
                <h3 className="font-semibold">Driver Details</h3>
                <p>
                  <strong>Name:</strong> {driver.name}
                </p>
                <p>
                  <strong>Contact Number:</strong> {driver.email}
                </p>
                <p>
                  <strong>Contact Number:</strong> {driver.mobile}
                </p>
              </div>
            )}
            <button
              onClick={handleConfirmBooking}
              className="bg-green-500 mt-5 w-full text-white p-2 rounded"
              disabled={isLoading}
            >
              {isLoading ? "Confirming..." : "Confirm Booking"}
            </button>
          </div>
        )}

        {vehicles.length > 0 && !isBooking && (
          <div className="mt-5">
            <h2 className="text-xl font-semibold mb-2">Available Vehicles</h2>
            <ul className="space-y-4">
              {vehicles.map((vehicle) => (
                <li
                  key={vehicle.vehicle_id}
                  className="border p-4 rounded bg-white shadow"
                >
                  <h3 className="font-semibold">{vehicle.model_name}</h3>
                  <p>
                    <strong>Registration Number:</strong>{" "}
                    {vehicle.registration_number}
                  </p>
                  <p>
                    <strong>Capacity:</strong> {vehicle.capacity_in_kg} kg
                  </p>
                  <p>
                    <strong>Fuel Type:</strong> {vehicle.fuel_type}
                  </p>
                  <p>
                    <strong>Distance from Pickup:</strong>{" "}
                    {vehicle.distance_from_pickup.toFixed(2)} km
                  </p>
                  <p>
                    <strong>Total Distance:</strong>{" "}
                    {vehicle.total_distance_km.toFixed(2)} km
                  </p>
                  <p>
                    <strong>Total Price:</strong> Rs.{" "}
                    {vehicle.total_price.toFixed(2)}
                  </p>
                  <button
                    onClick={() => handleSelectVehicle(vehicle)}
                    className="bg-textSecondary text-white p-2 rounded mt-2"
                  >
                    Select Vehicle
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
