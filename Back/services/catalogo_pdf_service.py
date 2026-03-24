from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _truncate(value: str, max_chars: int) -> str:
    return value if len(value) <= max_chars else value[: max_chars - 1] + "…"


def _center_x(text: str, font_size: int, page_width: int = 595) -> float:
    # Aproximación simple para Helvetica
    text_width = len(text) * (font_size * 0.52)
    return max(20, (page_width - text_width) / 2)


def _hex_to_rgb01(color_hex: str) -> tuple[float, float, float]:
    value = color_hex.lstrip("#")
    if len(value) != 6:
        return (0, 0, 0)
    r = int(value[0:2], 16) / 255
    g = int(value[2:4], 16) / 255
    b = int(value[4:6], 16) / 255
    return (r, g, b)


def _parse_jpeg_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        return None

    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2

        if marker in {0xD8, 0xD9}:
            continue

        if i + 2 > len(data):
            break
        seg_len = int.from_bytes(data[i:i + 2], "big")
        if seg_len < 2:
            break

        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if i + 7 > len(data):
                break
            height = int.from_bytes(data[i + 3:i + 5], "big")
            width = int.from_bytes(data[i + 5:i + 7], "big")
            return width, height

        i += seg_len

    return None


def _load_jpeg(path: Path) -> tuple[bytes, int, int] | None:
    if not path.exists() or not path.is_file():
        return None
    data = path.read_bytes()
    size = _parse_jpeg_size(data)
    if not size:
        return None
    return data, size[0], size[1]


def _resolve_local_image(imagen_url: str | None) -> tuple[bytes, int, int] | None:
    if not imagen_url:
        return None

    repo_root = Path(__file__).resolve().parent.parent.parent

    if imagen_url.startswith("/uploads/"):
        return _load_jpeg(repo_root / "Back" / imagen_url.lstrip("/"))

    if imagen_url.startswith("/assets/"):
        return _load_jpeg(repo_root / "Front" / imagen_url.lstrip("/"))

    path = Path(imagen_url)
    if path.is_absolute():
        return _load_jpeg(path)

    return _load_jpeg(repo_root / path)


class PdfPage:
    def __init__(self):
        self.commands: list[str] = []
        self.images: dict[str, tuple[bytes, int, int]] = {}


