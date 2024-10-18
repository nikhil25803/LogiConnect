"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

// Define the UserProfile interface
interface UserProfile {
  name: string;
  email: string;
  country: string;
  state: string;
  phone_number: string;
  role: string;
}

// Define the DriverDetails interface
interface DriverDetails {
  name: string;
  email: string;
  mobile: string;
}

// Define the Booking interface
interface Booking {
  pickup_location: string;
  drop_location: string;
  distance_to_cover: number;
  estimated_delivery_time: number;
  total_price: number;
  request_status: string;
  delivery_status: string;
  driver_details: DriverDetails;
  booking_id: string; // Add booking_id to the Booking interface
}

export default function UserProfilePage() {
  const router = useRouter();
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      const accessToken = localStorage.getItem("access_token");
      const userId = localStorage.getItem("userid");

      if (!accessToken || !userId) {
        router.push("/login");
        return;
      }

      try {
        // Fetch user profile
        const userResponse = await fetch(
          `http://localhost:3001/user/profile?user_id=${userId}`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUserProfile(userData);
        } else {
          toast.error("Failed to fetch user profile.");
          localStorage.removeItem("access_token");
          localStorage.removeItem("user_id");
          router.push("/login");
        }

        // Fetch bookings
        const bookingsResponse = await fetch(
          `http://localhost:3001/booking/?user_id=${userId}`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (bookingsResponse.ok) {
          const bookingsData = await bookingsResponse.json();
          setBookings(bookingsData);
        } else {
          toast.error("Failed to fetch bookings.");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        toast.error("An error occurred while fetching user data.");
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [router]);

  const updateOrderStatus = async (bookingId: string) => {
    const accessToken = localStorage.getItem("access_token");
    const userId = localStorage.getItem("userid");

    try {
      const response = await fetch(
        `http://localhost:3001/booking/update-order-status?booking_id=${bookingId}&new_status=Received&user_id=${userId}`,
        {
          method: "PUT",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.ok) {
        toast.success("Order status updated successfully!");
        // Optionally, you can re-fetch the bookings to update the state
        const updatedBookingsResponse = await fetch(
          `http://localhost:3001/booking/?user_id=${userId}`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (updatedBookingsResponse.ok) {
          const updatedBookingsData = await updatedBookingsResponse.json();
          setBookings(updatedBookingsData);
        }
      } else {
        toast.error("Failed to update order status.");
      }
    } catch (error) {
      console.error("Error updating order status:", error);
      toast.error("An error occurred while updating order status.");
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        Loading...
      </div>
    );
  }

  return (
    <section className="bg-backgroundPrimary w-full h-fit font-montserrat">
      <div className="max-w-[1280px] w-full mx-auto p-5">
        <header className="mb-6">
          <h1 className="text-3xl font-bold text-center text-gray-800">
            User Dashboard
          </h1>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {userProfile ? (
            <>
              <div className="bg-white p-4 rounded shadow-lg">
                <h2 className="text-xl font-semibold mb-2">
                  Profile Information
                </h2>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Name:</strong> {userProfile.name}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Email:</strong> {userProfile.email}
                </p>
              </div>
              <div className="bg-white p-4 rounded shadow-lg">
                <h2 className="text-xl font-semibold mb-2">
                  Contact Information
                </h2>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Phone Number:</strong> {userProfile.phone_number}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Country:</strong> {userProfile.country}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>State:</strong> {userProfile.state}
                </p>
              </div>
              <div className="bg-white p-4 rounded shadow-lg md:col-span-2">
                <h2 className="text-xl font-semibold mb-2">User Role</h2>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Role:</strong> {userProfile.role}
                </p>
              </div>
            </>
          ) : (
            <p className="text-center">No user profile found.</p>
          )}
        </div>

        <div className="mt-6">
          <h2 className="text-2xl font-semibold mb-4">Bookings</h2>
          {bookings.length > 0 ? (
            <table className="min-w-full bg-white border border-gray-300">
              <thead>
                <tr>
                  <th className="border px-4 py-2">Pickup Location</th>
                  <th className="border px-4 py-2">Drop Location</th>
                  <th className="border px-4 py-2">Distance</th>
                  <th className="border px-4 py-2">Delivery Time (hrs)</th>
                  <th className="border px-4 py-2">Total Price</th>
                  <th className="border px-4 py-2">Request Status</th>
                  <th className="border px-4 py-2">Delivery Status</th>
                  <th className="border px-4 py-2">Driver Name</th>
                  <th className="border px-4 py-2">Driver Email</th>
                  <th className="border px-4 py-2">Driver Mobile</th>
                  <th className="border px-4 py-2">Actions</th>{" "}
                  {/* Add Actions column */}
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking, index) => (
                  <tr key={index}>
                    <td className="border px-4 py-2">
                      {booking.pickup_location}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.drop_location}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.distance_to_cover}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.estimated_delivery_time}
                    </td>
                    <td className="border px-4 py-2">{booking.total_price}</td>
                    <td className="border px-4 py-2">
                      {booking.request_status}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.delivery_status}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.driver_details.name}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.driver_details.email}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.driver_details.mobile}
                    </td>
                    <td className="border px-4 py-2">
                      {booking.request_status === "Accepted" &&
                        booking.delivery_status === "Delivered" && (
                          <button
                            className="bg-blue-500 text-white px-4 py-2 rounded"
                            onClick={() =>
                              updateOrderStatus(booking.booking_id)
                            } // Use booking_id for the API call
                          >
                            Confirm Order Received
                          </button>
                        )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No bookings found.</p>
          )}
        </div>
      </div>
    </section>
  );
}
