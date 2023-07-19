import { useState } from "react";
import { Nav, NavItemProps } from "@component/Nav";
import Download from "./Download";
import Config from "./Config";
import Refresh from "./Refresh";
import GitHub from "./Github";

const items: NavItemProps[] = [
  {
    key: "1",
    children: <img src="/img/download.png" className="w-5 h-5" />,
  },
  {
    key: "2",
    children: <img src="/img/menu.png" className="w-5 h-5" />,
  },
  {
    key: "3",
    children: <img src="/img/refresh.png" className="w-5 h-5" />,
  },
  {
    key: "4",
    children: <img src="/img/github.png" className="w-5 h-5" />,
  },
];

interface RouterItemProps {
  key: string;
  children: React.ReactNode;
}

const router: RouterItemProps[] = [
  {
    key: "1",
    children: <Download />,
  },
  {
    key: "2",
    children: <Config />,
  },
  {
    key: "3",
    children: <Refresh />,
  },
  {
    key: "4",
    children: <GitHub />,
  },
];

function Router({
  items,
  activeKey,
}: {
  items: RouterItemProps[];
  activeKey: string;
}) {
  return <>{items.filter((item) => item.key === activeKey)[0]?.children}</>;
}

function App() {
  const [activeKey, setActiveKey] = useState("1");

  const onChange = (key: string) => {
    setActiveKey(key);
  };

  return (
    <div className="w-80 h-auto py-2">
      <Nav items={items} onChange={onChange} />
      <div className="flex flex-col space-y-3 mt-2 mx-2">
        <Router items={router} activeKey={activeKey} />
      </div>
    </div>
  );
}

export default App;
