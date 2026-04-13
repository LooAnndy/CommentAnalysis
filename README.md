# B站评论爬虫 + 热度分析系统

一个基于 Flask 的 B站评论爬虫与数据分析工具，支持二维码登录、评论抓取以及热度趋势可视化。

---

## 🚀 功能介绍

* 📱 二维码扫码登录B站
* 🕷️ 评论爬取（支持BV号）
* 📊 评论热度趋势分析（按天统计）
* 📈 图表展示（ECharts）
* 📁 本地CSV数据存储

---

## 🛠️ 技术栈


* Python 3.8
* Flask
* requests
* pandas
* ECharts（前端）

---

## 📥 获取项目

```bash
git clone https://github.com/LooAnndy/CommentAnalysis.git
cd ./CommentAnalysis
```

---

## 📦 安装依赖

### ✅ 方式一：venv

```bash
# 创建虚拟环境
python -m venv venv

# 激活（Windows）
venv\Scripts\activate

# 激活（Mac/Linux）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

### ✅ 方式二：conda（推荐 Anaconda / Miniconda 用户）

```bash
# 创建环境（指定Python版本更稳）
conda create -n bilibili-analyzer python=3.8

# 激活环境
conda activate bilibili-analyzer

# 安装依赖
pip install -r requirements.txt
```

---

## ▶️ 启动项目

```bash
python app.py
```

打开浏览器：

```
http://127.0.0.1:5000
```

---

## 📌 使用说明

1. 点击获取二维码并扫码登录
2. 输入或选择 BV 号
3. 点击“开始爬取”
4. 点击“查看热度趋势”

---

## 📂 数据说明

* 评论数据存储在 `data/` 目录
* 文件格式：`BVxxxx.csv`

---

## ⚠️ 注意事项

* 需要保持网络通畅，建议关闭 VPN
* B站接口可能存在反爬限制
* 建议不要高频请求

---

## 📄 其他说明

* 首次运行会自动生成数据目录（如不存在）
* 登录信息会保存在本地 cookies 文件中
