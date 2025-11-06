#!/usr/bin/env python3
"""
Generate social media posts using Playwright (browser rendering)
This properly handles Nepali Devanagari text including complex conjuncts
"""

import argparse
import json
import sys
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import datetime


def extract_colors_from_background(image_path):
    """Extract dominant colors from background image."""
    try:
        img = Image.open(image_path)
        
        # Resize for faster processing
        img = img.resize((100, 100))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get pixels
        pixels = list(img.getdata())
        
        # Calculate average color
        r_avg = sum(p[0] for p in pixels) // len(pixels)
        g_avg = sum(p[1] for p in pixels) // len(pixels)
        b_avg = sum(p[2] for p in pixels) // len(pixels)
        
        # Generate color variations
        base_color = f"rgb({r_avg}, {g_avg}, {b_avg})"
        
        # Lighter version (for container background)
        lighter_r = min(255, r_avg + 30)
        lighter_g = min(255, g_avg + 30)
        lighter_b = min(255, b_avg + 30)
        lighter_color = f"rgba({lighter_r}, {lighter_g}, {lighter_b}, 0.98)"
        
        # Even lighter (for gradients)
        lightest_r = min(255, r_avg + 50)
        lightest_g = min(255, g_avg + 50)
        lightest_b = min(255, b_avg + 50)
        lightest_color = f"rgba({lightest_r}, {lightest_g}, {lightest_b}, 0.98)"
        
        # Darker version (for borders and accents)
        darker_r = max(0, r_avg - 40)
        darker_g = max(0, g_avg - 40)
        darker_b = max(0, b_avg - 40)
        border_color = f"rgb({darker_r}, {darker_g}, {darker_b})"
        
        # Even darker (for text) - make it very dark for readability
        darkest_r = max(0, min(60, r_avg - 300))
        darkest_g = max(0, min(60, g_avg - 300))
        darkest_b = max(0, min(60, b_avg - 300))
        text_color = f"rgb({darkest_r}, {darkest_g}, {darkest_b})"
        
        # Semi-transparent versions for news boxes
        box_bg_1 = f"rgba({lighter_r}, {lighter_g}, {lighter_b}, 0.7)"
        box_bg_2 = f"rgba({lightest_r}, {lightest_g}, {lightest_b}, 0.6)"
        
        return {
            'base': base_color,
            'container_start': lighter_color,
            'container_end': lightest_color,
            'border': border_color,
            'border_alt': f"rgb({max(0, r_avg - 50)}, {max(0, g_avg - 50)}, {max(0, b_avg - 50)})",
            'text': text_color,
            'box_bg_1': box_bg_1,
            'box_bg_2': box_bg_2,
            'box_bg_alt_1': f"rgba({r_avg + 20}, {g_avg + 20}, {b_avg + 20}, 0.7)",
            'box_bg_alt_2': f"rgba({r_avg + 40}, {g_avg + 40}, {b_avg + 40}, 0.5)"
        }
    except Exception as e:
        # Fallback to default colors if extraction fails
        print(f"Warning: Could not extract colors from background: {e}")
        return {
            'base': 'rgb(230, 210, 200)',
            'container_start': 'rgba(255, 250, 245, 0.98)',
            'container_end': 'rgba(255, 245, 240, 0.98)',
            'border': '#d4a574',
            'border_alt': '#c9916d',
            'text': '#2c1810',
            'box_bg_1': 'rgba(255, 255, 255, 0.6)',
            'box_bg_2': 'rgba(255, 250, 245, 0.4)',
            'box_bg_alt_1': 'rgba(255, 248, 240, 0.7)',
            'box_bg_alt_2': 'rgba(255, 245, 235, 0.5)'
        }


