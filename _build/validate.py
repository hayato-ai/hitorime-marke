"""v14 の静的チェック（brief_v14.md の期待値に更新。FV の写真→フォームのカード、フォームは js/forms.js、先着3社、スポットプラン、強み）。以下は v13 の説明：
v13 の静的チェック（標準ライブラリのみ）。brief_v13.md（本人のフィードバック）を最優先に、v12 以前の確認のうち今も有効なものを含む。
- タグの開閉・入れ子、重複 id、aria-labelledby の参照先
- 内部リンクとアンカー（#id）の存在
- 全ページでヘッダー／下部バーに2つのCTAがあること
- 【要記入：…】の数（v2との比較）
- 禁止表現
"""
import os
import re
import sys
from html.parser import HTMLParser

from common import OUT
SP = OUT
V3 = OUT
V2 = SP + "site_v13/"   # 比較元（1つ前の版。件数の参考のみ）
PAGES = ["index.html", "contact.html", "download.html", "privacy.html"]

VOID = {"meta", "link", "br", "img", "hr", "input", "source", "wbr", "col"}
# svg 内の自己完結要素（<line/> など）は startendtag で届くので問題ない


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = []
        self.hrefs = []
        self.labelledby = []
        self.text = []
        self.in_script = False
        self.in_comment_todo = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if "aria-labelledby" in a:
            self.labelledby.append(a["aria-labelledby"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"余分な閉じタグ </{tag}> {self.getpos()}")
            return
        top, pos = self.stack[-1]
        if top == tag:
            self.stack.pop()
        else:
            # 入れ子のずれ：どこかで閉じ忘れ
            names = [t for t, _ in self.stack]
            if tag in names:
                while self.stack and self.stack[-1][0] != tag:
                    t, p = self.stack.pop()
                    self.errors.append(f"閉じ忘れ <{t}> (開始 {p}) が </{tag}> {self.getpos()} より先に閉じられていない")
                if self.stack:
                    self.stack.pop()
            else:
                self.errors.append(f"対応する開始タグのない </{tag}> {self.getpos()}")

    def handle_data(self, data):
        self.text.append(data)


def parse(path):
    c = Checker()
    src = open(path, encoding="utf-8").read()
    c.feed(src)
    c.close()
    for t, p in c.stack:
        c.errors.append(f"閉じられていない <{t}> (開始 {p})")
    return c, src


ok = True
info = {}
for page in PAGES:
    path = V3 + page
    if not os.path.exists(path):
        print(f"[NG] {page} が存在しない")
        ok = False
        continue
    c, src = parse(path)
    info[page] = (c, src)

    errs = list(c.errors)
    # 重複 id
    seen = set()
    for i in c.ids:
        if i in seen:
            errs.append(f"重複 id: {i}")
        seen.add(i)
    # aria-labelledby の参照先
    for ref in c.labelledby:
        for r in ref.split():
            if r not in seen:
                errs.append(f"aria-labelledby の参照先がない: {r}")
    # 必須の構造
    for needle, label in [
        ('<html lang="ja">', "lang=ja"),
        ("<title>", "title"),
        ('name="description"', "meta description"),
        ('property="og:title"', "OGP"),
        ('href="css/style.css?v=', "css 参照"),
        ('src="js/main.js?v=', "js 参照"),
        ('class="header-cta"', "ヘッダーのCTA"),
        ('class="cta-bar"', "下部バー"),
    ]:
        if needle not in src:
            errs.append(f"{label} がない")
    # 2つのCTA（ヘッダー）と（下部バー）
    hdr = re.search(r'<div class="header-cta">(.*?)</div>', src, re.S)
    bar = re.search(r'<div class="cta-bar".*?>(.*?)</div>', src, re.S)
    for name, m in [("ヘッダー", hdr), ("下部バー", bar)]:
        exp_labels = ["無料相談", "資料請求"] if name == "ヘッダー" else ["無料相談（60分）", "資料請求"]
        if not m:
            errs.append(f"{name}のCTAが見つからない")
            continue
        h = re.findall(r'href="([^"]+)"', m.group(1))
        if h != ["contact.html", "download.html"]:
            errs.append(f"{name}のCTAのリンクが想定と違う: {h}")
        labels = re.findall(r"<span>([^<]+)</span>", m.group(1))
        if labels != exp_labels:
            errs.append(f"{name}のCTAの文言が想定と違う: {labels}")
    # 外部リソース：Google Fonts と images.unsplash.com（v10）以外を使っていない（src／href／srcset すべて）
    ext = re.findall(r'(?:src|href)="(https?://[^"]+)"', src)
    for ss in re.findall(r'srcset="([^"]+)"', src):
        ext += [x.strip().split(" ")[0] for x in ss.split(",")]
    for u in ext:
        if not (u.startswith("https://fonts.googleapis.com") or u.startswith("https://fonts.gstatic.com") or u.startswith("https://images.unsplash.com") or u.startswith("img/profile") or (page == "privacy.html" and u.startswith("https://www.ppc.go.jp/"))):
            errs.append(f"許可していない外部URL: {u}")
    for u in re.findall(r'<link rel="preconnect" href="([^"]+)"', src):
        if u not in ("https://fonts.googleapis.com", "https://fonts.gstatic.com", "https://images.unsplash.com"):
            errs.append(f"許可していない preconnect: {u}")
    # <img> は index の Unsplash 写真3枚だけ（それ以外のページには画像を置かない）
    n_img = len(re.findall(r"<img\b", src))
    if page == "index.html":
        if n_img != 3:
            errs.append(f"index の <img> が {n_img} 枚（Unsplash の2枚＋代表の写真の3枚のはず）")
    elif page == "profile.html":
        if n_img != 1:
            errs.append(f"profile の <img> が {n_img} 枚（代表の写真の1枚のはず）")
    elif n_img:
        errs.append(f"<img> を使っている（{n_img}）")

    status = "OK" if not errs else "NG"
    print(f"[{status}] {page}: ids={len(seen)} links={len(c.hrefs)}")
    for e in errs:
        ok = False
        print("    -", e)

# 内部リンクとアンカー
print("\n--- 内部リンク ---")
link_errs = 0
for page, (c, src) in info.items():
    for h in c.hrefs:
        if re.match(r"^(https?:|mailto:|tel:)", h):
            continue
        h = re.sub(r"\?[^#]*", "", h)   # contact.html?plan=1 → contact.html
        if h.startswith("#"):
            target_file, frag = page, h[1:]
        elif h == "./" or h.startswith("./#"):
            target_file, frag = "index.html", (h[3:] or None)
        else:
            if "#" in h:
                target_file, frag = h.split("#", 1)
            else:
                target_file, frag = h, None
        if not os.path.exists(V3 + target_file):
            print(f"[NG] {page}: {h} → ファイルがない")
            link_errs += 1
            continue
        if frag:
            tc = info.get(target_file)
            if tc is None:
                tc = parse(V3 + target_file)
            if frag not in tc[0].ids:
                print(f"[NG] {page}: {h} → #{frag} がない")
                link_errs += 1
if link_errs == 0:
    print("全ての内部リンクとアンカーが存在する")
else:
    ok = False

# 【要記入】の数
print("\n--- 【要記入：…】 ---")
ph_re = re.compile(r"【要記入：[^】]*】")
tot2 = tot3 = 0
for page in PAGES:
    s3 = open(V3 + page, encoding="utf-8").read()
    n3 = len(ph_re.findall(s3))
    if os.path.exists(V2 + page):
        s2 = open(V2 + page, encoding="utf-8").read()
        n2 = len(ph_re.findall(s2))
        kinds2 = sorted(set(ph_re.findall(s2)))
        kinds3 = sorted(set(ph_re.findall(s3)))
        tot2 += n2
        flag = "OK" if n3 >= n2 else "減少（v10 で確定した事実を反映）"
        print(f"{page}: v2={n2} → v3={n3} [{flag}]  新種類: {sorted(set(kinds3) - set(kinds2))}  消えた種類: {sorted(set(kinds2) - set(kinds3))}")
    else:
        print(f"{page}: (新規) v3={n3}  種類: {sorted(set(ph_re.findall(s3)))}")
    tot3 += n3
print(f"合計: v2(既存ページ)={tot2} → v3(全ページ)={tot3}")

# 禁止表現（本文テキストに対して。要記入は除く）
print("\n--- 【要記入】一覧（ページ別・種類別） ---")
from collections import Counter
for page in PAGES:
    src_ = open(V3 + page, encoding="utf-8").read()
    body_ = re.sub(r"<!--.*?-->", "", src_, flags=re.S)
    body_ = re.sub(r"<title>.*?</title>", "", body_, flags=re.S)
    cnt = Counter(ph_re.findall(body_))
    print(page, dict(cnt))

# v14：残す【要記入】は、読み仮名、メールアドレス、プライバシーポリシーの制定日（と代表の写真）だけ。GoogleフォームのURLは全ページから削除。HubSpot の設定は【要記入】ではなく forms.js の空の設定値。以下は v13 の説明：社名の【要記入】は全ページから無くす。代表の写真はプレースホルダーのまま（【要記入】の文字は無い）
ALLOWED_TODO = {
    "index.html": set(),
    "contact.html": set(),
    "download.html": set(),
    "privacy.html": set(),
}
print("\n--- v13：残す【要記入】の確認 ---")
for page in PAGES:
    src_ = open(V3 + page, encoding="utf-8").read()
    kinds = set(re.findall(r"【要記入：([^】]*)】", src_))
    extra = kinds - ALLOWED_TODO[page]
    if extra:
        print(f"[NG] {page}: 指示書にない【要記入】が残っている: {sorted(extra)}"); ok = False
    else:
        print(f"[OK] {page}: {sorted(kinds)}")
    # title に【要記入】がない
    if "【要記入：社名】" in src_: print(f"[NG] {page}: 社名の【要記入】が残っている"); ok = False
    t = re.search(r"<title>(.*?)</title>", src_, re.S).group(1)
    if "ひとりめマーケ" not in t or "要記入" in t: print(f"[NG] {page}: title にサービス名「ひとりめマーケ」がない: {t}"); ok = False
if re.search(r"【要記入：(金額|有無|時間|期間)】", re.sub(r"<!--.*?-->", "", open(V3 + "index.html", encoding="utf-8").read(), flags=re.S)):
    print("[NG] index に確定済みの項目の【要記入】が残っている"); ok = False

print("\n--- 旧用語（可視テキスト・title・meta） ---")
OLD = ["経路", "本線", "パイプライン", "スコアリング", "架電", "受け渡し", "導線", "手当て", "テストプラン", "選ばれる", "社長の声", "担当者は最後まで", "現状診断", "実行設計図", "御社", "営業・CS"]
for page in PAGES:
    src_ = open(V3 + page, encoding="utf-8").read()
    vis = re.sub(r"<!--.*?-->", "", src_, flags=re.S)
    vis = re.sub(r'class="[^"]*"', "", vis)
    vis = re.sub(r"<style.*?</style>|<script.*?</script>", "", vis, flags=re.S)
    for w in OLD:
        for m in re.finditer(re.escape(w), vis):
            print(f"[旧用語] {page}: {w} … {vis[max(0,m.start()-15):m.end()+15]!r}")
if 'og:image' in "".join(open(V3 + p_, encoding="utf-8").read() for p_ in PAGES):
    print("[NG] og:image が残っている"); ok = False
print("(何も出ていなければ該当なし)")

print("\n--- 禁止表現 ---")
bad = ["AI", "人工知能", "ChatGPT", "必ず", "劇的", "No.1", "ナンバーワン", "マーケター一人分", "全部任せ", "保証します", "絶対"]
for page, (c, src) in info.items():
    body = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    for w in bad:
        if w in body:
            ctx = body[max(0, body.index(w) - 20): body.index(w) + 30].replace("\n", " ")
            print(f"[要確認] {page}: 「{w}」 … {ctx}")
print("(上に何も出ていなければ該当なし)")


print("\n--- v5 指摘・v6 指示の確認 ---")
v5bad = ["service.html", "年商", "60分で確かめ", "自社に合うかどうか", "手が止まる", "商談が生まれる", "仕事で大事", "大事にしている", "受注単価", "有効商談率", "パイプライン", "比較の基準", "こんな時に", "<svg class=\"diagram", "class=\"tag\"",
         "一人目マーケター代行", "ここまでは無料です", "相談で伺うこと", "担当範囲", "初回のお客様向けプラン", "column-reverse", "aria-label=\"TOPページへ", "1,300", "相談だけで終わって", "その後の連絡の方針", "href=\"index.html", "ph__desc",
         "代表が直接対応します", "実務をまるごと", "いま一番困っていること", "続けるか見直す", "5名のチームを率い", "新規のリード数", "保証するものではありません", "事例として掲載させてください"]
for page in PAGES:
    src_ = open(V3 + page, encoding="utf-8").read()
    body_ = re.sub(r"<!--.*?-->", "", src_, flags=re.S)
    for w in v5bad:
        if w in body_:
            print(f"[NG] {page}: 「{w}」が残っている"); ok = False
    if page != "index.html":
        if 'class="breadcrumb"' not in src_: print(f"[NG] {page}: パンくずがない"); ok = False
        if "TOPページへ戻る" not in src_: print(f"[NG] {page}: 「TOPページへ戻る」がない"); ok = False
    if '<li><a href="./">TOP</a></li>' not in src_: print(f"[NG] {page}: フッターの「TOP」がない"); ok = False
    if 'class="logo" href="./"' not in src_: print(f"[NG] {page}: ロゴのリンクがない"); ok = False
    pre = "" if page == "index.html" else "./"
    for nav in [f'{pre}#service', f'{pre}#plans', f'{pre}#flow', f'{pre}#faq', f'{pre}#about', './']:
        if f'href="{nav}"' not in src_: print(f"[NG] {page}: ナビ {nav} がない"); ok = False
    # 先頭が「主、従」の順（btn-row 内）
    for row in re.findall(r'<div class="btn-row[^"]*">(.*?)</div>', src_, re.S):
        hs = re.findall(r'href="([^"]+)"', row)
        # v14：index の FV の従ボタンだけは同じページのフォーム（#hero-form）へ
        if hs not in (["contact.html", "download.html"], ["contact.html", "#hero-form"]) or (hs[1] == "#hero-form" and (page != "index.html" or 'class="hero"' not in src_)): print(f"[NG] {page}: btn-row の順が主、従でない {hs}"); ok = False
    if page == "privacy.html" and '<meta name="robots" content="noindex">' not in src_: print("[NG] privacy: noindex がない"); ok = False
    if page != "privacy.html" and 'noindex' in src_: print(f"[NG] {page}: noindex が付いている"); ok = False
    if "<script>" in src_ and "__revealTimer" not in src_: print(f"[NG] {page}: 保険タイマーがない"); ok = False
    # .mark の数（見出しの要の語句だけ）
    nm = len(re.findall(r'class="mark"', body_))
    print(f"  {page}: .mark = {nm}")
css = open(OUT + "css/style.css", encoding="utf-8").read()
if "column-reverse" in re.sub(r"/\*.*?\*/", "", css, flags=re.S): print("[NG] CSS に column-reverse が残っている"); ok = False
js = open(OUT + "js/main.js", encoding="utf-8").read()
if "__revealTimer" not in js or "clearTimeout" not in js: print("[NG] main.js がタイマーを解除していない"); ok = False

print("\n--- v9 指示の確認（fix_brief_v9.md ＋ brief_v8.md） ---")
for page in PAGES:
    src_ = open(V3 + page, encoding="utf-8").read()
    if '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' not in src_: print(f"[NG] {page}: favicon（ロゴの人の形）がない"); ok = False
    if 'class="logo__person"' not in src_ or '<span class="logo__name">ひとりめマーケ</span>' not in src_: print(f"[NG] {page}: ロゴ（案G）がない"); ok = False
UNW = lambda t: re.sub(r'<span class="nw">([^<]*)</span>', r"\1", t)   # finalize が付ける折り返し防止の span は外して照合する
RAW = {p_: open(V3 + p_, encoding="utf-8").read() for p_ in PAGES}
idx = UNW(RAW["index.html"])
idx_body = re.sub(r"<!--.*?-->", "", idx, flags=re.S)
ct = UNW(RAW["contact.html"])
ct_body = re.sub(r"<!--.*?-->", "", ct, flags=re.S)
dl = UNW(RAW["download.html"])
pv = UNW(RAW["privacy.html"])


def need(label, text, items):
    global ok
    for n in items:
        if n not in text:
            print(f"[NG] {label}: 「{n}」がない"); ok = False


def gone(label, text, items):
    global ok
    for g in items:
        if g in text:
            print(f"[NG] {label}: 削除するはずの「{g}」が残っている"); ok = False


def section(src, pattern):
    m = re.search(pattern, src, re.S)
    if not m:
        print(f"[NG] セクションが見つからない: {pattern[:50]}"); return ""
    return m.group(0)


S_HERO = section(idx_body, r'<section class="hero".*?</section>')
S_SVC = section(idx_body, r'<section class="section section--alt" id="service".*?</section>')
S_PLANS = section(idx_body, r'<section class="section" id="plans".*?</section>')
S_ABOUT = section(idx_body, r'<section class="section section--alt" id="about".*?</section>')
S_ROW = section(idx_body, r'<section class="cta-row".*?</section>')
S_FLOW = section(idx_body, r'<section class="section" id="flow".*?</section>')
S_FAQ = section(idx_body, r'<section class="section" id="faq".*?</section>')
S_CTA = section(idx_body, r'<section class="cta-band".*?</section>')
import html as _html
TXT = lambda t: re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", t))).strip()   # タグを外して空白を詰めた可視テキスト
BUBBLE_HTML = '<p class="bubble"><span>＼ 先着3社 モニター価格 月30万円 ／</span></p>'
PILLS3 = ["担当者ゼロからの立ち上げ", "止まっている施策の立て直し", "施策の実行だけのご依頼もOK"]

print("\n--- v13 指示書：index（文面はそのまま） ---")
# 共通：メタ（v11 のまま）
need("index meta", idx, [
    "<title>ひとりめマーケ｜BtoBマーケティング支援・代行｜元マーケティング責任者が戦略から実行まで</title>",
    'content="ひとりめマーケ｜BtoBマーケティング支援・代行｜元マーケティング責任者が戦略から実行まで"',
])
# 1. FV
need("FV", S_HERO, [
    '<p class="sec-label">BtoBマーケティング支援・代行</p>',
    '<h1 id="hero-title"><span class="phrase">マーケティングに</span><span class="phrase">手が回らない</span><span class="phrase">BtoB企業の、</span><span class="phrase"><span class="mark">一人目のマーケター</span>に</span><span class="phrase">なります</span></h1>', '<p class="hero__sub">元マーケティング責任者が、戦略から実行まで担当します。</p>',
    BUBBLE_HTML, "<span>まずは無料で相談する</span>", "<span>資料請求はこちら</span>",
])
if [TXT(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", re.search(r'<ul class="pills">.*?</ul>', S_HERO, re.S).group(0))] != PILLS3: print("[NG] FV のピルが指示書の3つでない"); ok = False
gone("FV", S_HERO, ["hero__monitor", "mon-tag", "hero__micro", "60分", "オンライン", "お見積りまで無料", "マーケティング経験5年以上", "社長直下で部門を一人で立ち上げ", "6名体制まで拡大", "モニター募集中", "hero__lead", "ph--hero", "<img", "Googleフォーム"])
if "【要記入" in S_HERO: print("[NG] FV に【要記入】が残っている"); ok = False
# 並び：ピル → 吹き出し → ボタン。吹き出しは主ボタンのすぐ上
pos = [S_HERO.find(x) for x in ['<ul class="pills">', 'class="bubble"', 'class="btn-row"', 'id="hero-form"']]
if pos != sorted(pos) or min(pos) < 0: print("[NG] FV の並びが「ピル → 吹き出し → ボタン → フォームのカード」でない", pos); ok = False
if "key-facts" in S_HERO or "初期費用" in S_HERO: print("[NG] FV に要点カードが残っている"); ok = False
if re.findall(r'<a class="btn[^"]*" href="([^"]+)"', re.search(r'<div class="btn-row">.*?</div>', S_HERO, re.S).group(0)) != ["contact.html", "#hero-form"]: print("[NG] FV のボタンのリンクが「contact.html／#hero-form」でない"); ok = False
# FV のフォームのカード（資料請求）
HF = section(S_HERO, r'<div class="form-card hero-form" id="hero-form".*?</form>')
need("FV のフォームのカード", HF, ['<h2 class="form-card__title" id="hero-form-title">サービス資料はこちら（無料）</h2>', 'data-form="download"', '<span>資料を受け取る</span>', '<a href="privacy.html" target="_blank" rel="noopener">プライバシーポリシー</a>に同意する', '（設定前のため送信されません）'])
for nm_, lb_, rq_ in [("company", "会社名", True), ("firstname", "お名前", True), ("email", "メールアドレス", True), ("phone", "電話番号", True)]:
    if not re.search(rf'<label for="hf-{nm_}"><span class="field__name">{lb_}</span><span class="{"req" if rq_ else "opt"}">{"必須" if rq_ else "任意"}</span></label>\s*<input id="hf-{nm_}" name="{nm_}"[^>]*?{"required" if rq_ else ""}', HF): print(f"[NG] FV のフォーム：{lb_}（{'必須' if rq_ else '任意'}）"); ok = False
if 'name="privacy" type="checkbox" required' not in HF: print("[NG] FV のフォーム：同意のチェック（必須）"); ok = False
if len(re.findall(r'<button class="btn btn--block" type="submit">', HF)) != 1: print("[NG] FV のフォームの送信ボタン"); ok = False
if not re.search(r'<p class="bubble"><span>[^<]*</span></p>\s*<div class="btn-row">\s*<a class="btn" href="contact.html">', S_HERO): print("[NG] FV：吹き出しが主ボタンのすぐ上でない"); ok = False
if S_HERO.count('class="bubble"') != 1 or S_HERO.count("モニター") != 1: print("[NG] FV のモニター表示が吹き出しの1か所だけでない", S_HERO.count("モニター")); ok = False

# 2. サービスの特長
need("特長", S_SVC, [
    '<p class="sec-label">サービスの特長</p>', 'id="service-title"', '<span class="mark">解決できる</span>', '<img ', 'class="svc-intro"',
])
if TXT(re.search(r'<h2 class="sec-title" id="service-title">(.*?)</h2>', S_SVC, re.S).group(1)) != "元事業会社のマーケティング責任者だから解決できる、4つのこと": print("[NG] 特長の見出し"); ok = False
FEAT_EXP = [
    ("ムダ打ちせず、商談につながる施策から始める", "何から手をつけるかで、成果は大きく変わります。BtoBマーケティングの責任者として、狙う顧客、KPI、予算を決めてきた経験から、貴社が最初に打つべき施策を見極め、限られた予算と時間を集中させます。"),
    ("人手が足りなくても、施策が止まらない", "戦略を描いて終わる支援ではありません。広告の運用、LPや資料の制作、展示会の集客まで、自ら手を動かしてきた私が実行まで担当します。社内の手が空くのを待たずに、すぐに動き出せます。"),
    ("任せきりにならない。社内に仕組みが残る", "マーケティング部門を1人から6名体制に育てた経験から、進め方や判断の基準を手順書にして残します。契約が終わったあとも、社内でマーケティングが回る状態をつくります。"),
    ("イベントを、商談の入り口に変える", "展示会や決裁者向けのカンファレンスを、ゼロから立ち上げてきました。誰を呼ぶかを決めて集め、当日の接点を商談にし、営業に渡すまで。場をつくるところから商談化までを、一人で担えます。"),
]
feats = [(TXT(a), TXT(b)) for a, b in re.findall(r'<li class="card feat-card">.*?<h3>(.*?)</h3>\s*<p>(.*?)</p>', S_SVC, re.S)]
if feats != FEAT_EXP: print("[NG] 特長3つの見出し・本文が指示書と違う", feats); ok = False
gone("特長", S_SVC, ["<table", "cmp", "svc-close", "sec-lead", "代表が直接", "担当者が途中で変わる", "3つの特長"])
if len(re.findall(r'class="card feat-card"', S_SVC)) != 4: print("[NG] 特長が4つでない"); ok = False
if [m for m in re.findall(r'<span class="num-xl" aria-hidden="true">(\d+)</span>', S_SVC)] != ["01", "02", "03", "04"]: print("[NG] 特長の番号が01〜04でない"); ok = False

# 3. プラン
need("プラン", S_PLANS, ['<p class="sec-label">プラン</p>', 'ご依頼に合わせた<span class="mark">3つのプラン</span>'])
if len(re.findall(r'<li class="card plan-card', S_PLANS)) != 3: print("[NG] プランのカードが3枚でない"); ok = False
PLAN_NAMES = ["ひとりめ代行プラン", "リード獲得プラン", "HubSpot導入・活用プラン"]
plan_heads = [TXT(m) for m in re.findall(r'<li class="card plan-card" id="plan-\d">.*?<h3>(.*?)</h3>', S_PLANS, re.S)]
print("プランの名前:", plan_heads)
if plan_heads != PLAN_NAMES: print("[NG] プラン名が指示書と違う"); ok = False


def card(i):
    m = re.search(rf'<li class="card plan-card" id="plan-{i}">.*?\n        </li>', S_PLANS, re.S)
    return m.group(0) if m else ""


C1, C2, C3 = card(1), card(2), card(3)
# 上から：（タグ）→ 名前 → ひとこと → こんな方におすすめ → 担当すること → 料金と期間
for i, (c_, lead, who) in enumerate([
    (C1, "戦略から実行まで、丸ごと任せたい", "マーケティングの担当者がいない企業様"),
    (C2, "リードを増やす施策を、任せたい", "リードの数を増やしたい企業様"),
    (C3, "HubSpotを、使いこなしたい", "HubSpotを導入したい、または使いこなせていない企業様"),
], 1):
    dl_ = "対応できる施策" if i == 2 else "担当すること"
    need(f"プラン{i}", c_, [f'<p class="plan-card__lead">{lead}</p>', f"<p>{who}</p>", "こんな方におすすめ", dl_, '<p class="k-label">料金</p>'])
    keys = ["<h3>", 'class="plan-card__lead"', "こんな方におすすめ", dl_, '<div class="plan-card__bottom">']
    pos = [c_.find(k) for k in keys]
    if min(pos) < 0 or pos != sorted(pos): print(f"[NG] プラン{i}：項目の順が「名前 → ひとこと → おすすめ → 担当 → 料金」でない", pos); ok = False
    if "<a " in c_ or "btn" in c_: print(f"[NG] プラン{i}：カードの中に相談ボタン（リンク）がある"); ok = False
    for old_ in ["主な成果物", "chips", "plan-card__desc", "plan-card__keep", "コース<"]:
        if old_ in c_: print(f"[NG] プラン{i}：v12 の「{old_}」が残っている"); ok = False
    dlist = re.search(r'<ul class="dot-list[^"]*">.*?</ul>', c_, re.S)
    if not dlist or len(re.findall(r"<li>", dlist.group(0))) != 4: print(f"[NG] プラン{i}：担当すること（4項目）"); ok = False
if '<span class="plan-card__tag">基本のプラン</span>' not in C1 or "plan-card__tag" in C2 or "plan-card__tag" in C3: print("[NG] 「基本のプラン」のタグは1枚目だけのはず"); ok = False
if [TXT(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'<ul class="dot-list">.*?</ul>', C1, re.S).group(0))] != ["目標・KPIの設計", "戦略と施策計画の策定", "施策の実行（広告・LP・イベントなど）", "効果測定と改善"]: print("[NG] 代行プランの担当すること"); ok = False
if '<p class="plan-card__note">戦略だけでなく、実行まで担当します。</p>' not in C1: print("[NG] 代行プランに「実行まで担当」の補足がない"); ok = False
if [TXT(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'<ul class="dot-list">.*?</ul>', C2, re.S).group(0))] != ["LP・ホワイトペーパーの制作", "広告運用", "セミナー・カンファレンスの企画から商談化まで", "メール配信"]: print("[NG] リード獲得プランの対応できる施策"); ok = False
need("代行プランの料金", C1, [
    '<span class="plan-price__old"><s>通常 月40万円</s></span>',
    '<span class="plan-price__off">先着3社 10万円OFF</span>',
    '<span class="plan-price__k">モニター価格</span> <span class="plan-price__amt">月<span class="big">30</span>万円<span class="plan-price__tax">（税別）</span></span>',
    '<p class="plan-price__sub">3か月〜</p>',
    '<p class="plan-price__cond">※成果が出た場合に、事例として掲載させていただきます</p>',
])
if TXT(re.search(r'<p class="plan-price plan-price--monitor">.*?</p>', C1, re.S).group(0)) != "通常 月40万円 先着3社 10万円OFF モニター価格 月30万円（税別）": print("[NG] 代行プランの料金の文字", TXT(re.search(r'<p class="plan-price plan-price--monitor">.*?</p>', C1, re.S).group(0))); ok = False
bottom = lambda c_: TXT(re.search(r'<div class="plan-card__bottom">.*?</div>\s*</div>', c_, re.S).group(0))
if bottom(C1) != "料金 通常 月40万円 先着3社 10万円OFF モニター価格 月30万円（税別） 3か月〜 ※成果が出た場合に、事例として掲載させていただきます": print("[NG] 代行プランの料金と期間", bottom(C1)); ok = False
if bottom(C2) != "料金 10万円〜（税別） 施策ごと": print("[NG] リード獲得プランの料金と期間", bottom(C2)); ok = False
if bottom(C3) != "料金 導入 10万円〜 運用 月5万円〜（税別）": print("[NG] HubSpotプランの料金", bottom(C3)); ok = False
MEASURES = [TXT(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'<ul class="dot-list">.*?</ul>', C3, re.S).group(0))]
if MEASURES != ["導入の設計と初期設定", "データの移行とフォーム・メールの設定", "営業との運用ルールづくり", "レポート作成と使い方のレクチャー"]: print("[NG] HubSpotプランの担当すること", MEASURES); ok = False
# 注記（小さく、1行ずつ）→ CTAの行1つ
if "plan-notes" in S_PLANS or "初期費用はかかりません" in S_PLANS: print("[NG] プランの下の注記が残っている"); ok = False
pos = [S_PLANS.find(x) for x in ['class="plan-grid', 'class="plans-cta"', 'class="bubble"', 'class="btn-row"']]
if pos != sorted(pos) or min(pos) < 0: print("[NG] プランの並びが「カード → CTAの行（吹き出し → ボタン）」でない", pos); ok = False
need("プランのCTA", S_PLANS, [BUBBLE_HTML, "<span>まずは無料で相談する</span>", "<span>資料請求はこちら</span>"])
if not re.search(r'<p class="bubble"><span>[^<]*</span></p>\s*<div class="btn-row">\s*<a class="btn" href="contact.html">', S_PLANS): print("[NG] プランのCTA：吹き出しが主ボタンのすぐ上でない"); ok = False
if S_PLANS.count("<a ") != 2 or S_PLANS.count('class="btn-row"') != 1: print("[NG] プランのセクションのボタンは CTAの行の2つ（主・従）だけのはず", S_PLANS.count("<a ")); ok = False
if S_PLANS.count("こんな方におすすめ") != 3 or S_PLANS.count('class="k-label">担当すること<') != 2 or S_PLANS.count('class="k-label">対応できる施策<') != 1 or S_PLANS.count('class="k-label">料金<') != 3: print("[NG] ラベルの数（おすすめ3・担当2＋対応できる施策1・料金3）"); ok = False
if S_PLANS.count('class="plan-card__tag"') != 1 or "いちばん人気" in S_PLANS: print("[NG] 「基本のプラン」タグが1つだけ・「いちばん人気」なしでない"); ok = False
if S_PLANS.count("モニター") != 2: print("[NG] プランのセクションのモニター表示が 代行の料金＋CTAの吹き出し の2か所でない", S_PLANS.count("モニター")); ok = False
gone("プラン", S_PLANS, ["?plan=", "このプランで相談する", "コースを見る", "#price-course", "plan-help", "どのプランが合うか", "迷ったら", "plans-note", "num-xl", "ひとりめ施策", "sec-lead", "掲載内容は事前にご相談", "現状の整理とゴール設定", "戦略シート", "実行計画", "週次レポート", "運用の手順書"])

