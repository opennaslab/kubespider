import classnames from "classnames";
import { ChangeEvent } from "react";

function Input({
  name,
  value,
  lable,
  onChange,
}: {
  name: string;
  value?: string;
  lable: string;
  onChange?: (key: string, value: string) => void;
}) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange?.(name, e.target.value);
  };

  return (
    <div className="flex rounded-md">
      <span className="px-2 inline-flex items-center min-w-fit rounded-l-md border border-r-0 border-gray-200 bg-gray-50 text-sm font-medium">
        {lable}
      </span>
      <input
        name={name}
        type="text"
        className="py-2 px-1 pr-11 block w-full border-gray-200 rounded-r-md text-sm focus:z-10 border-l-0 border-t border-r border-b foucs:border-blue-500 focus:ring-4 focus:ring-blue-300 focus:outline-none"
        value={value}
        onChange={(e) => handleChange(e)}
      />
    </div>
  );
}

interface ButtonProps {
  label: string;
  type?: "primary" | "success" | "error";
  loading: boolean;
}

function Button({
  label,
  type = "primary",
  loading = false,
  onClick,
}: {
  label: string;
  type?: "primary" | "success" | "error";
  loading?: boolean;
  onClick: () => void;
}) {
  const handleClick = () => {
    onClick?.();
  };

  const className = classnames([
    "px-4 py-2 text-white rounded-md text-sm font-medium active:ring-4",
    {
      "bg-blue-500 hover:bg-blue-700 active:ring-blue-300": type === "primary",
      "bg-red-500 hover:bg-red-700 active:ring-red-300": type === "error",
      "bg-teal-500 hover:bg-teal-700 active:ring-teal-300": type === "success",
    },
  ]);

  return (
    <button className={className} onClick={handleClick}>
      {loading ? <Loading /> : label}
    </button>
  );
}

function Loading() {
  return (
    <div
      className="inline-block h-4 w-4 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"
      role="status"
    >
      <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">
        Loading...
      </span>
    </div>
  );
}

function Switch({
  name,
  value,
  label,
  onChange,
}: {
  name: string;
  value?: boolean;
  label: string;
  onChange?: (key: string, checked: boolean) => void;
}) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange?.(name, e.target.checked);
  };
  return (
    <label
      className="relative inline-flex items-center cursor-pointer"
      htmlFor={name}
    >
      <input
        id={name}
        name={name}
        type="checkbox"
        className="sr-only peer"
        checked={value}
        onChange={handleChange}
      />
      <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
      <span className="ml-3 text-sm font-medium">{label}</span>
    </label>
  );
}

export { Input, Button, Switch };
export type { ButtonProps };
