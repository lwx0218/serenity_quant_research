import { match, useRouter } from "./lib/router";
import { BasketPage } from "./pages/BasketPage";
import { CompaniesPage } from "./pages/CompaniesPage";
import { CompanyPage } from "./pages/CompanyPage";
import { ExplorerPage } from "./pages/ExplorerPage";
import { JudgementPage } from "./pages/JudgementPage";
import { ResearchPage } from "./pages/ResearchPage";

export function App() {
  const { route } = useRouter();
  const p = route.path;

  let m: Record<string, string> | null;
  if (p === "/" || p === "") return <ExplorerPage />;
  if ((m = match("/explore/:id", p))) return <ExplorerPage nodeId={m.id} />;
  if (p === "/companies") return <CompaniesPage />;
  if ((m = match("/companies/:id", p))) return <CompanyPage id={m.id} />;
  if ((m = match("/baskets/:id", p))) return <BasketPage nodeId={m.id} />;
  if (p === "/research") return <ResearchPage />;
  if ((m = match("/judgement/:subject", p))) return <JudgementPage subject={m.subject} />;
  return <ExplorerPage />;
}
