import { match, useRouter } from "./lib/router";
import { CompaniesPage } from "./pages/CompaniesPage";
import { CompanyPage } from "./pages/CompanyPage";
import { ExplorerPage } from "./pages/ExplorerPage";

export function App() {
  const { route } = useRouter();
  const p = route.path;

  let m: Record<string, string> | null;
  if (p === "/" || p === "") return <ExplorerPage />;
  if ((m = match("/explore/:id", p))) return <ExplorerPage nodeId={m.id} />;
  if (p === "/companies") return <CompaniesPage />;
  if ((m = match("/companies/:id", p))) return <CompanyPage id={m.id} />;
  return <ExplorerPage />;
}
