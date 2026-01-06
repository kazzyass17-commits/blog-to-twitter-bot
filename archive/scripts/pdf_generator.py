"""
PDF生成モジュール（NotebookLM用）
"""
import os
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDFを生成するクラス"""
    
    def __init__(self, output_dir: str = "pdfs"):
        """
        Args:
            output_dir: PDF出力ディレクトリ
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 日本語フォントの設定（Windowsの場合）
        try:
            # Windows標準の日本語フォントを試行
            font_paths = [
                "C:/Windows/Fonts/msgothic.ttc",  # MS ゴシック
                "C:/Windows/Fonts/msmincho.ttc",  # MS 明朝
                "C:/Windows/Fonts/meiryo.ttc",    # メイリオ
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                        self.japanese_font = 'JapaneseFont'
                        logger.info(f"日本語フォントを登録しました: {font_path}")
                        break
                    except:
                        continue
            else:
                # フォントが見つからない場合はデフォルトフォントを使用
                self.japanese_font = 'Helvetica'
                logger.warning("日本語フォントが見つかりません。デフォルトフォントを使用します。")
        except Exception as e:
            logger.warning(f"フォント設定エラー: {e}")
            self.japanese_font = 'Helvetica'
    
    def generate_pdf(self, post_data: Dict[str, str], filename: Optional[str] = None) -> Optional[str]:
        """
        ブログ投稿からPDFを生成
        
        Args:
            post_data: ブログ投稿データ（title, content, link, published_dateなど）
            filename: 出力ファイル名（省略時は自動生成）
        
        Returns:
            生成されたPDFファイルのパス、またはNone（エラー時）
        """
        try:
            if not filename:
                # ファイル名を自動生成
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c for c in post_data.get('title', 'post')[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')
                filename = f"{safe_title}_{timestamp}.pdf"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # PDFドキュメントを作成
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # スタイルを設定
            styles = getSampleStyleSheet()
            
            # 日本語用スタイル
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.japanese_font,
                fontSize=18,
                textColor='#000000',
                spaceAfter=12,
                alignment=TA_CENTER
            )
            
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['BodyText'],
                fontName=self.japanese_font,
                fontSize=12,
                textColor='#000000',
                spaceAfter=6,
                alignment=TA_LEFT,
                leading=18
            )
            
            link_style = ParagraphStyle(
                'CustomLink',
                parent=styles['BodyText'],
                fontName=self.japanese_font,
                fontSize=10,
                textColor='#0066CC',
                spaceAfter=12,
                alignment=TA_LEFT
            )
            
            # コンテンツを構築
            story = []
            
            # タイトル
            title = post_data.get('title', 'タイトルなし')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12*mm))
            
            # 公開日
            if post_data.get('published_date'):
                date_text = f"公開日: {post_data['published_date']}"
                story.append(Paragraph(date_text, content_style))
                story.append(Spacer(1, 6*mm))
            
            # リンク
            if post_data.get('link'):
                link_text = f"URL: {post_data['link']}"
                story.append(Paragraph(link_text, link_style))
                story.append(Spacer(1, 6*mm))
            
            # コンテンツ
            content = post_data.get('content', '')
            if content:
                # 長いコンテンツを段落に分割
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # HTMLタグをエスケープ
                        para_escaped = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(para_escaped, content_style))
                        story.append(Spacer(1, 6*mm))
            else:
                story.append(Paragraph("コンテンツがありません。", content_style))
            
            # PDFを生成
            doc.build(story)
            
            logger.info(f"PDFを生成しました: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"PDF生成エラー: {e}")
            return None
    
    def generate_multiple_pdfs(self, posts_data: list[Dict[str, str]], prefix: str = "posts") -> list[str]:
        """
        複数のブログ投稿からPDFを生成
        
        Args:
            posts_data: ブログ投稿データのリスト
            prefix: ファイル名のプレフィックス
        
        Returns:
            生成されたPDFファイルのパスのリスト
        """
        generated_files = []
        
        for i, post_data in enumerate(posts_data, 1):
            filename = f"{prefix}_{i:03d}.pdf"
            filepath = self.generate_pdf(post_data, filename)
            if filepath:
                generated_files.append(filepath)
        
        return generated_files


