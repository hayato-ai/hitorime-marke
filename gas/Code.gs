/**
 * ひとりめマーケ：サイトのフォームの受け取り口（Google Apps Script）
 *
 * - サイトのフォーム（資料請求・無料相談）の内容をスプレッドシートに1行ずつ記録する
 * - 送られるたびに、運営者へ通知メールを送る
 * - 送った人へ、受付の自動返信メールを送る
 * - 予約スケジュールで入った無料相談を「予約」シートに記録し、前日にリマインドメールを送る（1時間ごとのトリガー）
 *
 * 使い方は docs/google-setup.md。最初に setup() を1回実行してから、ウェブアプリとして公開する。
 */

// ===== 設定（ここだけ書き換える） =====
var CONFIG = {
  NOTIFY_TO: "hayato.ogayu@gmail.com",       // 通知の送り先
  SENDER_NAME: "ひとりめマーケ 大萱生 隼人",   // 自動返信の差出人名
  SITE_URL: "https://hayato-ai.github.io/hitorime-marke/",
  DOC_URL: "",                                // サービス資料（PDF）の共有リンク。空の間は「資料は追ってお送りします」と書く
  BOOKING_URL: "https://calendar.app.google/9eAQ7uN3q36Fq3tw9",   // 予約ページのURL（自動返信に載せる）
  BOOKING_KEYWORD: "無料相談",                 // 予約スケジュールの名前に含まれる語。この語を含む予定をリマインドの対象にする
  REMIND_HOURS_BEFORE: 24,                    // 何時間前にリマインドするか
  SHEET_ID: "1tLQVbLVs-5uwaMjOQZO838lbLWKDgi7FeolzwxAEDQE"   // 記録先のスプレッドシートのID（URL の /d/ と /edit の間）。空ならスクリプトが紐づくスプレッドシート
};

var SHEETS = {
  download: { name: "資料請求", header: ["受付日時", "会社名", "お名前", "メールアドレス", "電話番号", "送信元のページ"] },
  consult: { name: "無料相談", header: ["受付日時", "会社名", "お名前", "メールアドレス", "電話番号", "ご相談内容", "ご相談の内容", "送信元のページ"] },
  booking: { name: "予約", header: ["記録日時", "相談の日時", "お名前", "メールアドレス", "予定のタイトル", "リマインド送信"] }
};

// ===== 初期設定（エディタで1回だけ実行する） =====
function setup() {
  var ss = CONFIG.SHEET_ID ? SpreadsheetApp.openById(CONFIG.SHEET_ID) : SpreadsheetApp.getActiveSpreadsheet();
  PropertiesService.getScriptProperties().setProperty("SHEET_ID", ss.getId());
  Object.keys(SHEETS).forEach(function (k) { sheet_(ss, k); });
  var def = ss.getSheetByName("シート1");
  if (def && ss.getSheets().length > 1 && def.getLastRow() === 0) ss.deleteSheet(def);
  // リマインドのトリガー（1時間ごと）。二重に作らない
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === "hourly") ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger("hourly").timeBased().everyHours(1).create();
  Logger.log("準備ができました。スプレッドシート：" + ss.getUrl());
}

// ===== フォームの受け取り =====
function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || "{}");
    var kind = d.form === "consult" ? "consult" : "download";
    // ロボット対策：人には見えない欄（website）が埋まっていたら、記録もメールもせずに受け付けたことにする
    if (d.website) return json_({ ok: true });
    var v = {
      company: clean_(d.company, 100),
      firstname: clean_(d.firstname, 60),
      email: clean_(d.email, 120),
      phone: clean_(d.phone, 30),
      consult_type: clean_(d.consult_type, 40),
      message: clean_(d.message, 2000),
      page: clean_(d.page, 300)
    };
    if (!v.company || !v.firstname || !v.phone || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email)) {
      return json_({ ok: false, error: "invalid" });
    }

    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      var sh = sheet_(book_(), kind);
      var now = new Date();
      var row = kind === "consult"
        ? [now, v.company, v.firstname, v.email, v.phone, v.consult_type, v.message, v.page]
        : [now, v.company, v.firstname, v.email, v.phone, v.page];
      sh.appendRow(row.map(safe_));
    } finally {
      lock.releaseLock();
    }

    // 同じメールアドレスからの連続送信（60秒以内）では、メールを送り直さない
    var cache = CacheService.getScriptCache();
    var key = "sent_" + kind + "_" + v.email.toLowerCase();
    if (!cache.get(key)) {
      cache.put(key, "1", 60);
      notify_(kind, v);
      autoReply_(kind, v);
    }
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: "server" });
  }
}

