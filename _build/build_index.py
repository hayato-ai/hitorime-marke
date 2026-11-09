"""v14 index.html（brief_v14.md。FV：ピル2つ・要点カード3つ・資料請求フォームのカード（写真は無し）、先着3社、代行プランの料金を割引感のある形に、スポットプランの改名と新しい目安価格、流れは1〜2週間、担当者の「これまで取り組んできたこと」を上流→下流の3つに。以下は v13 の説明：
v13 index.html（brief_v13.md。v12 のデザインの型のまま、文面と構成を差し替え）。構成と背景：
FV（白）→ サービスの特長（薄）→ プラン（白）→ 担当者（薄）→ 途中のCTA（白の行）→ ご支援の流れ（白）→ よくあるご質問（白）→ 最後のCTA（紺）
v13 の変更：FV のピルは数字をやめて「こういうことをします」、特長3つの文面を磨き直し、プランは名前を「ひとりめ代行／サポート／スポット」にして PC で横に3枚（高さと料金の下端をそろえる）＋注記＋CTAの行1つ（「迷ったら」の枠は削除）、
担当者は数字のカードをやめて新しい本文と「これまで取り組んできたこと」のチェック3つ、料金のセクションは削除、ヘッダーは開閉メニューをやめてナビ5項目、フッターは3列
"""
from common import *

TITLE = SERVICE + "｜BtoBマーケティング支援・代行｜元マーケティング責任者が戦略から実行まで"
OG_TITLE = SERVICE + "｜BtoBマーケティング支援・代行｜元マーケティング責任者が戦略から実行まで"
DESC = ("元マーケティング責任者が、BtoBマーケティングの戦略から実行まで担当します。"
        "ひとりめ代行プラン、ひとりめサポートプラン、スポットプランからお選びいただけます。ご相談は無料です。")

h = head(TITLE, DESC, OG_TITLE, DESC, images=True, forms=True) + header("index")

# ---------- 1. FV（白） ----------
h += f'''
  <!-- 1. ファーストビュー（v14：左にラベル・H1・ピル2つ・要点カード3つ・主ボタン（上に吹き出し）と従ボタン、右（スマホは下）に資料請求フォームのカード。写真は無し。従ボタンは同じページのフォーム #hero-form へ） -->
  <section class="hero" aria-labelledby="hero-title">
    <div class="container hero__grid">
      <div class="hero__text">
        <p class="sec-label">BtoBマーケティング支援・代行</p>
        <h1 id="hero-title"><span class="phrase"><span class="mark">元マーケティング責任者</span>が、</span><span class="phrase">戦略から実行まで担当します</span></h1>
        {pills()}
        {key_facts()}
        {cta_set(doc_href="#hero-form")}
      </div>
      <div class="form-card hero-form" id="hero-form" tabindex="-1" aria-labelledby="hero-form-title">
        <h2 class="form-card__title" id="hero-form-title">サービス資料はこちら（無料）</h2>
        {lead_form("download", "hf", "資料を受け取る")}
      </div>
    </div>
  </section>
'''

# ---------- 2. サービスの特長（薄。#service） ----------
FEATS = [
    ("受注から逆算して、|施策を選ぶ", "法人営業の現場を知っているからこそ、リードの数より、受注につながるかを基準に施策を選びます。まずは過去の受注データから、狙うべき顧客を見極めます。"),
    ("戦略で終わらず、|実行までやりきる", "広告の運用、LPや資料の制作、展示会の集客まで、事業会社で自ら手を動かしてきました。立てた戦略を、そのまま現場で形にします。"),
    ("立ち上げた後も、|回る体制を残す", "マーケティング部門を1人から6名体制に育てた経験をもとに、運用の手順書づくりや、担当者の採用・引き継ぎまで見据えて進めます。"),
]
feat_cards = "\n".join(f'''        <li class="card feat-card">
          <span class="num-xl" aria-hidden="true">{i:02d}</span>
          <h3>{"".join(f'<span class="phrase">{x}</span>' for x in t.split("|"))}</h3>
          <p>{d}</p>
        </li>''' for i, (t, d) in enumerate(FEATS, 1))
