import classNames from "classnames";
import { ReactNode, useEffect, useState } from "react";

interface NavItemProps {
  active?: boolean;
  key: string;
  children?: ReactNode;
}

function NavItem({
  id,
  onClick,
  active = false,
  children,
}: {
  id: string;
  onClick: (id: string) => void;
  active?: boolean;
  children?: ReactNode;
}) {
  const handleClick = () => {
    onClick(id);
  };

  const tagAClass = classNames([
    "block py-2 px-4 border-l border-t border-r rounded-t",
    {
      "border-transparent": !active,
      "hover:bg-gray-100 hover:border-gray-100": !active,
    },
  ]);

  const tagLiClass = classNames({
    "bg-white": true,
    "-mb-px": active,
  });

  return (
    <li className={tagLiClass} onClick={handleClick}>
      <a className={tagAClass} href="#">
        {children}
      </a>
    </li>
  );
}

function Nav({
  items,
  onChange,
}: {
  items: NavItemProps[];
  onChange?: (key: string) => void;
}) {
  const defaultActive = items.filter((item) => item.active)?.pop()?.key;

  const [activeKey, setActiveKey] = useState<string>(
    defaultActive ? defaultActive : "1"
  );

  const handleClick = (key: string) => {
    setActiveKey(key);
  };

  useEffect(() => {
    onChange?.(activeKey);
  }, [activeKey, onChange]);

  return (
    <ul className="flex border-b space-x-1 px-2">
      {items.map((item) => (
        <NavItem
          key={item.key}
          id={item.key}
          active={activeKey === item.key}
          onClick={handleClick}
        >
          {item.children}
        </NavItem>
      ))}
    </ul>
  );
}

export type { NavItemProps };
export { Nav };
