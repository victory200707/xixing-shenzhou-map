# 曦行神州·万里晨光

中国日出时空节律动态地图。

## 本地运行

本项目必须通过本地 HTTP 服务访问，不能直接双击 `index.html`。ES Module 和 `fetch()` 在 `file://` 下会受到浏览器同源策略限制，导致脚本或控制点数据无法加载。

请在项目目录启动已有本地服务器，然后访问：

```text
http://127.0.0.1:4173/index.html
```

详细步骤见 [docs/LOCAL_RUN.md](docs/LOCAL_RUN.md)。
