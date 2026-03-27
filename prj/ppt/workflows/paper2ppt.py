"""
Paper2PPT Workflow
"""
import os
import json
import gradio as gr
from pathlib import Path
from workflows.base import BaseWorkflow
from workflows import workflow_registry
from paper2ppt_agent import Paper2PPTAgent

try:
    from config import get_ocr_config, get_llm_config
    _has_config = True
except ImportError:
    _has_config = False


def get_default_token():
    if _has_config:
        cfg = get_llm_config()
        return cfg.get("api_token", "")
    return ""

def get_default_ocr_url():
    if _has_config:
        cfg = get_ocr_config()
        return cfg.get("api_url", "")
    return ""

def get_default_ocr_token():
    if _has_config:
        cfg = get_ocr_config()
        return cfg.get("api_token", "")
    return ""

_default_token = get_default_token()


class Paper2PPTWorkflow(BaseWorkflow):

    @property
    def name(self):
        return "🎯  Paper2PPT 智能转换"

    @property
    def icon(self):
        return "🎯"

    @property
    def description(self):
        return "AI智能体直接处理 · 自动OCR识别 · 智能内容提取 · 精美PPT生成"

    @staticmethod
    def _process(paper_file, requirements, time_limit, display_mode, template_choice,
                 api_token, ocr_url, ocr_token, progress=gr.Progress()):
        if not api_token:
            yield "❌ 请输入 LLM API Token", None
            return

        current_agent = Paper2PPTAgent(
            api_token=api_token,
            ocr_api_url=ocr_url if ocr_url else None,
        )

        if paper_file is None:
            yield "❌ 请先上传论文文件", None
            return

        try:
            log = "📤 正在处理论文...\n"
            log += f"📄 文件名: {Path(paper_file.name).name}\n"
            log += f"📏 文件大小: {os.path.getsize(paper_file.name) / 1024 / 1024:.2f} MB\n\n"
            yield log, None

            base_name = Path(paper_file.name).stem
            run_dir = os.path.join("output", f"run_{base_name}")
            os.makedirs(run_dir, exist_ok=True)

            output_filename = f"{base_name}.pptx"
            output_path = os.path.join(run_dir, output_filename)

            log += "🔍 **步骤 1/4**: OCR识别中...\n"
            yield log, None

            result_path = current_agent.process(
                paper_path=paper_file.name,
                requirements=requirements or "",
                time_limit=time_limit,
                display_mode=display_mode,
                template_id=template_choice,
                output_path=output_path
            )

            log += "✅ OCR识别完成\n\n"
            log += "📝 **步骤 2/4**: 内容提取完成\n"
            log += "✅ 已提取标题、摘要、章节等信息\n\n"
            log += "🤖 **步骤 3/4**: PPT结构生成完成\n"
            log += "✅ AI已生成PPT大纲\n\n"
            log += "🎨 **步骤 4/4**: PPT创建完成\n"
            log += "✅ 已应用模板和插入图片\n\n"

            debug_json_path = os.path.join(run_dir, "debug_ppt_structure.json")
            if os.path.exists(debug_json_path):
                with open(debug_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    log += "\n<details><summary>👉 <b>点击查看 AI 生成的 PPT 大纲和内容 (JSON)</b></summary>\n\n```json\n"
                    log += json.dumps(data, ensure_ascii=False, indent=2)
                    log += "\n```\n</details>\n\n"

            log += "\n<details><summary>👉 <b>关于提取结果的说明</b></summary>\n\n"
            log += f"所有的提取结果，包括裁剪的照片 (`images/`)、公式 (`formulas.md`) 以及调试文件都已独立保存在了 `{run_dir}` 文件夹下，您可以前往此文件夹查看和校验。\n"
            log += "</details>\n\n"
            log += "=" * 50 + "\n"
            log += "🎉 **成功！** PPT已生成\n"
            log += f"📁 文件路径: `{output_path}`\n"
            log += f"📊 模板: 模板{template_choice}\n"
            log += f"⏱️ 演讲时间: {time_limit}\n"
            log += "=" * 50 + "\n"

            yield log, result_path

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()

            error_log = "❌ **处理失败**\n\n"
            error_log += f"**错误信息**: {str(e)}\n\n"
            error_log += "**可能的原因**:\n"
            error_log += "- 论文文件格式不支持或损坏\n"
            error_log += "- OCR API调用失败（网络问题或配额不足）\n"
            error_log += "- 大模型API调用失败\n"
            error_log += "- 文件内容无法正确解析\n\n"
            error_log += "**建议**:\n"
            error_log += "1. 检查论文文件是否清晰可读\n"
            error_log += "2. 确认网络连接正常\n"
            error_log += "3. 验证API Token是否有效\n"
            error_log += "4. 尝试使用较小的PDF文件测试\n\n"
            error_log += "**详细错误信息**:\n"
            error_log += f"```\n{error_trace}\n```\n"

            yield error_log, None

    def build_tab(self):
        gr.HTML(f"""
        <div class="tab-desc">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c9a84c" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          {self.description}
        </div>
        """)

        with gr.Row(equal_height=False):
            with gr.Column(scale=4, min_width=320):
                gr.HTML('<p style="font-family:\'DM Sans\',sans-serif; font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#5a6478; margin-bottom:14px; font-weight:500;">输入参数</p>')

                api_token_input = gr.Textbox(
                    label="LLM API Token",
                    placeholder="输入百度文心一言 API Token",
                    value=_default_token,
                    type="password"
                )
                ocr_url_input = gr.Textbox(
                    label="OCR API URL（可选）",
                    placeholder="留空使用.env或默认地址",
                    value=""
                )
                ocr_token_input = gr.Textbox(
                    label="OCR API Token（可选）",
                    placeholder="留空使用.env或默认Token",
                    value="",
                    type="password"
                )

                paper_input = gr.File(
                    label="论文文件（必填）",
                    file_types=[".pdf", ".jpg", ".jpeg", ".png"],
                )
                reqs_input = gr.Textbox(
                    label="特殊需求（选填）",
                    placeholder="例如：重点突出实验结果、简化理论部分、增加可视化图表",
                    lines=2,
                )
                with gr.Row():
                    time_input = gr.Dropdown(
                        label="演讲时间",
                        choices=["5分钟", "10分钟", "15分钟", "20分钟", "30分钟"],
                        value="15分钟",
                    )
                    display_input = gr.Dropdown(
                        label="展示方式",
                        choices=["线下演讲", "线上会议", "课堂展示", "学术报告"],
                        value="线下演讲",
                    )
                template_input = gr.Radio(
                    label="PPT模板",
                    choices=[
                        ("模板1 - 经典深海蓝", "1"),
                        ("模板2 - 现代简洁白", "2"),
                        ("模板3 - 暗色科技风", "3")
                    ],
                    value="1",
                )
                gr.HTML('<hr class="section-divider">')
                gr.HTML("""
                <div style="background:#1e2530; border:1px solid #2a3242; border-radius:8px; padding:14px 16px; margin-bottom:16px;">
                  <p style="font-size:12px; color:#8b95a8; margin:0; line-height:1.7; font-family:'DM Sans',sans-serif;">
                    <span style="color:#c9a84c; font-weight:500;">✨ 智能特性</span><br>
                    • 自动OCR识别论文内容<br>
                    • AI提取关键信息和图表<br>
                    • 智能生成PPT结构<br>
                    • 自动插入图片和表格<br>
                    • 美观排版和布局优化
                  </p>
                </div>
                """)
                btn = gr.Button("🚀  智能生成 PPT", variant="primary", size="lg")

            with gr.Column(scale=6, min_width=400):
                gr.HTML('<p style="font-family:\'DM Sans\',sans-serif; font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#5a6478; margin-bottom:14px; font-weight:500;">处理状态 &amp; 结果</p>')
                log_output = gr.Markdown(
                    value="*等待运行…*",
                    label="处理日志",
                    elem_id="paper2ppt_log",
                )
                file_output = gr.File(
                    label="生成的PPT文件",
                    elem_id="paper2ppt_file",
                )

        btn.click(
            fn=self._process,
            inputs=[paper_input, reqs_input, time_input, display_input, template_input,
                    api_token_input, ocr_url_input, ocr_token_input],
            outputs=[log_output, file_output],
        )


workflow_registry.register(Paper2PPTWorkflow())
