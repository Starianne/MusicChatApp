let selectedItems = document.getElementsByClassName('selectedItem');

function storeArtist() {
    let itemUpdate = [];
    for (let s of selectedItems) {
        itemUpdate.push({
            title: s.querySelector("p").innerText,
            img: s.querySelector("img").src
        });
    }

    sessionStorage.setItem("itemlist", JSON.stringify(itemUpdate));  
};

function removeItem(e) {
    var currentDiv = e.target.closest(".selectedItem")
    currentDiv.querySelector("p").innerText=""
    currentDiv.querySelector(".selectedItemImg").src=""

    store()
};