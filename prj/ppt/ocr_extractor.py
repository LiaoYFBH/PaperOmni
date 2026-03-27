"""
OCR Extractor - PaddleOCR-VL-1.5 Layout Analysis API
"""
import os, re, json, base64, requests, io
from PIL import Image
from typing import Dict, List, Optional, Tuple


def call_ocr_api(
    file_path: str,
    api_url: str,
    api_token: str,
    *,
    use_chart_recognition: bool = False,
    use_doc_orientation_classify: bool = False,
    use_doc_unwarping: bool = False,
    timeout: int = 300,
) -> Dict:
    print("正在进行版面分析OCR识别...")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"文件大小: {file_size_mb:.2f} MB")
    if file_size_mb > 50:
        raise Exception(f"文件过大({file_size_mb:.2f} MB)，建议小于50MB")

    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("ascii")

    headers = {
        "Authorization": f"token {api_token}",
        "Content-Type": "application/json",
    }

    file_type = 0 if file_path.lower().endswith(".pdf") else 1

    payload = {
        "file": file_data,
        "fileType": file_type,
        "useDocOrientationClassify": use_doc_orientation_classify,
        "useDocUnwarping": use_doc_unwarping,
        "useChartRecognition": use_chart_recognition,
    }

    print(f"正在调用版面分析API: {api_url}")
    print(f"参数: fileType={file_type}, useChartRecognition={use_chart_recognition}")

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        result = resp.json()

        if "result" not in result:
            raise Exception(f"API响应缺少'result'字段: {list(result.keys())}")
        if "layoutParsingResults" not in result["result"]:
            raise Exception(
                f"API响应缺少'layoutParsingResults'字段: {list(result['result'].keys())}"
            )

        pages = result["result"]["layoutParsingResults"]
        total_md_imgs = sum(
            len(p.get("markdown", {}).get("images", {})) for p in pages
        )
        print(f"✅ OCR识别成功，共 {len(pages)} 页，Markdown图片 {total_md_imgs} 张")
        return result

    except requests.exceptions.Timeout:
        raise Exception("版面分析API请求超时")
    except requests.exceptions.HTTPError as e:
        body = resp.text[:500] if resp is not None else ''
        raise Exception(f"API请求失败(HTTP {resp.status_code}): {e}\n响应内容: {body}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求失败: {e}")
    except Exception as e:
        raise Exception(f"版面分析处理失败: {e}")


def extract_content(
    ocr_data: Dict,
    output_dir: Optional[str] = None,
) -> Dict:
    print("正在提取论文内容...")

    layout_results = ocr_data.get("result", {}).get("layoutParsingResults", [])
    if not layout_results:
        raise Exception("在API响应中未找到 'layoutParsingResults' 或其为空")

    full_text = ""
    images: List[Dict] = []
    formulas: List[str] = []
    tables: List[Dict] = []

    images_dir = None
    if output_dir:
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

    for page_idx, res in enumerate(layout_results):
        md = res.get("markdown", {})
        if not md:
            continue

        page_text = md.get("text", "")
        full_text += page_text + "\n\n"

        md_image_boxes = []

        for fname, img_value in md.get("images", {}).items():
            if not img_value:
                continue

            filename_bbox = None
            m = re.search(r'box_(\d+)_(\d+)_(\d+)_(\d+)', fname)
            if m:
                filename_bbox = [int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))]
                md_image_boxes.append(filename_bbox)

            img_info = {
                "url": img_value,
                "page": page_idx,
                "filename": fname,
                "local_path": None,
                "type": "markdown"
            }

            if images_dir:
                local_path = _download_image(img_value, fname, images_dir)
                if local_path:
                    img_info["local_path"] = local_path
            else:
                 img_info["local_path"] = img_value

            images.append(img_info)

        pruned = res.get("prunedResult", {})
        ldr = pruned.get("layout_det_res", {})
        boxes = ldr.get("boxes", [])
        input_img_val = res.get("inputImage")

        img_boxes = [b for b in boxes if b.get('label') in ('image', 'figure', 'chart')]

        if img_boxes and input_img_val:
            try:
                page_img = None
                if input_img_val.startswith("http"):
                    resp = requests.get(input_img_val, timeout=15)
                    if resp.status_code == 200:
                        page_img = Image.open(io.BytesIO(resp.content))
                elif input_img_val.startswith("data:"):
                    _, encoded = input_img_val.split(",", 1)
                    page_img = Image.open(io.BytesIO(base64.b64decode(encoded)))
                else:
                    page_img = Image.open(io.BytesIO(base64.b64decode(input_img_val)))

                if page_img:
                    for b_idx, box in enumerate(img_boxes):
                        coord = box.get('coordinate')
                        if coord and len(coord) == 4:
                            x1, y1, x2, y2 = coord

                            is_duplicate = False
                            for md_box in md_image_boxes:
                                iou = _calculate_iou(coord, md_box)
                                if iou > 0.5:
                                    is_duplicate = True
                                    break

                            if is_duplicate:
                                continue

                            pad = 5
                            box_crop = (
                                max(0, x1 - pad),
                                max(0, y1 - pad),
                                min(page_img.width, x2 + pad),
                                min(page_img.height, y2 + pad)
                            )
                            cropped = page_img.crop(box_crop)

                            fname = f"crop_p{page_idx}_{box.get('label', 'img')}_{b_idx}.jpg"
                            img_info = {
                                "url": "",
                                "page": page_idx,
                                "filename": fname,
                                "local_path": None,
                                "type": "crop"
                            }

                            if images_dir:
                                local_path = os.path.join(images_dir, fname)
                                cropped.save(local_path, "JPEG", quality=95)
                                img_info["local_path"] = local_path
                                print(f"  已截取图片: {fname}")
                            else:
                                buf = io.BytesIO()
                                cropped.save(buf, format="JPEG")
                                img_info["url"] = f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"
                                img_info["local_path"] = img_info["url"]
                            images.append(img_info)
            except Exception as e:
                print(f"  截取图片失败(page {page_idx}): {e}")

        page_formulas = _extract_formulas(page_text)
        formulas.extend(page_formulas)

        page_tables = _extract_tables(page_text, page_idx)
        tables.extend(page_tables)

    unique_formulas = list(dict.fromkeys(formulas))[:50]

    content = {
        "full_text": full_text,
        "images": images,
        "formulas": unique_formulas,
        "tables": tables,
        "title": _extract_title(full_text),
        "abstract": _extract_abstract(full_text),
        "sections": _extract_sections(full_text),
    }

    print(f"提取完成: '{content['title'][:40]}...'")
    print(f"  章节={len(content['sections'])}, 图片={len(images)}, "
          f"公式={len(unique_formulas)}, 表格={len(tables)}")

    if output_dir:
        _save_formulas(unique_formulas, os.path.join(output_dir, "formulas.md"))

    return content


