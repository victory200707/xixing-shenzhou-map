# 本地 HTTP 运行说明

## 为什么不能双击打开

双击 `index.html` 使用的是 `file:///C:/Users/HUAWEI/Documents/ChatGPT/mask/index.html`。该入口的 origin 通常为 `null`，浏览器会限制 ES Module 的跨文件加载，并可能阻止：

- `src/js/main.js` 的模块执行；
- `fetch('assets/map/metadata/control-points.json')` 的数据读取；
- 依赖这些数据的城市标记、面板、季节和时间轴联动。

因此 `file://` 不是本项目的有效功能验收入口，也不应通过修改地图资产或数据逻辑来绕过限制。

## 正式入口

使用已有本地 HTTP 服务，在项目根目录提供静态文件，然后打开：

```text
http://127.0.0.1:4173/index.html
```

如果 4173 端口被占用，使用本项目服务器支持的其他端口，并以对应的 HTTP 地址访问。不要改用 `file://`。

## 发布入口

GitHub Pages、静态托管或其他 HTTP 部署应将项目根目录作为站点根目录，入口仍为 `/index.html`。部署时必须保留 `assets/`、`src/` 和 `vendor/` 的相对路径结构。

## 地图资产提示

官方地图源和派生文件具有独立的来源与发布控制。部署前请再次确认地图许可和资产上传范围。
