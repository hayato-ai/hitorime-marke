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
        "ひとりめ代行プラン、ひとりめサポートプラン、施策代行プランからお選びいただけます。施策の実行だけのご依頼も承ります。ご相談は無料です。")

h = head(TITLE, DESC, OG_TITLE, DESC, images=True, forms=True) + header("index")

# ---------- 1. FV（白） ----------
h += f'''
  <!-- 1. ファーストビュー（v14：左にラベル・H1・ピル3つ・主ボタン（上に吹き出し）と従ボタン、右（タブレットは下、スマホは非表示）に資料請求フォームのカード。写真は無し。従ボタンは同じページのフォーム #hero-form へ） -->
  <section class="hero" aria-labelledby="hero-title">
    <div class="container hero__grid">
      <div class="hero__text">
        <p class="sec-label">BtoBマーケティング支援・代行</p>
        <h1 id="hero-title"><span class="phrase">マーケティングに</span><span class="phrase">手が回らない</span><span class="phrase">BtoB企業の、</span><span class="phrase"><span class="mark">一人目のマーケター</span>に</span><span class="phrase">なります</span></h1>
        <p class="hero__sub">元マーケティング責任者が、戦略から実行まで担当します。</p>
        {pills()}
        {cta_set(doc_href="#hero-form")}
      </div>
      <div class="form-card hero-form" id="hero-form" tabindex="-1" aria-labelledby="hero-form-title">
        <h2 class="form-card__title" id="hero-form-title">サービス資料はこちら（無料）</h2>
        {lead_form("download", "hf", "資料を受け取る")}
      </div>
    </div>
  </section>
'''

# ---------- 1.5 お悩み（薄い黄。#problems）：誰のどんな課題か → サービス名の意味（一人目のマーケター）→ 特長へつなぐ ----------
PROBLEMS = [
    "商談の数が足りない",
    "マーケティングの担当者がいない",
    "担当者はいるが、施策を動かしきれていない",
    "広告やLPを作っても、商談につながらない",
    "何から手をつければいいか分からない",
]
problem_li = "\n".join(f"        <li>{x}</li>" for x in PROBLEMS)
h += f'''
  <!-- 1.5 お悩み（#problems。背景：薄い黄。チェック付きの悩み5つ → 下向きの矢印 → 答え（サービス名の意味）。この後の「3つの特長」につなぐ） -->
  <section class="section section--problems" id="problems" aria-labelledby="problems-title">
    <div class="container">
      {sec_head("お悩み", 'こんな<span class="mark">お悩み</span>はありませんか？', "problems-title")}
      <ul class="problem-list reveal">
{problem_li}
      </ul>
      <div class="problem-answer reveal">
        <p class="problem-answer__title"><span class="phrase">そのお悩み、</span><span class="phrase"><span class="mark">ひとりめマーケ</span>が解決します</span></p>
        <p class="problem-answer__text">ひとりめマーケは、貴社の「一人目のマーケター」として社内に入り、戦略づくりから施策の実行まで担当します。担当者がいない企業様も、担当者がいて手が回らない企業様も、すぐに動き出せます。</p>
        <ul class="problem-answer__points">
          <li><span class="num">01</span>施策を絞れる</li>
          <li><span class="num">02</span>施策が回る</li>
          <li><span class="num">03</span>ノウハウが残る</li>
        </ul>
        <p class="problem-answer__more"><a href="#service">3つの特長を見る</a></p>
      </div>
    </div>
  </section>
'''

