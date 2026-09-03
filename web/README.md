# web

Vite + React 19 + TypeScript。没有 UI 框架,没有 Tailwind:所有样式是 `src/styles/tokens.css`(变量)+ `app.css`(基础与五种原语)+ 每页一个 css。

```bash
npm install
npm run dev        # http://localhost:5173,/api 代理到 :8000
npm run build      # tsc --noEmit && vite build
```

- `src/lib/router.tsx` — history 路由:`/`、`/explore/:id`、`/companies`、`/companies/:id`、`/baskets/:node`、`/research`、`/judgement/:subject`
- `src/lib/theme.ts` — 主题:auto(跟随系统)/ light / dark,存 `localStorage.sqr.theme`;`index.html` 首屏前应用
- `src/lib/signal.ts` — 方向色约定:红涨绿跌(默认)/ 绿涨红跌,存 `localStorage.td.signal`,通过 `data-signal` 交换 `--sig-pos/--sig-neg`
- `src/components/Signal.tsx` — 方向标记 `Dir`、带号数字 `Sig`、结论行 `Conclusion`、`AsOf`、时效 `Fresh`
- `src/components/Research.tsx` — 事件表(窄 / 宽)、判断块(`[[链接]]` 解析)、共振块、拥挤度读数
- `src/components/LineChart.tsx` — 指数化折线 + 事件标记 + 十字线
- `src/components/ExplodedStack.tsx` — 由模块的 `visual` 类型生成分层图 SVG,并暴露每层锚点供引线使用
- `src/pages/ExplorerPage.tsx` — 总览 / 选中 / 部件三种状态在同一页;布局常量 `OVERVIEW` / `FOCUSED`
- `src/pages/{JudgementPage,CompanyPage,ResearchPage,BasketPage}.tsx` — 编辑判断 / 公司 / 研究收件箱 / 环节篮子
- 字体自托管在 `public/fonts/`(Geist,OFL)

设计规则见 `../docs/product/design-rules.md`。
