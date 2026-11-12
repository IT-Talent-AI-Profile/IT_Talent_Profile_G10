from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.utils.pdf_parser import (
    MAX_PDF_SIZE,
    InvalidPdfError,
    PdfEncryptedError,
    PdfNoTextError,
    PdfTooLargeError,
    extract_pdf_text,
)


def create_text_pdf(page_texts: list[str]) -> bytes:
    """Create a small valid PDF with selectable text and a correct xref table."""
    objects: list[bytes] = []
    page_object_ids = [3 + index * 2 for index in range(len(page_texts))]
    content_object_ids = [page_id + 1 for page_id in page_object_ids]
    font_object_id = 3 + len(page_texts) * 2

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects.append(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_texts)} >>".encode("ascii")
    )

    page_objects: dict[int, bytes] = {}
    for page_id, content_id in zip(page_object_ids, content_object_ids):
        page_objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("ascii")

    content_objects: dict[int, bytes] = {}
    for content_id, page_text in zip(content_object_ids, page_texts):
        safe_text = (
            page_text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        stream = f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET".encode("latin-1")
        content_objects[content_id] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"\nendstream"
        )

    for object_id in range(3, font_object_id):
        if object_id in page_objects:
            objects.append(page_objects[object_id])
        else:
            objects.append(content_objects[object_id])
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


def create_blank_pdf(password: str | None = None) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    if password:
        writer.encrypt(password)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_pdf_not_bytes():
    with pytest.raises(TypeError, match="bytes"):
        extract_pdf_text("string_content")


def test_pdf_empty_bytes():
    with pytest.raises(InvalidPdfError, match="không được để trống"):
        extract_pdf_text(b"")


def test_pdf_oversize():
    oversized = b"%PDF-1.4\n" + b"x" * MAX_PDF_SIZE
    with pytest.raises(PdfTooLargeError, match="5 MB"):
        extract_pdf_text(oversized)


def test_pdf_invalid_header():
    with pytest.raises(InvalidPdfError, match="không đúng định dạng PDF"):
        extract_pdf_text(b"This is not a PDF")


def test_pdf_corrupted_data():
    with pytest.raises(InvalidPdfError, match="không hợp lệ hoặc đã bị hỏng"):
        extract_pdf_text(b"%PDF-1.4\ncorrupted bytes without a PDF catalog")


def test_pdf_valid_text_extraction():
    extracted = extract_pdf_text(create_text_pdf(["Vo Chi Duc - Fullstack Developer"]))
    assert "Vo Chi Duc" in extracted
    assert "Fullstack Developer" in extracted


def test_pdf_extracts_text_from_multiple_pages():
    extracted = extract_pdf_text(create_text_pdf(["First page", "Second page"]))
    assert extracted == "First page\nSecond page"


def test_pdf_no_text_scanned_image():
    with pytest.raises(PdfNoTextError, match="Không trích xuất được văn bản"):
        extract_pdf_text(create_blank_pdf())


def test_pdf_encrypted():
    with pytest.raises(PdfEncryptedError, match="mật khẩu"):
        extract_pdf_text(create_blank_pdf(password="secret"))
