import { useEffect } from "react";
import { Tab } from "@bridge";

function GitHub() {
  useEffect(() => {
    Tab.create("https://github.com/opennaslab/kubespider");
  });

  return <></>;
}

export default GitHub;