# 4. 担当者
need("担当者", S_ABOUT, [
    '<p class="sec-label">代表</p>', '<span class="mark">担当者</span>について', '<p class="role-tag"><span>元マーケティング責任者（BtoB）</span></p>',
    '<p class="about__name">大萱生 隼人</p>', '<div class="about__career">', '私も、同じところから始めました。', '社長直下でBtoBマーケティング部門を一人で立ち上げました。', '2026年に独立した今、貴社にお約束するのは3つです。', '私がいなくても回る体制を、社内に残すことです。', '<div class="about__works reveal">',
    '<h3 class="works-title">これまで取り組んできたこと</h3>',
    '<div class="ph ph--img ph--portrait ph--about">', 'src="img/profile.webp"', 'alt="大萱生 隼人の写真"',
])
WORKS_EXP = [("戦略と設計", "過去の受注データを分析して狙う顧客を決め、BtoBマーケティングの戦略、KPI、予算を設計してきました。"),
             ("施策の実行", "Google・Meta広告の運用、LPや資料の制作、展示会やカンファレンスの企画と集客を、自ら手を動かして進めてきました。"),
             ("商談化と組織づくり", "インサイドセールスと連携して商談につなげる仕組みをつくり、マーケティング部門を1人から6名体制に育てました。")]
