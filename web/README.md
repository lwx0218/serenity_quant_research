# web

Vite + React 19 + TypeScript。没有 UI 框架,没有 Tailwind:所有样式是 `src/styles/tokens.css`(变量)+ `app.css`(基础与五种原语)+ 每页一个 css。

```bash
npm install
npm run dev        # http://localhost:5173,/api 代理到 :8000
npm run build      # tsc --noEmit && vite build
```

- `src/lib/router.tsx` — 40 行的 history 路由:`/`、`/explore/:id`、`/companies`、`/companies/:id`
- `src/lib/theme.ts` — 主题:auto(跟随系统)/ light / dark,存 `localStorage.sqr.theme`;`index.html` 首屏前应用
- `src/components/ExplodedStack.tsx` — 由模块的 `visual` 类型生成分层图 SVG,并暴露每层锚点供引线使用
- `src/pages/ExplorerPage.tsx` — 总览 / 选中 / 部件三种状态在同一页;布局常量 `OVERVIEW` / `FOCUSED`
- 字体自托管在 `public/fonts/`(Geist,OFL)

设计规则见 `../docs/product/design-rules.md`。
