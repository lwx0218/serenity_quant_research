(() => {
  const rect = (element) => {
    if (!element) return null;
    const value = element.getBoundingClientRect();
    return {
      left: Math.round(value.left * 10) / 10,
      top: Math.round(value.top * 10) / 10,
      right: Math.round(value.right * 10) / 10,
      bottom: Math.round(value.bottom * 10) / 10,
      width: Math.round(value.width * 10) / 10,
      height: Math.round(value.height * 10) / 10
    };
  };

  const viewportWidth = document.documentElement.clientWidth;
  const viewportHeight = document.documentElement.clientHeight;
  const bodyRect = rect(document.body);
  const app = document.querySelector("#cpo-explorer-app") ?? document.querySelector("main");
  const appRect = rect(app);
  const visibleElements = [...document.querySelectorAll("body *")].filter((element) => {
    const box = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return box.width > 0 && box.height > 0 && style.display !== "none" && style.visibility !== "hidden";
  });
  const horizontalOffenders = visibleElements
    .filter((element) => {
      const box = element.getBoundingClientRect();
      return box.left < -1 || box.right > viewportWidth + 1;
    })
    .slice(0, 20)
    .map((element) => ({
      selector: element.id ? `#${element.id}` : `${element.tagName.toLowerCase()}.${[...element.classList].slice(0, 2).join(".")}`,
      rect: rect(element)
    }));

  const leftGap = appRect?.left ?? 0;
  const rightGap = appRect ? viewportWidth - appRect.right : 0;
  const balanceTolerance = Math.max(24, viewportWidth * 0.02);

  return {
    viewport: { width: viewportWidth, height: viewportHeight },
    document: {
      scrollWidth: document.documentElement.scrollWidth,
      horizontalScroll: document.documentElement.scrollWidth > viewportWidth + 1,
      bodyRect
    },
    primarySurface: appRect,
    gutters: appRect ? {
      left: Math.round(leftGap * 10) / 10,
      right: Math.round(rightGap * 10) / 10,
      delta: Math.round(Math.abs(leftGap - rightGap) * 10) / 10,
      balanced: Math.abs(leftGap - rightGap) <= balanceTolerance,
      widthRatio: Math.round((appRect.width / viewportWidth) * 1000) / 1000
    } : null,
    horizontalOffenders
  };
})()