h += f'''
  <!-- 2. サービスの特長（#service。背景：薄い青灰。見出しの横（PC）／下（スマホ）に写真1枚（16:10）、特長3つ） -->
  <section class="section section--alt" id="service" aria-labelledby="service-title">
    <div class="container">
      <div class="svc-intro">
        {sec_head("サービスの特長", '<span class="phrase"><span class="mark">元マーケティング責任者</span></span><span class="phrase">だからできる、</span><span class="phrase">3つのこと</span>', "service-title")}
        {unsplash(**IMG_SERVICE)}
      </div>
      <ol class="feat-grid reveal">
{feat_cards}
      </ol>
    </div>
  </section>
'''


# ---------- 3. プラン（白。#plans） ----------
# ひとりめ代行／サポート／スポットの3枚（1024px以上で横に3列、それ未満は1列。高さと料金の下端をそろえる）→ 注記（1行ずつ）→ CTAの行1つ。カードの中に相談ボタンは置かない
# 各カードは上から：タグ（1枚目だけ）→ プラン名 → ひとこと → こんな方におすすめ → 担当すること（3つまで）→ 料金と期間
PLANS = [
    dict(id=1, name="ひとりめ代行プラン", tag="基本のプラン",
         lead="戦略から実行まで、丸ごと任せたい",
         who="マーケティングの担当者がいない企業様",
         does=["戦略と施策の設計", "施策の実行と改善", "営業との連携"],
         price=(
             '<p class="plan-price plan-price--monitor">'
             '<span class="plan-price__old"><s>通常 月40万円</s></span> '
             '<span class="plan-price__off">先着3社 10万円OFF</span> '
             '<span class="plan-price__now"><span class="plan-price__k">モニター価格</span> <span class="plan-price__amt">月<span class="big">30</span>万円<span class="plan-price__tax">（税別）</span></span></span>'
             '</p>\n'
             '              <p class="plan-price__sub">3か月〜</p>\n'
             '              <p class="plan-price__cond">※成果が出た場合に、事例として掲載させていただきます</p>')),
    dict(id=2, name="ひとりめサポートプラン", tag=None,
         lead="社内の担当者を、支えてほしい",
         who="マーケティングの担当者が1人いる（兼任を含む）企業様",
         does=["戦略と優先順位の決定", "計画と制作物のレビュー", "毎週の定例とご相談"],
         price='<p class="plan-price"><span class="plan-price__amt">月<span class="big">15</span>万円〜<span class="plan-price__tax">（税別）</span></span></p>\n'
               '              <p class="plan-price__sub">3か月〜</p>'),
    dict(id=3, name="スポットプラン", tag=None,
         lead="必要な施策だけ、頼みたい",
         who="やりたい施策が決まっている企業様",
         does=None,
         courses=[("ライト", "15万円〜", "（LP・資料などの制作。構成の設計込み）"),
                  ("スタンダード", "30万円〜", "（設計・制作・配信まで）"),
                  ("フル", "45万円〜", "（実行・振り返り・営業への引き渡しまで）")],
         price='<p class="plan-price"><span class="plan-price__amt plan-price__amt--quote">お見積り</span></p>\n'
               '              <p class="plan-price__sub">目安：15万円〜（税別）・施策ごと</p>'),
]
plan_cards = []
for p in PLANS:
    tag = f'\n          <span class="plan-card__tag">{p["tag"]}</span>' if p["tag"] else ""
    if p["does"]:
        does = "\n".join(f"              <li>{d}</li>" for d in p["does"])
        body = f'''
          <div class="plan-card__sec plan-card__does">
            <p class="k-label">担当すること</p>
            <ul class="dot-list">
{does}
            </ul>
          </div>'''
    else:
        rows = "\n".join(f'              <li><span class="course-list__name">{n}</span> <b>{pr}</b><span class="course-list__scope">{sc}</span></li>' for n, pr, sc in p["courses"])
        body = f'''
          <div class="plan-card__sec plan-card__does">
            <p class="k-label">担当すること</p>
            <ul class="dot-list course-list">
{rows}
            </ul>
          </div>'''
    plan_cards.append(f'''        <li class="card plan-card" id="plan-{p["id"]}">{tag}
          <h3>{p["name"]}</h3>
          <p class="plan-card__lead">{p["lead"]}</p>
          <div class="plan-card__sec plan-card__for">
            <p class="k-label">こんな方におすすめ</p>
            <p>{p["who"]}</p>
          </div>{body}
          <div class="plan-card__bottom">
            <div class="plan-card__sec">
              <p class="k-label">料金</p>
              {p["price"]}
            </div>
          </div>
        </li>''')
