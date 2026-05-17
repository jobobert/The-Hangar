// Global utilities for The Hangar

function searchSelect(searchForID, searchInID) {
    var input = document.getElementById(searchForID).value.toLowerCase();
    var output = document.getElementById(searchInID).options;
    for (var i = 0; i < output.length; i++) {
        if (output[i].text.toLowerCase().indexOf(input) < 0) {
            output[i].style.display = "none";
            output[i].setAttribute('style', 'display:none');
        } else {
            output[i].style.display = "";
            output[i].setAttribute('style', 'display:');
        }
    }
}

function enableButton(id) {
    document.getElementById(id).classList.remove("btn-outline-primary");
    document.getElementById(id).classList.add("btn-primary");
}

function inchToMm(from, to) {
    var inch = document.getElementById(from).value;
    document.getElementById(to).value = inch * 25.4;
}

function gramToOz(from, to) {
    var gram = document.getElementById(from).value;
    document.getElementById(to).value = gram / 28.35;
}

function dm2ToSqin(from, to) {
    var dm2 = document.getElementById(from).value;
    document.getElementById(to).value = dm2 * 15.5;
}

document.addEventListener('DOMContentLoaded', function () {
    var path = window.location.pathname;
    var currentUrl = path + window.location.search;
    var isEditPage = /\/(update|add|edit)[^/]*(\/|$)/.test(path);

    var stack = [];
    try { stack = JSON.parse(sessionStorage.getItem('hangar_nav_stack') || '[]'); } catch (e) {}

    if (!isEditPage) {
        if (stack.length === 0 || stack[stack.length - 1] !== currentUrl) {
            stack.push(currentUrl);
            if (stack.length > 30) stack.shift();
            try { sessionStorage.setItem('hangar_nav_stack', JSON.stringify(stack)); } catch (e) {}
        }
    }

    var canGoBack = isEditPage ? stack.length > 0 : stack.length > 1;
    var goBackWrap = document.getElementById('go-back-wrap');
    if (goBackWrap && canGoBack) goBackWrap.style.display = '';

    var goBackLink = document.getElementById('go-back-link');
    if (goBackLink) {
        goBackLink.onclick = function (e) {
            e.preventDefault();
            var s = [];
            try { s = JSON.parse(sessionStorage.getItem('hangar_nav_stack') || '[]'); } catch (e) {}
            if (isEditPage) {
                if (s.length > 0) window.location.href = s[s.length - 1];
                else history.back();
            } else {
                if (s[s.length - 1] === currentUrl) s.pop();
                if (s.length > 0) {
                    try { sessionStorage.setItem('hangar_nav_stack', JSON.stringify(s)); } catch (e) {}
                    window.location.href = s[s.length - 1];
                } else {
                    history.back();
                }
            }
        };
    }
});

$(document).ready(function () {
    $("textarea:not(.no-markitup)").markItUp(mySettings);
    $('img').on("error", function () {
        $(this).attr('src', window._hangarNopicture || '');
    });
    $('#model-details > table').addClass('table');
    $('.string').addClass('form-control');
    $('select').addClass('form-control');
});