works = [(TXT(a), TXT(b)) for a, b in re.findall(r"<li><strong>(.*?)</strong><span>(.*?)</span></li>", re.search(r'<ul class="check-list">.*?</ul>', S_ABOUT, re.S).group(0))]
if works != WORKS_EXP: print("[NG] これまで取り組んできたこと（上流→下流の3つ。太字の見出し＋1文）", works); ok = False
career = re.findall(r'<p class="about__text">(.*?)</p>', re.search(r'<div class="about__career">.*?</div>', S_ABOUT, re.S).group(0))
if len(career) != 2 or "promise-list" in S_ABOUT or "career__when" in S_ABOUT: print("[NG] 担当者の本文（経歴と約束の2段落、お約束は文章）", len(career)); ok = False
need("対応できる施策", S_SVC, ['<div class="scope reveal">', '一気通貫でご支援します', '<li>リスティング広告の運用</li>', '<li>Meta広告の運用</li>', '<li>共催ウェビナーの企画・運営</li>', '<li>ホワイトペーパー制作</li>', '<li>インサイドセールス</li>', '<li>MA・CRMの導入支援（HubSpotなど）</li>'])
for p_ in PAGES:
    if "逆算" in RAW[p_] or "300名" in RAW[p_]: print(f"[NG] {p_}: 「逆算」か「300名」が残っている"); ok = False
