from yt_dlp.cookies import extract_cookies_from_browser

def extract_cookies():
    try:
        cookies = extract_cookies_from_browser('chrome')
        print(f"✅ Extracted {len(cookies)} cookies from Chrome")
    except:
        try:
            cookies = extract_cookies_from_browser('firefox')
            print(f"✅ Extracted {len(cookies)} cookies from Firefox")
        except:
            print("❌ Could not extract cookies. Please install browser extension.")
            return
    
    with open('cookies.txt', 'w') as f:
        for cookie in cookies:
            f.write(f"{cookie.domain}\tTRUE\t{cookie.path}\t{cookie.secure}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
    
    print("✅ cookies.txt created successfully!")

if __name__ == '__main__':
    extract_cookies()