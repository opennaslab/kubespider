import { Error, Success, Info } from "./Svg";
import classNames from "classnames";

interface AlertProps {
  title: string;
  content: string;
  type?: "success" | "error" | "info";
}

function Alert({ title, content, type = "success" }: AlertProps) {
  const classname = classNames([
    "border-t-4 rounded-b px-4 py-3 shadow-md",
    {
      "bg-red-100 border-red-500 text-red-900": type === "error",
      "bg-teal-100 border-teal-500 text-teal-900": type === "success",
      "bg-blue-100 border-blue-500 text-blue-900": type === "info",
    },
  ]);

  function renderIcon(type: string) {
    switch (type) {
      case "error":
        return <Error />;
      case "success":
        return <Success />;
      case "info":
        return <Info />;
    }
  }

  return (
    <div className={classname} role="alert">
      <div className="flex items-center">
        <div>{renderIcon(type)}</div>
        <div>
          <p className="font-bold">{title}</p>
          <p className="text-sm break-all">{content}</p>
        </div>
      </div>
    </div>
  );
}

export { Alert };
