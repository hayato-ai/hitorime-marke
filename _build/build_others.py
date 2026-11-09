from common import *

# =============== profile.html ===============
p = head(
    f"プロフィール｜{SERVICE}（{SITE_TAG}）",
    "BtoBマーケティングの戦略の策定から施策の実行、改善まで、一人で担当しています。経歴と実績です。",
    f"プロフィール｜{SERVICE}",
    "経歴と実績。",
) + header("profile", crumb="プロフィール")

# 経歴（年月つきの縦のタイムライン。brief_v11.md「プロフィールの事実」の年月どおり）
career = [
    ("2020年4月", "事業会社（ペット業界の人材・経営支援。従業員約300名）に入社。法人営業（1年）"),
    ("2021年4月", "同社でBtoCマーケティング（就職イベント・人材紹介の集客。予算設計から広告・CRMの運用まで）"),
    ("2023年4月", "社長直下でBtoBマーケティング部門を一人で立ち上げ、6名体制まで拡大（2024年8月 リーダー、2025年8月 マネージャー）。戦略から施策の実行、インサイドセールスとの連携まで担当"),
    ("2026年10月", "コンサルティング会社で、クライアント企業の新規事業開発を支援"),
    ("2026年", "独立"),
]
career_li = "\n".join(f'''        <li{' class="is-last"' if k == len(career) - 1 else ""}><span class="career__when">{w}</span><span class="career__what">{t}</span></li>''' for k, (w, t) in enumerate(career))

# 得意領域のタグ
skills = ["BtoBマーケティング戦略", "Web広告（Google・Meta）", "イベント・展示会の集客", "MA・CRM（HubSpot・Salesforce）", "インサイドセールスとの連携"]
skill_li = "\n".join(f"        <li>{x}</li>" for x in skills)

strength_cards = "\n".join(f'''        <li class="card feat-card">
          <span class="num-xl" aria-hidden="true">{i:02d}</span>
          <h3>{"".join(f'<span class="phrase">{x}</span>' for x in t.split("|"))}</h3>
          <p>{d}</p>
        </li>''' for i, (t, d) in enumerate(STRENGTHS, 1))

p += f'''
  <!-- 上部：写真P9（枠のまま）・肩書きのタグ・氏名・ピル2つ（FV と同じ）・本文 -->
  <section class="page-head" aria-labelledby="page-title">
    <div class="container person">
      <div class="reveal">
        <p class="sec-label">プロフィール</p>
        <h1 id="page-title">プロフィール</h1>
        {role_tag()}
        <p class="person__name">{NAME} <span class="about__reading">{READING}</span></p>
        {pills()}
        <p class="person__text">{PROFILE_TEXT}</p>
      </div>
      {photo(P9, reveal=False)}
    </div>
  </section>

  <!-- 強み（カード3つ：大きな番号＋見出し＋本文。見出しは職務経歴書の本人の言葉） -->
  <section class="section section--alt" id="strengths" aria-labelledby="strengths-title">
    <div class="container">
      {sec_head(None, "強み", "strengths-title")}
      <ol class="feat-grid strength-grid reveal">
{strength_cards}
      </ol>
    </div>
  </section>

  <!-- これまで取り組んできたこと（index の担当者と同じ。上流→下流の3つ） -->
  <section class="section" aria-labelledby="results-title">
    <div class="container">
      {sec_head(None, WORKS_TITLE, "results-title")}
      <div class="reveal">
        {works_list("check-list--wide")}
      </div>
    </div>
  </section>

  <!-- 経歴（年月つきの縦のタイムライン） -->
  <section class="section section--alt" aria-labelledby="career-title">
    <div class="container">
      {sec_head(None, "経歴", "career-title")}
      <ol class="career reveal">
{career_li}
      </ol>
    </div>
  </section>

  <!-- 得意領域（タグ） -->
  <section class="section" aria-labelledby="skills-title">
    <div class="container">
      {sec_head(None, "得意領域", "skills-title")}
      <ul class="skill-tags reveal">
{skill_li}
      </ul>
    </div>
  </section>

  <!-- 最後のCTA（紺の全幅帯） -->
  <section class="cta-band cta-band--plain" aria-labelledby="cta-title">
    <div class="container">
      <div class="reveal">
        <p class="sec-label">無料相談</p>
        <h2 class="sec-title" id="cta-title">まずは<span class="mark">無料</span>でご相談ください</h2>
        {btn_pair()}
      </div>
    </div>
  </section>
''' + back_top() + footer("profile")
open(OUT + "profile.html", "w", encoding="utf-8").write(finalize(p))

