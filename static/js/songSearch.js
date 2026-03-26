let selectedItems = document.getElementsByClassName('selectedItem');

function storeSong() {
    let itemUpdate = [];
    for (let s of selectedItems) {
        itemUpdate.push({
            songTitle: s.querySelector(".songTitle").innerText,
            songArtist: s.querySelector(".songArtist").innerText,
            img: s.querySelector("img").src
        });
    }

    sessionStorage.setItem("itemlist", JSON.stringify(itemUpdate));  
}

function removeItem(e) {
    var currentDiv = e.target.closest(".selectedItem")
    currentDiv.querySelector("p").innerText=""
    currentDiv.querySelector(".selectedItemImg").src=""

    storeSong()
};