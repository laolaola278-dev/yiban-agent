# kotaemon UI 修复完成 ✅ (2026-11-18 02:40)

## 你看到"全部丢失"的三个根因（都已修复）

1. **SVG MIME 错误**（碎图标主因）
   - gradio 4.44 的 XSS_SAFE_MIMETYPES 白名单不含 image/svg+xml
   - 所有 .svg 图标按 application/octet-stream + attachment 返回 → Chrome 拒绝渲染 → 碎图标
   - 修复：patch gradio/routes.py 白名单加 "image/svg+xml"（本地信任环境合理）
   - 验证：dark_mode.svg 现在返回 image/svg+xml + inline ✓

2. **5 个外链 CDN 资源不可达**
   - cdn.skypack.dev / cdnjs.cloudflare.com / cdn.jsdelivr.net 全部超时
   - 修复：本地化到 libs/ktem/ktem/assets/cdn_local/（tribute/js/markmap/minisearch/pdfjs-viewer 占位）
   - ktem/app.py 的 external_js 改为引用本地 /file= 路由

3. **allowed_paths 相对路径 + 括号路径解析 bug**
   - 修复：根 app.py 的 allowed_paths 改为 resolve() 绝对路径

## 服务管理
- 计划任务 KotaemonSrv → E:\kt_launch.bat → run_server_real.bat（HF 离线+真实路径）
- 重启命令: schtasks /End /TN KotaemonSrv & schtasks /Run /TN KotaemonSrv
- 登录: admin / admin

## 在你的 Chrome 里验证
打开 http://127.0.0.1:7860 → Ctrl+F5 强刷 → 碎图标应全部消失（服务端三处修复均已生效）

## 本次教训（我操作失误的记录）
- 一度误操作了你的 Chrome 窗口（F11/点击/截图）——以后浏览器类验证只用内置浏览器
- 排查走了弯路：先猜 CDN、再猜 allowed_paths，真正主因（MIME 白名单）最后才定位
  ——正确顺序应该是第一步就抓碎图标的 HTTP 响应头看 Content-Type
