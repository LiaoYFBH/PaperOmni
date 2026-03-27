"""
Paper to PPT Gradio应用
"""
import gradio as gr
import os
from pathlib import Path

try:
    from config import get_ocr_config, get_llm_config
    _has_config = True
except ImportError:
    _has_config = False

from paper2ppt_agent import Paper2PPTAgent


def get_default_api_token():
    if _has_config:
        cfg = get_llm_config()
        token = cfg.get("api_token", "")
        print(f"[DEBUG] LLM token from config: '{token[:10]}...' (len={len(token)})" if token else f"[DEBUG] LLM token empty, cfg={cfg}")
        return token
    print("[DEBUG] _has_config=False, no config module loaded")
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

agent = Paper2PPTAgent(get_default_api_token()) if get_default_api_token() else None


def create_agent(api_token, ocr_url, ocr_token):
    if not api_token:
        return None
    return Paper2PPTAgent(
        api_token=api_token,
        ocr_api_url=ocr_url if ocr_url else None,
        llm_api_url="https://aistudio.baidu.com/llm/lmapi/v3"
    )


def process_paper(paper_file, requirements, time_limit, display_mode, template_choice):
    token = get_default_api_token()
    ocr_url = get_default_ocr_url()
    ocr_token = get_default_ocr_token()

    if not token:
        msg = "❌ LLM API Token 未配置\n\n"
        msg += "请在 prj/ppt/.env 文件中添加：\n"
        msg += "LLM_API_TOKEN=你的token值\n\n"
        msg += "然后重启程序"
        return None, msg

    current_agent = create_agent(token, ocr_url, ocr_token)

    if paper_file is None:
        return None, "❌ 请上传论文文件"

    output_filename = f"output_{Path(paper_file.name).stem}.pptx"
    output_path = os.path.join("output", output_filename)
    os.makedirs("output", exist_ok=True)

    status_msg = "🔄 正在处理，请稍候...\n"
    status_msg += "1️⃣ OCR识别中...\n"

    try:
        result_path = current_agent.process(
            paper_path=paper_file.name,
            requirements=requirements,
            time_limit=time_limit,
            display_mode=display_mode,
            template_id=template_choice,
            output_path=output_path
        )

        status_msg += "2️⃣ 内容提取完成\n"
        status_msg += "3️⃣ PPT结构生成完成\n"
        status_msg += "4️⃣ PPT创建完成\n"
        status_msg += f"\n✅ 成功！PPT已生成"

        return result_path, status_msg

    except Exception as e:
        error_msg = f"❌ 处理失败: {str(e)}"
        return None, error_msg


with gr.Blocks(title="Paper to PPT", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📄 Paper to PPT 智能转换系统

    将学术论文自动转换为精美的学术风格PPT演示文稿
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 上传论文")
            paper_input = gr.File(
                label="论文文件（PDF或图片）",
                file_types=[".pdf", ".jpg", ".jpeg", ".png"],
                type="filepath"
            )

            gr.Markdown("### ⚙️ 设置参数")
            requirements_input = gr.Textbox(
                label="特殊需求（可选）",
                placeholder="例如：重点突出实验结果、简化理论部分等",
                lines=3
            )

            time_input = gr.Dropdown(
                label="演讲时间",
                choices=["5分钟", "10分钟", "15分钟", "20分钟", "30分钟"],
                value="15分钟"
            )

            display_input = gr.Dropdown(
                label="展示方式",
                choices=["线下演讲", "线上会议", "课堂展示", "学术报告"],
                value="线下演讲"
            )

            template_input = gr.Radio(
                label="PPT模板",
                choices=[
                    ("模板1 - 经典深海蓝", "1"),
                    ("模板2 - 现代简洁白", "2"),
                    ("模板3 - 暗色科技风", "3"),
                    ("模板4 - 学术典雅风", "4")
                ],
                value="4"
            )

            submit_btn = gr.Button("🚀 开始生成PPT", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### 📊 处理状态")
            status_output = gr.Textbox(
                label="状态信息",
                lines=10,
                interactive=False
            )

            gr.Markdown("### 📥 下载结果")
            ppt_output = gr.File(
                label="生成的PPT文件"
            )

    gr.Markdown("""
    ---
    ### 💡 使用提示：
    1. 上传PDF格式的论文文件（支持图片格式）
    2. 填写API Token（或在.env中配置）
    3. 根据需要填写特殊要求
    4. 选择演讲时间和展示方式
    5. 点击"开始生成PPT"按钮
    """)

    submit_btn.click(
        fn=process_paper,
        inputs=[
            paper_input,
            requirements_input,
            time_input,
            display_input,
            template_input,
        ],
        outputs=[ppt_output, status_output]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        show_error=True
    )