# ---------- 2. サービスの特長（薄。#service） ----------
FEATS = [
    ("商談につながる施策に、|絞れる", "BtoBマーケティングの責任者として、狙う顧客、KPI、予算の配分までを決めてきました。その経験をもとに、商談につながる施策を見極め、限られた予算と時間を集中させます。"),
    ("手が足りなくても、|施策が回る", "広告の運用、LPや資料の制作、展示会の集客まで、事業会社で自ら手を動かしてきました。戦略だけでなく実行まで担当するので、社内の人手が足りなくても施策が止まりません。"),
    ("社内に、|ノウハウが残る", "マーケティング部門を1人から6名体制に育てた経験をもとに、進め方や判断の基準を手順書にして残します。担当者の採用や引き継ぎまで見据えて進めます。"),
]
SCOPE = ["リスティング広告の運用", "Meta広告の運用", "共催ウェビナーの企画・運営", "ホワイトペーパー制作", "インサイドセールス", "MA・CRMの導入支援（HubSpotなど）"]
scope_li = "\n".join(f"          <li>{x}</li>" for x in SCOPE)
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
        {sec_head("サービスの特長", '<span class="phrase">元事業会社の</span><span class="phrase">マーケティング</span><span class="phrase">責任者だから</span><span class="phrase"><span class="mark">解決できる</span>、</span><span class="phrase">3つのこと</span>', "service-title")}
        {unsplash(**IMG_SERVICE)}
      </div>
      <ol class="feat-grid reveal">
{feat_cards}
      </ol>
      <div class="scope reveal">
        <p class="scope__title"><span class="phrase">戦略から施策の実行まで、</span><span class="phrase">一気通貫でご支援します</span></p>
        <ul class="scope__list">
{scope_li}
        </ul>
      </div>
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
         lead_note="戦略だけでなく、実行まで担当します。",
         does=["目標・KPIの設計", "戦略と施策計画の策定", "施策の実行（広告・LP・資料・メール・ウェビナー・展示会）",
               "効果測定と改善", "営業への引き渡しの仕組みづくり"],
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
         who="担当者が1人いる（兼任を含む）企業様",
         does=["目標・KPIの設計", "施策の優先順位づけ", "計画と制作物のレビュー", "毎週の定例とチャット相談", "担当者の育成"],
         price='<p class="plan-price"><span class="plan-price__amt">月<span class="big">15</span>万円〜<span class="plan-price__tax">（税別）</span></span></p>\n'
               '              <p class="plan-price__sub">3か月〜</p>'),
    dict(id=3, name="施策代行プラン", tag=None,
         lead="必要な施策だけ、頼みたい",
         who="やりたい施策が決まっている企業様",
         lead_note="設計から実行、振り返りまで担当します。",
         does=["LP制作", "ホワイトペーパー・記事の制作", "営業資料・サービス資料の制作", "ウェビナーの企画・運営",
               "広告運用", "メール配信", "展示会・イベントの集客"],
         does_label="対応できる施策",
         price='<p class="plan-price"><span class="plan-price__amt"><span class="big">10</span>万円〜<span class="plan-price__tax">（税別）</span></span></p>\n'
               '              <p class="plan-price__sub">施策ごと</p>'),
]
plan_cards = []
for p in PLANS:
    tag = f'\n          <span class="plan-card__tag">{p["tag"]}</span>' if p["tag"] else ""
    if p["does"]:
        does = "\n".join(f"              <li>{d}</li>" for d in p["does"])
        body = f'''
          <div class="plan-card__sec plan-card__does">
            <p class="k-label">{p.get("does_label", "担当すること")}</p>
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
          <h3>{"".join(f'<span class="phrase">{x}</span>' for x in p["name"].split("|"))}</h3>
          <div class="plan-card__head">
            <p class="plan-card__lead">{p["lead"]}</p>{f'{chr(10)}            <p class="plan-card__note">{p["lead_note"]}</p>' if p.get("lead_note") else ""}
          </div>
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
h += f'''
  <!-- 3. プラン（#plans。背景：白。3つの名前つきプランを PC（1024px以上）で横に3枚、それ未満は1列。カードの下に注記（1行ずつ）、その下にCTAの行を1つ） -->
  <section class="section" id="plans" aria-labelledby="plans-title">
    <div class="container">
      {sec_head("プラン", 'ご依頼に合わせた<span class="mark">3つのプラン</span>', "plans-title")}
      <ul class="plan-grid reveal">
{chr(10).join(plan_cards)}
      </ul>
      <div class="plans-cta">
        {cta_set("cta-set--center")}
      </div>
    </div>
  </section>
'''

# ---------- 4. 担当者（薄） ----------
# 左の列に写真と「これまで取り組んできたこと」（白いカード）、右の列に「肩書き → 氏名 → 本文（悩み → 私も同じ → 経歴 → 3つのお約束）」。
# スマホは 写真 → 本文 → これまで取り組んできたこと の順（grid の並べ替え）
ABOUT_LEAD = "マーケティングの担当者がいない。担当者はいても、手が回らない。何から始めればいいか分からない。<br>私も、同じところから始めました。"
ABOUT_STORY = ("法人営業を経てマーケティングに移り、社長直下でBtoBマーケティング部門を一人で立ち上げました。"
               "戦略を描くだけでなく、広告の運用、LPや資料づくり、展示会の集客、インサイドセールスとの連携まで、"
               "すべて自分で動かしながら、部門を6名体制のチームにしてきました。")
ABOUT_PROMISE_LEAD = "2026年に独立した今、貴社にお約束するのは3つです。"
PROMISES = ["商談につながる施策に絞って、すぐに動き出すこと。", "戦略で終わらせず、実行までやりきること。", "私がいなくても回る体制を、社内に残すこと。"]
promise_li = "\n".join(f'            <li><span class="promise-list__num" aria-hidden="true">{k:02d}</span><span>{t}</span></li>' for k, t in enumerate(PROMISES, 1))
h += f'''
  <!-- 4. 担当者（背景：薄い青灰。左に写真と「これまで取り組んできたこと」、右に 肩書きのタグ・氏名・本文・3つのお約束） -->
  <section class="section section--alt" id="about" aria-labelledby="about-title">
    <div class="container">
      {sec_head("代表", '<span class="mark">担当者</span>について', "about-title")}
      <div class="about">
        <div class="about__photo reveal">
          {portrait(P9_ABOUT, "(min-width: 960px) 400px, calc(100vw - 40px)")}
        </div>
        <div class="about__body reveal">
          {role_tag()}
          <p class="about__name">{NAME}</p>
          <div class="about__career">
            <p class="about__lead">{ABOUT_LEAD}</p>
            <p class="about__text">{ABOUT_STORY}</p>
            <p class="about__text about__text--promise">{ABOUT_PROMISE_LEAD}</p>
          </div>
          <ol class="promise-list">
{promise_li}
          </ol>
        </div>
        <div class="about__works reveal">
          <h3 class="works-title">{WORKS_TITLE}</h3>
          {works_list()}
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
    ("契約期間と、|途中解約について|教えてください。", "ひとりめ代行プランとひとりめサポートプランは、最初の3か月を最低期間とし、4か月目以降は1か月ごとに更新できます。最初の3か月の途中での解約は、原則としてお受けしていません。施策代行プランは、施策ごとのご契約です。"),
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
