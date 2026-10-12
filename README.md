# 家庭点餐系统

基于 **FastAPI + Vue 3 + WebSocket** 的家庭内部点餐系统，支持飞牛 NAS 一键部署。

## 功能特性

- 🔐 **账号登录**：管理员/普通用户两种角色
- 🍽️ **订餐模式**：选择餐段点餐，提交预订
- 👨‍🍳 **做餐模式**：查看待确认订单，一键确认开始制作
- 📊 **管理后台**：菜单/订单/用户管理
- 📺 **后厨大屏**：实时显示订单状态
- ⚡ **实时推送**：WebSocket 内网实时推送
- 💾 **数据持久化**：SQLite 数据库
- 🐳 **一键部署**：Docker Compose

## 快速部署

### 方法一：一键部署脚本（推荐）

```bash
# 1. 将项目上传到飞牛 NAS

# 2. 进入项目目录
cd 家庭点餐软件

# 3. 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 方法二：手动部署

```bash
# 1. 创建数据目录
mkdir -p data

# 2. 启动服务
docker-compose up -d --build

# 3. 查看状态
docker-compose ps
```

## 访问地址

| 功能 | 地址 |
|---|---|
| 登录页 | `http://NAS_IP:8888/login` |
| 管理后台 | `http://NAS_IP:8888/admin` |
| 后厨大屏 | `http://NAS_IP:8888/kitchen` |
| API 文档 | `http://NAS_IP:8889/docs` |

## 首次使用

1. **注册管理员**
   - 打开登录页 → 切换到"注册"
   - 输入用户名和密码
   - 勾选"设为管理员"
   - 点击注册 → 自动登录

2. **添加菜单**
   - 管理后台 → "菜单管理"
   - 点击"+ 新增菜单"
   - 填写菜品信息，选择餐段

3. **开始点餐**
   - 普通用户登录 → 选择餐段 → 点餐 → 提交预订
   - 切换做餐模式 → 确认订单

## 后续更新

### 一键更新脚本

```bash
chmod +x update.sh
./update.sh
```

### 手动更新

```bash
# 1. 备份数据
cp data/ordering.db data/ordering-backup-$(date +%Y%m%d-%H%M%S).db

# 2. 拉取更新
git pull origin main

# 3. 重新构建
docker-compose down
docker-compose up -d --build
```

## 系统架构

```
┌─────────────────────────────────────────┐
│              普通用户                      │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │  🍽️ 订餐模式  │  │  👨‍🍳 做餐模式  │    │
│  │  点餐下单     │  │  确认订单     │    │
│  │  状态: 待确认 │  │  状态: 预订   │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│              管理员                        │
│  - 所有普通用户权限                        │
│  - 管理菜单/订单                          │
│  - 管理用户（设置管理员）                  │
└─────────────────────────────────────────┘
```

## 订单状态流程

```
用户点餐下单
    ↓
[待确认] ──→ 用户确认 ──→ [预订]（开始制作）
    ↑                    │
    └──── 管理员退回 ←───┘
```

## 技术栈

| 组件 | 技术 |
|---|---|
| 后端 | FastAPI (Python 3.11) |
| 数据库 | SQLite |
| 前端 | Vue 3 + Vite + Element Plus |
| 实时推送 | WebSocket |
| 部署 | Docker Compose |

## 目录结构

```
家庭点餐软件/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py      # 应用入口
│   │   ├── database.py  # SQLite 连接
│   │   ├── models.py    # 数据模型
│   │   ├── websocket.py # WebSocket 管理
│   │   └── routers/     # API 路由
│   └── Dockerfile
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   └── api/         # API 客户端
│   └── Dockerfile
├── data/                 # 数据持久化（自动创建）
├── deploy.sh             # 一键部署脚本
├── update.sh             # 一键更新脚本
├── docker-compose.yml    # Docker 配置
└── README.md             # 本文件
```

## 常见问题

### Q: 如何备份数据？
A: 数据存储在 `data/ordering.db`，直接复制即可：
```bash
cp data/ordering.db data/ordering-backup-$(date +%Y%m%d).db
```

### Q: 如何恢复数据？
A: 停止服务后替换数据库文件：
```bash
docker-compose down
cp data/ordering-backup.db data/ordering.db
docker-compose up -d
```

### Q: 忘记管理员密码怎么办？
A: 需要重置数据库（会丢失数据）：
```bash
docker-compose down
rm data/ordering.db
docker-compose up -d
```

### Q: 如何外网访问？
A: 需要配置 DDNS + 反向代理 + SSL 证书，参考飞牛 NAS 文档。

## License

MIT
