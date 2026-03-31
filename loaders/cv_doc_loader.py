# cv_doc_loader.py

from pathlib import Path
from typing import Optional
from pypdf import PdfReader


class CVDocLoader:
    """
    用于加载用户简历（当前支持 PDF）
    """

    def __init__(self):
        pass

    def load_pdf(self, file_path: str) -> str:
        """
        读取 PDF 文件并返回纯文本

        :param file_path: PDF 文件路径
        :return: 文本内容
        """
        path = Path(file_path)

        # 基础校验
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("当前仅支持 PDF 文件")

        try:
            reader = PdfReader(str(path))
            text_list = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_list.append(page_text)

            full_text = "\n".join(text_list)

            if not full_text.strip():
                raise ValueError("PDF 解析失败，未提取到文本（可能是扫描版）")

            return full_text

        except Exception as e:
            raise RuntimeError(f"读取 PDF 失败: {e}")

    def load(self, file_path: str) -> str:
        """
        通用入口（后续可扩展 docx / txt）

        :param file_path: 文件路径
        :return: 文本内容
        """
        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            return self.load_pdf(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")