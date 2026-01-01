"""
索引ページのHTMLを保存して確認するスクリプト
"""
import requests

def save_html(url: str, filename: str):
    """HTMLを保存"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        response.encoding = response.apparent_encoding or 'utf-8'
        response.raise_for_status()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"HTMLを保存しました: {filename}")
        print(f"サイズ: {len(response.text)} 文字")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    # 索引4のHTMLを保存
    save_html(
        "http://notesofacim.blog.fc2.com/blog-entry-434.html",
        "index4.html"
    )