for p_ in PAGES:
    if "profile.html" in RAW[p_] or "読み仮名" in RAW[p_] or "about__reading" in RAW[p_]: print(f"[NG] {p_}: プロフィールのページへのリンクか読み仮名が残っている"); ok = False
if os.path.exists(OUT + "profile.html"): print("[NG] profile.html が残っている"); ok = False
gone("担当者", S_ABOUT, ['class="pills"', "stat-card", "about-stats", "stat-note", "部門の人数", "月間リード", "※事業会社在籍時の実績です", "マーケティング経験5年以上", "担当。社長直下", "6名体制まで広げました"])
for g_ in ["24件", "206件", "4,000", "8.5倍"]:
    if g_ in TXT(S_ABOUT): print(f"[NG] 担当者に細かい数字「{g_}」が残っている"); ok = False
pos = [S_ABOUT.find(x) for x in ['class="role-tag"', 'class="about__name"', 'class="about__career"', 'class="works-title"', 'class="check-list"']]
if pos != sorted(pos) or min(pos) < 0: print("[NG] 担当者の並びが「肩書き → 氏名 → 経歴の文章 → これまで取り組んできたこと」でない", pos); ok = False
if S_ABOUT.find('class="about__photo') > S_ABOUT.find('class="about__body'): print("[NG] 写真が左（DOM の先）でない"); ok = False