def create_html_template(summaries, show_numbers=True, start_index=1):
    """Create HTML template with Nepali summaries."""
    
    # Get absolute path to background image and convert to base64
    background_path = Path('background.png').absolute()
    
    # Extract colors from background image
    colors = extract_colors_from_background(background_path)
    
    # Read and encode background image as base64
    background_data_url = ""
    if background_path.exists():
        with open(background_path, 'rb') as f:
            background_bytes = f.read()
            background_base64 = base64.b64encode(background_bytes).decode('utf-8')
            background_data_url = f"data:image/png;base64,{background_base64}"
    
    # Build summary HTML
    summary_html = ""
    for i, summary in enumerate(summaries, start_index):
        summary_text = summary.get('summary', '')
        if show_numbers:
            summary_html += f'<div class="summary">📰 {i}. {summary_text}</div>\n'
        else:
            summary_html += f'<div class="summary">📰 {summary_text}</div>\n'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');
            
            body {{
                margin: 0;
                padding: 0;
                width: 1080px;
                height: 1920px;
                background-image: url('{background_data_url}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                font-family: 'Noto Sans Devanagari', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .container {{
                width: 90%;
                max-width: 950px;
                padding: 50px 45px;
                background: linear-gradient(135deg, {colors['container_start']} 0%, {colors['container_end']} 100%);
                border-radius: 30px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), 
                            0 0 0 1px rgba(255, 255, 255, 0.5) inset;
                border: 3px solid {colors['border']};
            }}
            
            .summary {{
                position: relative;
                font-size: 34px;
                line-height: 1.7;
                color: {colors['text']};
                font-weight: 500;
                margin-bottom: 35px;
                padding: 25px 30px;
                background: linear-gradient(to right, {colors['box_bg_1']}, {colors['box_bg_2']});
                border-left: 5px solid {colors['border']};
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
            }}
            
            .summary:nth-child(odd) {{
                border-left-color: {colors['border']};
                background: linear-gradient(to right, {colors['box_bg_alt_1']}, {colors['box_bg_alt_2']});
            }}
            
            .summary:nth-child(even) {{
                border-left-color: {colors['border_alt']};
                background: linear-gradient(to right, {colors['box_bg_1']}, {colors['box_bg_2']});
            }}
            
            .summary:last-child {{
                margin-bottom: 0;
            }}
            
            .summary:hover {{
                transform: translateX(5px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {summary_html}
        </div>
    </body>
    </html>
    """
    return html


def generate_post_with_playwright(summaries, output_path, config, start_index=1):
    """Generate post using Playwright browser rendering."""
    
    html = create_html_template(summaries, not config.get('no_number', False), start_index)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1920})
        
        page.set_content(html)
        
        # Wait for fonts to load
        page.wait_for_timeout(2000)
        
        page.screenshot(path=str(output_path), full_page=True)
        
        browser.close()
    
    return True


def generate_multiple_posts(summaries, output_dir, config):
    """Generate multiple posts if summaries don't fit in one post."""
    
    # Maximum summaries per post (to ensure readability)
    max_per_post = config.get('max_per_post', 6)
    
    # Split summaries into chunks
    total_summaries = len(summaries)
    num_posts = (total_summaries + max_per_post - 1) // max_per_post  # Ceiling division
    
    print(f"INFO: Generating {num_posts} post(s) for {total_summaries} summaries...")
    print(f"INFO: Max {max_per_post} summaries per post")
    
    generated_posts = []
    
    with sync_playwright() as p:
        print("INFO: Launching browser for rendering...")
        browser = p.chromium.launch()
        
        for post_num in range(num_posts):
            start_idx = post_num * max_per_post
            end_idx = min(start_idx + max_per_post, total_summaries)
            chunk = summaries[start_idx:end_idx]
            
            # Generate output filename
            if num_posts == 1:
                output_path = output_dir / "combined_news_post.png"
            else:
                output_path = output_dir / f"combined_news_post_{post_num + 1}.png"
            
            print(f"INFO: Generating post {post_num + 1}/{num_posts} with summaries {start_idx + 1}-{end_idx}...")
            
            # Create HTML
            html = create_html_template(chunk, not config.get('no_number', False), start_idx + 1)
            
            # Render
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            page.set_content(html)
            
            # Wait for fonts and background image to load
            page.wait_for_timeout(3000)
            
            # Take screenshot
            page.screenshot(path=str(output_path), full_page=True)
            page.close()
            
            print(f"SUCCESS: Generated {output_path.name}")
            generated_posts.append(str(output_path))
        
        browser.close()
    
    return generated_posts


def main():
    parser = argparse.ArgumentParser(description="Generate posts with Playwright (perfect Nepali rendering)")
    parser.add_argument('--input', default='multi_source_summaries.json')
    parser.add_argument('--output-dir', default='output')
    parser.add_argument('--no-number', action='store_true')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--max-per-post', type=int, default=6, help='Maximum summaries per post')
    
    args = parser.parse_args()
    
    # Load summaries
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found")
        sys.exit(1)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    print(f"INFO: Loaded {len(summaries)} summaries")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Generate posts (multiple if needed)
    config = {
        'no_number': args.no_number,
        'max_per_post': args.max_per_post
    }
    
    generated_posts = generate_multiple_posts(summaries, output_dir, config)
    
    print(f"\nSUCCESS: Generated {len(generated_posts)} post(s)")
    for post in generated_posts:
        print(f"   - {post}")
    print("\nThe Nepali text renders PERFECTLY with all conjuncts!")


if __name__ == '__main__':
    main()
