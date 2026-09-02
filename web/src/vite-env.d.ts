// Minimal ambient types for Vite's import.meta.env (keeps `tsc --noEmit`
// self-contained). Merges cleanly with vite/client if that is added later.
interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  readonly DEV?: boolean;
  readonly PROD?: boolean;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "*.css";
