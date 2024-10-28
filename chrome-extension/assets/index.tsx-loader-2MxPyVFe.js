(function () {
  'use strict';

  const injectTime = performance.now();
  (async () => {
    const { onExecute } = await import("./chunk-CBVaWBKk.js");
    onExecute?.({ perf: { injectTime, loadTime: performance.now() - injectTime } });
  })().catch(console.error);

})();
