# 📺 CommentAnalysis

## B站评论爬取与数据分析系统

CommentAnalysis 是一个面向 **Bilibili 评论数据洞察** 的综合处理平台。
它能够将异步爬虫抓取到的原始评论转化为结构化数据，并进一步生成可视化分析图表，实现完整的数据处理闭环。

---

# 🏗️ System Architecture

## 系统架构与模块解析

项目采用 **分层单体架构（Layered Monolith）**，确保代码具备良好的可维护性与扩展性。

---

## 1️⃣ Entry & Config Layer

### 入口与配置层（The Skeleton）

| 模块                  | 职责                        |
| ------------------- | ------------------------- |
| **app.py**          | Flask 应用初始化、蓝图注册、后台守护线程启动 |
| **config/paths.py** | 统一管理数据目录、Cookie、进度文件路径    |

---

## 2️⃣ Routing Layer

### 路由与通信层（The Nerve Center）

| 模块                         | 职责                        |
| -------------------------- | ------------------------- |
| **routes/auth_api.py**     | 扫码登录与状态轮询                 |
| **routes/crawl.py**        | 爬虫任务调度（task_queue + 进度管理） |
| **routes/analysis_api.py** | 分析接口，返回图表 JSON            |

---

## 3️⃣ Crawler Engine

### 爬虫核心层（The Engine Room）

| 模块                     | 职责              |
| ---------------------- | --------------- |
| **crawler.py**         | 主评论 + 楼中楼抓取     |
| **writer.py**          | 高性能 CSV 写入      |
| **progressManager.py** | 断点续爬            |
| **utils.py**           | 请求重试 / BV→AV 转换 |

---

## 4️⃣ Data Service Layer

### 数据服务层（The Brain）

| 模块                      | 职责             |
| ----------------------- | -------------- |
| **analysis_service.py** | Pandas 数据清洗与统计 |
| **auth_service.py**     | B站登录鉴权封装       |

---

# 🖥️ Operational Demo

## 系统运行流程

---

### 🔐 Step 1 · 登录阶段

访问 `/login` 获取二维码并扫码：

* 请求 B站登录接口生成二维码
* 登录成功后自动保存 `cookies.json`
* 页面自动跳转首页

---

### 🕷️ Step 2 · 爬取阶段

输入 BV 号 → 点击 **开始爬取**

实时进度示例：

```text
正在抓取第 5 页…
当前进度：45%
```

后台 `task_queue` 按顺序执行任务。

---

### 📊 Step 3 · 分析阶段

选择 BV → 点击 **热度统计**

自动生成：

* 评论时间趋势折线图
* IP 属地分布图
* 用户等级柱状图

---

# 🗺️ Roadmap

## 项目路线图

---

## 🟢 Completed Features

### 已完成功能

| 模块    | 功能      | 说明             |
| ----- | ------- | -------------- |
| 登录系统  | 二维码扫码登录 | 支持官方登录流程       |
| 爬虫系统  | 断点续爬    | 支持异常恢复         |
| 数据可视化 | 基础图表    | 趋势 / IP / 等级分析 |

---

## 🟡 Data Processing (In Progress)

### 数据处理优化

| 功能   | 说明             |
| ---- | -------------- |
| 评论清洗 | 过滤抽奖 / 打卡评论    |
| 词云优化 | 集成 jieba + 停用词 |

---

## 🔵 NLP Features (Planned)

### NLP 深度分析

| 功能   | 说明      |
| ---- | ------- |
| 情感分析 | 正负面趋势识别 |
| 语义聚类 | 热议话题发现  |

---

## ⚙️ Performance & Storage

### 架构与性能升级

| 功能        | 说明          |
| --------- | ----------- |
| 爬虫线程池     | 多 BV 并发抓取   |
| SQLite 支持 | 从 CSV 迁移数据库 |

---

# 📊 Data Schema

## 评论 CSV 字段规范

| 字段       | 说明    |
| -------- | ----- |
| rpid     | 评论 ID |
| user     | 用户昵称  |
| location | IP 属地 |
| comment  | 评论内容  |
| likes    | 点赞数   |
| time     | 发布时间  |
| root     | 主楼 ID |

---

# 🚀 Quick Start

## 快速运行

```bash
git clone https://github.com/LooAnndy/CommentAnalysis.git
pip install -r requirements.txt
python app.py
```

访问：

```
http://127.0.0.1:5000
```

---

# ⚖️ Disclaimer

## 免责声明

本项目仅用于学习与研究。
请遵守 Bilibili 用户协议与相关法律法规。

---