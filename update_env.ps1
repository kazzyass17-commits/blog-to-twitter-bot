# .envファイルを更新するスクリプト
# 365botGaryとpursahsgospelの認証情報を設定

$envContent = @"
# X (Twitter) API認証情報
# Twitter Developer Portal (https://developer.twitter.com/) で取得

# 365botGary アカウント用の認証情報
TWITTER_365BOT_API_KEY=lcm2kwFqZ66bjpHGEbdtrYrkZ
TWITTER_365BOT_API_SECRET=fYoQNSWgrrRP69tYr1gy9JtqS40Ukgw8MGeFpIkUwKLrKwX0hZ
TWITTER_365BOT_ACCESS_TOKEN=2420551951-CfPGziiIrG4XS6KlnduemgKkldS0QJXthQ39Eff
TWITTER_365BOT_ACCESS_TOKEN_SECRET=gArEjOxTjLffrExFbmdOSfINxVwVz7nbKW1tfvfWgDHxC

# pursahsgospel アカウント用の認証情報
TWITTER_PURSAHS_API_KEY=PCotoQSfRLlBPoWgcBA7455y1
TWITTER_PURSAHS_API_SECRET=5H4mO4WXSAyadI7yQqlXrOR9DgCm1UOEpZqfPGWlzZTEgCG6Iv
TWITTER_PURSAHS_ACCESS_TOKEN=2416625168-oaHuPjoGK4PrXE7sOFZOQ0PQEzSHSUkuHfERO3G
TWITTER_PURSAHS_ACCESS_TOKEN_SECRET=nWKeaynrv3ZZWzELUNz8P3CQ1kr7hXIqpSpbGY1r3bEm3

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

Write-Host ".env file updated."
Write-Host ""
Write-Host "Credentials configured:"
Write-Host "  365botGary: API Key, API Secret, Access Token, Access Token Secret"
Write-Host "  pursahsgospel: API Key, API Secret, Access Token, Access Token Secret"
Write-Host ""

