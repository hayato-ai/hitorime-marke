"""v14 共通部品（brief_v14.md。FV の写真をやめて資料請求フォームのカードに、フォームは自前（js/forms.js から HubSpot Forms API へ）、先着3社、スポットプラン、強みのカード、上流→下流の「これまで取り組んできたこと」を足した。以下は v13 の説明：
v13 共通部品（brief_v13.md。v12 の部品から、開閉メニュー（トグル）・実績の数字のカード・【要記入：社名】を外し、ナビ5項目のヘッダー、3列のフッター、「これまで取り組んできたこと」のチェックリスト、新しいピルを入れた）。
- ロゴ（氏名＋小さく「BtoBマーケティング支援」）→ ./ （TOP）
- パンくず（TOP以外）、ページ末尾の「TOPページへ戻る」、フッターの「TOPページ」
- ボタンは2種類（主＝紺の塗り、従＝白地に紺枠）。右端に黄の丸い矢印。DOM は全箇所「主、従」の順
- 写真プレースホルダー：箱の中は「アイコン＋被写体の1行」、構図は箱の下の figcaption
- TOPへのリンクは ./ 、index 内は #service などの同一ページアンカー、他ページからは ./#service
"""

import re

import os
# サイトの出力先はリポジトリの直下（GitHub Pages でそのまま公開する）。_build はこのフォルダ
SCRATCH = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = os.path.dirname(SCRATCH.rstrip("/")) + "/"

NAME = "大萱生 隼人"
# 読み仮名は本人が決める（brief_v13.md：残す【要記入】）。氏名のすぐ後ろに置く
READING = '<span class="todo">【要記入：読み仮名】</span>'
# 中身の無い mailto: リンクはやめ、【要記入】の span だけにする
MAIL_ADDR = "hayato.ogayu@gmail.com"
MAIL = f'<a href="mailto:{MAIL_ADDR}">{MAIL_ADDR}</a>'

SITE_TAG = "BtoBマーケティング支援"
NAV_MIN = 1024   # ナビを横に出す幅（実測で決めた値。style.css・main.js・qa と合わせる）
SERVICE = "ひとりめマーケ"
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

CAMERA = '<svg class="ph__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 8h3l1.6-2h6.8L17 8h3v11H4z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><circle cx="12" cy="13.5" r="3.6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

# JSが使える環境だけ html.js を付ける。main.js が正常に動けば解除、動かなければ4秒後に js クラスを外して全部表示する
INLINE_JS = '''<script>(function(){var d=document.documentElement,w=window;if("IntersectionObserver" in w&&!(w.matchMedia&&w.matchMedia("(prefers-reduced-motion: reduce)").matches)){d.classList.add("js");w.__revealTimer=setTimeout(function(){d.classList.remove("js")},4000)}})();</script>'''


def head(title, desc, og_title, og_desc, og_type="website", noindex=False, images=False, forms=False):
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    forms_js = '\n<script src="js/forms.js" defer></script>' if forms else ""
    img_pre = '\n<link rel="preconnect" href="https://images.unsplash.com">' if images else ""
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">{robots}
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SERVICE}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2032%2032%27%3E%3Ccircle%20cx%3D%2716%27%20cy%3D%2716%27%20r%3D%2716%27%20fill%3D%27%23FFC531%27/%3E%3Ccircle%20cx%3D%2716%27%20cy%3D%2711%27%20r%3D%275%27%20fill%3D%27%231C2A55%27/%3E%3Cpath%20d%3D%27M7%2026%20C7%2019%2011%2016.5%2016%2016.5%20C21%2016.5%2025%2019%2025%2026%20Z%27%20fill%3D%27%231C2A55%27/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{img_pre}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,700;0,900;1,900&amp;family=Noto+Sans+JP:wght@400;500;700;900&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@900&amp;text=%E3%81%B2%E3%81%A8%E3%82%8A%E3%82%81%E3%83%9E%E3%83%BC%E3%82%B1&amp;display=swap">
<link rel="stylesheet" href="css/style.css">
{INLINE_JS}
<script src="js/main.js" defer></script>{forms_js}
</head>
<body>
<a class="skip-link" href="#main">本文へ移動</a>
'''


def _cur(current, name):
    return ' aria-current="page"' if current == name else ''


# ナビの項目（5つ。開閉するメニューは無い。brief_v13.md）。index 内は同一ページアンカー、他ページからは ./#service
def nav_items(pre):
    return [(f"{pre}#service", "サービスの特長"), (f"{pre}#plans", "プラン"), (f"{pre}#about", "担当者"), (f"{pre}#flow", "ご支援の流れ"), (f"{pre}#faq", "よくある質問")]


def logo_html(cls=""):
    c = "logo" + (" " + cls if cls else "")
    return f'''<a class="{c}" href="./">
      <span class="logo__mark"><svg class="logo__person" viewBox="0 0 30 30" aria-hidden="true"><circle cx="15" cy="8" r="6.5" fill="#1C2A55"/><path d="M3 30 C3 20 8.5 16 15 16 C21.5 16 27 20 27 30 Z" fill="#1C2A55"/></svg></span>
      <span class="logo__name">{SERVICE}</span>
    </a>'''


def header(current="", crumb=None):
    """crumb: TOP以外のページのパンくず末尾の文字列"""
    on_top = current == "index"
    pre = "" if on_top else "./"
    crumb_html = ""
    if crumb:
        crumb_html = f'''
  <nav class="breadcrumb" aria-label="パンくず">
    <div class="container">
      <ol>
        <li><a href="./">TOP</a></li>
        <li aria-current="page">{crumb}</li>
      </ol>
    </div>
  </nav>
