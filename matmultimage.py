from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from PyQt6.QtGui import QPixmap

# --- Helper functions ---
def text_size(draw, text, font):
    bbox = draw.textbbox((0,0), text, font=font)
    width = bbox[2]-bbox[0]
    height = bbox[3]-bbox[1]
    ascent, descent = font.getmetrics()
    return width, height, ascent, descent

def matrix_size(mat, draw, font, padding_ratio=0.8):
    rows, cols = len(mat), len(mat[0])
    col_widths = [max(text_size(draw, str(mat[r][c]), font)[0] for r in range(rows)) for c in range(cols)]
    row_height = max(text_size(draw, "0", font)[1] for r in range(rows))
    width = sum(col_widths) + int(padding_ratio*row_height)*(cols-1)
    height = rows*row_height + int(padding_ratio*row_height)*(rows-1)
    return width, height, col_widths, row_height

def draw_matrix(draw, mat, top_left, font, padding_ratio=0.8):
    x, y = int(top_left[0]), int(top_left[1])
    width, height, col_widths, row_height = matrix_size(mat, draw, font, padding_ratio)

    # Brackets
    bracket_margin = int(0.35 * row_height)  # slightly bigger to cover numbers
    bracket_thickness = max(2, row_height // 6)
    bracket_width = max(12, bracket_thickness * 2)
    cap_length = bracket_thickness * 2.5
    y_top = y - bracket_margin
    y_bottom = y + height + bracket_margin

    # Draw vertical brackets
    draw.line([(x - bracket_width, y_top), (x - bracket_width, y_bottom)], fill="black", width=bracket_thickness)
    draw.line([(x + width + bracket_width, y_top), (x + width + bracket_width, y_bottom)], fill="black", width=bracket_thickness)
    # Draw top and bottom caps
    draw.line([(x - cap_length, y_top), (x, y_top)], fill="black", width=bracket_thickness)
    draw.line([(x + width, y_top), (x + width + cap_length, y_top)], fill="black", width=bracket_thickness)
    draw.line([(x - cap_length, y_bottom), (x, y_bottom)], fill="black", width=bracket_thickness)
    draw.line([(x + width, y_bottom), (x + width + cap_length, y_bottom)], fill="black", width=bracket_thickness)

    # Draw numbers with extra spacing
    for i, row in enumerate(mat):
        offset_y = y + i*(row_height + int(padding_ratio*row_height))
        offset_x = x
        for j, val in enumerate(row):
            draw.text((int(offset_x), int(offset_y)), str(val), font=font, fill="black")
            offset_x += col_widths[j] + int(1.2*padding_ratio*row_height)
    return width, height

# --- Full layout function with super-sampling and auto-scaling ---
def layout_matrices_ultra_example(matrices, symbols, max_width=2000, max_height=1600,
                                  initial_font_size=72, super_sample=12, margin_ratio=0.15):
    scale = super_sample
    font_size = initial_font_size

    while font_size > 8:
        font = ImageFont.truetype("arial.ttf", font_size*scale)
        temp_img = Image.new("RGB", (10,10))
        temp_draw = ImageDraw.Draw(temp_img)

        sizes = [matrix_size(mat, temp_draw, font) for mat in matrices]
        w_list, h_list = [s[0] for s in sizes], [s[1] for s in sizes]
        symbol_sizes = [text_size(temp_draw, s, font)[0:2] for s in symbols]
        space_list = [int((w_list[i]+w_list[i+1])*1.5/4) for i in range(len(symbols))]

        img_width = sum(w_list) + sum([s[0] for s in symbol_sizes]) + sum(space_list)
        img_height = max(h_list + [s[1] for s in symbol_sizes])

        margin_x = int(img_width*margin_ratio)
        margin_y = int(img_height*margin_ratio)
        img_width += 2*margin_x
        img_height += 2*margin_y

        if img_width <= max_width*scale and img_height <= max_height*scale:
            break
        font_size -= 4

    # Create image
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    x = margin_x
    y_base = margin_y

    for i in range(len(symbols)):
        y_matrix = y_base + (img_height - 2*margin_y - h_list[i])//2
        draw_matrix(draw, matrices[i], (x, y_matrix), font)
        x += w_list[i] + space_list[i]//2

        sym_w, sym_h = symbol_sizes[i]
        y_sym = y_base + (img_height - 2*margin_y - sym_h)//2
        draw.text((int(x), int(y_sym)), symbols[i], font=font, fill="black")
        x += sym_w + space_list[i]//2

    y_matrix = y_base + (img_height - 2*margin_y - h_list[-1])//2
    draw_matrix(draw, matrices[-1], (x, y_matrix), font)

    final_img = img.resize((img_width//scale, img_height//scale), Image.LANCZOS)
    return final_img


def render_matrix_mult_fixed_size(matrices, symbols, target_size=(400,150), super_sample=12):
    """
    Render matrices multiplication as a high-quality image, then scale
    to fixed size (target_size: width, height), return QPixmap.
    """
    # --- Step 1: Render ultra-high-quality image ---
    img = layout_matrices_ultra_example(
        matrices, symbols,
        max_width=2000, max_height=1600,
        initial_font_size=72, super_sample=super_sample
    )

    # --- Step 2: Resize to target size while preserving aspect ratio ---
    img.thumbnail(target_size, Image.LANCZOS)  # scales down in-place

    # --- Step 3: Convert to QPixmap ---
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    pixmap = QPixmap()
    pixmap.loadFromData(buffer.getvalue())
    return pixmap