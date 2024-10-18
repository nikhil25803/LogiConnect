"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

export default function Login() {
  const router = useRouter();
  const [isDriver, setIsDriver] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:3001/user/login", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const { access_token, userid, driverid } = data;

        const role = userid ? "user" : driverid ? "driver" : null;

        if (role) {
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("userid", userid || driverid);
          localStorage.setItem("role", role);

          toast.success("Login successful!");
          router.push(
            role === "driver" ? "/driver/profile" : "/user/profile"
          );
        } else {
          toast.error("User ID or Driver ID not found in the response.");
        }
      } else {
        toast.error("Invalid email or password.");
      }
    } catch (error) {
      toast.error("An error occurred while logging in. Please try again.");
    }
  };

  return (
    <section className="bg-backgroundPrimary w-full h-screen flex items-center justify-center font-montserrat">
      <div className="max-w-[500px] w-full mx-auto p-8 bg-white rounded shadow-lg">
        <h2 className="text-3xl font-bold text-center mb-6">Login Page</h2>

        <div className="flex justify-center gap-4 mb-6">
          <button
            className={`px-5 py-3 rounded-l-lg ${
              !isDriver
                ? "bg-textSecondary text-white"
                : "bg-backgroundPrimary text-textSecondary"
            } transition-all duration-300 ease-in-out`}
            onClick={() => setIsDriver(false)}
          >
            User Login
          </button>
          <button
            className={`px-5 py-3 rounded-r-lg ${
              isDriver
                ? "bg-textSecondary text-white"
                : "bg-backgroundPrimary text-textSecondary"
            } transition-all duration-300 ease-in-out`}
            onClick={() => setIsDriver(true)}
          >
            Driver Login
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-textSecondary">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full p-3 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-textSecondary">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full p-3 border border-gray-300 rounded-lg"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-backgroundSecondary text-white hover:bg-textSecondary transition-all duration-300 ease-in-out rounded-lg"
          >
            Login as {isDriver ? "Driver" : "User"}
          </button>
        </form>
      </div>
    </section>
  );
}
