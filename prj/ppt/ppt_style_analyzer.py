"""
ppt_style_analyzer.py
Template style analysis via Vision LLM
"""
import os, re, json, base64, subprocess, tempfile, shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ThemeStyle:
    name: str
    bg_cover: str
    bg_content: str
    bg_dark: bool
    header_bg: str
    header_text: str
    accent: str
    accent2: str
    text_primary: str
    text_secondary: str
    text_on_dark: str
    card_bg: str
    card_border: str
    font_title: str
    font_body: str
    style_notes: str


def _img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _pptx_to_images(pptx_path: str, workdir: str, max_slides: int = 4) -> list[str]:
    import platform
    name = Path(pptx_path).stem
    pdf = os.path.join(workdir, f"{name}.pdf")
    python_cmd = "python" if platform.system() == "Windows" else "python3"

    try:
        if platform.system() == "Windows":
            soffice_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
            soffice = None
            for path in soffice_paths:
                if os.path.exists(path):
                    soffice = path
                    break

            if soffice:
                subprocess.run(
                    [soffice, "--headless", "--convert-to", "pdf",
                     "--outdir", workdir, pptx_path],
                    check=True, capture_output=True, timeout=30
                )
            else:
                raise FileNotFoundError("LibreOffice not found on Windows")
        else:
            subprocess.run(
                [python_cmd, "/mnt/skills/public/pptx/scripts/office/soffice.py",
                 "--headless", "--convert-to", "pdf", pptx_path],
                cwd=workdir, check=True, capture_output=True, timeout=30
            )

        prefix = os.path.join(workdir, f"{name}_slide")
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "96", "-l", str(max_slides), pdf, prefix],
            check=True, capture_output=True, timeout=30
        )

        imgs = sorted([
            os.path.join(workdir, f)
            for f in os.listdir(workdir)
            if f.startswith(f"{name}_slide") and f.endswith(".jpg")
        ])[:max_slides]
        return imgs

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"PPTX to image conversion failed: {e}")


def analyze_template_style(
    pptx_path: str,
    llm_func,
    theme_id: str = "1"
) -> ThemeStyle:
    workdir = tempfile.mkdtemp()
    try:
        print(f"  截图中: {Path(pptx_path).name} ...")
        imgs = _pptx_to_images(pptx_path, workdir, max_slides=4)
        print(f"  获得 {len(imgs)} 张截图，发送给大模型分析...")

        prompt = """请仔细观察这几张 PPT 模板截图，提取其视觉设计风格。

请分析并以 JSON 格式返回以下信息（颜色统一用 6 位十六进制，如 "#1A2B5E"）：

{
  "name": "模板名称（自己起一个简短的名字）",
  "bg_cover": "封面/过渡页的背景主色",
  "bg_content": "内容页的背景色",
  "bg_dark": true/false（内容页背景是否是深色？浅色为 false）,
  "header_bg": "内容页顶部标题栏的背景色",
  "header_text": "标题栏内文字的颜色",
  "accent": "最主要的点缀/强调色（用于分割线、图标、高亮数字等）",
  "accent2": "次要强调色（副标题区、边框等）",
  "text_primary": "内容页正文主文字颜色",
  "text_secondary": "辅助/说明性文字的颜色（偏灰）",
  "text_on_dark": "深色背景上文字的颜色",
  "card_bg": "信息卡片/数据卡片的背景色",
  "card_border": "卡片左侧强调条的颜色",
  "font_title": "标题使用的字体名（如 Calibri、Arial 等，猜测即可）",
  "font_body": "正文使用的字体名",
  "style_notes": "用 10-20 字描述这套模板的视觉特征，比如'深海蓝主色+金色强调，左侧竖线边框'"
}

只返回 JSON，不要有任何其他说明。"""

        response = llm_func(prompt, imgs)

        m = re.search(r'\{.*\}', response, re.DOTALL)
        raw = json.loads(m.group() if m else response)

        style = ThemeStyle(
            name=raw.get("name", f"模板{theme_id}"),
            bg_cover=raw.get("bg_cover", "#1A2B5E"),
            bg_content=raw.get("bg_content", "#F4F6FB"),
            bg_dark=bool(raw.get("bg_dark", False)),
            header_bg=raw.get("header_bg", "#1A2B5E"),
            header_text=raw.get("header_text", "#FFFFFF"),
            accent=raw.get("accent", "#C9A84C"),
            accent2=raw.get("accent2", "#4A5580"),
            text_primary=raw.get("text_primary", "#1A2B5E"),
            text_secondary=raw.get("text_secondary", "#7A84AA"),
            text_on_dark=raw.get("text_on_dark", "#FFFFFF"),
            card_bg=raw.get("card_bg", "#1A2B5E"),
            card_border=raw.get("card_border", "#C9A84C"),
            font_title=raw.get("font_title", "Calibri"),
            font_body=raw.get("font_body", "Calibri"),
            style_notes=raw.get("style_notes", ""),
        )
        print(f"  ✅ 风格提取完成: {style.name} — {style.style_notes}")
        return style

    except Exception as e:
        print(f"  [Warning] 视觉分析失败({e})，使用默认主题")
        return _fallback_theme(theme_id)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _fallback_theme(theme_id: str) -> ThemeStyle:
    defaults = {
        "1": ThemeStyle("经典深海蓝","#1A2B5E","#F4F6FB",False,"#1A2B5E","#FFFFFF",
                        "#C9A84C","#4A5580","#1A2B5E","#7A84AA","#FFFFFF",
                        "#1A2B5E","#C9A84C","Calibri","Calibri","深海蓝+金色强调"),
        "2": ThemeStyle("现代简洁白","#0F172A","#FFFFFF",False,"#0D9488","#FFFFFF",
                        "#EA580C","#0D9488","#0F172A","#94A3B8","#FFFFFF",
                        "#F1F5F9","#0D9488","Calibri","Calibri","白底+青绿主色"),
        "3": ThemeStyle("暗色科技风","#1A2332","#2A3A4A",True,"#1A2332","#CDD9E5",
                        "#00D4AA","#2A3A4A","#CDD9E5","#6E8299","#FFFFFF",
                        "#1A2332","#00D4AA","Calibri","Calibri","全深色+青绿点缀"),
        "4": ThemeStyle("学术典雅","#2C3E50","#FAFBFC",False,"#34495E","#FFFFFF",
                        "#2980B9","#1ABC9C","#2C3E50","#7F8C8D","#FFFFFF",
                        "#ECF0F1","#2980B9","Times New Roman","Georgia","学术蓝+灰白配色"),
    }
    return defaults.get(theme_id, defaults["4"])