'''
    nav_li = "\n".join(f'          <li><a href="{h}"{_cur(current, "profile") if h == "profile.html" else ""}>{t}</a></li>' for h, t in nav_items(pre))
    return f'''
<header class="site-header">
  <div class="container site-header__inner">
    {logo_html()}
    <div class="site-header__right">
      <!-- ナビ（{NAV_MIN}px以上で横に並ぶ。それ未満はロゴとCTAだけ。開閉するメニューは無い） -->
      <nav class="site-nav" aria-label="メインメニュー">
        <ul>
{nav_li}
        </ul>
      </nav>
      <!-- 常時表示のCTA：{NAV_MIN}px以上はナビの右に2つ、768〜{NAV_MIN - 1}pxはロゴの右に2つ、767px以下は小さな主ボタン（無料相談）だけ（資料請求は画面下のバー）。そのページ自身へのボタンは CSS で隠す -->
      <div class="header-cta">
        <a class="btn btn--small" href="contact.html"{_cur(current, "contact")}><span>無料相談</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></a>
        <a class="btn btn--ghost btn--small" href="download.html"{_cur(current, "download")}><span>資料請求</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></a>
      </div>
    </div>
  </div>
</header>
{crumb_html}
<main id="main">
'''


def footer(current=""):
    pre = "" if current == "index" else "./"
    site_li = "\n".join(f'          <li><a href="{h}">{t}</a></li>' for h, t in [("./", "TOP")] + nav_items(pre))
    return f'''
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        {logo_html("logo--footer")}
        <p class="footer__desc">元マーケティング責任者が、BtoBマーケティングの戦略から実行まで担当します。</p>
        <p class="footer__op">運営：{NAME}</p>
      </div>
      <nav class="footer__col" aria-labelledby="footer-site">
        <h2 class="footer__h" id="footer-site">サイト内</h2>
        <ul>
{site_li}
        </ul>
      </nav>
      <div class="footer__col" role="group" aria-labelledby="footer-contact">
        <h2 class="footer__h" id="footer-contact">お問い合わせ</h2>
        <ul>
          <li><a href="contact.html">無料相談</a></li>
          <li><a href="download.html">サービス資料のダウンロード</a></li>
          <li><a href="contact.html#other">その他のお問い合わせ（提携・取材など）</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <a href="privacy.html">プライバシーポリシー</a>
      <p class="copyright"><small>&copy; 2026 {SERVICE}</small></p>
    </div>
  </div>
</footer>

<!-- スマホ（768px未満）：画面下に追従する2つのCTA。主（無料相談）が左、従（資料請求）が右。index では FV・プランのCTA・途中のCTA・最後の紺の帯のボタンが見えている間は隠れる（main.js） -->
<div class="cta-bar" role="group" aria-label="無料相談と資料請求">
  <a class="btn" href="contact.html"{_cur(current, "contact")}><span>無料相談（60分）</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></a>
  <a class="btn btn--ghost" href="download.html"{_cur(current, "download")}><span>資料請求</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></a>
