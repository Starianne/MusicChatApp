const searchList = document.getElementsByClassName('searchItem');
let selectedItems = document.getElementsByClassName('selectedItem');
let storedItems = JSON.parse(sessionStorage.getItem("itemlist")) || [];
let messageContainer = document.querySelector(".messageContainer")
let warningContainer = document.querySelector(".warningContainer")


function changeToRed(e) {
    e.target.closest("button").classList.toggle('filter')
};

function store() {
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

function removeWarning() {
    warningContainer.style.display = "none"
};

function checkSelectionFull() {
    var full = false
    for (let i of selectedItems) {
        if (i.querySelector("p").innerText != "") {
            full = true;
        } else {
            full = false;
            break;
        }   
    }
    return full
};

function checkSelection(toCheckItem) {
    var found = false
    for (let i of selectedItems) {
        if (i.querySelector("p").innerText == toCheckItem.querySelector("p").innerText) {
            found = true
            return found
        }

    }
    return found
};

function submit() {
    var full = checkSelectionFull()
    if (full) {
        //basically pass data to view or model idk yet - clean data? check for song or artist or have parameter? or have separate functions to save for artist and song
        console.log(sessionStorage);
        var itemList = JSON.parse(window.sessionStorage.itemlist)
        console.log(itemList)
    } else {
        var submitMessage = document.createElement("p")
        submitMessage.innerText = "You haven't picked all 5"
        warningContainer.style.display = "block"
        messageContainer.innerHTML = submitMessage.textContent
    }
};


for (let i of selectedItems) {
    let btn = i.querySelector('button')
        i.addEventListener("mouseover", function() {
            if (i.querySelector("p").innerText != "") {
                btn.style.display = "block"
            } else {
                btn.style.display = "none"
            }
        })
        i.addEventListener("mouseout", function() {
            btn.style.display = "none"
        })            

}
//send data to model + do same on artist


for (let item of searchList) {
    item.addEventListener("click", function() {
        var full = checkSelectionFull();
        var found = checkSelection(item);
        messageContainer.innerHTML = "";
        if (found == true ) {
            const message = document.createElement("p");
            message.innerText = "You've already added that one";
            if (messageContainer.innerHTML != message.textContent && full === false) {
                //if checks if there's already a message and selected isnt full 
                messageContainer.innerHTML = message.textContent;
                warningContainer.style.display = "block";
            }
        } else {
            for (let i of selectedItems) { //loops to find empty spot
                if (i.querySelector("p").innerText=="") {
                    i.querySelector("p").innerText = item.querySelector("p").innerText;
                    i.querySelector("img").src = item.querySelector("img").src;
                    warningContainer.style.display = "none"
                    store();
                    break;
                }
            }

            
        }
    })
};



for (let i = 0; i < storedItems.length && i< selectedItems.length; i++) {
    selectedItems[i].querySelector("p").innerText = storedItems[i].title;
    selectedItems[i].querySelector("img").src = storedItems[i].img;
}
