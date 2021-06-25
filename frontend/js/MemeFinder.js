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
// use var instead of let to allow access from parent
var socket; // socket.io
var dirty = false; // true indicates some inputs has changed since last query
var query_log = [{ // log of all sent queries, shrinks as undo() is called
    'img_query': [],
    'text_query': '',
    'weight': 0.5,
    'n_ranklist': 10,
}];
var onQuery; // called when query is sent
var spotlightOnClose;
var spotlightOnOpen;
var lock_spotlight = false; // prevent user from closing spotlight

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
    dirty = true;
}

function imgBoxOnContextMenu(event) {
    event.stopPropagation();
    event.preventDefault();
    fillSpotlight(this.id, 'Image ID: ' + this.id);
    if (typeof spotlightOnOpen != 'undefined')
        spotlightOnOpen();
    spotlight_background.style.display= 'block';
}

function crossOnClick(event) {
    event.stopPropagation();
    this.parentElement.remove();
}

function undo() {
    if (dirty === false) {
        if (query_log.length == 1) // state is same as initial state
            return;
        else // state is same as last entry in query_log
            query_log.pop();
    }
    const query = query_log[query_log.length - 1];
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
    dirty = false;
}

function documentOnKeydown(event) {
    // console.log('event.KeyCode =', event.keyCode);
    if (event.keyCode == 13) { // enter
        sendQuery();
    }
    if (event.keyCode == 90 && event.ctrlKey) { // Ctrl+Z
        event.preventDefault(); // prevent from focusing on last changed input
        undo();
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
    if (typeof onQuery != 'undefined')
    onQuery(query);
    query_log.push(query);
    socket.emit('query', query);
    console.log('send query:', query);
}

function sliderResultOnInput(event) {
    event.stopPropagation();
    n_result.innerText = this.value;
    dirty = true;
}

function fillSpotlight(id, text='') {
    const br = document.createElement('br');
    const img = document.createElement('img');
    img.src = 'img_db/' + id + '.jpg';
    spotlight.append(text, br, img);
}

function spotlightBackgroundOnClick(event) {
    event.stopPropagation();
    if (lock_spotlight)
        return;
    spotlight_background.style.display = 'none';
    spotlight.innerHTML = '';
    if (typeof spotlightOnClose != 'undefined')
        spotlightOnClose();
}

window.onload = function(event) {
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
    slider_weight.oninput = e => dirty = true;
    text_query.oninput = e => dirty = true;
    document.onkeydown = documentOnKeydown;
    document.getElementById('enter').onclick = sendQuery;
    document.getElementById('undo').onclick = undo;
    spotlight_background.onclick = spotlightBackgroundOnClick;
    spotlight.onclick = e => e.stopPropagation();

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
        query_log[query_log.length - 1].rank_list = data;
        dirty = false;
    });
};