</div>
</body>
</html>
'''


# ---- ボタン（形は2種類：主＝紺の塗り、従＝白地に紺枠。右端に黄の丸い矢印） ----
def btn(label, href, ghost=False, extra=""):
    cls = "btn btn--ghost" if ghost else "btn"
    if extra:
        cls += " " + extra
    return f'<a class="{cls}" href="{href}"><span>{label}</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></a>'


CONSULT_LABEL = "まずは無料で相談する"
DOC_LABEL = "資料請求はこちら"
# 主ボタンのすぐ上に付ける吹き出しのマイクロコピー（FV・プランのCTA・途中のCTA・最後のCTA帯の4か所だけ。モニターの告知はここと、代行プランの料金だけ）
BUBBLE = "＼ 先着3社 モニター価格 月30万円 ／"


def btn_pair(extra_class="", doc_href="download.html"):
    """ボタン行：DOM は主（相談）、従（資料）の順。縦積みでは主が上、横並びでは主が左。文言は全ページ同じ。"""
    cls = "btn-row" + (" " + extra_class if extra_class else "")
    return f'''<div class="{cls}">
          {btn(CONSULT_LABEL, "contact.html")}
          {btn(DOC_LABEL, doc_href, ghost=True)}
        </div>'''


def cta_set(extra_class="", doc_href="download.html"):
    """吹き出しのマイクロコピー（主ボタンの左端に合わせる。下に小さな三角）＋ボタン行。FV・プランのCTA・途中のCTA・最後のCTA帯で使う。"""
    cls = "cta-set" + (" " + extra_class if extra_class else "")
    return f'''<div class="{cls}">
          <p class="bubble"><span>{BUBBLE}</span></p>
          {btn_pair(doc_href=doc_href)}
        </div>'''


def cta_row_plain():
    """途中のCTA（担当者の後）：白地の行。吹き出し＋ボタン2つ。index に1本だけ置く。"""
    return f'''
  <section class="cta-row" aria-label="無料相談と資料請求">
    <div class="container">
      {cta_set("cta-set--center")}
    </div>
  </section>
'''


def back_top():
    return f'''
  <div class="back-top">
    <div class="container">
      <a class="btn btn--ghost btn--back" href="./"><span class="btn__arrow" aria-hidden="true">{ARROW}</span><span>TOPページへ戻る</span></a>
    </div>
  </div>
