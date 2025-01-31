import os
import json
import logging
import hashlib
import requests

from flask import Flask, request, jsonify
from doc2json.grobid2json.process_pdf import process_pdf_stream
from typing import Optional, Dict


# --------------------------------------------------------------------------------
# Logging Setup
# --------------------------------------------------------------------------------
def setup_logging():
    """
    配置日志记录器的基本设置
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


setup_logging()

app = Flask(__name__)


# --------------------------------------------------------------------------------
# Optional: If you need doc2json or GROBID-specific configs,
# you can define them here. Or pass them inline to parse_pdf_in_memory.
# --------------------------------------------------------------------------------
# Example:
# GROBID_CONFIG = {
#     "grobid_url": "http://localhost:8070/api",
#     "batch_size": 20
# }

# --------------------------------------------------------------------------------
# Helper Function
# --------------------------------------------------------------------------------
def parse_pdf_in_memory(pdf_bytes: bytes, filename: str = "uploaded.pdf",
                        grobid_config: Optional[Dict] = None) -> Dict:
    """
    使用 doc2json 的 process_pdf_stream 来解析 PDF 字节流，直接返回 Python dict。

    :param pdf_bytes: PDF 文件的原始二进制内容
    :param filename: 用于 process_pdf_stream 的一个标识，可与实际文件名保持一致
    :param grobid_config: 可选 GROBID 配置 (dict)，如要自定义 GROBID URL 等
    :return: doc2json 解析产生的 Python 字典
    """
    if not pdf_bytes:
        raise ValueError("No PDF content provided or file is empty.")

    # 计算 SHA-1 值，用于 doc2json 的 'sha' 参数
    pdf_sha = hashlib.sha1(pdf_bytes).hexdigest()

    try:
        # 调用 process_pdf_stream
        result = process_pdf_stream(
            input_file=filename,  # 可保留原名，含空格也行
            sha=pdf_sha,
            input_stream=pdf_bytes,
            grobid_config=grobid_config
        )
        return result

    except Exception as e:
        logging.error(f"Failed to parse PDF in memory: {e}", exc_info=True)
        raise


# --------------------------------------------------------------------------------
# Main Routes
# --------------------------------------------------------------------------------
@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    """
    全程在内存中解析上传 PDF，不创建磁盘文件，返回 doc2json 的解析结果。
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    if not uploaded_file or not uploaded_file.filename.strip():
        return jsonify({"error": "Empty filename"}), 400

    try:
        # 从流中读取 PDF 内容到内存
        pdf_bytes = uploaded_file.read()
        filename = uploaded_file.filename  # 保留原文件名 (包含空格)
        logging.info(f"Received PDF in memory: {filename}")

        # 解析 PDF
        parsed_json = parse_pdf_in_memory(pdf_bytes, filename=filename)

        return jsonify({
            "message": "Processing complete (in-memory).",
            "parsed_json": parsed_json
        }), 200

    except Exception as e:
        logging.error(f"PDF processing failed in memory: {e}", exc_info=True)
        return jsonify({
            "error": "PDF processing failed",
            "details": str(e)
        }), 500


# (Optional) Another endpoint to demonstrate how you'd process a PDF from a URL in-memory
@app.route('/process_pdf_url', methods=['GET'])
def process_pdf_url():
    """
    从指定 URL 下载 PDF 至内存，再使用 process_pdf_stream 解析，返回 JSON。
    不产生任何本地文件。

    示例: GET /process_pdf_url?url=https://arxiv.org/pdf/2301.12345.pdf
    """
    pdf_url = request.args.get('url')
    if not pdf_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        logging.info(f"Downloading PDF from {pdf_url}")
        resp = requests.get(pdf_url, stream=True)
        resp.raise_for_status()

        pdf_bytes = resp.content
        if not pdf_bytes:
            return jsonify({"error": "Downloaded PDF is empty"}), 400

        # 以 URL 的结尾做 filename，或随意指定
        filename = os.path.basename(pdf_url) or "downloaded.pdf"
        if not filename.lower().endswith('.pdf'):
            filename += ".pdf"

        # 调用 in-memory 解析
        parsed_json = parse_pdf_in_memory(pdf_bytes, filename=filename)

        return jsonify({
            "message": "Successfully processed PDF from URL in-memory.",
            "parsed_json": parsed_json
        }), 200

    except requests.RequestException as re:
        logging.error(f"Failed to download PDF: {re}")
        return jsonify({"error": "Failed to download PDF", "details": str(re)}), 400
    except Exception as e:
        logging.error(f"Error processing PDF from URL in memory: {e}")
        return jsonify({"error": "Failed to process online PDF", "details": str(e)}), 500


# --------------------------------------------------------------------------------
# Start the server
# --------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
