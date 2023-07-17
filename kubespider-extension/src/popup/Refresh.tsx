import { useState } from "react";
import { Button, ButtonProps } from "@component/Input";
import { api, refreshRequest } from "@api";
import Storage from "@storage";
import { componentResult } from "../util";

const defaultBtn: ButtonProps = {
  label: "Refresh",
  type: "primary",
  loading: false,
};

function Refresh() {
  const [btn, setBtn] = useState(defaultBtn);

  const onClick = async () => {
    // Set loading
    setBtn({ ...btn, loading: true });

    const { server, token } = await Storage.read();
    if (!server || server === "") {
      componentResult(
        {
          label: "No Server!",
          type: "error",
          loading: false,
        },
        defaultBtn,
        setBtn
      );
      return;
    }
    const response = await api(refreshRequest(server, token));
    if (response.status === 200) {
      componentResult(
        {
          label: "Refresh Success!",
          type: "success",
          loading: false,
        },
        defaultBtn,
        setBtn
      );
      return;
    }
    componentResult(
      {
        label: "Refresh Error!",
        type: "error",
        loading: false,
      },
      defaultBtn,
      setBtn
    );
  };

  return (
    <Button
      label={btn.label}
      type={btn.type}
      loading={btn.loading}
      onClick={onClick}
    />
  );
}

export default Refresh;
