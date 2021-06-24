'use strict';
//==============================================================================
// global objects

// elements
let fb_list; // element holding feedback ImgBox elements
let rank_list; // element holding ranked list ImgBox elements
let slider_weight; // element controlling weight
let slider_result; // element controlling n_result
let n_result; // element displaying n_result
let text_query; // element displaying text_query
let spotlight_background;
let spotlight;

// objects
let socket; // socket.io
let query_log = [];

//==============================================================================
// functions

function createImgBox(id) {
    const div = document.createElement('div');
    const img = document.createElement('img');
    const br = document.createElement('br');
    div.className = 'img-box';
    img.src = 'img_db/' + id + '.jpg';
    img.className = 'img-icon';
    div.append(img, br, id);
    div.id = id;
    div.onclick = imgBoxOnClick;
    div.oncontextmenu = imgBoxOnContextMenu;
    return div;
}

function createImgBox_cross(id) {
    const div = createImgBox(id);
    const cross = document.createElement('img');
    cross.className = 'cross';
    cross.src = 'img/cross.png';
    cross.onclick = crossOnClick;
    div.append(cross);
    return div;
}

function imgBoxOnClick(event) {
    event.stopPropagation();
    const new_id = this.id; // string
    for (let el of fb_list.children)
        if (el.id == new_id)
            return;
    const div = createImgBox_cross(new_id)
    fb_list.insertBefore(div, fb_list.firstChild);
}

function imgBoxOnContextMenu(event) {
    event.stopPropagation();
    event.preventDefault();
    fillSpotlight(this.id, 'Image ID: ' + this.id);
    spotlight_background.style.display= 'block';
}

function crossOnClick(event) {
    event.stopPropagation();
    this.parentElement.remove();
}

function documentOnKeydown(event) {
    // console.log('event.KeyCode =', event.keyCode);
    if (event.keyCode == 13) { // enter
        sendQuery();
    }
    if (event.keyCode == 90 && event.ctrlKey) { // Ctrl+Z
        event.preventDefault(); // prevent from focusing on last changed input
        if (query_log.length > 0) {
            const query = query_log.pop();
            fb_list.innerHTML = '';
            for (let id of query.img_query)
                fb_list.append(createImgBox_cross(id));
            text_query.value = query.text_query;
            slider_weight.value = query.weight;
            slider_result.value = query.n_ranklist;
            n_result.innerText = query.n_ranklist;
            rank_list.innerHTML = '';
            for (let id of query.rank_list)
                rank_list.append(createImgBox(id));
        }
    }
}

function sendQuery() {
    const query_list = [];
    for (let el of fb_list.children) {
        query_list.push(Number(el.id));
    }
    const query = {
        'img_query': query_list,
        'text_query': text_query.value,
        'weight': Number(slider_weight.value),
        'n_ranklist': Number(slider_result.value),
    }
    query_log.push(query);
    socket.emit('query', query);
    console.log('send query:', query);
}

function sliderResultOnInput(event) {
    event.stopPropagation();
    n_result.innerText = this.value;
}

function fillSpotlight(id, text='') {
    const br = document.createElement('br');
    const img = document.createElement('img');
    img.src = 'img_db/' + id + '.jpg';
    img.className = 'img-spotlight';
    spotlight.append(text, br, img);
}

function spotlightBackgroundOnClick(event) {
    event.stopPropagation();
    spotlight_background.style.display = 'none';
    spotlight.innerHTML = '';
}

window.onload = function() {
    // elements
    fb_list = document.getElementById('fb-list');
    rank_list = document.getElementById('rank-list');
    slider_weight = document.getElementById('slider-weight');
    slider_result = document.getElementById('slider-result');
    n_result = document.getElementById('n-result');
    text_query = document.getElementById('text-query');
    spotlight_background = document.getElementById('spotlight-background');
    spotlight = document.getElementById('spotlight');

    // callbacks
    slider_result.oninput = sliderResultOnInput;
    document.onkeydown = documentOnKeydown;
    spotlight_background.onclick = spotlightBackgroundOnClick;
    spotlight.onclick = event => event.stopPropagation();

    // socket
    socket = io();
    socket.on('connect', function() {
        console.log('socket connected');
    });
    socket.on('disconnect', function() {
        console.log('socket disconnected');
    });
    socket.on('rank_list', function(data) {
        console.log('ranked list received:', data);
        rank_list.innerHTML = '';
        for (let id of data)
            rank_list.append(createImgBox(id));
        if (query_log.length > 0)
            query_log[query_log.length - 1].rank_list = data;
    });
};

/*
TODOs:
 * right click to enlarge image
*/