'''


def sec_head(label, title_html, title_id, lead=None, tag="h2"):
    lead_html = f'\n        <p class="sec-lead">{lead}</p>' if lead else ""
    label_html = f'\n        <p class="sec-label">{label}</p>' if label else ""
    return f'''<div class="sec-head reveal">{label_html}
        <{tag} class="sec-title" id="{title_id}">{title_html}</{tag}>{lead_html}
      </div>'''


# ---- 写真プレースホルダー（v10：代表の写真 P9 だけが残る。本人の写真が必要なのでプレースホルダーのまま） ----
# 箱の中は「写真アイコン＋被写体の1行」だけ。比率タグは左上。箱の下の figcaption は「代表の写真（本人の写真に差し替えてください）」
def ph(code, ratio_label, ar, subject, comp, cls="", reveal=True):
    style = f' style="--ar:{ar}"' if ar else ""
    rv = " reveal" if reveal else ""
    return f'''<figure class="ph-fig{rv}">
        <div class="ph {cls}"{style} role="img" aria-label="写真プレースホルダー：{subject}">
          <span class="ph__tag">写真 {ratio_label}</span>
          {CAMERA}
          <p class="ph__subject">{subject}</p>
        </div>
        <figcaption>{comp}</figcaption>
      </figure>'''


P9 = dict(code="P9", ratio_label="8:5", ar="8/5", cls="",
          subject="本人のポートレート。背景は淡い青灰（#DCE8F2前後）のシームレス、紺ジャケット＋白シャツ、胸上、真顔から微笑み",
          comp="代表の写真（本人の写真に差し替えてください）")

# index の担当者の写真（v12：右の列が縦に長いので、960px以上は縦長 4:5、それ未満は 8:5。枠の比率は CSS の .ph--about）
P9_ABOUT = dict(code="P9", ratio_label="4:5（スマホは8:5）", ar=None, cls="ph--about",
                subject="本人のポートレート。背景は淡い青灰（#DCE8F2前後）のシームレス、紺ジャケット＋白シャツ、胸上、真顔から微笑み",
                comp="代表の写真（本人の写真に差し替えてください）")


# ---- 写真（Unsplash。無料ライセンス、帰属表示は不要。出典 URL は HTML コメントに残す）----
# 既存の .ph の枠（比率・角丸・object-fit:cover）の中身を <img> に置き換える。撮影指示の figcaption と比率タグは付けない
UNSPLASH = "https://images.unsplash.com/"


def unsplash(photo_id, source, alt, w, h, sizes, ar=None, cls="", eager=False, reveal=True):
    """photo_id: 'photo-…'、source: https://unsplash.com/photos/…（HTML コメントに残す）、w×h: 1200w の実寸（width／height 属性）。"""
    def u(width):
        return f"{UNSPLASH}{photo_id}?auto=format&amp;fit=crop&amp;w={width}&amp;q=75"
    style = f' style="--ar:{ar}"' if ar else ""
    rv = " reveal" if reveal else ""
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return f'''<figure class="ph-fig{rv}">
        <div class="ph ph--img {cls}"{style}>
          <!-- 写真：Unsplash（無料ライセンス、帰属表示は不要）。出典 {source} -->
          <img src="{u(1200)}" srcset="{u(600)} 600w, {u(1200)} 1200w" sizes="{sizes}" alt="{alt}" width="{w}" height="{h}" {load} decoding="async">
        </div>
      </figure>'''


# （v14：FV の写真は無くした）サービスの特長（16:10）。最後のCTA帯（P15 の枠：4:3）。sizes は、枠の中で実際に敷かれる画像の幅（object-fit:cover で枠からはみ出す分を含む。1440px で 672／512／486px）に合わせてある
IMG_SERVICE = dict(photo_id="photo-1631557777232-a2632ae3c67d", source="https://unsplash.com/photos/3q4V539j_bw",
                   alt="ノートパソコンと書類が置かれた机", w=1200, h=675, ar="16/10", cls="ph--svc",
                   sizes="(min-width: 1120px) 512px, (min-width: 960px) calc((100vw - 96px) * 0.5), calc((100vw - 40px) * 1.11)")
IMG_CTA = dict(photo_id="photo-1688380692117-63178554d76d", source="https://unsplash.com/photos/MnPWB-ybjHQ",
               alt="ノートパソコンを囲んだ打ち合わせ", w=1200, h=800, ar="4/3", cls="",
               sizes="(min-width: 1120px) 486px, (min-width: 900px) calc((100vw - 104px) * 0.478), calc((100vw - 40px) * 1.125)")


def photo(d, reveal=True):
    return ph(d["code"], d["ratio_label"], d["ar"], d["subject"], d["comp"], d["cls"], reveal=reveal)


# ---- 代表の写真（本人のスーツの写真。原寸 1086×1448）。枠の比率は P9／P9_ABOUT のまま、顔が切れないよう object-position で上寄せ ----
def portrait(d, sizes, reveal=False):
    style = f' style="--ar:{d['ar']}"' if d["ar"] else ""
    rv = " reveal" if reveal else ""
    return f'''<figure class="ph-fig{rv}">
        <div class="ph ph--img ph--portrait {d['cls']}"{style}>
          <img src="img/profile.webp" srcset="img/profile-600.jpg 600w, img/profile.webp 1086w" sizes="{sizes}" alt="{NAME}の写真" width="1086" height="1448" loading="lazy" decoding="async">
        </div>
      </figure>'''


# ---- 複数ページで同文を使う部品 ----
ROLE = "元マーケティング責任者（BtoB）"
# index の担当者（v13 指示書の文面）
ABOUT_TEXT = ('法人営業を経て、事業会社でBtoCとBtoBのマーケティングを担当してきました。社長直下でBtoBマーケティング部門を一人で立ち上げ、'
              '6名体制まで広げています。2026年に独立。')
# profile の本文（index の担当者の本文と同じにそろえる。細かい数字は載せない）
PROFILE_TEXT = ABOUT_TEXT

WORKS_TITLE = "これまで取り組んできたこと"
# 上流（戦略）→ 下流（営業との連携・組織）の順。各項目は「太字の見出し＋1文」（index の担当者と profile で同じ）
WORKS = [
    ("戦略と設計", "過去の受注データを分析して狙う顧客を決め、BtoBマーケティングの戦略、KPI、予算を設計してきました。"),
    ("施策の実行", "Google・Meta広告の運用、LPや資料の制作、展示会やカンファレンスの企画と集客を、自ら手を動かして進めてきました。"),
    ("商談化と組織づくり", "インサイドセールスと連携して商談につなげる仕組みをつくり、マーケティング部門を1人から6名体制に育てました。"),
]

# profile の「強み」（職務経歴書の本人の言葉。見出しの | は折り返してよい位置）
STRENGTHS = [
    ("ゼロからマーケティング部門を|立ち上げ、|売上に直結させる", "社長直下でBtoBマーケティング部門を一人で立ち上げ、戦略と目標の設計から始めて、6名体制まで広げました。"),
    ("自ら手を動かし、|集客効率を|改善し続ける", "戦略だけでなく、広告の入稿・運用やデータ分析まで自分で行い、集客の効率を改善してきました。"),
    ("営業出身ならではの、|売上から逆算する視点", "キャリアの起点は法人営業です。リード数ではなく、売上につながるマーケティングの設計を重視しています。"),
]


def role_tag():
    """肩書きの黄のタグ（index の担当者、profile）"""
    return f'<p class="role-tag"><span>{ROLE}</span></p>'


# 担当者の経歴（職務経歴書 2026年11月版の事実。勤めてきた会社がどういう会社かを書く）
CAREER = [
    ("2020年4月", "ペット業界で人材・経営支援を行う事業会社（従業員約300名）に入社。法人営業を担当"),
    ("2021年4月", "同社でBtoCマーケティングを担当。就職イベントや人材紹介の集客を、予算設計から広告・CRMの運用まで担う"),
    ("2023年4月", "社長直下でBtoBマーケティング部門を一人で立ち上げ、6名体制まで拡大（2024年8月 リーダー、2025年8月 マネージャー）"),
    ("2026年", "独立し、ひとりめマーケを開始"),
]


def pills():
    """FV のピル3つ。3つ目（黄）は、施策の実行だけの依頼も受けることを示す"""
    return '''<ul class="pills">
              <li>BtoBマーケ部門をゼロから構築</li>
              <li>戦略から施策の実行まで担当</li>
              <li class="is-accent">施策の実行だけのご依頼もOK</li>
            </ul>'''


def works_list(cls=""):
    """「これまで取り組んできたこと」のチェック付きの箇条書き3つ（index の担当者と profile で同じ）"""
    c = "check-list" + (" " + cls if cls else "")
    items = "\n".join(f"          <li><strong>{h}</strong><span>{p}</span></li>" for h, p in WORKS)
    return f'''<ul class="{c}">
{items}
        </ul>'''


# ---- FV の要点カード3つ（v14：白地・紺2px枠・角丸、横並び） ----
KEY_FACTS = [("初期費用", "0円"), ("ご相談から開始まで", "最短1〜2週間"), ("モニター価格", "先着3社")]


def key_facts():
    items = "\n".join(f'              <li><span class="key-facts__k">{k}</span><span class="key-facts__v">{v}</span></li>' for k, v in KEY_FACTS)
    return f'''<ul class="key-facts">
{items}
            </ul>'''


# ---- 自前のフォーム（js/forms.js が検証して Google Apps Script（gas/Code.gs）に POST する。設定が空のときは送信せず注記を出す） ----
CONSULT_OPTIONS = ["ひとりめ代行プラン", "ひとりめサポートプラン", "施策代行プラン", "まだ決まっていない"]
FORM_ERR = "入力してください"


def _field(pfx, name, label, req, kind="text", autocomplete=None, options=None, rows=None, hint=None):
    fid = f"{pfx}-{name}"
    badge = '<span class="req">必須</span>' if req else '<span class="opt">任意</span>'
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ""
    rq = ' required aria-required="true"' if req else ""
    desc = f' aria-describedby="{fid}-err"'
    if kind == "select":
        opts = "".join(f"<option value=\"{o}\">{o}</option>" for o in options)
        ctl = f'<select id="{fid}" name="{name}"{rq}{desc}><option value="">選択してください</option>{opts}</select>'
    elif kind == "textarea":
        ctl = f'<textarea id="{fid}" name="{name}" rows="{rows or 4}"{rq}{desc}></textarea>'
    else:
        im = ' inputmode="email" spellcheck="false" autocapitalize="off"' if kind == "email" else (' inputmode="tel"' if kind == "tel" else "")
        ctl = f'<input id="{fid}" name="{name}" type="{kind}"{ac}{im}{rq}{desc}>'
    return f'''<div class="field" data-field="{name}">
            <label for="{fid}"><span class="field__name">{label}</span>{badge}</label>
            {ctl}
            <p class="field__err" id="{fid}-err" hidden>{FORM_ERR}</p>
          </div>'''


def lead_form(kind, pfx, submit_label, consult=False):
    """kind: download（資料請求）／consult（無料相談）。送る項目名：company／firstname（お名前）／email／phone／message／consult_type（受け取りは gas/Code.gs）"""
    f = [
        _field(pfx, "company", "会社名", True, autocomplete="organization"),
        _field(pfx, "firstname", "お名前", True, autocomplete="name"),
        _field(pfx, "email", "メールアドレス", True, kind="email", autocomplete="email"),
        _field(pfx, "phone", "電話番号", True, kind="tel", autocomplete="tel"),
    ]
    if consult:
        f.append(_field(pfx, "consult_type", "ご相談内容（選択）", False, kind="select", options=CONSULT_OPTIONS))
        f.append(_field(pfx, "message", "ご相談の内容", False, kind="textarea", rows=4))
    fields = "\n          ".join(f)
    return f'''<form class="lead-form" data-form="{kind}" method="post" novalidate>
          {fields}
          <div class="field field--check" data-field="privacy">
            <label class="check" for="{pfx}-privacy"><input id="{pfx}-privacy" name="privacy" type="checkbox" required aria-required="true" aria-describedby="{pfx}-privacy-err"><span class="check__text"><a href="privacy.html" target="_blank" rel="noopener">プライバシーポリシー</a>に同意する<span class="req">必須</span></span></label>
            <p class="field__err" id="{pfx}-privacy-err" hidden>{FORM_ERR}</p>
          </div>
          <div class="lead-form__hp" aria-hidden="true"><label for="{pfx}-website">ウェブサイト</label><input id="{pfx}-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
          <button class="btn btn--block" type="submit"><span>{submit_label}</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></button>
          <p class="lead-form__note" role="status" hidden>（設定前のため送信されません）</p>
          <div class="lead-form__fail" role="alert" hidden>
            <p>送信できませんでした。お手数ですが、次のメールアドレスへご連絡ください。</p>
            <p>{MAIL}</p>
          </div>
          <noscript><p class="lead-form__note">このフォームの送信にはJavaScriptが必要です。</p></noscript>
        </form>
        <div class="lead-form__done" role="status" tabindex="-1" hidden>
          {'<p>お申し込みありがとうございます。</p><p class="lead-form__meet-lead" hidden>続けて、下のカレンダーからご都合のよい日時をお選びください。</p><div class="lead-form__meet" hidden></div><p class="lead-form__meet-fallback">2営業日以内に、メールで日程の候補をお送りします。</p>' if consult else '<p>お申し込みありがとうございます。1営業日以内に、メールで資料をお送りします。</p>'}
        </div>'''


# ---- 仕上げ：「3か月」「1か月」「2026年12月」のような期間・年月は途中で折り返さない（「1か／月ごと」の折れ防止）。本文のテキストだけに適用し、文言は変えない
_NW = re.compile(r"(\d{4}年\d{1,2}月|\d+か月)")


def finalize(html):
    parts = re.split(r"(<[^>]*>)", html)
    out = []
    in_head = False
    for x in parts:
        if x.startswith("<"):
            if x.startswith("<title") or x.startswith("<script") or x.startswith("<style"):
                in_head = True
            elif x.startswith("</title") or x.startswith("</script") or x.startswith("</style"):
                in_head = False
            out.append(x)
        else:
            out.append(x if in_head else _NW.sub(r'<span class="nw">\1</span>', x))
    return "".join(out)
