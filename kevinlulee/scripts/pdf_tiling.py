# pip install pymupdf kevinlulee
import math
import fitz  # PyMuPDF
import kevinlulee as kx

import functools
import inspect
from pathlib import Path
from typing import Callable, Any

from kevinlulee.extras.autopath import autopath 



# Example usage

PT_PER_IN = 72.0
MM_PER_IN = 25.4

def inches(x: float) -> float:
    return x * PT_PER_IN

def mm(x: float) -> float:
    return (x / MM_PER_IN) * PT_PER_IN

PAPER_SIZES_IN = {
    "letter": (8.5, 11.0),
    "legal":  (8.5, 14.0),
    "tabloid": (11.0, 17.0),
    "a4": (8.27, 11.69),   # 210 × 297 mm
    "a3": (11.69, 16.54),  # 297 × 420 mm
}

@autopath
def tile_poster_pdf(
    src_path: str,
    dst_path: str,
    paper: str = "letter",           # ["letter","legal","tabloid","a4","a3"]
    orientation: str = "portrait",   # ["portrait","landscape"]
    margin_in: float = 0.25,
    overlap_in: float = 0.25,
    page_index: int = 0,
    scale: float = 1.0
):
    """
    Split a large single PDF page into printer-friendly tiles (preserves 1:1 scale).
    - paper: target paper size name (see PAPER_SIZES_IN)
    - orientation: portrait/landscape orientation for tiles
    - margin_in: margin around the printable content on each tile (inches)
    - overlap_in: content overlap between adjacent tiles (inches)
    - page_index: which page from the source PDF to tile
    - scale: optional scale factor applied to the source page before tiling (1.0 = 100%)
    Output is a multi-page PDF where each page is one tile.
    """
    # kx.pretty_print(src_path, dst_path)
    # return 
    pw_in, ph_in = PAPER_SIZES_IN[paper.lower()]
    if orientation.lower() == "landscape":
        pw_in, ph_in = ph_in, pw_in

    page_margin = inches(margin_in)
    content_w = inches(pw_in) - 2 * page_margin
    content_h = inches(ph_in) - 2 * page_margin
    if content_w <= 0 or content_h <= 0:
        raise ValueError("Margins are too large for the chosen paper size.")

    overlap = inches(overlap_in)
    # Effective step between tiles (how much we move the clipping window each time)
    step_x = content_w - overlap if overlap < content_w else content_w
    step_y = content_h - overlap if overlap < content_h else content_h

    src = fitz.open(kx.readfile(src_path)["__path__"] if isinstance(kx.readfile(src_path), dict) else src_path)
    src_page = src[page_index]

    # Optionally scale the source page (e.g., 0.5 = 50%)
    if scale != 1.0:
        m = fitz.Matrix(scale, scale)
        rc = src_page.rect
        new_w, new_h = rc.width * scale, rc.height * scale
        # Create a temporary PDF with a scaled copy of the page
        tmp = fitz.open()
        tpage = tmp.new_page(width=new_w, height=new_h)
        tpage.show_pdf_page(tpage.rect, src, page_index, matrix=m)
        src.close()
        src = tmp
        src_page = src[0]

    W, H = src_page.rect.width, src_page.rect.height

    # How many tiles we need, stepping by (content_size - overlap)
    cols = max(1, math.ceil((W + overlap) / step_x))
    rows = max(1, math.ceil((H + overlap) / step_y))

    out = fitz.open()

    # Each output page (tile) should have fixed paper size
    tile_page_size = fitz.Rect(0, 0, inches(pw_in), inches(ph_in))
    inner_rect = fitz.Rect(
        page_margin, page_margin,
        page_margin + content_w, page_margin + content_h
    )

    for r in range(rows):
        for c in range(cols):
            # Compute the clip rect on the source page.
            # IMPORTANT: Keep clip size EXACTLY equal to content_w x content_h
            # so there's no scaling when mapping to inner_rect.
            left = c * step_x
            top  = r * step_y
            clip = fitz.Rect(left, top, left + content_w, top + content_h)

            # Allow the clip to extend beyond the page bounds;
            # content outside becomes blank—this keeps scale consistent on edge tiles.
            # (PyMuPDF is fine with clip partly outside the page.)
            tpage = out.new_page(width=tile_page_size.width, height=tile_page_size.height)
            tpage.show_pdf_page(inner_rect, src, src_page.number, clip=clip)

    # Save
    out.save(dst_path)
    out.close()
    src.close()



from pypdf import PdfReader, PdfWriter, Transformation
import math

from pypdf import PdfReader, PdfWriter, Transformation
import math
from pathlib import Path

