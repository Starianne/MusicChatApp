const searchList = document.getElementsByClassName('searchItem');
let selectedItems = document.getElementsByClassName('selectedItem');
let storedItems = JSON.parse(sessionStorage.getItem("itemlist")) || [];

function changeToRed(e) {
    e.target.closest("button").classList.toggle('filter')
}

function store() {
    let itemUpdate = [];
    for (let s of selectedItems) {
        itemUpdate.push({
            title: s.querySelector("p").innerText,
            img: s.querySelector("img").src
        });
    }

    sessionStorage.setItem("itemlist", JSON.stringify(itemUpdate));  
}

function removeItem(e) {
    var currentDiv = e.target.closest(".selectedItem")
    currentDiv.querySelector("p").innerText=""
    currentDiv.querySelector(".selectedItemImg").src=""

    store()
}

function submit() {
    var full = false
    for (let i of selectedItems) {
        if (i.querySelector("p").innerText != "") {
            full = true;
        } else {
            full = false;
            break;
        }   
    }
    if (full) {
        //basically pass data to view or model idk yet - clean data? check for song or artist or have parameter? or have separate functions to save for artist and song
    } else {
        //write error message "you haven't picked your top 5"
    }
}

for (let i of selectedItems) {
    let btn = i.querySelector('button')
        i.addEventListener("mouseover", function() {
            if (i.querySelector("p").innerText != "") {
                btn.style.display = "inline"
            } else {
                btn.style.display = "none"
            }
        })
        i.addEventListener("mouseout", function() {
            btn.style.display = "none"
        })            

}


//send data to model + do same on artist
let messageContainer = document.querySelector(".messageContainer")

for (let item of searchList) {
    item.addEventListener("click", function() {
        for (let selected of selectedItems) {
            messageContainer.innerHTML = ""
            if (selected.querySelector("p").innerText != item.querySelector("p").innerText) {
                if (selected.querySelector("p").innerText == "") {
                    selected.querySelector("p").innerText = item.querySelector('p').innerText;
                    selected.querySelector("img").src = item.querySelector('img').src;
                    store();
                    break; //required
                }

            } else {
                const message = document.createElement('p');
                message.innerText = "You've already added that one";
                if (messageContainer.innerHTML != message.textContent && selectedItems[4].querySelector("p").innerText == "") {
                    //if checks if there's already a message and selected isnt full 
                    messageContainer.innerHTML = message.textContent
                } 
                break;
            }
        }
    });
}

for (let i = 0; i < storedItems.length && i< selectedItems.length; i++) {
    selectedItems[i].querySelector("p").innerText = storedItems[i].title;
    selectedItems[i].querySelector("img").src = storedItems[i].img;
}

