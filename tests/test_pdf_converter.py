from app.services.pdf_converter import PDFBackend, _resolve_backend_order


def test_resolve_backend_order_auto() -> None:
    assert _resolve_backend_order("auto") == (PDFBackend.DOCX2PDF, PDFBackend.SOFFICE)


def test_resolve_backend_order_docx2pdf() -> None:
    assert _resolve_backend_order("docx2pdf") == (PDFBackend.DOCX2PDF, PDFBackend.SOFFICE)


def test_resolve_backend_order_soffice() -> None:
    assert _resolve_backend_order("soffice") == (PDFBackend.SOFFICE, PDFBackend.DOCX2PDF)

