"""
本番形式のテスト投稿スクリプト
実際のブログ投稿形式（タイトル、コンテンツ、URL）でテスト投稿を実行
"""
import os
import sys
from dotenv import load_dotenv
import logging
from config import Config
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
import tweepy

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def test_production_post(blog_url: str, twitter_handle: str, account_name: str):
    """本番形式のテスト投稿を実行"""
    logger.info(f"\n{'='*60}")
    logger.info(f"{account_name} アカウントの本番形式テスト投稿")
    logger.info(f"{'='*60}\n")
    
    try:
        # 認証情報を取得
        if account_name == "365botGary":
            credentials = Config.get_twitter_credentials_365bot()
        else:
            credentials = Config.get_twitter_credentials_pursahs()
        
        if not credentials.get('api_key') or not credentials.get('access_token'):
            logger.error("認証情報が設定されていません")
            return False
        
        # データベースからランダムに投稿を取得
        db = PostDatabase()
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning("未投稿の投稿がありません。")
            return False
        
        page_url = post_data.get('link', '')
        if not page_url:
            logger.warning("URLが取得できませんでした")
            return False
        
        logger.info(f"選択された投稿: {post_data.get('title', '')}")
        logger.info(f"URL: {page_url}")
        
        # ページからコンテンツを取得
        logger.info("ページからコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            page_content = {
                'title': post_data.get('title', ''),
                'content': '',
                'link': page_url,
                'published_date': '',
                'author': '',
            }
        
        logger.info(f"取得した投稿: {page_content.get('title', 'タイトルなし')}")
        
        # Twitter投稿テキストをフォーマット
        poster = TwitterPoster(credentials)
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', page_url)
        )
        
        logger.info(f"\n投稿予定のツイートテキスト:")
        logger.info(f"  {tweet_text}")
        logger.info(f"  文字数: {len(tweet_text)} 文字")
        logger.info(f"\n実際の投稿形式（改行とURLを含む）:")
        actual_tweet = f"{tweet_text}\n{page_content.get('link', page_url)}"
        logger.info(f"  {actual_tweet}")
        logger.info(f"  文字数: {len(tweet_text)} 文字 + 改行(1) + URL(23) = {len(tweet_text) + 24} 文字（合計280文字以内）")
        
        # 実際に投稿（診断スクリプトと同じ方法で直接create_tweetを使用）
        logger.info("\n実際にTwitterに投稿します...")
        
        # クライアントを直接作成（診断スクリプトと同じ方法）
        # bearer_tokenは使用しない（診断スクリプトと同じ）
        client = tweepy.Client(
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=True
        )
        
        # 実際の投稿形式（テキスト + 改行 + URL）
        actual_tweet_text = f"{tweet_text}\n{page_content.get('link', page_url)}"
        
        try:
            response = client.create_tweet(text=actual_tweet_text)
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"\n✓ 投稿成功!")
                logger.info(f"  ツイートID: {tweet_id}")
                logger.info(f"  ツイートURL: https://twitter.com/i/web/status/{tweet_id}")
                logger.warning(f"\n⚠ このツイートはテスト投稿です。確認後、削除してください。")
                return True
            else:
                logger.error("投稿失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"403 Forbidden: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            return False
        except Exception as e:
            logger.error(f"投稿エラー: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        return False


def main():
    """メイン関数"""
    logger.info("="*60)
    logger.info("本番形式のテスト投稿を実行します")
    logger.info("="*60)
    
    results = []
    
    # 365botGary
    logger.info("\n[365botGary]")
    result_365bot = test_production_post(
        Config.BLOG_365BOT_URL,
        Config.TWITTER_365BOT_HANDLE,
        "365botGary"
    )
    results.append(("365botGary", result_365bot))
    
    # pursahsgospel
    logger.info("\n[pursahsgospel]")
    result_pursahs = test_production_post(
        Config.BLOG_PURSAHS_URL,
        Config.TWITTER_PURSAHS_HANDLE,
        "pursahsgospel"
    )
    results.append(("pursahsgospel", result_pursahs))
    
    # 結果サマリー
    logger.info("\n" + "="*60)
    logger.info("テスト投稿結果サマリー")
    logger.info("="*60)
    for account_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        logger.info(f"{account_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    logger.info(f"\n成功: {success_count}/{len(results)} 件")
    
    if success_count > 0:
        logger.warning("\n⚠ テスト投稿が完了しました。X (Twitter)で投稿内容を確認し、問題がなければ削除してください。")


if __name__ == "__main__":
    main()

