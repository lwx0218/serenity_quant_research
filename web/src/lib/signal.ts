/** Direction-colour convention: "cn" 红涨绿跌 (default) or "intl" 绿涨红跌. */
import { useState } from "react";

export type SignalPref = "cn" | "intl";
const KEY = "td.signal";

export function readSignalPref(): SignalPref {
  try {
    return localStorage.getItem(KEY) === "intl" ? "intl" : "cn";
  } catch {
    return "cn";
  }
}

export function applySignalPref(p: SignalPref) {
  const root = document.documentElement;
  if (p === "intl") root.setAttribute("data-signal", "intl");
  else root.removeAttribute("data-signal");
  try {
    if (p === "intl") localStorage.setItem(KEY, "intl");
    else localStorage.removeItem(KEY);
  } catch {
    /* private mode */
  }
}

export function useSignalPref() {
  const [pref, setPref] = useState<SignalPref>(readSignalPref);
  const set = (p: SignalPref) => { applySignalPref(p); setPref(p); };
  const toggle = () => set(pref === "cn" ? "intl" : "cn");
  return { pref, set, toggle };
}