# 途中のCTA（担当者の後：白地の行。v12 のまま）
need("途中のCTA", S_ROW, [BUBBLE_HTML, "<span>まずは無料で相談する</span>", "<span>資料請求はこちら</span>"])
gone("途中のCTA", S_ROW, ["モニター募集中", "cta-row--band", "cta-row__", "monitor-title", "成果が出た場合に事例として"])
if not re.search(r'<p class="bubble"><span>[^<]*</span></p>\s*<div class="btn-row">\s*<a class="btn" href="contact.html">', S_ROW): print("[NG] 途中のCTA：吹き出しが主ボタンのすぐ上でない"); ok = False
if S_ROW.find('id="about"') != -1 or idx.find('id="about"') > idx.find('<section class="cta-row"'): print("[NG] 途中のCTAが担当者の後でない"); ok = False

# 5. 流れ（v12 のまま）
need("流れ", S_FLOW, [
    'ご相談から<span class="mark">支援開始</span>までの流れ', "オンライン（60分）", "ご状況に合うプラン、進め方、費用をご提案します。", "ここまで全て無料です", "ご相談から開始までの目安は1〜2週間です。",
    "毎週の定例ミーティングで、実績・実施内容・次回の施策をご報告します。", "定期的な見直し", "実績を見ながら、施策と進め方を見直します。ひとりめ代行プランは、3か月目に継続するかどうかを一緒に判断します。",
    "実際のスケジュールは貴社の状況に合わせてご提示します。",
])
if S_FLOW.count('<li class="card step') != 6: print("[NG] 流れのステップが6つでない"); ok = False

# 6. 料金のセクションは削除（id=price・id=price-course・表・縦積み・「月額プラン」「コース」の見出しが無いこと）
for g_ in ['id="price"', 'id="price-course"', "price-tbl", "price-stack", "price-col", "price-block", "price-note", "<table", "月額プラン", "<dt>", "phead"]:
    if g_ in idx_body: print(f"[NG] 料金のセクションの名残「{g_}」が index に残っている"); ok = False
if 'href="#price' in idx or "#price" in "".join(RAW.values()): print("[NG] 「#price」へのリンクが残っている"); ok = False

# 6'. FAQ（4問・閉じたアコーディオン）
need("FAQ", S_FAQ, ['<p class="sec-label">ご質問</p>', 'よくある<span class="mark">ご質問</span>'])
FAQ_EXP = [
    ("契約期間と、途中解約について教えてください。", "ひとりめ代行プランは、最初の3か月を最低期間とし、4か月目以降は1か月ごとに更新できます。最初の3か月の途中での解約は、原則としてお受けしていません。リード獲得プランは施策ごと、HubSpot導入・活用プランは内容に応じてご契約いただけます。"),
    ("社内にマーケティング担当者がいなくても進められますか？", "はい。担当者がいない状態からでも始められます。"),
    ("料金に含まれないものはありますか？", "広告費やツール代などの実費は含まれません。扱いはご相談のうえで決めます。"),
    ("具体的に相談したいことが決まっていなくても申し込んでいいですか？", "はい。現状をお聞きしながら一緒に整理します。"),
]
faqs = [(TXT(q), TXT(a)) for q, a in re.findall(r'<summary class="qa__q">.*?<h3>(.*?)</h3>.*?</summary>\s*<div class="qa__a">.*?<p>(.*?)</p></div>', S_FAQ, re.S)]
if faqs != FAQ_EXP: print("[NG] FAQ の4問が指示書と違う", faqs); ok = False
if len(re.findall(r'<details class="qa">', S_FAQ)) != 4: print("[NG] FAQ が <details class=qa> の4つでない"); ok = False
if re.search(r"<details[^>]*\bopen\b", S_FAQ): print("[NG] FAQ が最初から開いている"); ok = False
if len(re.findall(r'<details class="qa">\s*<summary class="qa__q">', S_FAQ)) != 4: print("[NG] details の最初の子が summary でない"); ok = False
if S_FAQ.count('class="qa__badge"') != 4 or S_FAQ.count('class="qa__badge qa__badge--a"') != 4 or S_FAQ.count('class="qa__icon"') != 4: print("[NG] Q/A バッジ・＋−アイコンの数"); ok = False
gone("FAQ", S_FAQ, ["成果が出るまで", "商材や検討期間", "qa__row", "月額プランは、最初の3か月", "件数のお約束"])

