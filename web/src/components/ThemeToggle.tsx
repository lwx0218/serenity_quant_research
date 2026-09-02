import { useTheme } from "../lib/theme";

/** Cycles auto → light → dark. The icon shows what is on screen right now. */
export function ThemeToggle() {
  const { pref, effective, cycle } = useTheme();
  const title =
    pref === "auto" ? `跟随系统(当前${effective === "dark" ? "深色" : "浅色"})· 点击切换` : pref === "light" ? "浅色 · 点击切换" : "深色 · 点击切换";
  return (
    <button type="button" className="theme-btn" onClick={cycle} title={title} aria-label={title}>
      {effective === "dark" ? <Moon /> : <Sun />}
    </button>
  );
}

function Sun() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" aria-hidden="true">
      <circle cx="8" cy="8" r="3" />
      <path d="M8 1.5v1.8M8 12.7v1.8M1.5 8h1.8M12.7 8h1.8M3.4 3.4l1.3 1.3M11.3 11.3l1.3 1.3M3.4 12.6l1.3-1.3M11.3 4.7l1.3-1.3" />
    </svg>
  );
}

function Moon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" aria-hidden="true">
      <path d="M13.5 10.2A6 6 0 0 1 5.8 2.5a6 6 0 1 0 7.7 7.7Z" />
    </svg>
  );
}
