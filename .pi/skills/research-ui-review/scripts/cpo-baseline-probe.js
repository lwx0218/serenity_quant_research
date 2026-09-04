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

  const viewportWidth = document.documentElement.clientWidth;
  const app = rect("#cpo-explorer-app");
  const heading = rect(".cpo-page-heading");
  const workbench = rect(".cpo-explorer-workbench");
  const canvas = rect("#cpo-canvas-frame");
  const stage = rect(".cpo-viewport-stage");
  const leftGap = app?.left ?? 0;
  const rightGap = app ? viewportWidth - app.right : 0;
  const alignmentTolerance = 24;
  const gutterTolerance = Math.max(24, viewportWidth * 0.02);
  const data = {
    capturedAt: new Date().toISOString(),
    viewport: { width: viewportWidth, height: document.documentElement.clientHeight },
    selected: document.querySelector("#cpo-explorer-app")?.dataset.selected ?? null,
    view: document.querySelector("#cpo-explorer-app")?.dataset.view ?? null,
    app,
    heading,
    workbench,
    canvas,
    stage,
    checks: {
      idle: (document.querySelector("#cpo-explorer-app")?.dataset.selected ?? "") === "",
      drawerHidden: !!document.querySelector("#cpo-research-drawer")?.hidden,
      headingTracksAppLeft: !!heading && !!app && Math.abs(heading.left - app.left) <= alignmentTolerance,
      headingLeftDelta: heading && app ? round(heading.left - app.left) : null,
      balancedOuterGutters: !!app && Math.abs(leftGap - rightGap) <= gutterTolerance,
      outerGutters: app ? { left: round(leftGap), right: round(rightGap), delta: round(Math.abs(leftGap - rightGap)) } : null,
      appWidthRatio: app ? round(app.width / viewportWidth) : null
    }
  };

  window.__researchUiReview = window.__researchUiReview || {};
  window.__researchUiReview.cpoBaseline = data;
  return data;
})()
