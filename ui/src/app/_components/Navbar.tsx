"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

export default function Navbar() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    const validateToken = async () => {
      const currentToken = localStorage.getItem("access_token");
      const role = localStorage.getItem("role");
      const userId = localStorage.getItem("userid");

      if (!currentToken || !userId) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `http://localhost:3001/user/profile?user_id=${userId}`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${currentToken}`,
            },
          }
        );
        if (response.ok) {
          const data = await response.json();
          setUserProfile(data);
        } else {
          toast.error("Session expired. Logging out...");
          localStorage.removeItem("access_token");
          localStorage.removeItem("userid");
          localStorage.removeItem("role");
          router.push("/login");
        }
      } catch (error) {
        console.error("Error validating token:", error);
        toast.error("An error occurred while validating token.");
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };

    validateToken();
  }, []);

  return (
    <nav className="bg-backgroundSecondary w-full font-montserrat">
      <div className="max-w-[1280px] mx-auto p-5 flex justify-between items-center">
        <Link
          href="/"
          style={{ textDecoration: "none" }}
          className="text-2xl font-semibold"
        >
          Logi<span className="text-textPrimary">Connect</span>
        </Link>
        <div className="flex justify-center items-center gap-x-5">
          {isLoading ? (
            <span>Loading...</span>
          ) : userProfile ? (
            <>
              <Link
                href="/user/profile"
                className="py-2 px-4 bg-backgroundSecondary hover:bg-textSecondary hover:text-textWhite transition duration-500 rounded-xl text-sm"
                style={{ textDecoration: "none" }}
              >
                Profile
              </Link>
              <button
                className="py-2 px-4 bg-textSecondary hover:bg-backgroundSecondary hover:text-textSecondary transition duration-500 rounded-xl text-white text-sm"
                onClick={() => {
                  localStorage.removeItem("access_token");
                  localStorage.removeItem("role");
                  localStorage.removeItem("userid");
                  router.push("/login");
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <button
                className="py-2 px-4 bg-backgroundSecondary text-textSecondary border-0 hover:bg-textSecondary hover:text-textWhite transition duration-500 rounded-xl text-sm"
                onClick={() => {
                  router.push("/login");
                }}
              >
                LogIn
              </button>
              <button
                className="py-2 px-4 bg-textSecondary hover:bg-backgroundSecondary border-0 hover:text-textSecondary transition duration-500 rounded-xl text-white text-sm"
                onClick={() => {
                  router.push("/signup");
                }}
              >
                SignUp
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