# 8. 最後のCTA
need("最後のCTA", S_CTA, [
    'まずは<span class="mark">無料</span>でご相談ください', '<p class="sec-lead">お申し込みから2営業日以内にご返信します。</p>', BUBBLE_HTML,
    "<span>まずは無料で相談する</span>", "<span>資料請求はこちら</span>",
])
gone("最後のCTA", S_CTA, ["mon-tag", "モニター募集中", "cta-band__monitor", "cta-band__micro", "60分・オンライン", "お見積りまで無料"])
pos = [S_CTA.find(x) for x in ['id="cta-title"', 'class="sec-lead"', 'class="bubble"', 'class="btn-row"']]
if pos != sorted(pos) or min(pos) < 0: print("[NG] 最後のCTAの並びが「見出し → 説明 → 吹き出し → ボタン」でない", pos); ok = False
if not re.search(r'<p class="bubble"><span>[^<]*</span></p>\s*<div class="btn-row">\s*<a class="btn" href="contact.html">', S_CTA): print("[NG] 最後のCTA：吹き出しが主ボタンのすぐ上でない"); ok = False

# 全体
gone("index 全体", idx_body, ["代表が直接", "担当者が途中で変わる", "60分・オンライン", "お見積りまで無料", "?plan=", "このプランで相談する", "コースを見る", "いちばん人気", "モニタープラン", "モニター募集中", "hero__monitor", "cta-row--band", "mon-tag", "class=\"monitor", "plans-note", "どれに当てはまるか", "section--navy", "svc-card", "svc-grid", 'class="cmp', "svc-close", "5名のチーム", "社長直下の一人目マーケター", "成果が出るまで", "リード数を約8.5倍", "展示会で約4,000名を集客", "stat-card", "ひとりめ施策", "迷ったら", "どのプランが合うか"])
if "【要記入" in idx_body: print("[NG] index に【要記入】が残っている"); ok = False
if 'class="stat-grid' in idx or idx.count("stat-card") != 0: print("[NG] index に実績の数字のカードが残っている"); ok = False
if len(re.findall(r'<details class="qa">', idx_body)) != 4: print("[NG] FAQ が4問でない"); ok = False
if idx_body.count('class="pills"') != 1: print("[NG] ピルは FV の1か所だけのはず", idx_body.count('class="pills"')); ok = False
if len(re.findall(r'<table', idx_body)) != 0: print("[NG] index に表が残っている"); ok = False
# ボタン行は4か所（FV・プランの後・担当者の後の白の行・最後のCTA）。それぞれ「吹き出し → 主、従」
rows = re.findall(r'<div class="btn-row[^"]*">(.*?)</div>', idx_body, re.S)
if len(rows) != 4: print("[NG] index のボタン行が4つ（FV・プランの後・担当者の後・最後のCTA）でない", len(rows)); ok = False
for r_ in rows:
    labs = re.findall(r"<span>([^<]+)</span>", r_)
    if labs != ["まずは無料で相談する", "資料請求はこちら"]: print("[NG] ボタン行の文言", labs); ok = False
if idx_body.count('class="bubble"') != 4: print("[NG] 吹き出しが FV・プランの後・担当者の後・最後のCTAの4つでない", idx_body.count('class="bubble"')); ok = False
if len(re.findall(r'<p class="bubble"><span>＼ 先着3社 モニター価格 月30万円 ／</span></p>\s*<div class="btn-row">', idx_body)) != 4: print("[NG] 吹き出しの文言・位置（4か所とも主ボタンの行の直前）"); ok = False
# モニターの表示：FV の吹き出し・プランの代行の料金とCTAの吹き出し・途中と最後のCTAの吹き出しだけ
mon = {k: v.count("モニター") for k, v in {"FV": S_HERO, "特長": S_SVC, "プラン": S_PLANS, "担当者": S_ABOUT, "途中のCTA": S_ROW, "流れ": S_FLOW, "FAQ": S_FAQ, "最後のCTA": S_CTA}.items()}
print("モニターの出現箇所:", mon)
if mon != {"FV": 1, "特長": 0, "プラン": 2, "担当者": 0, "途中のCTA": 1, "流れ": 0, "FAQ": 0, "最後のCTA": 1}: print("[NG] モニターの表示が想定の箇所（FV・代行の料金とプランのCTA・途中・最後のCTA）だけになっていない"); ok = False
if "モニター" in re.search(r"<head>.*?</head>", idx, re.S).group(0): print("[NG] head にモニターがある"); ok = False
if "、HubSpot導入・活用プランからお選びいただけます" not in re.search(r"<head>.*?</head>", idx, re.S).group(0): print("[NG] head（description）に3つのプランがない"); ok = False


# 写真（v10 と同じ：Unsplash の3枚＋代表のプレースホルダー）
nph = len(re.findall(r'class="ph ', idx))
if nph != 3: print(f"[NG] index の写真の枠が {nph} 枚（Unsplash 2枚＋代表の写真1枚の3枚のはず）"); ok = False
if len(re.findall(r'class="ph ph--img', idx)) != 3: print("[NG] index の写真（<img> 入りの枠）が3枚でない"); ok = False
for p_ in PAGES:
    if "写真プレースホルダー" in RAW[p_] or "<figcaption>" in RAW[p_] or "ph__subject" in RAW[p_]: print(f"[NG] {p_}: 写真のプレースホルダーが残っている"); ok = False
for p_ in PAGES:
    if "1分" in RAW[p_]: print(f"[NG] {p_}: 「入力は1分」の文が残っている"); ok = False
for f_ in ["img/profile.webp", "img/profile-600.jpg"]:
    if not os.path.exists(OUT + f_): print(f"[NG] {f_} が出力にない"); ok = False
UNS = [
    ("photo-1631557777232-a2632ae3c67d", "https://unsplash.com/photos/3q4V539j_bw", "ノートパソコンと書類が置かれた机", False),
    ("photo-1688380692117-63178554d76d", "https://unsplash.com/photos/MnPWB-ybjHQ", "ノートパソコンを囲んだ打ち合わせ", False),
]
for pid, srcurl, alt, eager in UNS:
    base = f"https://images.unsplash.com/{pid}?auto=format&amp;fit=crop&amp;w="
    m = re.search(r"<!-- [^>]*?出典 " + re.escape(srcurl) + r" -->\s*<img ([^>]*)>", RAW["index.html"])
    if not m: print(f"[NG] index: {pid} の出典コメント付きの <img> がない"); ok = False; continue
    at = m.group(1)
    for n in [f'src="{base}1200&amp;q=75"', f'srcset="{base}600&amp;q=75 600w, {base}1200&amp;q=75 1200w"', f'alt="{alt}"', "sizes=", "width=\"1200\"", "height="]:
        if n not in at: print(f"[NG] index: {pid} の <img> に「{n}」がない"); ok = False
    if eager and not ('loading="eager"' in at and 'fetchpriority="high"' in at): print("[NG] index: FV の <img> が eager／fetchpriority=high でない"); ok = False
    if not eager and ('loading="lazy"' not in at or "fetchpriority" in at): print(f"[NG] index: {pid} の <img> が lazy でない"); ok = False
if "ph--hero" in idx or "photo-1775163024488" in idx: print("[NG] FV の写真が残っている"); ok = False
if 'class="ph ph--img ph--svc" style="--ar:16/10"' not in idx: print("[NG] サービスの特長の写真が 16:10 の枠でない"); ok = False
if 'class="ph ph--img " style="--ar:4/3"' not in idx: print("[NG] 最後のCTA帯の写真が 4:3 の枠でない"); ok = False
m_svc = re.search(r'<div class="svc-intro">(.*?)</div>\s*<ol class="feat-grid', idx, re.S)
if not m_svc or "sec-head" not in m_svc.group(1) or "<img" not in m_svc.group(1): print("[NG] サービスの特長：見出しと写真が .svc-intro の中にない"); ok = False

