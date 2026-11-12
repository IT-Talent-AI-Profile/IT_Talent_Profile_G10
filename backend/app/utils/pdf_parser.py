from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError


MAX_PDF_SIZE = 5 * 1024 * 1024
PDF_HEADER = b"%PDF-"


class PdfValidationError(ValueError):
    """Base class for PDF input validation and extraction errors."""


class PdfTooLargeError(PdfValidationError):
    pass


class InvalidPdfError(PdfValidationError):
    pass


class PdfEncryptedError(PdfValidationError):
    pass


class PdfNoTextError(PdfValidationError):
    """Raised when a valid PDF contains no selectable text (for example, a scan)."""


def extract_pdf_text(file_content: bytes) -> str:
    """Validate a PDF (maximum 5 MB) and extract selectable text from every page."""
    if not isinstance(file_content, bytes):
        raise TypeError("Nội dung file PDF phải ở dạng bytes")

    if not file_content:
        raise InvalidPdfError("File PDF không được để trống")

    if len(file_content) > MAX_PDF_SIZE:
        raise PdfTooLargeError("Dung lượng CV không được vượt quá 5 MB")

    if PDF_HEADER not in file_content[:1024]:
        raise InvalidPdfError("File tải lên không đúng định dạng PDF")

    try:
        reader = PdfReader(BytesIO(file_content), strict=False)

        if reader.is_encrypted:
            raise PdfEncryptedError("Không hỗ trợ file PDF được bảo vệ bằng mật khẩu")

        extracted_pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = (page.extract_text() or "").strip()
            except (PdfReadError, PdfStreamError, ValueError, OSError) as error:
                raise InvalidPdfError(
                    f"Không thể đọc nội dung trang {page_number} của PDF"
                ) from error

            if page_text:
                extracted_pages.append(page_text)

    except PdfValidationError:
        raise
    except (PdfReadError, PdfStreamError, ValueError, OSError, EOFError) as error:
        raise InvalidPdfError("File PDF không hợp lệ hoặc đã bị hỏng") from error

    result = "\n".join(extracted_pages).strip()
    if not result:
        raise PdfNoTextError(
            "Không trích xuất được văn bản từ PDF. "
            "File có thể là ảnh quét hoặc không chứa văn bản. Hãy nhập hồ sơ thủ công."
        )

    return result
