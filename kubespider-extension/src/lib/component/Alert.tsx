import { useEffect, useState } from "react";
import { Error, Success } from "./Svg";
import classNames from "classnames";

interface AlertProps {
  title: string;
  content: string;
  type?: "success" | "error";
  delay?: number;
}

function Alert({ title, content, type = "success", delay = 4500 }: AlertProps) {
  const [show, setShow] = useState(true);

  const classname = classNames([
    "border-t-4 rounded-b px-4 py-3 shadow-md",
    {
      "bg-red-100 border-red-500 text-red-900": type === "error",
      "bg-teal-100 border-teal-500 text-teal-900": type === "success",
    },
  ]);

  useEffect(() => {
    setInterval(() => {
      setShow(false);
    }, delay);
  });

  return (
    <>
      {show && (
        <div className={classname} role="alert">
          <div className="flex items-center">
            <div>{type === "error" ? <Error /> : <Success />}</div>
            <div>
              <p className="font-bold">{title}</p>
              <p className="text-sm break-all">{content}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export { Alert };
