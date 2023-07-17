import { useEffect, useState } from "react";
import { Input, Switch, Button, ButtonProps } from "@component/Input";
import Storage from "@storage";
import { api, healthzRequest } from "@api";
import { componentResult } from "../util";

const defaultBtn: ButtonProps = {
  label: "Save",
  type: "primary",
  loading: false,
};

function Config() {
  // form state
  const [form, setForm] = useState({
    server: "",
    enableAuth: false,
    token: "",
    captureCookies: false,
  });
  // sumbit button state
  const [btn, setBtn] = useState(defaultBtn);
  // load config
  useEffect(() => {
    Storage.read().then((config) => {
      setForm({
        server: config.server || "",
        enableAuth: config.auth || false,
        token: config.token || "",
        captureCookies: config.captureCookies || false,
      });
    });
  }, []);
  // handle form change
  const handleChange = (key: string, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };
  // handle submit
  const handleClick = async () => {
    setBtn((prev) => ({ ...prev, loading: true }));
    const param = healthzRequest(form.server);
    const response = await api(param);
    if (response.status !== 200) {
      componentResult(
        {
          label: "Save Error!",
          type: "error",
          loading: false,
        },
        defaultBtn,
        setBtn
      );
      return;
    }
    await Storage.save({
      server: form.server,
      auth: form.enableAuth,
      token: form.token,
      captureCookies: form.captureCookies,
    });

    componentResult(
      {
        label: "Saved",
        type: "success",
        loading: false,
      },
      defaultBtn,
      setBtn
    );
  };

  return (
    <>
      <Input
        name="server"
        value={form.server}
        lable="SERVER"
        onChange={handleChange}
      />
      <Switch
        name="enableAuth"
        value={form.enableAuth}
        label="Enable Auth"
        onChange={handleChange}
      />
      {form.enableAuth && (
        <Input
          name="token"
          value={form.token}
          lable="TOKEN"
          onChange={handleChange}
        />
      )}
      <Switch
        name="captureCookies"
        value={form.captureCookies}
        label="Capture Cookies"
        onChange={handleChange}
      />
      <Button
        label={btn.label}
        type={btn.type}
        loading={btn.loading}
        onClick={handleClick}
      />
    </>
  );
}

export default Config;
