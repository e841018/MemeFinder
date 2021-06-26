'use strict';
//==============================================================================
// global objects

// elements
let embed_global;
let embed_document;
let spotlight_background;
let spotlight;
let status;
let skip;

// objects
let quiz; // array of [id, quadrant]
let set_len; // 10
let quiz_idx; // 0, 1, ..., 19

//==============================================================================
// functions

function AnnotateQuery(query) {
    const set = Math.floor(quiz_idx / set_len); // 0 or 1
    query.set = set;
}

function showSpotlight() {
    spotlight_background.style.display= 'block';
}

function hideSpotlight() {
    spotlight_background.style.display = 'none';
}

function clearSpotlight() {
    spotlight.innerHTML = '';
}

function submitOnClick(event) {
    spotlight_background.style.display = 'none';
    const id = Number(spotlight.children[2].src.split('/').pop().split('.')[0]);
    spotlight.innerHTML = '';
    embed_global.socket.emit('submit', [quiz_idx, id]);
    nextQuestion();
}

function skipOnClick(event) {
    if (embed_global.lock_spotlight)
        return;
    embed_global.socket.emit('submit', [quiz_idx, -1]);
    nextQuestion();
}

function nextQuestion() {
    // reset search status
    embed_global.dirty = true;
    embed_global.query_log = [embed_global.query_log[0]];
    embed_global.undo();
    // update quiz_idx
    quiz_idx += 1;
    if (quiz_idx == set_len * 2) {
        finishQuiz();
        return;
    }
    // update UI
    const set = Math.floor(quiz_idx / set_len);
    const idx = quiz_idx % set_len;
    status.innerHTML = `Set ${set + 1}: ${idx + 1}/${set_len}`;
    // show question
    const question = quiz[quiz_idx];
    showQuestion(question[0], question[1]);
}

function showQuestion(id, quadrant) {
    clearSpotlight();
    const img = appendImgToSpotlight(id);
    maskQuadrant(img, quadrant);
    embed_global.lock_spotlight = true;
    showSpotlight();
    img.addEventListener('load', () => {
        setTimeout(() => {
            hideSpotlight();
            clearSpotlight();
            embed_global.lock_spotlight = false;
        }, 1000);
    });
}

function appendImgToSpotlight(id) {
    const img = document.createElement('img');
    img.src = 'img_db/' + id + '.jpg';
    spotlight.append(img);
    return img;
}

function maskQuadrant(img, quadrant) {
    // wrap img with div
    const par = img.parentNode;
    const div = par.insertBefore(document.createElement('div'), img);
    div.style.position = 'relative';
    div.append(img);
    img.style.visibility = 'hidden';
    // create canvas
    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0px';
    canvas.style.left = '0px';
    canvas.style.zIndex = '2';
    div.append(canvas);
    img.addEventListener('load', () => {
        const w = img.width;
        const h = img.height;
        canvas.width = w;
        canvas.height = h;
        let left, top;
        switch(quadrant) {
            case 1:
                left = w/2; top = 0;
                break;
            case 2:
                left = 0;   top = 0;
                break;
            case 3:
                left = 0;   top = h/2;
                break;
            case 4:
                left = w/2; top = h/2;
                break;
        }
        const context = canvas.getContext('2d');
        context.fillRect(left, top, w/2, h/2);
        img.style.visibility = 'visible';
    });
}

function finishQuiz() {
    // cancel registered callbacks
    embed_global.onQuery = () => {};
    embed_global.spotlightOnOpen = () => {};
    skip.onclick = () => {};
    // disable closing spotlight until form is filled
    embed_global.lock_spotlight = true;

    // modify elements
    status.innerHTML = 'Finished';
    skip.remove();
    spotlight.innerHTML =
        '感謝你，測驗結束囉！<br>' +
        '請留下你的聯絡方式<br>' +
        '(email、手機或 Facebook 名字都可以)<br>' +
        '預計於 2021/6/30(三) 公布中獎名單。<br>';
    const contact = document.createElement('input');
    contact.type = 'text';
    contact.id = 'contact';
    contact.value = 'example@gmail.com';
    contact.style.fontSize = '24px';
    contact.style.margin = '5px';
    contact.style.width = '450px';
    const button = document.createElement('input');
    button.type = 'button';
    button.value = 'Submit';
    button.style.fontSize = '24px';
    button.style.margin = '5px';
    button.onclick = (event) => {
        hideSpotlight();
        const contact_value = embed_document.getElementById('contact').value;
        embed_global.socket.emit('finish', contact_value);
        embed_global.lock_spotlight = false;
        clearSpotlight();
    }
    spotlight.append(contact, button);
    showSpotlight();
}

window.onload = function(event) {
    // initialize global objects
    const iframe = document.getElementById('embed-doc');
    embed_document = iframe.contentDocument;
    embed_global = iframe.contentWindow;
    spotlight_background = embed_document.getElementById('spotlight-background');
    spotlight = embed_document.getElementById('spotlight');
    status = document.getElementById('status');
    skip = document.getElementById('skip');

    // modify iframe
    embed_document.getElementById('right-click').innerHTML = 'Right-click on images: Enlarge and <b>show SUBMIT button</b>.';
    embed_global.onQuery = AnnotateQuery;
    embed_global.spotlightOnOpen = () => {
        const submit = document.createElement('input');
        submit.type = 'button';
        submit.value = 'Submit';
        submit.style.fontSize = '24px';
        submit.style.margin = '5px';
        submit.onclick = submitOnClick;
        spotlight.insertBefore(submit, spotlight.children[0]);
    };
    embed_global.socket.on('quiz', function(data) {
        console.log('quiz received');
        quiz = data;
        set_len = quiz.length / 2;
        quiz_idx = -1;
        nextQuestion();
    });

    // start
    spotlight.innerHTML =
        '在開始測驗前，請確認你已經瞭解：<br>' +
        '- Enter 可以送出檢索<br> - Ctrl+Z 可以回到上一步<br>' +
        '- 對圖片按右鍵可以放大圖片跟<b>提交結果</b><br>' +
        '- 可以放大網頁讓圖片更清楚<br>' +
        '<br>' +
        '本次測驗共有 20 個迷因，每個迷因會提示 1 秒，請在最短的時間內使用 MemeFinder 找出那個迷因，對那張圖片按右鍵放大後按下 Submit 按鈕。如果覺得找不到可以按上方的 Skip 按鈕。' +
        '完成所有測驗後，會請你留下聯絡方式，預計於 2021/6/30(三) 公布中獎名單。<br>' +
        '請按框框外的空白處開始測驗。<br>';
    embed_global.spotlightOnClose = () => {
        embed_global.spotlightOnClose = () => {}; // cancel registered callback
        embed_global.socket.emit('start_quiz');
        skip.onclick = skipOnClick;
    };
    showSpotlight();
}