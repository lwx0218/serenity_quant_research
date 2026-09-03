# Teardown 方向稿 v3(2026-09-03,已收敛)

`*.html` 是画布「Teardown 研究工作台」十二块画板的静态导出(六页 × 浅 / 深),可直接用浏览器打开,1440 宽。
`contact-sheet.jpg` 是十二块画板的缩略总览。`gen/` 是生成这些画板的脚本:

```bash
cd gen && python3 gen_v3.py   # 产出 *.dc.html 与 canvas.json(Claude Design 画布格式)
```

规则见 `../../design-rules.md`;画板里的事件、价格、读数全部是样式示例。
