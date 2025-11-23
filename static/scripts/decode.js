function utf8ToBase64(str) {
    return btoa(unescape(encodeURIComponent(str)));
}

function base64ToUtf8(str) {
    return decodeURIComponent(escape(atob(str)));
}

document.addEventListener("DOMContentLoaded", function(event){
    maskedElements = document.getElementsByClassName("mask");
    if (maskedElements.length > 0) {
        for (let elem of maskedElements) {
            var newHref = atob(elem.getAttribute("href"));
            elem.setAttribute("href", newHref);
        }
    }
});
