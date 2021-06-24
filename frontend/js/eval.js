'use strict';

let embed_global;
let embed_document;
let spotlight_background;
let spotlight;

function evalAnnotateQuery(query) {
    query.eval = 'yoooo';
}

window.onload = function(event) {
    const iframe = document.getElementById('embed-doc');
    embed_document = iframe.contentDocument;
    embed_global = iframe.contentWindow;
    spotlight_background = embed_document.getElementById('spotlight-background');
    spotlight = embed_document.getElementById('spotlight');

    embed_global.EVAL = true;
    embed_document.getElementById('right-click').innerHTML = 'Right-click on images: Enlarge and <b>show SUBMIT button</b>.';

    const hints =
        '在開始測驗前，請確認你已經瞭解：<br>' +
        '- Enter 可以送出檢索<br> - Ctrl+Z 可以回到上一步<br>' +
        '- 對圖片按右鍵可以放大圖片跟<b>提交結果</b><br>' +
        '- 可以放大網頁讓圖片更清楚<br>' +
        '<br>' +
        '本次測驗共有 20 個迷因，每個迷因會提示 1 秒，請在最短的時間內使用 MemeFinder 找出那個迷因，對那張圖片按右鍵放大後按下 Submit。' +
        '完成所有測驗後，會請你留下聯絡方式，預計於 2021/6/30(三) 公布中獎名單。<br>' +
        '請按框框外的空白處開始測驗。<br>';
    spotlight.innerHTML = hints;
    spotlight_background.style.display= 'block';
}