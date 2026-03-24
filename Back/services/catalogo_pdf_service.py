from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable


def _escape_pdf_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _truncate(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1] + "…"


class SimplePdfBuilder:
    def __init__(self):
        self.pages: list[str] = []
        self._content_lines: list[str] = []

    def new_page(self):
        if self._content_lines:
            self.pages.append("\n".join(self._content_lines))
        self._content_lines = []

    def text(self, x: float, y: float, text: str, size: int = 11, bold: bool = False):
        font = "F2" if bold else "F1"
        safe = _escape_pdf_text(text)
        self._content_lines.append(f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({safe}) Tj ET")

    def line(self, x1: float, y1: float, x2: float, y2: float):
        self._content_lines.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def build(self) -> bytes:
        if self._content_lines:
            self.pages.append("\n".join(self._content_lines))

        objects: list[str] = []
        objects.append("<< /Type /Catalog /Pages 2 0 R >>")

        page_count = len(self.pages)
        kids_refs = []

        page_obj_start = 3
        content_obj_start = page_obj_start + page_count

        for i in range(page_count):
            page_obj = page_obj_start + i
            content_obj = content_obj_start + i
            kids_refs.append(f"{page_obj} 0 R")
            objects.append(
                "<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 595 842] /Contents {content_obj} 0 R "
                "/Resources << /Font << /F1 0 0 R /F2 0 0 R >> >> >>"
            )

        objects[1 - 1] = objects[0]
        pages_obj = f"<< /Type /Pages /Count {page_count} /Kids [{' '.join(kids_refs)}] >>"
        objects.insert(1, pages_obj)

        for content in self.pages:
            stream = content.encode("latin-1", errors="replace")
            objects.append(f"<< /Length {len(stream)} >>\nstream\n{content}\nendstream")

        # Font objects as last two
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        # remap font refs to actual object indexes
        f1_obj = len(objects) - 1
        f2_obj = len(objects)
        for i in range(2, 2 + page_count):
            objects[i] = objects[i].replace("/F1 0 0 R", f"/F1 {f1_obj} 0 R").replace(
                "/F2 0 0 R", f"/F2 {f2_obj} 0 R"
            )

        out = ["%PDF-1.4\n"]
        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(sum(len(x.encode("latin-1")) for x in out))
            out.append(f"{idx} 0 obj\n{obj}\nendobj\n")

        xref_pos = sum(len(x.encode("latin-1")) for x in out)
        out.append(f"xref\n0 {len(objects) + 1}\n")
        out.append("0000000000 65535 f \n")
        for idx in range(1, len(objects) + 1):
            out.append(f"{offsets[idx]:010d} 00000 n \n")
        out.append(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
        )

        return "".join(out).encode("latin-1", errors="replace")


def cargar_config_catalogo_pdf() -> dict:
    ruta = Path(__file__).resolve().parent.parent / "core" / "catalogo_pdf_config.json"
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def generar_catalogo_pdf(productos_por_categoria: dict[str, Iterable], categorias: list[str]) -> bytes:
    cfg = cargar_config_catalogo_pdf()
    tienda = cfg.get("tienda", {})
    pdf_cfg = cfg.get("pdf", {})
    moneda = pdf_cfg.get("moneda", "Bs")

    total_productos = sum(len(items) for items in productos_por_categoria.values())

    pdf = SimplePdfBuilder()
    pdf.new_page()

    y = 790
    pdf.text(50, y, pdf_cfg.get("titulo", "Catalogo de Productos"), size=20, bold=True)
    y -= 30
    pdf.text(50, y, f"Tienda: {tienda.get('nombre', '-')}", size=12, bold=True)
    y -= 18
    pdf.text(50, y, f"Sucursal: {tienda.get('sucursal', '-')}", size=11)
    y -= 16
    pdf.text(50, y, f"Telefono: {tienda.get('telefono', '-')}", size=11)
    y -= 16
    pdf.text(50, y, f"Direccion: {tienda.get('direccion', '-')}", size=11)
    y -= 16
    pdf.text(50, y, f"Mensaje: {tienda.get('mensaje', '-')}", size=11)
    y -= 25

    categorias_txt = ", ".join(categorias) if categorias else "General (todas las categorias)"
    pdf.text(50, y, f"Categorias incluidas: {categorias_txt}", size=11)
    y -= 16
    pdf.text(50, y, f"Total productos: {total_productos}", size=11)
    y -= 16
    pdf.text(50, y, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", size=11)

    # Páginas de detalle
    for categoria, items in productos_por_categoria.items():
        pdf.new_page()
        y = 800
        pdf.text(50, y, f"Categoria: {categoria}", size=16, bold=True)
        y -= 20

        pdf.text(50, y, "Codigo", size=10, bold=True)
        pdf.text(140, y, "Nombre", size=10, bold=True)
        pdf.text(500, y, f"Precio 1 ({moneda})", size=10, bold=True)
        y -= 6
        pdf.line(50, y, 545, y)
        y -= 16

        for p in items:
            if y < 60:
                pdf.new_page()
                y = 800
                pdf.text(50, y, f"Categoria: {categoria} (continuacion)", size=13, bold=True)
                y -= 20
                pdf.text(50, y, "Codigo", size=10, bold=True)
                pdf.text(140, y, "Nombre", size=10, bold=True)
                pdf.text(500, y, f"Precio 1 ({moneda})", size=10, bold=True)
                y -= 6
                pdf.line(50, y, 545, y)
                y -= 16

            codigo = _truncate(str(getattr(p, "codigo", "-")), 16)
            nombre = _truncate(str(getattr(p, "nombre", "-")), 52)
            precio = f"{float(getattr(p, 'precio1', 0.0)):.2f}"

            pdf.text(50, y, codigo, size=10)
            pdf.text(140, y, nombre, size=10)
            pdf.text(500, y, precio, size=10)
            y -= 14

    return pdf.build()
