
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

---

## 📊 PPT Agent (论文转PPT)

> 将学术论文自动转换为精美的学术风格PPT

**功能：**
- 🔍 智能OCR识别论文内容（版面分析）
- 🤖 AI提取标题、摘要、章节、图表、公式、表格
- 🎨 4种精美模板可选
- 📊 自动插入原文图片和数据表格
- ✨ 学术风格排版，美观专业

**主要文件：**
- `paper2ppt_agent.py` - 核心Agent类
- `ppt_renderer.py` - PPT渲染引擎
- `ppt_style_analyzer.py` - 模板风格分析
- `ocr_extractor.py` - OCR API封装
- `app.py` - Gradio UI启动入口

**使用方法：**
1. 复制 `.env.example` 为 `.env`，填入API配置
2. `pip install -r requirements.txt`
3. `python app.py` 或在Dify工作流中集成

**依赖插件**：`gradio` · `requests` · `python-pptx` · `python-dotenv` · `Pillow` · `lxml`

---

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

---

## 📊 PPT Agent (Paper to PPT)

> Automatically convert academic papers into elegant academic-style PPT presentations

**Key Features:**
- 🔍 Intelligent OCR for paper content analysis
- 🤖 AI extracts title, abstract, sections, figures, formulas, tables
- 🎨 4 beautiful templates available
- 📊 Auto-insert figures and data tables
- ✨ Professional academic layout

**Main Files:**
- `paper2ppt_agent.py` - Core Agent class
- `ppt_renderer.py` - PPT rendering engine
- `ppt_style_analyzer.py` - Template style analysis
- `ocr_extractor.py` - OCR API wrapper
- `app.py` - Gradio UI entry point

**How to use:**
1. Copy `.env.example` to `.env` and fill in API credentials
2. `pip install -r requirements.txt`
3. `python app.py` or integrate into Dify workflow

**Required packages**: `gradio` · `requests` · `python-pptx` · `python-dotenv` · `Pillow` · `lxml`

---

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
