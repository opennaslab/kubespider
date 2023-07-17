import { useEffect, useState } from "react";
import { Input, Button, ButtonProps } from "@component/Input";
import { MessageType, sender } from "@message";
import Storage from "@storage";
import { componentResult } from "../util";

const defaultBtn: ButtonProps = {
  label: "Download",
  type: "primary",
  loading: false,
};

function Download() {
  const [form, setForm] = useState({
    dataSource: "",
    path: "",
  });
  // load config
  useEffect(() => {
    Storage.read().then((config) => {
      setForm((prev) => ({ ...prev, path: config.path || "" }));
    });
  }, []);
  // button state
  const [btn, setBtn] = useState(defaultBtn);
  // update form data
  const handleChange = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };
  // send message to background
  const onClick = async () => {
    setBtn((prev) => ({ ...prev, loading: true }));
    if (!form.dataSource || form.dataSource === "") {
      componentResult(
        {
          label: "No URL!",
          type: "error",
          loading: false,
        },
        defaultBtn,
        setBtn
      );
      return;
    }
    const { path } = await Storage.read();
    if (path !== form.path) {
      Storage.save({ path: form.path });
    }
    // send message to background
    const reply = await sender.sendMessage({
      type: MessageType.Download,
      payload: {
        dataSource: form.dataSource,
        path: form.path,
      },
    });
    if (reply.success) {
      componentResult(
        {
          label: "Download Success!",
          type: "success",
          loading: false,
        },
        defaultBtn,
        setBtn
      );
    } else {
      componentResult(
        {
          label: "Download Error!",
          type: "error",
          loading: false,
        },
        defaultBtn,
        setBtn
      );
    }
  };

  return (
    <>
      <Input
        name="dataSource"
        value={form.dataSource}
        lable="URL"
        onChange={handleChange}
      />
      <Input
        name="path"
        value={form.path}
        lable="PATH"
        onChange={handleChange}
      />
      <Button
        label={btn.label}
        type={btn.type}
        loading={btn.loading}
        onClick={onClick}
      />
    </>
  );
}

export default Download;
