from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Comment:
    text: str
    owner_username: str
    created_at: str

@dataclass
class Post:
    shortcode: str
    caption: str
    display_url: str
    is_video: bool
    owner_username: str
    likes: int
    comments_count: int
    comments: List[Comment] = field(default_factory=list)
    local_path: str = ""  # مسیر ذخیره فایل‌ها در کامپیوتر