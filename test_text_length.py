"""
テキストの長さを変えながら投稿テストを実行
280文字から少しずつ短くして、どこで403エラーが発生するか確認
"""
import os
import sys
from dotenv import load_dotenv
import logging
import tweepy
from config import Config

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def test_text_length(account_name: str, credentials: dict, base_text: str, url: str):
    """テキストの長さを変えながら投稿テスト"""
    logger.info(f"\n{'='*60}")
    logger.info(f"{account_name} アカウントのテキスト長テスト")
    logger.info(f"{'='*60}\n")
    
    # クライアントを作成
    client = tweepy.Client(
        consumer_key=credentials.get('api_key'),
        consumer_secret=credentials.get('api_secret'),
        access_token=credentials.get('access_token'),
        access_token_secret=credentials.get('access_token_secret'),
        wait_on_rate_limit=True
    )
    
    # テストする長さのリスト（50文字から段階的に長く）
    # 診断スクリプトで成功した短いテキストから始めて、段階的に長くする
    # レート制限を考慮して、重要なポイントのみをテスト
    test_lengths = [50, 100, 150, 200, 230, 250, 270, 280]
    
    logger.info(f"ベーステキストの長さ: {len(base_text)} 文字")
    logger.info(f"URLの長さ: {len(url)} 文字（実際は23文字としてカウント）")
    logger.info(f"\nテストする長さ: {test_lengths}\n")
    
    results = []
    
    for target_length in test_lengths:
        # URLを含めた合計がtarget_lengthになるように調整
        # URLは23文字 + 改行1文字 = 24文字（Twitter APIが自動的に短縮）
        available_text_length = target_length - 24
        
        if available_text_length < 0:
            logger.warning(f"  長さ {target_length}: スキップ（URL分を引くと負の値）")
            continue
        
        # テキストを切り詰める
        if len(base_text) > available_text_length:
            test_text = base_text[:available_text_length - 3] + "..."
        else:
            test_text = base_text
        
        # 実際の投稿形式（テキスト + 改行 + URL）
        # 注意: Twitter APIはURLを自動的に短縮するため、実際のURLの長さではなく23文字としてカウント
        actual_tweet = f"{test_text}\n{url}"
        # 実際の文字数（URLは実際の長さ）
        actual_length = len(actual_tweet)
        # Twitter APIがカウントする文字数（URLは23文字）
        twitter_counted_length = len(test_text) + 1 + 23
        
        print(f"  長さ {target_length}: テキスト={len(test_text)}文字, Twitterカウント={twitter_counted_length}文字, 実際={actual_length}文字 → ", end='')
        
        try:
            response = client.create_tweet(text=actual_tweet)
            if response and response.data:
                tweet_id = response.data.get('id')
                print(f"✓ 成功 (ID: {tweet_id})")
                results.append({
                    'length': target_length,
                    'text_length': len(test_text),
                    'twitter_counted_length': twitter_counted_length,
                    'actual_length': actual_length,
                    'success': True,
                    'tweet_id': tweet_id
                })
                logger.warning(f"    削除してください: https://twitter.com/i/web/status/{tweet_id}")
            else:
                logger.error("✗ 失敗: レスポンスが不正")
                results.append({
                    'length': target_length,
                    'text_length': len(test_text),
                    'twitter_counted_length': twitter_counted_length,
                    'actual_length': actual_length,
                    'success': False,
                    'error': 'レスポンスが不正'
                })
        except tweepy.Forbidden as e:
            logger.error(f"✗ 403 Forbidden")
            results.append({
                'length': target_length,
                'text_length': len(test_text),
                'twitter_counted_length': twitter_counted_length,
                'actual_length': actual_length,
                'success': False,
                'error': '403 Forbidden'
            })
            # 403エラーが出ても続行（すべての長さをテスト）
        except tweepy.TooManyRequests as e:
            logger.warning(f"⚠ レート制限: しばらく待ってから再試行してください")
            results.append({
                'length': target_length,
                'text_length': len(test_text),
                'twitter_counted_length': twitter_counted_length,
                'actual_length': actual_length,
                'success': False,
                'error': 'レート制限'
            })
            break
        except Exception as e:
            logger.error(f"✗ エラー: {type(e).__name__}: {e}")
            results.append({
                'length': target_length,
                'text_length': len(test_text),
                'twitter_counted_length': twitter_counted_length,
                'actual_length': actual_length,
                'success': False,
                'error': str(e)
            })
    
    # 結果サマリー
    logger.info(f"\n{'='*60}")
    logger.info("結果サマリー")
    logger.info(f"{'='*60}")
    success_count = sum(1 for r in results if r.get('success'))
    logger.info(f"成功: {success_count}/{len(results)} 件\n")
    
    for r in results:
        status = "✓" if r.get('success') else "✗"
        error = f" ({r.get('error')})" if not r.get('success') else ""
        logger.info(f"{status} 長さ {r['length']}: テキスト={r['text_length']}文字, Twitterカウント={r.get('twitter_counted_length', r['actual_length'])}文字, 実際={r['actual_length']}文字{error}")
        if r.get('tweet_id'):
            logger.warning(f"  削除: https://twitter.com/i/web/status/{r['tweet_id']}")
    
    return results


def main():
    """メイン関数"""
    logger.info("="*60)
    logger.info("テキストの長さを変えながら投稿テスト")
    logger.info("="*60)
    
    # テスト用のベーステキスト（実際のブログ投稿形式を想定）
    base_text_365bot = "Day289（神の使者:P.401、ACIM:T-26.V.13-14:01） 例えば、「コース」にはすべてが分離の象徴に過ぎないと言っているようだが、実際にはすべてが分離の象徴に過ぎないように、その中には時間が含まれていると思う。また、それぞれの問題の人がそれぞれが問題を解決する方法で解決できないとして、あるいはすべてが分離の象徴に過ぎないように発生しているように見えるのか？For example, it seems the Course is saying that everything is just a symbol of separati"
    url_365bot = "http://notesofacim.blog.fc2.com/blog-entry-350.html"
    
    base_text_pursahs = "語録５１ | パーサによるトマスの福音書 語録５１弟子たちが言った。「死者に安らぎが起こり、新しい世界が来るのはいつでしょうか？」彼は彼らに言った。「あなたがたが探しているものはすでに来ているが、あなたがたはそれを知らない」The disciples said to him, \"When will the rest for the dead take place, and when will the new world come?\" He said to them,"
    url_pursahs = "https://ameblo.jp/pursahs-gospel/entry-11575417569.html"
    
    # 365botGary
    logger.info("\n[365botGary]")
    credentials_365bot = Config.get_twitter_credentials_365bot()
    results_365bot = test_text_length("365botGary", credentials_365bot, base_text_365bot, url_365bot)
    
    # pursahsgospel
    logger.info("\n[pursahsgospel]")
    credentials_pursahs = Config.get_twitter_credentials_pursahs()
    results_pursahs = test_text_length("pursahsgospel", credentials_pursahs, base_text_pursahs, url_pursahs)
    
    # 最終結果
    logger.info(f"\n{'='*60}")
    logger.info("最終結果")
    logger.info(f"{'='*60}")
    logger.info(f"365botGary: 成功 {sum(1 for r in results_365bot if r.get('success'))}/{len(results_365bot)} 件")
    logger.info(f"pursahsgospel: 成功 {sum(1 for r in results_pursahs if r.get('success'))}/{len(results_pursahs)} 件")


if __name__ == "__main__":
    main()

