import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import csv
from .models import Post

class ReportGenerator:
    def __init__(self, template_dir="templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def generate_html_report(self, posts: list[Post], output_path: str):
        """تولید فایل HTML برای نمایش پست‌ها"""
        template = self.env.get_template("report_template.html")
        
        # محاسبه آمار کلی
        total_likes = sum(p.likes for p in posts)
        total_comments = sum(p.comments_count for p in posts)
        
        html_content = template.render(
            posts=posts,
            total_likes=total_likes,
            total_comments=total_comments,
            post_count=len(posts)
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
    def generate_csv_report(self, posts: list[Post], output_path: str):
        """تولید فایل اکسل (CSV)"""
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Shortcode", "Type", "Likes", "Comments Count", "Caption", "Local Path"])
            for p in posts:
                p_type = "Video" if p.is_video else "Image"
                writer.writerow([p.shortcode, p_type, p.likes, p.comments_count, p.caption, p.local_path])