// 動作確認用（ブラウザでウェブアプリのURLを開いたとき）
function doGet() {
  return json_({ ok: true, service: "hitorime-marke forms" });
}

// ===== メール =====
function notify_(kind, v) {
  var label = kind === "consult" ? "無料相談" : "資料請求";
  var lines = [
    label + "のお申し込みがありました。", "",
    "会社名：" + v.company,
    "お名前：" + v.firstname,
    "メールアドレス：" + v.email,
    "電話番号：" + v.phone
  ];
  if (kind === "consult") {
    lines.push("ご相談内容：" + (v.consult_type || "（未選択）"));
    lines.push("ご相談の内容：" + (v.message || "（なし）"));
  }
  lines.push("", "送信元：" + v.page, "記録：" + book_().getUrl());
  MailApp.sendEmail({
    to: CONFIG.NOTIFY_TO,
    subject: "【ひとりめマーケ】" + label + "：" + v.company + " " + v.firstname + "様",
    body: lines.join("\n"),
    replyTo: v.email,
    name: "ひとりめマーケ（サイトのフォーム）"
  });
}

function autoReply_(kind, v) {
  var head = [v.company, v.firstname + " 様", "", "ひとりめマーケの大萱生です。"];
  var body;
  if (kind === "consult") {
    body = head.concat([
      "無料相談のお申し込みをいただき、ありがとうございます。", "",
      "お申し込みの画面で日程をお選びいただいた場合は、カレンダーの招待が別途届きます。",
      CONFIG.BOOKING_URL
        ? "日程がまだの場合は、こちらからご都合のよい日時をお選びください。\n" + CONFIG.BOOKING_URL
        : "日程は、2営業日以内にメールで候補をお送りします。",
      "", "■ お申し込みの内容",
      "ご相談内容：" + (v.consult_type || "（未選択）"),
      "ご相談の内容：" + (v.message || "（なし）")
    ]);
  } else {
    body = head.concat([
      "サービス資料のご請求をいただき、ありがとうございます。", "",
      CONFIG.DOC_URL
        ? "資料は、こちらからご覧いただけます。\n" + CONFIG.DOC_URL
        : "資料は、1営業日以内にこのメールアドレスへお送りします。",
      "", "資料をお送りした後に、こちらから営業のご連絡はいたしません。",
      "ご不明な点やご相談があれば、このメールにそのままご返信ください。"
    ]);
  }
  body = body.concat(signature_());
  MailApp.sendEmail({
    to: v.email,
    subject: kind === "consult" ? "【ひとりめマーケ】無料相談のお申し込みを受け付けました" : "【ひとりめマーケ】サービス資料のご請求ありがとうございます",
    body: body.join("\n"),
    replyTo: CONFIG.NOTIFY_TO,
    name: CONFIG.SENDER_NAME
  });
}

function signature_() {
  return ["", "――――――――――", "ひとりめマーケ（BtoBマーケティング支援・代行）", "大萱生 隼人", CONFIG.NOTIFY_TO, CONFIG.SITE_URL,
    "", "※このメールは、フォームの送信に合わせて自動でお送りしています。"];
}