# index の面の並び：FV（白）→ サービスの特長（薄）→ プラン（白）→ 担当者（薄）→ 途中のCTA（白の行）→ 流れ（白）→ FAQ（白）→ 最後のCTA（紺）。紺は最後の1つだけ
seq = re.findall(r'<(section|div) class="((?:section|cta-band|cta-row|hero(?!__)|page-head|back-top)[^"]*)"[^>]*?(?: id="([^"]*)")?', idx)
def is_navy(c): return "section--navy" in c or "cta-band" in c
def tone(c): return "紺" if is_navy(c) else ("黄" if "section--problems" in c else ("薄" if "section--alt" in c else "白"))
prev = False
for tag, c, _ in seq:
    n = is_navy(c)
    if n and prev: print(f"[NG] 紺が隣り合っている: {c}"); ok = False
    prev = n
order = " → ".join(tone(c) for _, c, _ in seq)
print("index の面の並び:", order)
need("お悩み", idx_body, ['id="problems"', 'こんな<span class="mark">お悩み</span>はありませんか？', '<li>商談の数が足りない</li>', '<li>担当者はいるが、施策を動かしきれていない</li>', '貴社の「一人目のマーケター」として社内に入り', '<a href="#service">4つの特長を見る</a>'])
if order != "白 → 黄 → 薄 → 白 → 薄 → 白 → 白 → 白 → 紺": print("[NG] 面の並びが想定と違う"); ok = False
ids_order = [i for i in re.findall(r'<section[^>]*? id="([^"]+)"', idx) if i in ("service", "plans", "about", "flow", "price", "faq")]
print("index のセクション順:", ids_order)
if ids_order != ["service", "plans", "about", "flow", "faq"]: print("[NG] セクションの順が想定と違う（料金は削除）"); ok = False
# ナビ：ラベルと順（全ページ）。5項目。開閉するメニュー（トグル）は無い
NAV_EXPECT = [("#service", "サービスの特長"), ("#plans", "プラン"), ("#about", "担当者"), ("#flow", "ご支援の流れ"), ("#faq", "よくある質問")]
for page in PAGES:
    s_ = RAW[page]
    m = re.search(r'<nav class="site-nav".*?</nav>', s_, re.S)
    items = re.findall(r'<li><a href="([^"]+)"[^>]*>([^<]+)</a></li>', m.group(0))
    items = [(h.replace("./", "", 1) if h.startswith("./#") else h, t) for h, t in items]
    if items != NAV_EXPECT: print(f"[NG] {page}: ナビの項目・順が違う {items}"); ok = False
    for g_ in ["nav-toggle", 'id="site-nav"', 'aria-controls', 'aria-expanded', "nav-top", "メニュー</button>"]:
        if g_ in s_: print(f"[NG] {page}: 開閉メニューの名残「{g_}」がある"); ok = False
    if "料金" in m.group(0): print(f"[NG] {page}: ナビに「料金」が残っている"); ok = False

# ---- 全ページ：氏名・禁止語・ヘッダー／フッター／バー
print("\n--- v13：全ページ（氏名・AI・ヘッダー／フッター／バー） ---")
for page in PAGES:
    s_ = RAW[page]
    b_ = re.sub(r"<!--.*?-->", "", s_, flags=re.S)
    # フッター（紺の3列）
    ft = re.search(r'<footer class="site-footer">.*?</footer>', s_, re.S).group(0)
    pre_ = "" if page == "index.html" else "./"
    FT_EXPECT = [
        ("サイト内", ["TOP", "サービスの特長", "プラン", "担当者", "ご支援の流れ", "よくある質問"]),
        ("お問い合わせ", ["無料相談", "サービス資料のダウンロード", "その他のお問い合わせ（提携・取材など）"]),
    ]
    if 'class="logo logo--footer" href="./"' not in ft: print(f"[NG] {page}: フッターのロゴ（案G）がない"); ok = False
    if '<p class="footer__desc">元マーケティング責任者が、BtoBマーケティングの戦略から実行まで担当します。</p>' not in ft or '<p class="footer__op">運営：大萱生 隼人</p>' not in ft: print(f"[NG] {page}: フッターの説明・運営"); ok = False
    heads = re.findall(r'<h2 class="footer__h"[^>]*>(.*?)</h2>', ft)
    if heads != ["サイト内", "お問い合わせ"]: print(f"[NG] {page}: フッターの見出し {heads}"); ok = False
    cols = re.findall(r'<(?:nav|div) class="footer__col".*?</(?:nav|div)>', ft, re.S)
    for (hd_, labs_), col_ in zip(FT_EXPECT, cols):
        got = [TXT(x) for x in re.findall(r"<li><a [^>]*>(.*?)</a></li>", col_)]
        if got != labs_: print(f"[NG] {page}: フッター「{hd_}」の項目 {got}"); ok = False
    site_h = re.findall(r'<li><a href="([^"]+)">', cols[0]) if cols else []
    if site_h != ["./", f"{pre_}#service", f"{pre_}#plans", f"{pre_}#about", f"{pre_}#flow", f"{pre_}#faq"]: print(f"[NG] {page}: フッター「サイト内」のリンク {site_h}"); ok = False
    ct_h = re.findall(r'<li><a href="([^"]+)">', cols[1]) if len(cols) > 1 else []
    if ct_h != ["contact.html", "download.html", "contact.html#other"]: print(f"[NG] {page}: フッター「お問い合わせ」のリンク {ct_h}"); ok = False
    if not re.search(r'<div class="footer__bottom">\s*<a href="privacy.html">プライバシーポリシー</a>\s*<p class="copyright"><small>&copy; 2026 ひとりめマーケ</small></p>\s*</div>', ft): print(f"[NG] {page}: フッターの最下段（プライバシーポリシー／© 2026 ひとりめマーケ）"); ok = False
    for g_ in ["【要記入", "代表：", "運営：<span"]:
        if g_ in ft: print(f"[NG] {page}: フッターに「{g_}」が残っている"); ok = False
    for w in ["TYL", "CINCA", "たべるーと", "EXPO", "EventCanvas", "AI", "人工知能", "ChatGPT", "生成"]:
        if w in re.sub(r"<[^>]+>", " ", b_) or w in re.search(r"<head>.*?</head>", s_, re.S).group(0): print(f"[NG] {page}: 「{w}」が含まれている"); ok = False
    bar = re.search(r'<div class="cta-bar".*?>(.*?)</div>', s_, re.S).group(1)
    if "<span>無料相談（60分）</span>" not in bar: print(f"[NG] {page}: 下部バーの主ボタンが「無料相談（60分）」でない"); ok = False
    hd = re.search(r'<div class="header-cta">(.*?)</div>', s_, re.S).group(1)
    if "<span>無料相談</span>" not in hd or "<span>資料請求</span>" not in hd: print(f"[NG] {page}: ヘッダーのボタンが「無料相談」「資料請求」でない"); ok = False

# ---- contact：?plan= の表示と JS は廃止。選択肢は3プラン＋まだ決まっていない
print("\n--- v13：contact／?plan= の廃止 ---")
opts = re.search(r'<select id="cf-consult_type"[^>]*>(.*?)</select>', ct, re.S)
opt_list = re.findall(r'<option value="([^"]+)">', opts.group(1)) if opts else []
if opt_list != ["ひとりめ代行プラン", "リード獲得プラン", "HubSpot導入・活用プラン", "まだ決まっていない"]: print("[NG] contact の選択肢が指示書（3プラン＋まだ決まっていない）と違う", opt_list); ok = False
CF = section(ct_body, r'<form class="lead-form" data-form="consult".*?</form>')
need("contact のフォーム", CF, ['id="cf-company"', 'id="cf-firstname"', 'id="cf-email"', 'id="cf-phone"', 'id="cf-consult_type"', '<textarea id="cf-message" name="message"', 'name="privacy" type="checkbox" required', '<span>無料相談を申し込む</span>', '（設定前のため送信されません）'])
if len(re.findall(r'<span class="req">必須</span>', CF)) != 5 or len(re.findall(r'<span class="opt">任意</span>', CF)) != 2: print("[NG] contact のフォーム：必須（会社名・お名前・メール・電話・同意）5／任意（電話・相談内容の選択・相談の内容）3"); ok = False
DF = section(dl, r'<form class="lead-form" data-form="download".*?</form>')
need("download のフォーム", DF, ['id="df-company"', 'id="df-firstname"', 'id="df-email"', 'id="df-phone"', 'name="privacy" type="checkbox" required', '<span>資料を受け取る</span>', '（設定前のため送信されません）'])
if len(re.findall(r'<span class="req">必須</span>', DF)) != 5 or len(re.findall(r'<span class="opt">任意</span>', DF)) != 0: print("[NG] download のフォーム：必須5／任意0"); ok = False
for p_ in PAGES:
    if re.search(r"Googleフォーム|GoogleフォームのURL|<iframe|form-frame\"?>\s*<!--", RAW[p_]) and p_ != "privacy.html": print(f"[NG] {p_}: Googleフォームの名残がある"); ok = False
