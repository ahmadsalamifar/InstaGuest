import quopri

def clean_and_decode_text(text: str) -> str:
    """
    متن را بررسی می‌کند و اگر انکدینگ Quoted-Printable داشته باشد، آن را اصلاح می‌کند.
    """
    if not text:
        return ""
    
    try:
        # بررسی احتمال وجود فرمت quoted-printable
        if "=" in text and any(x in text for x in ["=D8", "=D9", "=20"]):
            decoded_bytes = quopri.decodestring(text.encode('utf-8'))
            return decoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error decoding text: {e}")
    
    return text