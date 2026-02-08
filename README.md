
# Paper-Essence Workflow 📄✨

**[中文说明](#中文说明) | [English Guide](#english-guide)**

---

## 中文说明

> **让论文阅读回归本质**

Paper-Essence 是基于 [Dify](https://dify.ai) 的自动化论文推送工作流，现已支持**中英文双版本**：

- `prj/Paper-Essence-cn.yml`：中文工作流，适合中文用户
- `prj/Paper-Essence-en.yml`：英文工作流，适合英文用户

每个工作流均可直接导入 Dify 平台，自动获取 ArXiv 最新论文，AI 智能筛选、分析并生成日报推送到邮箱。

**主要功能：**
- 🕐 每日定时自动运行
- 🤖 AI 智能筛选高质量论文
- 📄 PDF OCR 技术细节提取
- 📧 邮件自动推送日报
- 💾 Supabase 去重，避免重复

**依赖插件**：`wenxin` · `paddleocr` · `163-smtp` · `supabase` · `ernie-api`

**使用方法：**
1. 登录 [Dify](https://dify.ai)
2. 创建新工作流应用
3. 导入 `prj/Paper-Essence-cn.yml` 或 `prj/Paper-Essence-en.yml`
4. 配置环境变量
5. 启动工作流

详细教程见：[中文教程](docs/Paper-Essence-Tutorial.md)

---

## English Guide

> **Let paper reading return to its essence**

Paper-Essence is an automated paper workflow for [Dify](https://dify.ai), now available in **both Chinese and English versions**:

- `prj/Paper-Essence-cn.yml`: Chinese workflow for Chinese users
- `prj/Paper-Essence-en.yml`: English workflow for English users

Import either workflow into Dify to fetch the latest ArXiv papers, use AI to filter and analyze, and receive a structured daily digest by email.

**Key Features:**
- 🕐 Scheduled daily execution
- 🤖 AI-powered high-quality paper selection
- 📄 PDF OCR for technical detail extraction
- 📧 Automated email digest
- 💾 Supabase deduplication

**Plugins required**: `wenxin` · `paddleocr` · `163-smtp` · `supabase` · `ernie-api`

**How to use:**
1. Log in to [Dify](https://dify.ai)
2. Create a new workflow app
3. Import `prj/Paper-Essence-cn.yml` or `prj/Paper-Essence-en.yml`
4. Configure environment variables
5. Start the workflow

See [English Guide](docs/Paper-Essence-Tutorial-en.md) for details.

---

### 📝 License

MIT License

---

> ⭐ If you find this project helpful, please give it a star!
