(() => {
  const round = (value) => Math.round(value * 10) / 10;
  const rect = (selector) => {
    const element = document.querySelector(selector);
    if (!element) return null;
    const value = element.getBoundingClientRect();
    return {
      left: round(value.left),
      top: round(value.top),
      right: round(value.right),
      bottom: round(value.bottom),
      width: round(value.width),
      height: round(value.height)
    };
  };
  const delta = (before, after, key) => before && after ? round(after[key] - before[key]) : null;
  const close = (value, tolerance) => value !== null && Math.abs(value) <= tolerance;

  const baseline = window.__researchUiReview?.cpoBaseline ?? null;
  const appElement = document.querySelector("#cpo-explorer-app");
  const drawerElement = document.querySelector("#cpo-research-drawer");
  const app = rect("#cpo-explorer-app");
  const heading = rect(".cpo-page-heading");
  const workbench = rect(".cpo-explorer-workbench");
  const canvas = rect("#cpo-canvas-frame");
  const stage = rect(".cpo-viewport-stage");
  const drawer = rect("#cpo-research-drawer");
  const drawerStyle = drawerElement ? getComputedStyle(drawerElement) : null;
  const selectedId = appElement?.dataset.selected ?? "";
  const view = appElement?.dataset.view ?? "";
  const scene = view === "three" ? "three" : "flat";
  const activeComponent = document.querySelector(`#cpo-scene-${scene} .cpo-component.is-active[data-component-id="${CSS.escape(selectedId)}"]`);
  const activeCallout = document.querySelector(`#cpo-scene-${scene} .cpo-callout.is-active[data-component-id="${CSS.escape(selectedId)}"]`);
  const stateTitle = document.querySelector("#cpo-state-line strong")?.textContent?.trim() ?? "";
  const drawerTitle = document.querySelector("#cpo-drawer-title")?.textContent?.trim() ?? "";
  const drawerText = document.querySelector("#cpo-drawer-content")?.textContent?.trim() ?? "";
  const calloutTitle = activeCallout?.querySelector(".cpo-callout-title")?.textContent?.trim() ?? "";
  const workbenchWidthDelta = delta(baseline?.workbench, workbench, "width");
  const workbenchLeftDelta = delta(baseline?.workbench, workbench, "left");
  const canvasWidthDelta = delta(baseline?.canvas, canvas, "width");
  const stageWidthDelta = delta(baseline?.stage, stage, "width");
  const topDelta = workbench && drawer ? round(drawer.top - workbench.top) : null;
  const rightDelta = workbench && drawer ? round(drawer.right - workbench.right) : null;
  const bottomDelta = workbench && drawer ? round(drawer.bottom - workbench.bottom) : null;
  const headingLeftDelta = heading && app ? round(heading.left - app.left) : null;

  return {
    capturedAt: new Date().toISOString(),
    baselineAvailable: !!baseline,
    selectedId,
    view,
    identity: { calloutTitle, stateTitle, drawerTitle },
    rects: { app, heading, workbench, canvas, stage, drawer },
    deltasFromIdle: { workbenchWidthDelta, workbenchLeftDelta, canvasWidthDelta, stageWidthDelta },
    drawerAlignment: { topDelta, rightDelta, bottomDelta },
    drawerPresentation: drawerStyle ? {
      position: drawerStyle.position,
      transform: drawerStyle.transform,
      transitionProperty: drawerStyle.transitionProperty,
      transitionDuration: drawerStyle.transitionDuration,
      zIndex: drawerStyle.zIndex
    } : null,
    checks: {
      selectedIdentityPresent: selectedId.length > 0,
      componentAndCalloutActive: !!activeComponent && !!activeCallout,
      stateLineSynchronized: selectedId.length > 0 && stateTitle.length > 0 && stateTitle.toLowerCase().includes("selected"),
      drawerVisible: !!drawerElement && !drawerElement.hidden && drawerElement.classList.contains("is-open"),
      drawerHasImmediateContext: drawerText.length > 0 && (drawerText.includes(calloutTitle) || drawerText.includes(selectedId) || drawerText.includes("正在读取")),
      canvasInvariant: !!baseline && close(workbenchWidthDelta, 2) && close(workbenchLeftDelta, 2) && close(canvasWidthDelta, 2) && close(stageWidthDelta, 2),
      overlayPositioning: !!drawerStyle && (drawerStyle.position === "absolute" || drawerStyle.position === "fixed"),
      drawerSlidesByTransform: !!drawerStyle && drawerStyle.transitionProperty.split(",").map((x) => x.trim()).includes("transform"),
      drawerTopAligned: close(topDelta, 8),
      drawerRightAligned: close(rightDelta, 8),
      drawerBottomAligned: close(bottomDelta, 8),
      headingTracksAppLeft: close(headingLeftDelta, 24)
    }
  };
})()
