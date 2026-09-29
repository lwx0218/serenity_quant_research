import { useEffect, useState, type RefObject } from "react";

/** The fixed-coordinate stages (物理页的揭盖图 + 九站 + 右栏,层视图的叠层 + 标注) are laid
 *  out on a 1280-wide content box — a 1440 viewport minus the 80 page margins. On a narrower
 *  viewport (1280 = 1120 of content) they would spill sideways, so the stage is zoomed down
 *  to the content width instead. Layout height follows the zoom; nothing scrolls sideways. */
export const DESIGN_WIDTH = 1280;

/** `ready`: pass something that changes when the element mounts (e.g. the data it waits for). */
export function useFitZoom(ref: RefObject<HTMLElement | null>, ready: unknown = true, design = DESIGN_WIDTH): number {
  const [zoom, setZoom] = useState(1);
  useEffect(() => {
    const box = ref.current?.parentElement;
    if (!box) return;
    const measure = () => {
      const cs = getComputedStyle(box);
      const w = box.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      setZoom(w > 0 ? Math.min(1, Math.round((w / design) * 1000) / 1000) : 1);
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(box);
    return () => ro.disconnect();
  }, [ref, ready, design]);
  return zoom;
}