# forms.js：先頭に設定（空）、Apps Script へ送る、必須の検証。HubSpot の名残がないこと
FJS = open(OUT + "js/forms.js", encoding="utf-8").read()
for n_ in ['var FORM_ENDPOINT = "https://script.google.com/macros/s/', "var BOOKING_URL = \"\";", "入力してください", "gv=true"]:
    if n_ not in FJS: print(f"[NG] forms.js に「{n_}」がない"); ok = False
if re.search(r"HUBSPOT|hsforms|\"Content-Type\"", FJS): print("[NG] forms.js に HubSpot の名残か Content-Type の指定がある"); ok = False
for p_ in ["index.html", "contact.html", "download.html"]:
    if RAW[p_].count('name="website" type="text" tabindex="-1"') != RAW[p_].count('<form class="lead-form"'): print(f"[NG] {p_}: ロボット対策の見えない欄がフォームの数だけない"); ok = False
GS = open(OUT + "gas/Code.gs", encoding="utf-8").read()
for n_ in ["function doPost(", "function setup(", "function hourly(", "hayato.ogayu@gmail.com", "if (d.website)"]:
    if n_ not in GS: print(f"[NG] gas/Code.gs に「{n_}」がない"); ok = False
for p_ in ["index.html", "contact.html", "download.html"]:
    if not re.search(r'src="js/forms\.js\?v=[0-9a-f]{8}" defer', RAW[p_]): print(f"[NG] {p_}: forms.js を読んでいない"); ok = False
for p_ in ["privacy.html"]:
    if "forms.js" in RAW[p_]: print(f"[NG] {p_}: フォームが無いのに forms.js を読んでいる"); ok = False
for need_ in ["まだ決まっていない", "ご相談の内容",
              '<p class="step-note reveal">ご契約を前提とせず、まずはお気軽にお悩みをお聞かせください。</p>', "返信の目安：2営業日以内</p>", "<h3>日程のご案内</h3>", "2営業日以内に、メールで日程調整のご案内をお送りします。", "<h3>オンラインでご相談（60分）</h3>"]:
    if need_ not in ct_body: print(f"[NG] contact: 「{need_}」がない"); ok = False
for g_ in ["plan-pick", "data-plan-", "選択中のご相談", "事前入力URL", "?plan=", "一人目のマーケターとして、立ち上げてほしい", "決まった戦略を", "担当者を支えながら", "施策単位で、任せたい"]:
    if g_ in ct: print(f"[NG] contact: 「{g_}」が残っている"); ok = False
for page_ in PAGES:
    if "?plan=" in RAW[page_] or "plan=" in RAW[page_]: print(f"[NG] {page_}: ?plan= が残っている"); ok = False
if opt_list[:3] != plan_heads: print("[NG] contact の選択肢の3つがプランのカードの名前と一致しない", opt_list, plan_heads); ok = False

# ---- download／privacy（v10 のまま）
for need_ in ["<p>フォームの送信後、1営業日以内にメールでお送りします。</p>", "<p class=\"mt-s\">資料をお送りした後に、こちらから営業のご連絡はいたしません。</p>", "形式：PDF</p>"]:
    if need_ not in dl: print(f"[NG] download: 「{need_}」がない"); ok = False
if dl.count("ご支援の進め方") != 4: print("[NG] download: 「ご支援の進め方」は4か所のはず", dl.count("ご支援の進め方")); ok = False
for need_ in ["大萱生 隼人（個人事業者）", "Google LLC（米国）", "GitHub Pages", "日程調整", "電話番号", "2026年11月9日 制定", "hayato.ogayu@gmail.com"]:
    if need_ not in pv: print(f"[NG] privacy: 「{need_}」がない"); ok = False
if "【要記入" in pv or "役職" in pv or "HubSpot" in pv: print("[NG] privacy: 【要記入】か「役職」が残っている"); ok = False


# ---- JS / CSS
print("\n--- v13：JS / CSS ---")
js_ = open(OUT + "js/main.js", encoding="utf-8").read()
if "plan-pick" in js_ or "initPlanPick" in js_ or "section--navy" in js_ or "cta-row--band" in js_: print("[NG] main.js に plan-pick／initPlanPick／cta-row--band／section--navy が残っている"); ok = False
if ".hero .btn-row, .hero-form, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row" not in js_: print("[NG] main.js: 下部バーを隠すボタン行が FV・プランの後・途中の白の行・最後の帯でない"); ok = False
for g_ in ["NAV_INLINE_MIN", "initNav", "nav-toggle", "site-nav", "aria-expanded", "Escape"]:
    if g_ in js_: print(f"[NG] main.js に開閉メニューの名残「{g_}」がある"); ok = False
css_ = re.sub(r"/\*.*?\*/", "", open(OUT + "css/style.css", encoding="utf-8").read(), flags=re.S)
css_c = re.sub(r"\s+", " ", css_)
for g_ in ["section--navy", ".worry", ".split", ".svc-card", ".svc-grid", ".ph--wide", "column-reverse", ".cmp", ".svc-close", ".stat__period", ".cta-row--band", ".cta-row__", ".hero__monitor", ".hero__micro", ".mon-tag", ".monitor", ".plan-pick", ".plans-note", ".plan-card__monitor", ".plan-card__cta", ".phead", ".cta-band__monitor", ".cta-band__micro", ".qa__row",
           ".nav-toggle", ".nav-top", ".site-nav.is-open", ".plan-help", ".about-stats", ".stat-", ".stat__", ".price-", ".mon-line", ".footer-rep", ".footer-links", ".footer-other", ".footer__inner", ".chips", ".plan-card__desc"]:
    if g_ in css_: print(f"[NG] CSS に {g_} が残っている"); ok = False
for n_ in [".bubble {", ".bubble::after {", ".cta-set {", ".cta-row {", ".role-tag", ".career-flow", ".course-list", ".plan-price__old", ".qa__q {", ".qa__icon {", ".qa[open]", ".career li::before", ".skill-tags {", "word-break: auto-phrase",
           ".works-title", ".check-list {", ".footer__grid", ".footer__bottom", ".logo--footer", ".plan-notes", ".plans-cta", "grid-template-rows: subgrid",
           "@media (min-width: 1024px) { .plan-grid { grid-template-columns: repeat(3, minmax(0, 1fr));", ".site-nav { display: none; }", "@media (min-width: 1024px) { .site-header__right { gap: 16px; } .site-nav { display: block; }"]:
    if n_ not in css_c: print(f"[NG] CSS に「{n_}」がない"); ok = False
if "background: var(--yellow); color: var(--navy)" not in re.search(r"\.plan-card__tag \{.*?\}", css_c).group(0): print("[NG] プランのタグが黄地・紺文字でない"); ok = False
if "background: rgba(255, 255, 255, 0.1)" not in re.search(r"\.logo--footer \{.*?\}", css_c).group(0): print("[NG] フッターのロゴが白の10%の透明の背景でない"); ok = False
if "var(--navy-deep)" not in re.search(r"\.site-footer \{.*?\}", css_c).group(0): print("[NG] フッターの地が --navy-deep でない"); ok = False
print("(上に何も出ていなければ全て満たす)")

print("\n結果:", "全て通過" if ok else "問題あり")
sys.exit(0 if ok else 1)