@autopath
def split_pdf_into_tiles(
    src_path,
    dst_path,
    tile_width_inches=8.5,
    tile_height_inches=11.0,
    overlap_inches=0.5
):
    """
    Split a large PDF into smaller tiles for printing.
    
    Args:
        src_path: Path to input PDF file
        dst_path: Directory path for output files
        tile_width_inches: Width of each tile in inches (default: 8.5")
        tile_height_inches: Height of each tile in inches (default: 11")
        overlap_inches: Overlap between tiles in inches (default: 0.5")
    """
    # Convert inches to points (1 inch = 72 points)
    tile_width = tile_width_inches * 72
    tile_height = tile_height_inches * 72
    overlap = overlap_inches * 72
    
    # Create output directory if it doesn't exist
    dst_dir = Path(dst_path)
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    reader = PdfReader(src_path)
    page = reader.pages[0]  # Assuming single-page poster
    
    # Get original dimensions
    orig_width = float(page.mediabox.width)
    orig_height = float(page.mediabox.height)
    
    # Calculate number of tiles needed
    cols = math.ceil(orig_width / (tile_width - overlap))
    rows = math.ceil(orig_height / (tile_height - overlap))
    
    print(f"Original size: {orig_width/72:.1f}\" × {orig_height/72:.1f}\"")
    print(f"Tile size: {tile_width_inches}\" × {tile_height_inches}\"")
    print(f"Overlap: {overlap_inches}\"")
    print(f"Creating {rows}×{cols} = {rows*cols} tiles")
    print(f"Output directory: {dst_dir}")
    print()
    return 
    
    for row in range(rows):
        for col in range(cols):
            # Calculate crop box for this tile
            x_offset = col * (tile_width - overlap)
            y_offset = orig_height - (row + 1) * (tile_height - overlap)
            
            # Adjust last tiles to not exceed boundaries
            actual_width = min(tile_width, orig_width - x_offset)
            actual_height = min(tile_height, orig_height - (row * (tile_height - overlap)))
            
            # Create new PDF for this tile
            writer = PdfWriter()
            new_page = writer.add_blank_page(actual_width, actual_height)
            
            # Copy content with translation
            new_page.merge_transformed_page(
                page,
                Transformation().translate(-x_offset, -y_offset)
            )
            
            # Save tile
            output_file = dst_dir / f"tile_r{row+1}_c{col+1}.pdf"
            with open(output_file, "wb") as f:
                writer.write(f)
            
            print(f"Created: {output_file.name} ({actual_width/72:.1f}\" × {actual_height/72:.1f}\")")

# pip install pymupdf
import math
import fitz  # PyMuPDF

PT_PER_IN = 72.0
MM_PER_IN = 25.4

def inches(x: float) -> float:
    return x * PT_PER_IN

def mm(x: float) -> float:
    return (x / MM_PER_IN) * PT_PER_IN

PAPER_SIZES_IN = {
    "letter":  (8.5, 11.0),
    "legal":   (8.5, 14.0),
    "tabloid": (11.0, 17.0),
    "a4":      (8.27, 11.69),   # 210 × 297 mm
    "a3":      (11.69, 16.54),  # 297 × 420 mm
}

@autopath
def tile_poster_pdf(
    src_path: str,
    dst_path: str,
    *,
    paper: str = "letter",           # ["letter","legal","tabloid","a4","a3"]
    orientation: str = "portrait",   # ["portrait","landscape"]
    margin_in: float = 0.0,
    overlap_in: float = 0.0,
    page_index: int = 0,
    scale: float = 1.0
):
    """
    Split a large single PDF page into printer-friendly tiles, preserving 1:1 scale.
    Each output page is a tile of size = selected paper, with margins and overlap.
    Print the result at 100% (no "fit to page").
    """
    pw_in, ph_in = PAPER_SIZES_IN[paper.lower()]
    if orientation.lower() == "landscape":
        pw_in, ph_in = ph_in, pw_in

    page_margin = inches(margin_in)
    content_w = inches(pw_in) - 2 * page_margin
    content_h = inches(ph_in) - 2 * page_margin
    if content_w <= 0 or content_h <= 0:
        raise ValueError("Margins are too large for the chosen paper size.")

    overlap = inches(overlap_in)
    step_x = content_w - overlap if overlap < content_w else content_w
    step_y = content_h - overlap if overlap < content_h else content_h

    src = fitz.open(src_path)
    src_page = src[page_index]

    # Optional uniform scale of the source page before tiling
    if scale != 1.0:
        m = fitz.Matrix(scale, scale)
        rc = src_page.rect
        new_w, new_h = rc.width * scale, rc.height * scale
        tmp = fitz.open()
        tpage = tmp.new_page(width=new_w, height=new_h)
        tpage.show_pdf_page(tpage.rect, src, page_index, matrix=m)
        src.close()
        src = tmp
        src_page = src[0]

    W, H = src_page.rect.width, src_page.rect.height

    cols = max(1, math.ceil((W + overlap) / step_x))
    rows = max(1, math.ceil((H + overlap) / step_y))
    # kx.stop(W, H, cols, rows)

    out = fitz.open()
    tile_page_size = fitz.Rect(0, 0, inches(pw_in), inches(ph_in))
    # kx.stop(tile_page_size, content_w, content_h, page_margin)
    inner_rect = fitz.Rect(
        page_margin, page_margin,
        page_margin + content_w, page_margin + content_h
    )

    # kx.stop(step_x, step_y, H, W, rows, cols)
    for r in range(rows):
        for c in range(cols):
            left = c * step_x
            top  = r * step_y
            clip = fitz.Rect(left, top, left + content_w, top + content_h)

            tpage = out.new_page(width=tile_page_size.width, height=tile_page_size.height)
            tpage.show_pdf_page(inner_rect, src, src_page.number, clip=clip)

    out.save(dst_path)
    out.close()
    src.close()
    return True

if __name__ == "__main__":
    tile_poster_pdf('file:///media/fuse/crostini_25bd1ae3ef71bac8d459747ce670faa67d509f14_termina_penguin/projects/typst/mathbook/pymathbook/server/static/tempfile.pdf')
    # split_pdf_into_tiles("file:///media/fuse/crostini_25bd1ae3ef71bac8d459747ce670faa67d509f14_termina_penguin/projects/typst/mathbook/pymathbook/server/static/tempfile.pdf")
    
    # No overlap
    # split_pdf_into_tiles("large_poster.pdf", overlap_inches=0)