# =============== contact.html（無料相談） ===============
c = head(
    f"無料相談のお申し込み｜{SERVICE}（{SITE_TAG}）",
    "ご相談は無料です。入力は1分ほどで完了します。",
    f"無料相談のお申し込み｜{SERVICE}",
    "ご相談は無料です。",
    forms=True,
) + header("contact", crumb="無料相談")

c += f'''
  <div class="page-head">
    <div class="container">
      <p class="sec-label">お問い合わせ</p>
      <h1>無料相談のお申し込み</h1>
      <p class="sec-lead">ご相談は無料です。入力は1分ほどで完了します。</p>
    </div>
  </div>

  <!-- フォーム（先） -->
  <section class="section section--alt" id="form" aria-labelledby="form-title">
    <div class="container">
      {sec_head("お申し込み", "お申し込みフォーム", "form-title")}

      <div class="form-card form-card--page reveal" id="form-frame" role="group" aria-label="無料相談のお申し込みフォーム">
        {lead_form("consult", "cf", "無料相談を申し込む", consult=True)}
      </div>

      <div class="card info-card reveal">
        <p>メールでのご連絡先</p>
        <p>{MAIL}</p>
        <p class="mt-s">返信の目安：2営業日以内</p>
      </div>

      <p class="small mt-m">お預かりした情報の扱いは、<a href="privacy.html">プライバシーポリシー</a>をご覧ください。</p>
    </div>
  </section>

  <!-- 流れ（後） -->
  <section class="section" aria-labelledby="flow-title">
    <div class="container">
      {sec_head("流れ", "ご相談の流れ", "flow-title")}
      <ol class="step-grid reveal">
        <li class="card step">
          <span class="num-badge" aria-hidden="true">1</span>
          <h3>フォームから申し込み</h3>
          <p>入力は1分ほどで完了します。</p>
        </li>
        <li class="card step">
          <span class="num-badge" aria-hidden="true">2</span>
          <h3>日程のご連絡</h3>
          <p>2営業日以内に、メールで候補日をお送りします。</p>
        </li>
        <li class="card step step--goal">
          <span class="num-badge" aria-hidden="true">3</span>
          <h3>オンラインでご相談（60分）</h3>
          <p>現状とお悩みをお聞かせください。ご相談は無料です。</p>
        </li>
      </ol>
      <p class="step-note reveal">ご契約を前提とせず、まずはお気軽にお悩みをお聞かせください。</p>
    </div>
  </section>

  <!-- その他のお問い合わせ（フッターの小さなリンクの飛び先） -->
  <section class="section section--small section--alt" id="other" aria-labelledby="other-title">
    <div class="container container--text">
      <h2 class="h2-small" id="other-title">その他のお問い合わせ</h2>
      <p>提携のご相談や取材などは、こちらのメールアドレスへご連絡ください。</p>
      <p class="mt-s">{MAIL}</p>
    </div>
  </section>
''' + back_top() + footer("contact")
open(OUT + "contact.html", "w", encoding="utf-8").write(finalize(c))

# =============== download.html（資料請求） ===============
d = head(
    f"サービス資料の請求｜{SERVICE}（{SITE_TAG}）",
    "サービスの内容、ご支援の進め方、料金をまとめた資料です。入力は1分ほどで完了します。",
    f"サービス資料の請求｜{SERVICE}",
    "サービスの内容、ご支援の進め方、料金をまとめた資料です。",
    forms=True,
) + header("download", crumb="資料請求")

d += f'''
  <div class="page-head page-head--form">
    <div class="container">
      <p class="sec-label">資料請求</p>
      <h1>サービス資料の請求</h1>
      <p class="sec-lead">サービスの内容、ご支援の進め方、料金をまとめた資料です。入力は1分ほどで完了します。</p>
    </div>
  </div>

  <!-- フォーム（先） -->
  <section class="section section--alt section--form-first" id="form" aria-label="資料請求フォーム">
    <div class="container">
      <div class="form-card form-card--page reveal" id="form-frame" role="group" aria-label="資料請求フォーム">
        <h2 class="form-card__title">サービス資料はこちら（無料）</h2>
        {lead_form("download", "df", "資料を受け取る")}
      </div>

      <div class="card info-card reveal">
        <p>資料の送付</p>
        <p>フォームの送信後、1営業日以内にメールでお送りします。</p>
        <p class="mt-s">資料をお送りした後に、こちらから営業のご連絡はいたしません。</p>
      </div>

      <p class="small mt-m">お預かりした情報の扱いは、<a href="privacy.html">プライバシーポリシー</a>をご覧ください。</p>
    </div>
  </section>

  <!-- 資料に載っていること（後） -->
  <section class="section" aria-labelledby="inside-title">
    <div class="container">
      {sec_head("資料請求", "資料に載っていること", "inside-title")}
      <ul class="check-grid reveal">
        <li>サービス内容</li>
        <li>ご支援の進め方</li>
        <li>料金</li>
      </ul>
      <p class="small mt-m reveal">形式：PDF</p>
    </div>
  </section>
''' + back_top() + footer("download")
open(OUT + "download.html", "w", encoding="utf-8").write(finalize(d))

