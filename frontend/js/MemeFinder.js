'use strict';
//==============================================================================
// global objects

let fb_list; // element holding feedback ImgBox elements
let rank_list; // element holding ranked list ImgBox elements
let slider_result; // element controlling n_result
let n_result; // element displaying n_result
let text_query; // element displaying text_query
let socket; // socket.io

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
    return div;
}

function imgBoxOnClick(event) {
    event.stopPropagation();
    const new_id = this.id; // string
    for(let el of fb_list.children) {
        if(el.id == new_id)
            return;
    }
    const div = createImgBox(new_id);
    const cross = document.createElement('img');
    cross.className = 'cross';
    cross.src = 'img/cross.png';
    cross.onclick = crossOnClick;
    div.append(cross);
    fb_list.insertBefore(div, fb_list.firstChild);
}

function crossOnClick(event) {
    event.stopPropagation();
    this.parentElement.remove();
}

function documentOnKeydown(event) {
    console.log('event.KeyCode =', event.keyCode);
    if (event.keyCode == 13) { // enter
        sendQuery();
    }
}

function sendQuery() {
    const query_list = [];
    for(let el of fb_list.children) {
        query_list.push(Number(el.id));
    }
    const n_ranklist = Number(slider_result.value);
    const query = {'img_query': query_list, 'text_query': text_query.value, 'n_ranklist': n_ranklist}
    socket.emit('query', query);
    console.log('send query:', query);
}

function sliderResultOnInput(event) {
    n_result.innerText = this.value;
}

window.onload = function() {
    fb_list = document.getElementById('fb-list');
    rank_list = document.getElementById('rank-list');
    slider_result = document.getElementById('slider-result');
    n_result = document.getElementById('n-result');
    text_query = document.getElementById('text-query')
    slider_result.oninput = sliderResultOnInput;
    document.onkeydown = documentOnKeydown;

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
        rank_list.textContent = '';
        for(let id of data) {
            rank_list.append(createImgBox(id));
        }
    });
};

/*
TODOs:
 * right click to enlarge image
*/