def save_ocr_result(ocr_data: Dict, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, ensure_ascii=False, indent=2)
    print(f"OCR结果已保存到: {output_path}")
    return output_path


def _download_image(img_value: str, filename: str, images_dir: str) -> Optional[str]:
    safe_name = os.path.basename(filename)
    if not safe_name:
        safe_name = "unnamed.jpg"
    local_path = os.path.join(images_dir, safe_name)
    os.makedirs(os.path.dirname(local_path) or images_dir, exist_ok=True)

    try:
        if img_value.startswith(("http://", "https://")):
            resp = requests.get(img_value, timeout=15)
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                print(f"  已下载图片: {safe_name} (page)")
                return local_path
            else:
                print(f"  下载图片失败 ({resp.status_code}): {safe_name}")
        elif img_value.startswith("data:"):
            _, encoded = img_value.split(",", 1)
            with open(local_path, "wb") as f:
                f.write(base64.b64decode(encoded))
            print(f"  已解码图片(data URI): {safe_name}")
            return local_path
        else:
            try:
                img_bytes = base64.b64decode(img_value)
                if len(img_bytes) > 100:
                    with open(local_path, "wb") as f:
                        f.write(img_bytes)
                    print(f"  已解码图片(Base64): {safe_name}")
                    return local_path
            except Exception:
                print(f"  无法解析图片格式: {safe_name}")
    except Exception as e:
        print(f"  下载图片异常: {safe_name}, {e}")

    return None


def _extract_formulas(text: str) -> List[str]:
    formulas = []

    block_matches = re.findall(r'\$\$(.+?)\$\$', text, re.DOTALL)
    for m in block_matches:
        formula = m.strip()
        if formula and len(formula) > 1:
            formulas.append(formula)

    inline_matches = re.findall(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', text, re.DOTALL)
    for m in inline_matches:
        formula = m.strip()
        if formula and len(formula) > 1:
            formulas.append(formula)

    return formulas


def _extract_tables(text: str, page_idx: int) -> List[Dict]:
    tables = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and line.endswith("|") and line.count("|") >= 3:
            table_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("|") and next_line.endswith("|"):
                    table_lines.append(next_line)
                    j += 1
                elif not next_line:
                    j += 1
                else:
                    break

            non_empty = [l for l in table_lines if l.strip()]
            if len(non_empty) >= 3:
                table_content = "\n".join(non_empty)
                tables.append({
                    "page": page_idx,
                    "content": table_content,
                })
            i = j
        else:
            i += 1

    return tables


def _extract_title(text: str) -> str:
    for line in text.split("\n")[:50]:
        line = line.strip()
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        if 10 < len(line) < 150 and not re.match(r'^[\d\.\s]+$', line) and not line.isupper():
            return line
    return "论文标题"


def _extract_abstract(text: str) -> str:
    patterns = [
        r'摘\s*要[：:]\s*(.*?)(?=关键词|Abstract|ABSTRACT|\n\n\n)',
        r'Abstract[：:]\s*(.*?)(?=Keywords|Introduction|\n\n\n)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip().replace("\n", " ")
    return ""


def _extract_sections(text: str) -> List[Dict]:
    pat = (
        r'(?:^|\n)(?:(?:第[一二三四五六七八九十\d]+章)|'
        r'(?:[A-Za-z\d]+(?:\.\d+)*))'
        r'[ \.、\t]+'
        r'([^\n]*[A-Za-z\u4e00-\u9fa5]+[^\n]*)(?=\n|$)'
    )
    seen, secs = set(), []
    for m in re.finditer(pat, text, re.MULTILINE):
        t = m.group(1).strip()
        skip = {"abstract", "references", "contents", "acknowledgements", "conclusion"}
        if t.lower() in skip:
            continue
        if 2 < len(t) < 150 and t not in seen:
            secs.append({"title": t, "position": m.start()})
            seen.add(t)
    secs.sort(key=lambda x: x["position"])
    return secs[:15]


def _save_formulas(formulas: List[str], path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 提取的公式\n\n")
        for i, formula in enumerate(formulas, 1):
            f.write(f"## 公式 {i}\n\n")
            f.write(f"```latex\n{formula}\n```\n\n")
    print(f"公式已保存到: {path}")


def _calculate_iou(box1: List[int], box2: List[int]) -> float:
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    ix1 = max(x1_1, x1_2)
    iy1 = max(y1_1, y1_2)
    ix2 = min(x2_1, x2_2)
    iy2 = min(y2_1, y2_2)

    inter_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)

    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)

    if box1_area == 0 or box2_area == 0:
        return 0.0

    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area