# =============== privacy.html ===============
v = head(
    f"プライバシーポリシー｜{SERVICE}（{SITE_TAG}）",
    "当サイトにおける個人情報の取得、利用目的、第三者提供、委託、アクセス解析、開示等の請求についての方針です。",
    f"プライバシーポリシー｜{SERVICE}",
    "個人情報の取扱いについての方針です。",
    noindex=True,
) + header("privacy", crumb="プライバシーポリシー")

v += f'''
  <div class="page-head">
    <div class="container">
      <p class="sec-label">方針</p>
      <h1>プライバシーポリシー</h1>
    </div>
  </div>

  <section class="section section--alt" aria-label="プライバシーポリシー本文">
    <div class="container container--text legal">
      <p>運営者（以下「当方」といいます）は、当サイト「{SERVICE}」（以下「当サイト」といいます）における個人情報の取扱いについて、次のとおり定めます。</p>

      <h2>1. 運営者</h2>
      <p>{NAME}（個人事業者）</p>

      <h2>2. 取得する情報</h2>
      <p>当サイトでは、無料相談のお申し込みフォームと資料請求フォームを通じて、次の情報をご入力いただきます。</p>
      <ul class="dot-list">
        <li>会社名</li>
        <li>お名前</li>
        <li>メールアドレス</li>
        <li>電話番号（任意）</li>
        <li>ご相談内容（選択）（無料相談のお申し込みフォームのみ・任意）</li>
        <li>ご相談の内容（無料相談のお申し込みフォームのみ・任意）</li>
      </ul>
      <p>メールでご連絡いただいた場合は、メールアドレスとメールの内容を取得します。</p>

      <h2>3. 利用目的</h2>
      <p>取得した情報は、次の目的で利用します。</p>
      <ul class="dot-list">
        <li>お問い合わせへの回答</li>
        <li>資料請求への対応（資料の送付、サービスのご案内）</li>
        <li>サービスの提供</li>
        <li>サービスに関するご案内</li>
      </ul>
      <p>上記以外の目的で利用する場合は、あらかじめお知らせします。</p>

      <h2>4. 第三者提供の制限</h2>
      <p>法令に基づく場合を除き、ご本人の同意なく、取得した個人情報を第三者に提供しません。</p>

      <h2>5. 委託</h2>
      <p>お問い合わせや資料請求の受付に、HubSpotなどの外部サービスを利用しています。これらのサービスの提供事業者に、情報の取扱いを伴う業務を委託する場合があります。各サービスにおける情報の取扱いは、それぞれの提供事業者の定めに従います。</p>

      <h2>6. アクセス解析</h2>
      <p>当サイトでは、利用状況を把握するために、アクセス解析のサービスを使用する場合があります。使用する場合、Cookieなどを通じて、個人を特定しない形で閲覧状況を収集します。Cookieはブラウザの設定で無効にできます。</p>

      <h2>7. 開示等の請求</h2>
      <p>ご本人から、保有する個人情報の開示、訂正、追加、削除、利用停止などのご請求があった場合は、ご本人であることを確認のうえ、法令に従って対応します。下記の窓口までご連絡ください。</p>

      <h2>8. お問い合わせ窓口</h2>
      <p>個人情報の取扱いについてのお問い合わせは、次のメールアドレスで受け付けます。</p>
      <p>{MAIL}</p>

      <h2>9. 改定</h2>
      <p>必要に応じて、この方針を改定することがあります。改定した場合は、当サイトに掲載します。</p>

      <p class="mt-l">制定日：<span class="todo">【要記入：制定日】</span></p>
    </div>
  </section>
''' + back_top() + footer("privacy")
open(OUT + "privacy.html", "w", encoding="utf-8").write(finalize(v))
print("others ok")
