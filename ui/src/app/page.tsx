"use client";
import Lottie from "lottie-react";
import LogisticAnimation from "../../public/asset/LogisticAnimation.json";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter()
  return (
    <main className="bg-backgroundPrimary w-full font-montserrat h-screen">
      <div className="max-w-[1280px] mx-auto p-5 flex items-center justify-center h-screen lg:grid lg:grid-cols-2 lg:items-center lg:h-fit">
        {/* Text section */}
        <div className="lg:text-left">
          <h1 className="text-textSecondary text-4xl">
            Quick & reliable <span className="text-textPrimary">logistics</span>{" "}
            solution.
          </h1>
          <p className="">
            ShipUp delivers an unparalleled customer service through dedicated
            customer teams, engaged people working in an agile culture, and a
            global footprint.
          </p>
          <button className="px-5 py-3 bg-textSecondary hover:bg-backgroundPrimary hover:text-textSecondary transition duration-500 rounded-xl text-white" onClick={() => {
            router.push("user/booking")
          }}>
            Get Started
          </button>
        </div>

        <div className="hidden lg:flex justify-end">
          <Lottie animationData={LogisticAnimation} loop={true} />
        </div>
      </div>
    </main>
  );
}
