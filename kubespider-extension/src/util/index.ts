function uuidv4(): string {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return `${1e7}-${1e3}-${4e3}-${8e3}-${1e11}`.replace(/[018]/g, (c: any) =>
    (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  );
}

async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function componentResult<T>(
  restlt: T,
  preState: T,
  setFunction: (value: T) => void,
  delay?: number
) {
  setFunction(restlt);
  return new Promise((resolve) => setTimeout(resolve, delay || 2000)).then(() =>
    setFunction(preState)
  );
}

export { uuidv4, delay, componentResult };