class StyledPdfBuilder:
    def __init__(self):
        self.pages: list[PdfPage] = []
        self.current = PdfPage()

    def new_page(self):
        if self.current.commands or self.current.images:
            self.pages.append(self.current)
        self.current = PdfPage()

    def set_fill_color(self, color: tuple[float, float, float]):
        r, g, b = color
        self.current.commands.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

    def set_stroke_color(self, color: tuple[float, float, float]):
        r, g, b = color
        self.current.commands.append(f"{r:.4f} {g:.4f} {b:.4f} RG")

    def text(self, x: float, y: float, text: str, size: int = 11, bold: bool = False, color: tuple[float, float, float] | None = None):
        font = "F2" if bold else "F1"
        safe = _escape_pdf_text(text)
        prefix = ""
        if color:
            r, g, b = color
            prefix = f"{r:.4f} {g:.4f} {b:.4f} rg\n"
        self.current.commands.append(f"{prefix}BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({safe}) Tj ET")

    def line(self, x1: float, y1: float, x2: float, y2: float):
        self.current.commands.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def rect(self, x: float, y: float, w: float, h: float):
        self.current.commands.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re S")

    def rect_fill(self, x: float, y: float, w: float, h: float):
        self.current.commands.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def image_jpeg(self, x: float, y: float, w: float, h: float, data: bytes, iw: int, ih: int):
        name = f"Im{len(self.current.images) + 1}"
        self.current.images[name] = (data, iw, ih)
        self.current.commands.append(f"q {w:.2f} 0 0 {h:.2f} {x:.2f} {y:.2f} cm /{name} Do Q")

    def build(self) -> bytes:
        if self.current.commands or self.current.images:
            self.pages.append(self.current)

        objects: list[str] = ["<< /Type /Catalog /Pages 2 0 R >>"]

        page_count = len(self.pages)
        page_obj_start = 3
        content_obj_start = page_obj_start + page_count

        image_obj_start = content_obj_start + page_count
        image_obj_cursor = image_obj_start
        page_image_refs: list[dict[str, int]] = []
        for page in self.pages:
            refs = {}
            for name in page.images:
                refs[name] = image_obj_cursor
                image_obj_cursor += 1
            page_image_refs.append(refs)

        font_f1_obj = image_obj_cursor
        font_f2_obj = image_obj_cursor + 1

        kids = []
        for i, page in enumerate(self.pages):
            page_obj_num = page_obj_start + i
            content_obj_num = content_obj_start + i
            kids.append(f"{page_obj_num} 0 R")

            xobjects = ""
            if page_image_refs[i]:
                xobj_parts = [f"/{k} {v} 0 R" for k, v in page_image_refs[i].items()]
                xobjects = f" /XObject << {' '.join(xobj_parts)} >>"

            objects.append(
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Contents {content_obj_num} 0 R "
                f"/Resources << /Font << /F1 {font_f1_obj} 0 R /F2 {font_f2_obj} 0 R >>{xobjects} >> >>"
            )

        objects.insert(1, f"<< /Type /Pages /Count {page_count} /Kids [{' '.join(kids)}] >>")

        for page in self.pages:
            content = "\n".join(page.commands)
            data = content.encode("latin-1", errors="replace")
            objects.append(f"<< /Length {len(data)} >>\nstream\n{content}\nendstream")

        for page in self.pages:
            for _name, (img_data, iw, ih) in page.images.items():
                stream_text = img_data.decode("latin-1")
                objects.append(
                    f"<< /Type /XObject /Subtype /Image /Width {iw} /Height {ih} "
                    "/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
                    f"/Length {len(img_data)} >>\nstream\n{stream_text}\nendstream"
                )

        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        out = ["%PDF-1.4\n"]
        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(sum(len(x.encode("latin-1", errors="replace")) for x in out))
            out.append(f"{idx} 0 obj\n{obj}\nendobj\n")

        xref_pos = sum(len(x.encode("latin-1", errors="replace")) for x in out)
        out.append(f"xref\n0 {len(objects) + 1}\n")
        out.append("0000000000 65535 f \n")
        for idx in range(1, len(objects) + 1):
            out.append(f"{offsets[idx]:010d} 00000 n \n")
        out.append(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF")
        return "".join(out).encode("latin-1", errors="replace")


def cargar_config_catalogo_pdf() -> dict:
    ruta = Path(__file__).resolve().parent.parent / "core" / "catalogo_pdf_config.json"
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def generar_catalogo_pdf(productos_por_categoria: dict[str, Iterable], categorias: list[str]) -> bytes:
    cfg = cargar_config_catalogo_pdf()
    tienda = cfg.get("tienda", {})
    pdf_cfg = cfg.get("pdf", {})
    pal = cfg.get("colores", {})

    c_bg = _hex_to_rgb01(pal.get("bg", "#080c09"))
    c_surface = _hex_to_rgb01(pal.get("surface", "#0d1a0f"))
    c_surface2 = _hex_to_rgb01(pal.get("surface2", "#122115"))
    c_border = _hex_to_rgb01(pal.get("border", "#1c3d22"))
    c_accent = _hex_to_rgb01(pal.get("accent", "#2ecc40"))
    c_text = _hex_to_rgb01(pal.get("text", "#f0f4f0"))
    c_muted = _hex_to_rgb01(pal.get("muted", "#7da882"))

    moneda = pdf_cfg.get("moneda", "Bs")
    pdf = StyledPdfBuilder()
    pdf.new_page()

    # Fondo portada
    pdf.set_fill_color(c_bg)
    pdf.rect_fill(0, 0, 595, 842)

    # Barra superior
    pdf.set_fill_color(c_surface)
    pdf.rect_fill(0, 780, 595, 62)
    titulo = pdf_cfg.get("titulo", "Catalogo de Productos")
    pdf.text(_center_x(titulo, 20), 806, titulo, size=20, bold=True, color=c_text)

    logo_path = tienda.get("logo_path", "Front/assets/img/logo.jpeg")
    logo = _resolve_local_image(str(logo_path))
    if logo:
        data, iw, ih = logo
        logo_w = 180
        logo_h = 120
        logo_x = (595 - logo_w) / 2
        logo_y = 600
        pdf.image_jpeg(logo_x, logo_y, logo_w, logo_h, data, iw, ih)

    # Panel inferior de datos
    panel_x, panel_y, panel_w, panel_h = 70, 360, 455, 200
    pdf.set_fill_color(c_surface)
    pdf.rect_fill(panel_x, panel_y, panel_w, panel_h)
    pdf.set_stroke_color(c_border)
    pdf.rect(panel_x, panel_y, panel_w, panel_h)

    y = panel_y + panel_h - 32
    pdf.text(panel_x + 24, y, tienda.get('nombre', '-'), size=16, bold=True, color=c_accent)
    y -= 24
    pdf.text(panel_x + 24, y, f"Sucursal: {tienda.get('sucursal', '-')}", color=c_text)
    y -= 18
    pdf.text(panel_x + 24, y, f"Telefono: {tienda.get('telefono', '-')}", color=c_text)
    y -= 18
    pdf.text(panel_x + 24, y, f"Direccion: {tienda.get('direccion', '-')}", color=c_text)
    y -= 18
    pdf.text(panel_x + 24, y, f"{tienda.get('mensaje', '-')}", color=c_muted)

    categorias_txt = ", ".join(categorias) if categorias else "General (todas)"
    total_productos = sum(len(items) for items in productos_por_categoria.values())
    pdf.text(95, 330, f"Categorias incluidas: {categorias_txt}", color=c_text)
    pdf.text(95, 312, f"Total productos: {total_productos}", color=c_text)
    pdf.text(95, 294, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", color=c_muted)

    # Tarjetas estilo UI
    card_w, card_h = 170, 220
    gap_x, gap_y = 12, 14
    start_x = 25
    top_y = 760

    for categoria, items in productos_por_categoria.items():
        if not items:
            continue

        # imágenes primero, sin imagen al final
        preparados = []
        for p in items:
            img = _resolve_local_image(getattr(p, "imagen_url", None))
            preparados.append((p, img))
        preparados.sort(key=lambda x: 1 if x[1] is None else 0)

        pdf.new_page()
        pdf.set_fill_color(c_bg)
        pdf.rect_fill(0, 0, 595, 842)

        pdf.set_fill_color(c_surface)
        pdf.rect_fill(0, 780, 595, 50)
        titulo_categoria = categoria or "General"
        pdf.text(_center_x(titulo_categoria, 15), 800, titulo_categoria, size=15, bold=True, color=c_accent)

        y_cursor = top_y
        col = 0

        for p, imagen in preparados:
            x = start_x + col * (card_w + gap_x)
            y = y_cursor - card_h

            if y < 40:
                pdf.new_page()
                pdf.set_fill_color(c_bg)
                pdf.rect_fill(0, 0, 595, 842)
                pdf.set_fill_color(c_surface)
                pdf.rect_fill(0, 780, 595, 50)
                titulo_cont = f"{titulo_categoria} · Continuacion"
                pdf.text(_center_x(titulo_cont, 13), 800, titulo_cont, size=13, bold=True, color=c_accent)
                y_cursor = top_y
                col = 0
                x = start_x
                y = y_cursor - card_h

            # tarjeta tipo "card" web
            pdf.set_fill_color(c_surface)
            pdf.rect_fill(x, y, card_w, card_h)
            pdf.set_stroke_color(c_border)
            pdf.rect(x, y, card_w, card_h)

            h_nombre, h_precio, h_img, h_codigo = 28, 22, 140, 30
            y_nombre = y + card_h - h_nombre
            y_precio = y_nombre - h_precio
            y_img = y_precio - h_img

            pdf.set_fill_color(c_surface2)
            pdf.rect_fill(x + 1, y_nombre, card_w - 2, h_nombre - 1)
            pdf.rect_fill(x + 1, y_precio, card_w - 2, h_precio - 1)
            pdf.rect_fill(x + 1, y, card_w - 2, h_codigo - 1)

            pdf.set_stroke_color(c_border)
            pdf.line(x, y_nombre, x + card_w, y_nombre)
            pdf.line(x, y_precio, x + card_w, y_precio)
            pdf.line(x, y_img, x + card_w, y_img)

            nombre = _truncate(getattr(p, "nombre", "-"), 28)
            codigo = _truncate(getattr(p, "codigo", "-"), 22)
            precio = f"{float(getattr(p, 'precio1', 0.0)):.2f}"

            pdf.text(x + 6, y + card_h - 18, nombre, size=10, bold=True, color=c_text)
            pdf.text(x + 6, y_nombre - 15, f"Precio: {moneda} {precio}", size=10, bold=True, color=c_accent)
            pdf.text(x + 6, y + 12, f"Codigo: {codigo}", size=9, color=c_muted)

            if imagen:
                data, iw, ih = imagen
                target_w, target_h = card_w - 12, h_img - 12
                ratio = min(target_w / iw, target_h / ih)
                w = iw * ratio
                h = ih * ratio
                img_x = x + (card_w - w) / 2
                img_y = y_img + ((h_img - h) / 2)
                pdf.image_jpeg(img_x, img_y, w, h, data, iw, ih)
            else:
                # Placeholder visual limpio (sin texto)
                pdf.set_fill_color(c_surface2)
                pdf.rect_fill(x + 8, y_img + 8, card_w - 16, h_img - 16)

            col += 1
            if col == 3:
                col = 0
                y_cursor -= (card_h + gap_y)

    return pdf.build()
