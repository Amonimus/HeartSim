/**
* Refreshes a page and clears POST data.
*/
function Reload(){
    console.log("Reload");
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
    window.location.assign(document.URL);
    if (window.location.hash) {
        window.location.reload();
    } else {
        window.location = window.location.href;
    }
}