import { GrLinkedin, GrGithub } from "react-icons/gr";
import { BsTwitterX } from "react-icons/bs";
export default function Footer() {
  return (
    <footer className="bg-backgroundSecondary w-full text-textSecondary">
      <div className="max-w-[1280px] flex justify-between items-center mx-auto p-5">
      <h3>LogiConnect @2024</h3>
        <div className="flex gap-x-5">
          <a
            className="hover:text-textDark transition duration-300"
            href="https://www.linkedin.com/in/nikhil25803/"
            target="_blank"
          >
            <GrLinkedin />
          </a>
          <a
            className="hover:text-textDark transition duration-300"
            href="https://github.com/nikhil25803"
            target="_blank"
          >
            <GrGithub />
          </a>
          <a
            className="hover:text-textDark transition duration-300"
            href="https://twitter.com/humans_write"
            target="_blank"
          >
            <BsTwitterX />
          </a>
        </div>
      </div>
    </footer>
  );
}
