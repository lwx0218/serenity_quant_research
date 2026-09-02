/**
 * Theme: "auto" follows the OS, "light"/"dark" are explicit. The choice is
 * stored per browser; index.html applies it before first paint.
 */
import { useEffect, useState } from "react";

export type ThemePref = "auto" | "light" | "dark";
const KEY = "sqr.theme";

export function readPref(): ThemePref {
  try {
    const v = localStorage.getItem(KEY);
    return v === "light" || v === "dark" ? v : "auto";
  } catch {
    return "auto";
  }
}

export function applyPref(pref: ThemePref) {
  const root = document.documentElement;
  if (pref === "auto") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", pref);
  try {
    if (pref === "auto") localStorage.removeItem(KEY);
    else localStorage.setItem(KEY, pref);
  } catch {
    /* private mode etc. */
  }
}

export function systemIsDark(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function useTheme() {
  const [pref, setPref] = useState<ThemePref>(readPref);
  const [sysDark, setSysDark] = useState<boolean>(systemIsDark);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const on = () => setSysDark(mq.matches);
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);

  const effective: "light" | "dark" = pref === "auto" ? (sysDark ? "dark" : "light") : pref;

  const set = (next: ThemePref) => {
    applyPref(next);
    setPref(next);
  };
  /** auto → light → dark → auto */
  const cycle = () => set(pref === "auto" ? "light" : pref === "light" ? "dark" : "auto");

  return { pref, effective, set, cycle };
}
