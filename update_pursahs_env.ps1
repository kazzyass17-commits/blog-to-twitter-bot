# pursahsgospel用の認証情報を.envファイルに更新するスクリプト
# 注意: 既存の.envファイルがある場合、手動で更新してください

$envContent = @"
# X (Twitter) API認証情報
# Twitter Developer Portal (https://developer.twitter.com/) で取得

# 365botGary アカウント用の認証情報
TWITTER_365BOT_API_KEY=lcm2kwFqZ66bjpHGEbdtrYrkZ
TWITTER_365BOT_API_SECRET=fYoQNSWgrrRP69tYr1gy9JtqS40Ukgw8MGeFpIkUwKLrKwX0hZ
TWITTER_365BOT_ACCESS_TOKEN=2420551951-CfPGziiIrG4XS6KlnduemgKkldS0QJXthQ39Eff
TWITTER_365BOT_ACCESS_TOKEN_SECRET=gArEjOxTjLffrExFbmdOSfINxVwVz7nbKW1tfvfWgDHxC
TWITTER_365BOT_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAJGu6gEAAAAAKipWzEG60uYmmv8Qoe0n07Q9BSM%3DL91SZLeHUaDlrc8vplQdX14etmxAkIx3T8XihNSdG3hkaTjoWI

# pursahsgospel アカウント用の認証情報
TWITTER_PURSAHS_API_KEY=PCotoQSfRLlBPoWgcBA7455y1
TWITTER_PURSAHS_API_SECRET=5H4mO4WXSAyadI7yQqlXrOR9DgCm1UOEpZqfPGWlzZTEgCG6Iv
TWITTER_PURSAHS_ACCESS_TOKEN=2416625168-HjSU1zutJdPiIkViltErroLVz81VusJBnGlP9BX
TWITTER_PURSAHS_ACCESS_TOKEN_SECRET=DyVPAj1Lj7Ebvi6kR2y1xqi1ES49B3XdzuOxLfDkNil7M
TWITTER_PURSAHS_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAP6u6gEAAAAANFP7mlTxPI1BeRpCpaJDtja2HB0%3DV443mkbthkCI5NC5ubm0l0AZYHL0YAIC9hJBDC5qoT9Q1pHHYL

# ブログURL設定
BLOG_365BOT_URL=http://notesofacim.blog.fc2.com/
TWITTER_365BOT_HANDLE=365botGary

BLOG_PURSAHS_URL=https://www.ameba.jp/profile/general/pursahs-gospel/
TWITTER_PURSAHS_HANDLE=pursahsgospel

# 投稿設定
POST_INTERVAL_HOURS=24
MAX_POST_LENGTH=280
"@

# .envファイルに書き込み
$envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline

Write-Host ".envファイルを更新しました。"
Write-Host "接続テストを実行します..."

