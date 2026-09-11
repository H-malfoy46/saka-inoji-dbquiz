/*
  ホーム画面に追加したあと、電波がなくても遊べるようにするためのファイル。
  仕組み: 一度読み込んだファイルを端末に保存しておき、次回は保存版をすぐ表示する。
          同時に裏で最新版を取りに行き、次に開いたときに新しい内容へ入れ替える。
  ※ https か localhost で開いたときだけ有効(ブラウザの仕様)。
*/
const CACHE = "sakamichi-quiz-v2";
const ASSETS = [
  "./",
  "./index.html",
  "./quiz_data.js",
  "./manifest.webmanifest",
  "./icons/icon-180.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => Promise.allSettled(ASSETS.map(u => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function save(req, res){
  if (res && res.ok) {
    const copy = res.clone();
    caches.open(CACHE).then(c => c.put(req, copy));
  }
  return res;
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;                    // 報告の送信などは素通し
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // 中身が変わっていくファイル(アプリ本体とデータ)は、まずネットを見に行く。
  // こうしないと、更新しても次に開いたときまで古い版が表示されてしまう。
  const isCore = req.mode === "navigate"
              || url.pathname.endsWith("/index.html")
              || url.pathname.endsWith("/quiz_data.js");

  if (isCore) {
    e.respondWith(
      fetch(req)
        .then(res => save(req, res))
        .catch(() => caches.match(req)                 // オフラインなら保存版
          .then(hit => hit || caches.match("./index.html")))
    );
    return;
  }

  // アイコンなど変わらないものは保存版を優先(表示が速い)
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => save(req, res)))
  );
});
