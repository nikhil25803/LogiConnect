"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";

export default function SignUp() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [country, setCountry] = useState("+91");
  const [state, setState] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();

    if (!name || !email || !state || !phoneNumber || !password) {
      toast.error("Please fill in all fields.");
      return;
    }

    const payload = {
      name,
      email,
      country,
      state,
      country_code: country,
      phone_number: phoneNumber,
      password,
    };

    try {
      const response = await fetch("http://localhost:3001/user/onboard", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 201) {
        toast.success(
          "Signup successful! Please check your email for verification."
        );

        setName("");
        setEmail("");
        setState("");
        setPhoneNumber("");
        setPassword("");

        router.push("/login");
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || "Signup failed! Please try again.");
      }
    } catch (error) {
      toast.error("An error occurred. Please try again later.");
      console.error("Signup error:", error);
    }
  };

  return (
    <section className="bg-backgroundPrimary w-full h-screen font-montserrat">
      <div className="max-w-[1280px] w-full mx-auto flex items-center justify-center">
        <div className="max-w-[500px] w-full mx-auto p-8 bg-white rounded shadow">
          <h2 className="text-3xl font-bold text-center mb-4">SignUp Page</h2>

          <form onSubmit={handleSubmit} className="space-y-4 text-lg">
            <div>
              <label htmlFor="name" className="block text-textSecondary">
                Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>

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
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>

            <div>
              <label htmlFor="country" className="block text-textSecondary">
                Country Code
              </label>
              <input
                id="country"
                type="text"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                required
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>

            <div>
              <label htmlFor="state" className="block text-textSecondary">
                State
              </label>
              <input
                id="state"
                type="text"
                value={state}
                onChange={(e) => setState(e.target.value)}
                required
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-textSecondary">
                Phone Number
              </label>
              <input
                id="phone"
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
                className="w-full p-2 border border-gray-300 rounded"
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
              className="w-full py-3 bg-backgroundSecondary hover:bg-textSecondary hover:text-white transition duration-500 rounded-lg border-0"
            >
              Sign Up
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
