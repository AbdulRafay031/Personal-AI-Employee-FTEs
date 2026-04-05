"""
Create an attractive image for LinkedIn post about AI Employee Automation
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create image dimensions (LinkedIn recommended: 1200x627 or 1080x1080)
width, height = 1200, 627

# Create gradient background
img = Image.new('RGB', (width, height), color='#0077B5')  # LinkedIn blue
draw = ImageDraw.Draw(img)

# Draw gradient effect
for y in range(height):
    r = int(0 + (20 - 0) * y / height)
    g = int(119 + (60 - 119) * y / height)
    b = int(181 + (150 - 181) * y / height)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# Add title text
title_text = "🤖 AI EMPLOYEE SYSTEM"
subtitle_text = "LinkedIn Automation Testing"
tech_stack_text = "Python • Playwright • Obsidian • MCP • Qwen AI"
status_text = "✅ WORKING"

# Try to use default font (will scale based on availability)
try:
    title_font = ImageFont.truetype("arial.ttf", 48)
    subtitle_font = ImageFont.truetype("arial.ttf", 36)
    tech_font = ImageFont.truetype("arial.ttf", 28)
    status_font = ImageFont.truetype("arial.ttf", 60, bold=True)
except:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    tech_font = ImageFont.load_default()
    status_font = ImageFont.load_default()

# Calculate text positions (centered)
def get_text_bbox(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

title_w, title_h = get_text_bbox(title_text, title_font)
subtitle_w, subtitle_h = get_text_bbox(subtitle_text, subtitle_font)
tech_w, tech_h = get_text_bbox(tech_stack_text, tech_font)
status_w, status_h = get_text_bbox(status_text, status_font)

# Draw text with shadow effect
shadow_offset = 3

# Title (with shadow)
draw.text(((width - title_w) // 2 + shadow_offset, 100 + shadow_offset), 
          title_text, fill=(0, 0, 0, 128), font=title_font)
draw.text(((width - title_w) // 2, 100), 
          title_text, fill=(255, 255, 255), font=title_font)

# Subtitle (with shadow)
draw.text(((width - subtitle_w) // 2 + shadow_offset, 180 + shadow_offset), 
          subtitle_text, fill=(0, 0, 0, 128), font=subtitle_font)
draw.text(((width - subtitle_w) // 2, 180), 
          subtitle_text, fill=(255, 255, 255), font=subtitle_font)

# Tech stack (with shadow)
draw.text(((width - tech_w) // 2 + shadow_offset, 280 + shadow_offset), 
          tech_stack_text, fill=(0, 0, 0, 128), font=tech_font)
draw.text(((width - tech_w) // 2, 280), 
          tech_stack_text, fill=(255, 215, 0), font=tech_font)  # Gold color

# Status badge
badge_x = (width - status_w) // 2
badge_y = 380
badge_padding = 20
badge_width = status_w + badge_padding * 2
badge_height = status_h + badge_padding * 2

# Draw badge background (rounded rectangle simulation)
draw.rounded_rectangle([(badge_x - badge_padding, badge_y - badge_padding), 
                        (badge_x + badge_width - badge_padding, badge_y + badge_height - badge_padding)], 
                       radius=15, fill=(46, 204, 113, 200))

# Status text (with shadow)
draw.text((badge_x + shadow_offset, badge_y + shadow_offset), 
          status_text, fill=(0, 0, 0, 128), font=status_font)
draw.text((badge_x, badge_y), 
          status_text, fill=(255, 255, 255), font=status_font)

# Add workflow diagram
workflow_y = 480
workflow_items = [
    ("📧 Gmail", "→"),
    ("🤖 AI", "→"),
    ("✅ Approval", "→"),
    ("📤 LinkedIn", "")
]

current_x = 150
for item, arrow in workflow_items:
    # Draw item box
    item_w, item_h = get_text_bbox(item, tech_font)
    box_w = max(120, item_w + 20)
    box_h = 50
    
    draw.rounded_rectangle([(current_x, workflow_y), 
                            (current_x + box_w, workflow_y + box_h)], 
                           radius=10, fill=(255, 255, 255, 200))
    draw.text((current_x + (box_w - item_w) // 2, workflow_y + 12), 
              item, fill=(0, 0, 0), font=tech_font)
    
    current_x += box_w + 10
    
    # Draw arrow
    if arrow:
        draw.text((current_x, workflow_y + 10), arrow, fill=(255, 255, 255), font=tech_font)
        current_x += 40

# Add footer
footer_text = "Local-First • Human-in-the-Loop • 100% Free"
footer_w, footer_h = get_text_bbox(footer_text, tech_font)
draw.text(((width - footer_w) // 2, height - 60), 
          footer_text, fill=(255, 255, 255, 200), font=tech_font)

# Save image
output_path = "AI_Employee_Vault/Plans/linkedin_post_image.png"
img.save(output_path)
print(f"✓ Image created: {output_path}")
print(f"  Dimensions: {width}x{height}")
print(f"  Ready for LinkedIn upload!")