// ===== 予約の記録とリマインド（1時間ごとのトリガー） =====
function hourly() {
  var cal = CalendarApp.getDefaultCalendar();
  var now = new Date();
  var until = new Date(now.getTime() + 60 * 24 * 3600 * 1000);   // 60日先まで
  var events = cal.getEvents(now, until).filter(function (ev) {
    return ev.getTitle().indexOf(CONFIG.BOOKING_KEYWORD) >= 0 && guests_(ev).length > 0;
  });
  var sh = sheet_(book_(), "booking");
  events.forEach(function (ev) {
    var g = guests_(ev);
    // 予約を記録（1回だけ）
    if (!ev.getTag("hm_logged")) {
      sh.appendRow([now, ev.getStartTime(), g[0].getName() || "", g[0].getEmail(), ev.getTitle(), ""].map(safe_));
      ev.setTag("hm_logged", "1");
    }
    // 前日のリマインド：開始まで REMIND_HOURS_BEFORE 時間を切ったら1回だけ。
    // 開始の直前（同じ時間内）に予約されたものは、カレンダーの招待が届いたばかりなので送らない
    var left = ev.getStartTime().getTime() - now.getTime();
    var bookedAhead = ev.getStartTime().getTime() - ev.getDateCreated().getTime();
    var limit = CONFIG.REMIND_HOURS_BEFORE * 3600 * 1000;
    if (!ev.getTag("hm_reminded") && left > 0 && left <= limit && bookedAhead > limit) {
      g.forEach(function (guest) { remind_(ev, guest); });
      ev.setTag("hm_reminded", "1");
      markReminded_(sh, ev);
    }
  });
}

function remind_(ev, guest) {
  var tz = Session.getScriptTimeZone();
  var when = Utilities.formatDate(ev.getStartTime(), tz, "M月d日（") + "日月火水木金土".charAt(ev.getStartTime().getDay()) +
    Utilities.formatDate(ev.getStartTime(), tz, "）H:mm") + "〜" + Utilities.formatDate(ev.getEndTime(), tz, "H:mm");
  var link = meetLink_(ev);
  var body = [
    (guest.getName() || "ご担当者") + " 様", "",
    "ひとりめマーケの大萱生です。",
    "明日の無料相談のご案内です。", "",
    "■ 日時：" + when,
    "■ 場所：オンライン" + (link ? "\n" + link : "（参加用のリンクは、カレンダーの招待に記載しています）"), "",
    "当日は、現状とお悩みをお聞かせください。事前の準備は不要です。",
    "日時の変更やキャンセルは、このメールにご返信ください。"
  ].concat(signature_());
  MailApp.sendEmail({
    to: guest.getEmail(),
    subject: "【ひとりめマーケ】明日の無料相談のご案内（" + when + "）",
    body: body.join("\n"),
    replyTo: CONFIG.NOTIFY_TO,
    name: CONFIG.SENDER_NAME
  });
}

// Google Meet のリンク。Calendar API（エディタの「サービス」で追加）が無いときは空にする
function meetLink_(ev) {
  try {
    var id = ev.getId().replace(/@google\.com$/, "");
    var r = Calendar.Events.get("primary", id);
    return r.hangoutLink || "";
  } catch (e) {
    return "";
  }
}

function markReminded_(sh, ev) {
  var t = ev.getStartTime().getTime();
  var vals = sh.getDataRange().getValues();
  for (var i = vals.length - 1; i >= 1; i--) {
    if (vals[i][1] instanceof Date && vals[i][1].getTime() === t) {
      sh.getRange(i + 1, 6).setValue(new Date());
      return;
    }
  }
}

function guests_(ev) {
  var me = Session.getEffectiveUser().getEmail().toLowerCase();
  return ev.getGuestList().filter(function (g) { return g.getEmail().toLowerCase() !== me; });
}

// ===== 共通 =====
function book_() {
  var id = PropertiesService.getScriptProperties().getProperty("SHEET_ID") || CONFIG.SHEET_ID;
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function sheet_(ss, kind) {
  var def = SHEETS[kind];
  var sh = ss.getSheetByName(def.name) || ss.insertSheet(def.name);
  if (sh.getLastRow() === 0) {
    sh.appendRow(def.header);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, def.header.length).setFontWeight("bold");
  }
  return sh;
}

function clean_(s, max) {
  return String(s == null ? "" : s).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);
}

// 文字のまま記録する。= + - @ で始まる値を数式にしない、電話番号の先頭の0を消さない
function safe_(x) {
  return typeof x === "string" && /^[=+\-@0-9]/.test(x) ? "'" + x : x;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
