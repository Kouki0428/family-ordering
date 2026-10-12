# 家庭点餐系统

基于 **FastAPI + Vue 3 + WebSocket** 的家庭内部点餐系统，支持飞牛 NAS 一键部署。

## 功能特性

- 🍽️ **扫码点餐**：餐桌扫码进入点餐页，无需安装 App
- 📱 **多端支持**：网页 + 安卓 TWA（Trusted Web Activity）套壳
- ⚡ **实时推送**：WebSocket 内网实时推送订单变更
- 📊 **管理后台**：菜单/餐桌/订单统一管理
- 📺 **后厨大屏**：实时显示新订单，状态一键切换
- 💾 **数据持久化**：SQLite 数据库，挂载到 NAS 共享文件夹
- 🐳 **一键部署**：Docker Compose，飞牛 NAS 友好

## 技术栈

| 组件 | 技术 |
|---|---|
| 后端 | FastAPI (Python 3.11) |
| 数据库 | SQLite |
| 前端 | Vue 3 + Vite + Element Plus |
| 实时推送 | WebSocket |
| 安卓端 | TWA (Trusted Web Activity) |
| 部署 | Docker Compose |

## 目录结构

```
家庭点餐软件/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # 入口
│   │   ├── database.py        # SQLite 连接
│   │   ├── models.py          # 数据模型
│   │   ├── routers/
│   │   │   ├── menus.py       # 菜单 API
│   │   │   ├── orders.py      # 订单 API
│   │   │   └── tables.py      # 餐桌 API
│   │   └── websocket.py       # WebSocket 推送
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── Order.vue      # 点餐页
│   │   │   ├── Admin.vue      # 管理后台
│   │   │   └── Kitchen.vue    # 后厨大屏
│   │   └── api/
│   ├── vite.config.ts
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── twa/                        # Android TWA 配置
│   ├── manifest.json
│   └── build-twa.sh
├── data/                       # 数据持久化目录（自动创建）
├── docker-compose.yml          # 一键部署
└── README.md                   # 本文件
```

## 快速开始

### 前置条件

- 飞牛 NAS（fnOS）
- Docker Compose（飞牛自带或手动安装）
- 至少 1GB 可用内存

### 一键部署

```bash
# 1. 将项目目录上传到 NAS
# 2. 进入项目目录
cd 家庭点餐软件

# 3. 启动服务
docker-compose up -d

# 4. 查看运行状态
docker-compose ps
```

### 访问地址

启动后访问（替换为你的 NAS IP）：

| 功能 | 地址 |
|---|---|
| 前端主页 | `http://NAS_IP:8080` |
| 点餐页 | `http://NAS_IP:8080/order/{餐桌token}` |
| 管理后台 | `http://NAS_IP:8080/admin` |
| 后厨大屏 | `http://NAS_IP:8080/kitchen` |
| API 文档 | `http://NAS_IP:8000/docs` |

### 初始化使用

1. **创建餐桌**：
   - 打开管理后台 `http://NAS_IP:8080/admin`
   - 进入"餐桌管理"标签页
   - 点击"+ 新增餐桌"，输入餐桌名称（如"1号桌"）
   - 系统会自动生成扫码 Token 和点餐链接

2. **添加菜单**：
   - 进入"菜单管理"标签页
   - 点击"+ 新增菜单"
   - 填写菜品名称、分类、价格等信息

3. **开始点餐**：
   - 访问餐桌对应的点餐链接（如 `http://NAS_IP:8080/order/abc123...`）
   - 或打印二维码贴在餐桌上扫码

## 开发模式（本地调试）

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

访问 API 文档：`http://localhost:8000/docs`

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问前端：`http://localhost:3000`

## 安卓 TWA 打包

将 Web 应用打包成安卓 APK（可选）：

1. 安装 bubblewrap CLI：
   ```bash
   npm install -g @bubblewrap/cli
   ```

2. 修改 `twa/build-twa.sh` 中的 `WEB_URL` 为你的 NAS 地址

3. 准备图标文件（192x192 和 512x512 PNG）放到 `twa/icons/` 目录

4. 运行构建脚本：
   ```bash
   cd twa
   bash build-twa.sh
   ```

5. APK 文件位于 `twa/output/app/build/outputs/apk/debug/`

## 数据备份

数据存储在 `./data/ordering.db`，建议定期备份：

```bash
# 备份命令
cp data/ordering.db data/ordering-backup-$(date +%Y%m%d).db
```

## 常见问题

### Q: 安卓 TWA 是什么？
A: TWA (Trusted Web Activity) 是把 PWA（渐进式 Web 应用）包成安卓 App 的技术。本质是 Chrome 内核 + Web 内容，无需原生开发，但能获得原生 App 级别的体验（全屏、独立图标、通知等）。

### Q: 为什么用 WebSocket 而不是云端推送？
A: 家庭内网场景下，WebSocket 是零成本、零配置的实时推送方案。云端推送（如 uni-push、FCM）需要公网、证书、云服务账号，对家庭自用过于复杂。WebSocket 在 Wi-Fi 环境下稳定可靠。

### Q: 飞牛 NAS 内存不够怎么办？
A: 4GB 内存足够运行本系统（~600MB）。如果内存紧张：
- 关闭其他不常用的 NAS 服务
- 将 SQLite 改为内存模式（重启后数据丢失，不推荐）
- 考虑升级内存到 8GB

### Q: 如何外网访问？
A: 家庭内网部署不支持 Web Push。如需外网访问：
1. 配置 DDNS（飞牛内置）
2. 配置反向代理（Nginx Proxy Manager）
3. 申请 Let's Encrypt 证书

### Q: 如何扩展功能？
A: 项目结构清晰，扩展方便：
- 添加新 API：在 `backend/app/routers/` 下新建文件
- 添加新页面：在 `frontend/src/views/` 下新建 Vue 组件
- 修改数据库：在 `backend/app/models.py` 中添加表，运行 `init_db()` 自动建表

## License

MIT
