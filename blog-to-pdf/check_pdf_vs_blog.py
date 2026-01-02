"""
PDFとブログの表記を比較するスクリプト
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import sys
import time
from generate_365bot_pdf import fetch_post_content

def fetch_blog_content(url: str) -> dict:
    """ブログからコンテンツを取得"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルを取得
        title_elem = soup.find('h2', class_='entry_header')
        if not title_elem:
            for h2 in soup.find_all('h2'):
                if h2.get('class') and 'entry_header' in h2.get('class'):
                    title_elem = h2
                    break
        
        title = title_elem.get_text(strip=True) if title_elem else "タイトルなし"
        
        # 「ACIM学習ガイド」や「ACIM学習ノート」を削除
        title = re.sub(r'^ACIM学習(ガイド|ノート)\s*[-|]?\s*', '', title)
        title = re.sub(r'\s*[-|]?\s*ACIM学習(ガイド|ノート)$', '', title)
        title = re.sub(r'ACIM学習(ガイド|ノート)', '', title)
        title = title.replace('神の使い', '神の使者')
        title = title.strip()
        
        # コンテンツを取得
        content_elem = soup.find('div', class_='entry_body')
        if not content_elem:
            for div in soup.find_all('div'):
                if div.get('class') and 'entry_body' in div.get('class'):
                    content_elem = div
                    break
        
        content = ""
        if content_elem:
            # <br>タグを改行に変換
            for br in content_elem.find_all('br'):
                br.replace_with('\n')
            
            # <p>タグの後に改行を追加
            for p in content_elem.find_all('p'):
                if p.string:
                    p.string = p.string + '\n\n'
                else:
                    if p.contents:
                        p.append('\n\n')
            
            # テキストを取得
            content = content_elem.get_text(separator='\n', strip=False)
            
            # Tweetセクションを削除
            tweet_pos = content.find('Tweet')
            if tweet_pos >= 0:
                content = content[:tweet_pos]
            
            # 連続する空白行を整理
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip()
        
        return {
            'title': title,
            'content': content,
            'url': url
        }
    except Exception as e:
        return {
            'title': "エラー",
            'content': f"エラー: {e}",
            'url': url
        }

def extract_pdf_text(pdf_path: str) -> list:
    """PDFからテキストを抽出"""
    posts = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            current_title = None
            current_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                
                if not text.strip():
                    continue
                
                # タイトル行を探す（Dayで始まる行）
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    line_stripped = line.strip()
                    if re.match(r'Day\d+', line_stripped):
                        # 前の投稿を保存
                        if current_title and current_content:
                            content_text = '\n'.join(current_content).strip()
                            if content_text:  # 空でない場合のみ追加
                                posts.append({
                                    'title': current_title,
                                    'content': content_text
                                })
                        
                        # 新しい投稿を開始
                        current_title = line_stripped
                        current_content = []
                        # タイトルの後の行からコンテンツを開始
                        if i + 1 < len(lines):
                            current_content = [l for l in lines[i+1:] if l.strip()]
                    elif current_title:
                        # コンテンツ行（空行でない場合のみ）
                        if line_stripped:
                            current_content.append(line_stripped)
            
            # 最後の投稿を保存
            if current_title and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    posts.append({
                        'title': current_title,
                        'content': content_text
                    })
    except Exception as e:
        print(f"PDF読み込みエラー: {e}")
        import traceback
        traceback.print_exc()
    
    return posts

