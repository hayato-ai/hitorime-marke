from common import *

# =============== contact.html（無料相談） ===============
c = head(
    f"無料相談のお申し込み｜{SERVICE}（{SITE_TAG}）",
    "ご相談は無料です。",
    f"無料相談のお申し込み｜{SERVICE}",
    "ご相談は無料です。",
    forms=True,
) + header("contact", crumb="無料相談")

c += f'''
  <div class="page-head">
    <div class="container">
      <p class="sec-label">お問い合わせ</p>
      <h1>無料相談のお申し込み</h1>
      <p class="sec-lead">ご相談は無料です。</p>
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
          <p>会社名、お名前、ご連絡先をご入力ください。</p>
        </li>
        <li class="card step">
          <span class="num-badge" aria-hidden="true">2</span>
          <h3>日程のご案内</h3>
          <p>2営業日以内に、メールで日程調整のご案内をお送りします。</p>
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
    "サービスの内容、ご支援の進め方、料金をまとめた資料です。",
    f"サービス資料の請求｜{SERVICE}",
    "サービスの内容、ご支援の進め方、料金をまとめた資料です。",
    forms=True,
) + header("download", crumb="資料請求")

d += f'''
  <div class="page-head page-head--form">
    <div class="container">
      <p class="sec-label">資料請求</p>
      <h1>サービス資料の請求</h1>
      <p class="sec-lead">サービスの内容、ご支援の進め方、料金をまとめた資料です。</p>
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
      <p>{NAME}（以下「当方」といいます）は、「{SERVICE}」のサイト（以下「当サイト」といいます）とサービスにおける個人情報の取扱いについて、個人情報の保護に関する法律その他の法令を守り、次のとおり定めます。</p>

      <h2>1. 事業者</h2>
      <p>名称：{SERVICE}<br>運営者：{NAME}（個人事業者）<br>お問い合わせ先：{MAIL}</p>

      <h2>2. 取得する情報</h2>
      <p>当方は、次の場面で、次の情報を取得します。</p>
      <ul class="dot-list">
        <li>資料請求フォーム：会社名、お名前、メールアドレス、電話番号</li>
        <li>無料相談のお申し込みフォーム：会社名、お名前、メールアドレス、電話番号、ご相談内容、ご相談の詳細（任意）</li>
        <li>日程調整のカレンダー：お名前、メールアドレス、ご予約の日時</li>
        <li>メールでのお問い合わせ：メールアドレス、お名前、メールの内容</li>
        <li>ご契約後のやりとり：業務の遂行に必要な範囲の情報</li>
      </ul>

      <h2>3. 利用目的</h2>
      <p>取得した個人情報は、次の目的の範囲で利用します。</p>
      <ul class="dot-list">
        <li>資料の送付と、お問い合わせへの回答</li>
        <li>無料相談の日程の調整と実施</li>
        <li>ご提案、お見積り、ご契約、サービスの提供</li>
        <li>サービスに関するご案内（ご不要の場合は、いつでも停止できます）</li>
        <li>サービスの改善</li>
      </ul>
      <p>上記以外の目的で利用する場合は、あらかじめご本人の同意をいただきます。</p>

      <h2>4. 第三者への提供</h2>
      <p>当方は、次の場合を除き、ご本人の同意なく個人情報を第三者に提供しません。</p>
      <ul class="dot-list">
        <li>法令に基づく場合</li>
        <li>人の生命、身体または財産の保護のために必要で、ご本人の同意を得ることが難しい場合</li>
        <li>利用目的の達成に必要な範囲で、個人情報の取扱いを委託する場合（次の項目）</li>
      </ul>

      <h2>5. 取扱いの委託と、外国にある事業者の利用</h2>
      <p>当方は、フォームの受付と記録、日程調整、メールの送信のために、Google LLC（米国）が提供するサービス（Googleスプレッドシート、Google Apps Script、Gmail、Googleカレンダー）を利用しており、入力いただいた情報はGoogleのサーバーに保存されます。米国の個人情報の保護に関する制度は、個人情報保護委員会のウェブサイト（<a href="https://www.ppc.go.jp/personalinfo/legal/kaiseihogohou/#gaikoku" target="_blank" rel="noopener">外国における個人情報の保護に関する制度等の調査</a>）で確認できます。Googleにおける情報の取扱いは、同社のプライバシーポリシーに従います。</p>

      <h2>6. 安全管理</h2>
      <p>当方は、取得した個人情報の漏えい、滅失または毀損を防ぐため、アクセスできる人の限定、パスワードの管理、二段階認証の利用など、必要かつ適切な措置を講じます。</p>

      <h2>7. Cookieと外部サービス</h2>
      <p>当サイトはGitHub Pages（GitHub, Inc.）で公開しており、文字の表示（Google Fonts）と一部の写真（Unsplash）を外部のサービスから読み込んでいます。その際、閲覧者のIPアドレスなどの技術的な情報が各サービスに送られることがあります。現在、アクセス解析のツールは使用していません。導入する場合は、この方針を改定してお知らせします。</p>

      <h2>8. 開示等のご請求</h2>
      <p>ご本人から、保有個人データの利用目的の通知、開示、訂正、追加、削除、利用の停止、第三者への提供の停止のご請求があった場合は、ご本人であることを確認したうえで、法令に従い遅滞なく対応します。上記のお問い合わせ先までご連絡ください。</p>

      <h2>9. 改定</h2>
      <p>法令の変更やサービスの内容の変更に応じて、この方針を改定することがあります。改定した場合は、当サイトに掲載した時点から効力を持ちます。</p>

      <p class="mt-l">2026年11月9日 制定</p>
    </div>
  </section>
''' + back_top() + footer("privacy")
open(OUT + "privacy.html", "w", encoding="utf-8").write(finalize(v))
print("others ok")
