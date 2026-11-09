# ひとりめマーケ LP

BtoBマーケティング支援・代行「ひとりめマーケ」のサイト。GitHub Pages でリポジトリ直下をそのまま公開する。

- ページ：`index.html`（LP。担当者の経歴もここ）、`contact.html`（無料相談）、`download.html`（資料請求）、`privacy.html`
- 生成：`_build/` の Python で HTML を書き出す。`python3 _build/build.py` → `python3 _build/validate.py`
- フォームと日程調整：Google Apps Script（`gas/Code.gs`）で受け取り、スプレッドシートへの記録・通知・自動返信・前日のリマインドを行う。`_build/forms.js` の先頭に受け取り口と予約ページの URL を入れると動く（空の間は送信しない）。手順は [docs/google-setup.md](docs/google-setup.md)
- 代表の写真：`_build/img/`（書き出し先は `img/`）
- 確認：`python3 -m http.server 8780` をリポジトリ直下で起動し、`node _build/qa/form.mjs` などを実行
