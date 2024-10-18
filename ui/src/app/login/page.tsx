"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

export default function Login() {
  const router = useRouter();
  const [isDriver, setIsDriver] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const requiredCredentials = {
    user: {
      email: "roshaen019@gmail.com",
      password: "Roshan@12345",
    },
    driver: {
      email: "driver@example.com",
      password: "Driver@12345",
    },
  };

  const handleSubmit = (e: { preventDefault: () => void }) => {
    e.preventDefault();

    const credentials = isDriver
      ? requiredCredentials.driver
      : requiredCredentials.user;

    if (email === credentials.email && password === credentials.password) {
      toast.success("Login successful!");
      //   router.push(isDriver ? "/driver-dashboard" : "/user-dashboard");
    } else {
      toast.error("Invalid email or password. Please try again.");
    }
  };

  return (
    <section className="bg-backgroundPrimary w-full h-screen flex items-center justify-center font-montserrat">
      <div className="max-w-[500px] w-full mx-auto p-8 bg-white rounded shadow">
        <h2 className="text-3xl font-bold text-center mb-4">Login Page</h2>

        <div className="flex justify-center gap-5 mb-4">
          <button
            className={`px-5 py-3 rounded-l rounded-lg ${
              !isDriver
                ? "bg-textSecondary text-white"
                : "bg-backgroundPrimary text-textSecondary"
            } trasition duration-500`}
            onClick={() => setIsDriver(false)}
          >
            User Login
          </button>
          <button
            className={`px-5 py-3  rounded-r rounded-lg ${
              isDriver
                ? "bg-textSecondary text-white"
                : "bg-backgroundPrimary text-textSecondary"
            } trasition duration-500"
            }`}
            onClick={() => setIsDriver(true)}
          >
            Driver Login
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-lg">
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
              className="w-full p-2 border border-1 rounded"
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
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-backgroundSecondary hover:bg-textSecondary hover:text-textWhite transition duration-500 rounded-lg border-0"
          >
            Login as {isDriver ? "Driver" : "User"}
          </button>
        </form>
      </div>
    </section>
  );
}
