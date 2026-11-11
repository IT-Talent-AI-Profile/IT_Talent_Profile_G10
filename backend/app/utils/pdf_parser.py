from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_PDF_SIZE = 5 * 1024 * 1024
PDF_HEADER = b"%PDF-"


def extract_pdf_text(file_content: bytes) -> str:
    """Validate a PDF file and extract its selectable text."""
    if not isinstance(file_content, bytes):
        raise TypeError("Nội dung file PDF phải ở dạng bytes")

    if not file_content:
        raise ValueError("File PDF không được để trống")

    if len(file_content) > MAX_PDF_SIZE:
        raise ValueError("Dung lượng CV không được vượt quá 5 MB")

    if PDF_HEADER not in file_content[:1024]:
        raise ValueError("File tải lên không đúng định dạng PDF")

    try:
        reader = PdfReader(BytesIO(file_content), strict=False)

        if reader.is_encrypted:
            raise ValueError("Không hỗ trợ file PDF được bảo vệ bằng mật khẩu")

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except (PdfReadError, ValueError) as error:
                raise ValueError(
                    f"Không thể đọc nội dung trang {page_number} của PDF"
                ) from error

            page_text = page_text.strip()
            if page_text:
                extracted_pages.append(page_text)

    except PdfReadError as error:
        raise ValueError("File PDF không hợp lệ hoặc đã bị hỏng") from error

    result = "\n".join(extracted_pages).strip()

    if not result:
        raise ValueError(
            "Không trích xuất được văn bản từ PDF. "
            "File có thể là ảnh quét hoặc không chứa văn bản."
        )

    return result
