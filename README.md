# ひとりめマーケ LP

BtoBマーケティング支援・代行「ひとりめマーケ」のサイト。GitHub Pages でリポジトリ直下をそのまま公開する。

- ページ：`index.html`（LP）、`profile.html`、`contact.html`（無料相談）、`download.html`（資料請求）、`privacy.html`
- 生成：`_build/` の Python で HTML を書き出す。`python3 _build/build.py` → `python3 _build/validate.py`
- フォーム：`js/forms.js` の先頭に HubSpot のポータルIDとフォームIDを入れると送信される（空の間は送信しない）
