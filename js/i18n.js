/*
 * Язык интерфейса и контента: русский (исходный) и казахский.
 * Строки в коде написаны по-русски и сами служат ключами: T.t('План на сегодня') вернёт перевод из js/kk.js.
 * Смена языка перезагружает страницу: темы, вопросы, уроки и решения подменяются один раз при загрузке.
 */
(function () {
  const T = window.Tamyr;
  const KEY = 'tamyr.lang';
  let lang = null;
  try { lang = localStorage.getItem(KEY); } catch (e) { /* нет хранилища */ }
  if (!lang) lang = (navigator.language || '').toLowerCase().startsWith('kk') ? 'kk' : 'ru';
  const forced = /[?&]lang=(kk|ru)\b/.exec(location.search); // ?lang=kk — для ссылок и тестов
  if (forced) lang = forced[1];
  T.lang = lang === 'kk' ? 'kk' : 'ru';
  document.documentElement.lang = T.lang;

  T.UI_KK = {};              // русская строка → казахская, заполняется в kk.js
  T.i18nMisses = new Set();  // строки без перевода — их проверяет tests-academy.html

  /* Перевод строки интерфейса. p — подстановки для {имя}. Казахский шаблон может не использовать часть подстановок. */
  T.t = function (s, p) {
    let out = s;
    if (T.lang === 'kk') {
      if (Object.prototype.hasOwnProperty.call(T.UI_KK, s)) out = T.UI_KK[s];
      else T.i18nMisses.add(s);
    }
    return p ? out.replace(/\{(\w+)\}/g, (m, k) => (k in p ? p[k] : m)) : out;
  };

  /* Русское склонение после числа. В казахском существительное после числа не меняется. */
  T.plural = function (n, one, few, many) {
    if (T.lang === 'kk') return T.UI_KK[one] || one;
    return n % 10 === 1 && n % 100 !== 11 ? one : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? few : many;
  };

  /* «4 октября» / «4 қазан». Казахские названия месяцев свои: в браузерах их часто нет, и дата выходит как «M10 4». */
  const MONTHS_KK = ['қаңтар', 'ақпан', 'наурыз', 'сәуір', 'мамыр', 'маусым', 'шілде', 'тамыз', 'қыркүйек', 'қазан', 'қараша', 'желтоқсан'];
  T.fmtDate = function (ts) {
    const d = new Date(ts);
    return T.lang === 'kk' ? d.getDate() + ' ' + MONTHS_KK[d.getMonth()] : d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
  };

  T.setLang = function (l) {
    try { localStorage.setItem(KEY, l); } catch (e) { /* нет хранилища */ }
    if (forced) location.search = ''; else location.reload();
  };
})();