PLAN_NOTES = ["初期費用はかかりません。", "代行プランとサポートプランは、毎週ご報告します。", "広告費などの実費は含まれません。扱いはご相談のうえで決めます。"]
plan_notes = "\n".join(f"        <li>{n}</li>" for n in PLAN_NOTES)
h += f'''
  <!-- 3. プラン（#plans。背景：白。3つの名前つきプランを PC（1024px以上）で横に3枚、それ未満は1列。カードの下に注記（1行ずつ）、その下にCTAの行を1つ） -->
  <section class="section" id="plans" aria-labelledby="plans-title">
    <div class="container">
      {sec_head("プラン", 'ご依頼に合わせた<span class="mark">3つのプラン</span>', "plans-title")}
      <ul class="plan-grid reveal">
{chr(10).join(plan_cards)}
      </ul>
      <ul class="plan-notes reveal">
{plan_notes}
      </ul>
      <div class="plans-cta">
        {cta_set("cta-set--center")}
      </div>
    </div>
  </section>
'''

# ---------- 4. 担当者（薄） ----------
# 左に写真（プレースホルダー）、右に「肩書き（黄のタグ）→ 氏名 → 本文 → これまで取り組んできたこと（チェック3つ）→ 経歴の流れ → プロフィールを見る」
CAREER_FLOW = ["法人営業", "BtoCマーケティング", "BtoBマーケティング部門の立ち上げ", "独立"]
career_flow = "\n".join(f'          <li{" class=\"is-last\"" if k == len(CAREER_FLOW) - 1 else ""}><span>{t}</span></li>' for k, t in enumerate(CAREER_FLOW))
h += f'''
  <!-- 4. 担当者（背景：薄い青灰。左に写真、右に 肩書きのタグ・氏名・本文・これまで取り組んできたこと・経歴の流れ・ボタン） -->
  <section class="section section--alt" id="about" aria-labelledby="about-title">
    <div class="container">
      {sec_head("代表", '<span class="mark">担当者</span>について', "about-title")}
      <div class="about">
        <div class="about__photo reveal">
          {portrait(P9_ABOUT, "(min-width: 960px) 400px, calc(100vw - 40px)")}
        </div>
        <div class="about__body reveal">
          {role_tag()}
          <p class="about__name">{NAME} <span class="about__reading">{READING}</span></p>
          <p class="about__text">{ABOUT_TEXT}</p>
          <h3 class="works-title">{WORKS_TITLE}</h3>
          {works_list()}
          <ol class="career-flow">
{career_flow}
          </ol>
          <p class="about__more"><a class="btn btn--ghost" href="profile.html"><span>プロフィールを詳しく見る</span><span class="btn__arrow" aria-hidden="true">{ARROW}</span></a></p>
        </div>
      </div>
    </div>
  </section>
{cta_row_plain()}'''

