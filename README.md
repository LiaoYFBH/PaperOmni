# PaperFlow 📄✨

**[中文](#中文) | [English](#english)**

---

## 中文

> **让论文阅读回归本质** — 一系列基于 [Dify](https://dify.ai) 的学术工作流工具集

我们相信，研究者的时间应该花在思考上，而不是信息检索上。PaperFlow 是一个开源的 Dify 工作流集合，专注于**论文工具**的全流程自动化。每个工具都是一个 `.yml` DSL 文件，导入 Dify 即可测试运行。

**🎯 愿景**：用 AI 工作流消除学术信息差，让每个研究者都能高效追踪前沿。

### 📦 工具列表

| # | 工具名称 | 描述 | 文件 | 教程 |
|---|---------|------|------|------|
| 1 | **Paper-Essence** 📚 | 自动化论文日报推送 - 每日从 ArXiv 获取论文，AI 筛选分析后邮件推送 | [DSL](prj/Paper-Essence.yml) | [教程](docs/Paper-Essence-Tutorial.md) |
| 2 | *Coming Soon...* | 🚧 更多工具正在路上 | - | - |

---

### 🔧 Paper-Essence

自动化论文推送工作流，每天从 ArXiv 获取指定领域的最新论文，通过大模型智能筛选分析，生成结构化日报并发送到邮箱。

**✨ 功能亮点**
- 🕐 定时触发，每天自动运行
- 🤖 AI 模拟顶会评审流程筛选高质量论文
- 📄 OCR 解析 PDF，提取核心技术细节
- 📧 自动生成日报并邮件推送
- 💾 Supabase 去重，避免重复推送

**🔌 依赖插件**：`wenxin` · `paddleocr` · `163-smtp` · `supabase` · `ernie-api`

---

### 🚀 通用使用方法

1. 登录 [Dify](https://dify.ai) 平台
2. 创建新的工作流应用
3. 导入对应的 `.yml` DSL 文件
4. 配置所需的环境变量
5. 启动工作流

---

## English

> **Let paper reading return to its essence** — A collection of academic workflow tools built on [Dify](https://dify.ai)

We believe researchers' time should be spent on thinking, not information retrieval. PaperFlow is an open-source collection of Dify workflows focused on automating **paper discovery, filtering, analysis, and delivery**. Each tool is a plug-and-play `.yml` DSL file — just import into Dify and run.

**🎯 Vision**: Bridge the academic information gap with AI workflows, enabling every researcher to efficiently track the frontier.

### 📦 Tool List

| # | Tool Name | Description | File | Tutorial |
|---|-----------|-------------|------|----------|
| 1 | **Paper-Essence** 📚 | Automated paper digest - Fetches from ArXiv, AI filters & emails daily | [DSL](Paper-Essence.yml) | [Guide](Paper-Essence-Tutorial.md) |
| 2 | *Coming Soon...* | 🚧 More tools on the way | - | - |

---

### 🔧 Paper-Essence

Automated paper recommendation workflow. Fetches latest papers from ArXiv daily, uses LLM to filter and analyze, then sends structured digest to your email.

**✨ Features**
- 🕐 Scheduled daily execution
- 🤖 AI-powered top-tier conference review simulation
- 📄 OCR parsing for PDF technical details
- 📧 Auto-generated email digest
- 💾 Supabase deduplication

**🔌 Plugins**：`wenxin` · `paddleocr` · `163-smtp` · `supabase` · `ernie-api`

---

### 🚀 General Usage

1. Log in to [Dify](https://dify.ai) platform
2. Create a new workflow application
3. Import the corresponding `.yml` DSL file
4. Configure required environment variables
5. Start the workflow

---

### 📝 License

MIT License

---

> ⭐ If you find this project helpful, please give it a star!
