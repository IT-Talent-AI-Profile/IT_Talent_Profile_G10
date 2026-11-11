import pytest
from io import BytesIO
from pypdf import PdfWriter
from app.utils.pdf_parser import extract_pdf_text, MAX_PDF_SIZE


def create_sample_pdf(text: str = "Hồ sơ ứng viên: Võ Chí Đức. Kỹ năng: Python, FastAPI.") -> bytes:
    """Tạo file PDF hợp lệ trong bộ nhớ để phục vụ test."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    # pypdf không có canvas text trực tiếp dễ dàng trừ khi dùng annotation hoặc reportlab,
    # nhưng chúng ta có thể thêm text qua annotation hoặc page layout
    # Hoặc ghi một PDF stream hợp lệ có text
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def create_raw_text_pdf(text: str) -> bytes:
    """Tạo PDF thô chứa stream văn bản thực tế."""
    content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 55 >> stream
BT /F1 12 Tf 72 712 Td ({text}) Tj ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000261 00000 n 
0000000367 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
444
%%EOF"""
    return content.encode("latin1")


def test_pdf_not_bytes():
    with pytest.raises(TypeError) as exc:
        extract_pdf_text("string_content")
    assert "dạng bytes" in str(exc.value)


def test_pdf_empty_bytes():
    with pytest.raises(ValueError) as exc:
        extract_pdf_text(b"")
    assert "không được để trống" in str(exc.value)


def test_pdf_oversize():
    oversized = b"%PDF-" + b"x" * (MAX_PDF_SIZE + 10)
    with pytest.raises(ValueError) as exc:
        extract_pdf_text(oversized)
    assert "vượt quá 5 MB" in str(exc.value)


def test_pdf_invalid_header():
    invalid_data = b"This is just a plain text file pretending to be pdf"
    with pytest.raises(ValueError) as exc:
        extract_pdf_text(invalid_data)
    assert "không đúng định dạng PDF" in str(exc.value)


def test_pdf_corrupted_data():
    corrupted = b"%PDF-1.4 corrupt data stream without catalog"
    with pytest.raises(ValueError) as exc:
        extract_pdf_text(corrupted)
    assert "không hợp lệ hoặc đã bị hỏng" in str(exc.value)


def test_pdf_valid_text_extraction():
    raw_pdf = create_raw_text_pdf("Vo Chi Duc - Fullstack Developer")
    extracted = extract_pdf_text(raw_pdf)
    assert "Vo Chi Duc" in extracted
    assert "Fullstack Developer" in extracted


def test_pdf_no_text_scanned_image():
    # PDF hợp lệ nhưng trang trắng không có text
    blank_pdf = create_sample_pdf()
    with pytest.raises(ValueError) as exc:
        extract_pdf_text(blank_pdf)
    assert "Không trích xuất được văn bản từ PDF" in str(exc.value)
