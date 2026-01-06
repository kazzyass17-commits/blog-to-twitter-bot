"""
pursahsgospel用の認証情報が正しいアカウントに接続できるか確認
"""
import tweepy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# pursahsgospel用の認証情報
API_KEY = "5Wlnhj5HUbCoH0QY6yXNZ2x4r"
API_SECRET = "oSD2Xp7kc6Oxf7O0n7nW4R8CMDTOZboYYY7XaMEJ6AD2XLeapH"
ACCESS_TOKEN = "2416625168-I1UdgjKXXunJQZhg38hwZqEYygzyjWo0ulWc3iD"
ACCESS_TOKEN_SECRET = "ZLJajygqRbZcUL5juPU3VSOxenwnhFyvg2RfBpdb9YbMI"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAP6u6gEAAAAAYj%2BasP05r85Q8tOuIOidqs%2FYQAM%3DAdI160P6XPfjytgmVgENMZBVaCh7RcT2N29DmBXGeC4xb87qmE"

def check_pursahs_account():
    """pursahsgospelアカウントに接続できるか確認"""
    logger.info("=" * 60)
    logger.info("pursahsgospel用認証情報の確認")
    logger.info("=" * 60)
    
    try:
        # Tweepyクライアントを作成
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        # アカウント情報を取得
        logger.info("\nアカウント情報を取得中...")
        me = client.get_me(user_fields=['username', 'name', 'id'])
        
        if me and me.data:
            username = me.data.username
            name = me.data.name
            user_id = me.data.id
            
            logger.info("✓ 接続成功！")
            logger.info(f"  ユーザー名（ハンドル）: @{username}")
            logger.info(f"  表示名: {name}")
            logger.info(f"  ユーザーID: {user_id}")
            logger.info(f"  Twitter URL: https://twitter.com/{username}")
            logger.info(f"  X URL: https://x.com/{username}")
            
            logger.info("\n" + "=" * 60)
            logger.info("確認結果")
            logger.info("=" * 60)
            
            username_lower = username.lower()
            if 'pursahs' in username_lower or 'pursah' in username_lower:
                logger.info("✓ この認証情報は pursahsgospel アカウント用です")
                logger.info("\nGitHub Secretsに設定する名前:")
                logger.info("  - TWITTER_PURSAHS_API_KEY")
                logger.info("  - TWITTER_PURSAHS_API_SECRET")
                logger.info("  - TWITTER_PURSAHS_ACCESS_TOKEN")
                logger.info("  - TWITTER_PURSAHS_ACCESS_TOKEN_SECRET")
                logger.info("  - TWITTER_BEARER_TOKEN (共通で使用可能)")
            else:
                logger.warning(f"⚠️ アカウント名が期待と異なります: @{username}")
                logger.info("  ただし、この認証情報を使用できます")
            
            return username
        else:
            logger.error("✗ アカウント情報の取得に失敗しました")
            return None
            
    except tweepy.Unauthorized:
        logger.error("✗ 認証エラー: API認証情報が無効です")
        return None
    except Exception as e:
        logger.error(f"✗ エラー: {e}")
        return None


if __name__ == "__main__":
    check_pursahs_account()