def compare_content(blog_content: str, pdf_content: str, title: str) -> dict:
    """コンテンツを比較"""
    # 空白を正規化して比較
    blog_normalized = re.sub(r'\s+', ' ', blog_content.strip())
    pdf_normalized = re.sub(r'\s+', ' ', pdf_content.strip())
    
    # 改行を保持した比較も行う
    blog_lines = [line.strip() for line in blog_content.split('\n') if line.strip()]
    pdf_lines = [line.strip() for line in pdf_content.split('\n') if line.strip()]
    
    differences = []
    
    # 行数比較
    if len(blog_lines) != len(pdf_lines):
        differences.append(f"行数が異なります: ブログ={len(blog_lines)}行, PDF={len(pdf_lines)}行")
    
    # 内容比較（最初の500文字）
    if blog_normalized[:500] != pdf_normalized[:500]:
        differences.append("最初の500文字が異なります")
        differences.append(f"ブログ: {blog_normalized[:200]}...")
        differences.append(f"PDF: {pdf_normalized[:200]}...")
    
    # 完全一致チェック
    if blog_normalized == pdf_normalized:
        return {
            'match': True,
            'differences': []
        }
    else:
        return {
            'match': False,
            'differences': differences,
            'blog_length': len(blog_content),
            'pdf_length': len(pdf_content)
        }

def main():
    """メイン処理"""
    # JSONファイルからデータを読み込む
    json_path = "神の使者365日の言葉_data.json"
    
    print("=" * 60)
    print("PDF生成データとブログの表記を比較します")
    print("=" * 60)
    
    # JSONファイルからデータを読み込む
    if os.path.exists(json_path):
        print(f"\nJSONファイルを読み込み中: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            pdf_posts_data = json.load(f)
        print(f"JSONから {len(pdf_posts_data)} 件の投稿データを読み込みました")
    else:
        print(f"[エラー] JSONファイルが見つかりません: {json_path}")
        print("まず generate_365bot_pdf.py を実行してデータを生成してください。")
        return
    
    # Day001からDay365まで全件をチェック（Day番号が含まれるもののみ）
    all_posts = []
    for post in pdf_posts_data:
        title = post.get('title', '')
        # Day番号が含まれる投稿のみを対象とする
        if re.search(r'Day0*(\d+)', title, re.IGNORECASE):
            all_posts.append(post)
    
    print(f"Day001～Day365の投稿: {len(all_posts)} 件をチェックします")
    
    # 各投稿をチェック
    for i, pdf_post_data in enumerate(all_posts, 1):
        url = pdf_post_data.get('url', '')
        if not url:
            print(f"\n[スキップ] {i}件目: URLがありません")
            continue
        
        print(f"\n{'='*60}")
        print(f"チェック {i}/{len(all_posts)}: {url}")
        print(f"{'='*60}")
        
        # ブログからコンテンツを取得
        blog_data = fetch_blog_content(url)
        print(f"ブログタイトル: {blog_data['title']}")
        print(f"ブログコンテンツ長: {len(blog_data['content'])} 文字")
        
        # PDFデータ
        pdf_post = {
            'title': pdf_post_data.get('title', ''),
            'content': pdf_post_data.get('content', '')
        }
        
        print(f"PDFタイトル: {pdf_post['title']}")
        print(f"PDFコンテンツ長: {len(pdf_post['content'])} 文字")
        
        # タイトル比較
        if blog_data['title'] != pdf_post['title']:
            print(f"[差異あり] タイトルが異なります:")
            print(f"  ブログ: {blog_data['title']}")
            print(f"  PDF: {pdf_post['title']}")
        else:
            print("[OK] タイトルは一致しています")
        
        # コンテンツ比較
        comparison = compare_content(blog_data['content'], pdf_post['content'], blog_data['title'])
        
        if comparison['match']:
            print("[OK] コンテンツは一致しています")
        else:
            print("[差異あり] コンテンツに差異があります:")
            for diff in comparison['differences']:
                print(f"  - {diff}")
            
            # 詳細な比較（最初の10行）
            blog_lines = blog_data['content'].split('\n')[:10]
            pdf_lines = pdf_post['content'].split('\n')[:10]
            
            print("\n最初の10行を比較:")
            print("ブログ:")
            for j, line in enumerate(blog_lines, 1):
                print(f"  {j}: {line[:80]}")
            print("PDF:")
            for j, line in enumerate(pdf_lines, 1):
                print(f"  {j}: {line[:80]}")
        
        import time
        time.sleep(1)  # サーバーへの負荷を軽減
    
    print("\n" + "=" * 60)
    print("比較完了")
    print("=" * 60)

if __name__ == "__main__":
    main()