# ---------- 5. ご支援の流れ（白。#flow） ----------
steps = [
    ("お問い合わせ・無料相談", "現状とお悩みをお聞かせください。ご相談は無料です。", '<span class="step__meta">オンライン（60分）</span>'),
    ("ヒアリング", "課題と目標を整理します。"),
    ("ご提案・お見積り", "ご状況に合うプラン、進め方、費用をご提案します。"),
    ("ご契約・支援開始", 'ご相談から開始までの目安は1〜2週間です。'),
    ("毎週の定例とご報告", "毎週の定例ミーティングで、実績・実施内容・次回の施策をご報告します。"),
    ("定期的な見直し", "実績を見ながら、施策と進め方を見直します。ひとりめ代行プランとひとりめサポートプランは、3か月目に継続するかどうかを一緒に判断します。"),
]
step_li = []
for i, st in enumerate(steps, 1):
    t, d = st[:2]
    extra = st[2] if len(st) > 2 else ""
    goal = " step--goal" if i == len(steps) else ""
    step_li.append(f'''        <li class="card step{goal}">
          <span class="num-badge" aria-hidden="true">{i}</span>
          <h3>{t}</h3>
          <p>{d}{extra}</p>
        </li>''')
    if i == 3:
        # 「ここまで全て無料です」はステップ3の下に1回だけ（S13）
        step_li.append('        <li class="step-free"><span>ここまで全て無料です</span></li>')
h += f'''
  <!-- 5. ご支援の流れ（#flow。背景：白。全プラン共通の6ステップ。最後のステップだけ紺に反転。v12 のまま） -->
  <section class="section" id="flow" aria-labelledby="flow-title">
    <div class="container">
      {sec_head("ご支援の流れ", 'ご相談から<span class="mark">支援開始</span>までの流れ', "flow-title")}
      <ol class="step-grid reveal">
{chr(10).join(step_li)}
      </ol>
      <p class="step-note reveal">実際のスケジュールは貴社の状況に合わせてご提示します。</p>
    </div>
  </section>
'''


# ---------- 6. よくあるご質問（白。#faq。4問。閉じたアコーディオン） ----------
faq = [
    ("契約期間と、|途中解約について|教えてください。", "ひとりめ代行プランとひとりめサポートプランは、最初の3か月を最低期間とし、4か月目以降は1か月ごとに更新できます。最初の3か月の途中での解約は、原則としてお受けしていません。スポットプランは、施策ごとのご契約です。"),
    ("社内に|マーケティング担当者が|いなくても|進められますか？", "はい。担当者がいない状態からでも始められます。"),
    ("料金に含まれない|ものはありますか？", "広告費やツール代などの実費は含まれません。扱いはご相談のうえで決めます。"),
    ("具体的に|相談したいことが|決まっていなくても|申し込んでいいですか？", "はい。現状をお聞きしながら一緒に整理します。"),
]
faq_html = "\n".join(f'''        <details class="qa">
          <summary class="qa__q"><span class="qa__badge" aria-hidden="true">Q</span><h3>{"".join(f'<span class="phrase">{x}</span>' for x in q.split("|"))}</h3><span class="qa__icon" aria-hidden="true"></span></summary>
          <div class="qa__a"><span class="qa__badge qa__badge--a" aria-hidden="true">A</span><p>{a}</p></div>
        </details>''' for q, a in faq)
h += f'''
  <!-- 6. よくあるご質問（#faq。背景：白。4問。details/summary のアコーディオン。最初は全部閉じる。Q/A の丸バッジ、右端に＋／−） -->
  <section class="section" id="faq" aria-labelledby="faq-title">
    <div class="container">
      {sec_head("ご質問", 'よくある<span class="mark">ご質問</span>', "faq-title")}
      <div class="qa-list reveal">
{faq_html}
      </div>
    </div>
  </section>
'''

# ---------- 7. 最後のCTA（紺の全幅帯） ----------
h += f'''
  <!-- 7. 最後のCTA（紺の全幅帯。右に写真（Unsplash））。主ボタンの上に吹き出しのマイクロコピー（白文字） -->
  <section class="cta-band" aria-labelledby="cta-title">
    <div class="container cta-band__grid">
      <div class="reveal">
        <p class="sec-label">無料相談</p>
        <h2 class="sec-title" id="cta-title">まずは<span class="mark">無料</span>でご相談ください</h2>
        <p class="sec-lead">お申し込みから2営業日以内にご返信します。</p>
        {cta_set("cta-set--band")}
      </div>
      {unsplash(**IMG_CTA)}
    </div>
  </section>
'''
h += footer("index")
open(OUT + "index.html", "w", encoding="utf-8").write(finalize(h))
print("index ok")
