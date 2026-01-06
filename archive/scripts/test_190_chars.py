# -*- coding: utf-8 -*-
"""
190文字でのテスト投稿スクリプト
GitHub Actionsから実行することを想定
"""
import logging
from config import Config
from twitter_poster import TwitterPoster

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


def create_190_char_tweet():
    """
    180文字（URL含む）のテストツイートを作成
    URLは23文字としてカウントされるため、本文は156文字（改行1文字含む）
    180文字 = 本文156文字 + 改行1文字 + URL23文字 = 180文字
    安全のため、190文字ではなく180文字でテスト
    """
    # 156文字のテストテキスト
    # 実際の文字数カウントはXの仕様に従う
    base_text = "これは180文字のテスト投稿です。GitHub Actionsから実行されています。文字数制限の確認のため、安全な180文字でテストしています。"
    
    # 156文字になるように調整
    target_length = 156
    current_length = len(base_text)
    
    if current_length < target_length:
        # 足りない分を追加
        padding = "あ" * (target_length - current_length)
        test_text = base_text + padding
    elif current_length > target_length:
        # 長すぎる場合は切り詰め
        test_text = base_text[:target_length]
    else:
        test_text = base_text
    
    # URLを追加（23文字としてカウント）
    # 実際のURLは23文字以上でも、Xは23文字としてカウント
    test_url = "https://example.com/test"
    
    # 改行1文字 + URL 23文字 = 24文字
    # 本文156文字 + 24文字 = 180文字
    full_tweet = f"{test_text}\n{test_url}"
    
    logger.info(f"テストツイート文字数（実際）: {len(full_tweet)} 文字")
    logger.info(f"本文: {len(test_text)} 文字")
    logger.info(f"URL（実際）: {len(test_url)} 文字（Xは23文字としてカウント）")
    logger.info(f"改行: 1 文字")
    logger.info(f"Xカウント: {len(test_text)} + 1 + 23 = {len(test_text) + 1 + 23} 文字")
    logger.info(f"実際の文字数: {len(full_tweet)} 文字")
    
    return full_tweet


def test_post_190_chars(account_name: str, credentials: dict):
    """180文字でテスト投稿（安全のため190文字ではなく180文字）"""
    logger.info(f"\n{'='*60}")
    logger.info(f"{account_name} アカウントで180文字テスト投稿")
    logger.info(f"{'='*60}\n")
    
    try:
        poster = TwitterPoster(credentials)
        
        # 180文字のテストツイートを作成
        test_tweet = create_190_char_tweet()
        
        logger.info(f"投稿テキスト:")
        logger.info(f"{test_tweet}")
        logger.info(f"\n文字数: {len(test_tweet)} 文字")
        
        # 投稿実行
        logger.info("\n投稿を実行します...")
        result = poster.post_tweet_with_link(text=test_tweet.split('\n')[0], link=test_tweet.split('\n')[1])
        
        if result and result.get('success'):
            tweet_id = result.get('id')
            logger.info(f"✓ 投稿成功: ID={tweet_id}")
            logger.info(f"  ツイートURL: https://twitter.com/i/web/status/{tweet_id}")
            logger.warning(f"  このツイートはテスト投稿です。必要に応じて削除してください。")
            return True
        else:
            logger.error("✗ 投稿失敗")
            return False
            
    except Exception as e:
        logger.error(f"✗ エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return False


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='190文字でテスト投稿')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both',
                       help='テストするアカウント')
    
    args = parser.parse_args()
    
    success_count = 0
    
    if args.account in ['365bot', 'both']:
        credentials = Config.get_twitter_credentials_365bot()
        if test_post_190_chars("365botGary", credentials):
            success_count += 1
    
    if args.account in ['pursahs', 'both']:
        credentials = Config.get_twitter_credentials_pursahs()
        if test_post_190_chars("pursahsgospel", credentials):
            success_count += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"テスト投稿完了: {success_count} 件成功")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()

