from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def pdf_to_markdown(pdf_path: Path) -> str:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.ocr_options.force_full_page_ocr = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )
    result = converter.convert(str(pdf_path))

    # Docling parses the PDF into a structured document, then exports that
    # structure to Markdown. This keeps the RAG module focused on using a
    # document parser instead of maintaining PDF layout heuristics ourselves.
    return result.document.export_to_markdown()
