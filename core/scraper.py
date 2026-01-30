import instaloader
from instaloader import ConnectionException
import time
import random
from pathlib import Path
from .models import Post
from .utils import clean_and_decode_text

# هویت مرورگر معمولی
FIXED_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'

class InstagramScraper:
    def __init__(self, download_path="output"):
        self.L = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            # --- تغییر مهم: جلوگیری از ذخیره فایل جیسون ---
            save_metadata=False, 
            compress_json=False,
            # ---------------------------------------------
            filename_pattern="{shortcode}",
            sleep=True, 
            user_agent=FIXED_USER_AGENT,
            max_connection_attempts=1,
            request_timeout=20.0,
        )
        
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)

    def get_existing_shortcodes(self, target_username):
        target_dir = self.download_path / target_username
        if not target_dir.exists():
            return set()
        return {d.name for d in target_dir.iterdir() if d.is_dir()}

    def scrape_profile(self, target_username, count=12, skip_existing=True, urls_only=False, progress_callback=None):
        try:
            profile = instaloader.Profile.from_username(self.L.context, target_username)
        except Exception as e:
            yield None, f"❌ Error loading profile: {str(e)}"
            return

        user_dir = self.download_path / target_username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        urls_file_path = user_dir / "urls_list.txt"
        existing_posts = self.get_existing_shortcodes(target_username)
        posts_iterator = profile.get_posts()
        
        downloaded_count = 0
        limit = count 
        
        url_file_handle = None
        if urls_only:
             url_file_handle = open(urls_file_path, "a", encoding="utf-8")

        try:
            while downloaded_count < limit:
                try:
                    post = next(posts_iterator)
                except StopIteration:
                    break
                except Exception as e:
                    # تشخیص خطای محدودیت مهمان
                    err_msg = str(e)
                    if "Expecting value" in err_msg or "Redirect" in err_msg or "401" in err_msg:
                        yield None, "⚠️ Guest Limit Reached (~12 Posts). Login required for more."
                    else:
                        yield None, f"⚠️ Stream Ended: {e}"
                    break

                post_link = f"https://www.instagram.com/p/{post.shortcode}/"

                # --- حالت فقط لینک ---
                if urls_only:
                    if progress_callback: progress_callback(f"🔗 Link Found: {post.shortcode}", 0)
                    if url_file_handle: url_file_handle.write(post_link + "\n")
                    downloaded_count += 1
                    
                    dummy_post = Post(post.shortcode, "URL Only", "", False, target_username, 0, 0, 0, [], str(urls_file_path))
                    yield dummy_post, f"✅ Link Saved: {post.shortcode}"
                    time.sleep(random.uniform(0.5, 1.0))
                    continue

                # --- حالت دانلود فایل ---
                if skip_existing and post.shortcode in existing_posts:
                    if progress_callback: progress_callback(f"⏩ Skipped existing: {post.shortcode}", 0)
                    continue

                if progress_callback: progress_callback(f"⬇️ Downloading {post.shortcode}...", 0)
                target_dir = user_dir / post.shortcode
                
                try:
                    self.L.download_post(post, target=target_dir)
                    
                    new_post = Post(
                        shortcode=post.shortcode,
                        caption=clean_and_decode_text(post.caption) if post.caption else "",
                        display_url=post.url,
                        is_video=post.is_video,
                        owner_username=post.owner_username,
                        likes=post.likes,
                        comments_count=post.comments,
                        view_count=0,
                        comments=[],
                        local_path=str(target_dir)
                    )
                    
                    downloaded_count += 1
                    yield new_post, f"✅ Saved: {post.shortcode}"
                    
                except Exception as e:
                    print(f"DL Error: {e}")
                
                time.sleep(random.uniform(3, 6))
        
        finally:
            if url_file_handle:
                url_file_handle.close()

        yield [], f"🏁 Finished. Downloaded {downloaded_count} items."