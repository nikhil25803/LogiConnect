"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();
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
          <button
            className="py-2 px-4 bg-backgroundSecondary hover:bg-textSecondary hover:text-textWhite transition duration-500 rounded-xl text-sm"
            onClick={() => {
              router.push("/login");
            }}
          >
            LogIn
          </button>
          <button
            className="py-2 px-4 bg-textSecondary hover:bg-backgroundSecondary hover:text-textSecondary transition duration-500 rounded-xl text-white  text-sm"
            onClick={() => {
              router.push("/signup");
            }}
          >
            SignUp
          </button>
        </div>
      </div>
    </nav>
  );
}
