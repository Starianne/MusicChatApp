const searchList = document.getElementsByClassName('searchItem');
let selectedItems = document.getElementsByClassName('selectedItem');
let storedItems = JSON.parse(sessionStorage.getItem("songlist")) || [];
let messageContainer = document.querySelector(".messageContainer")
let warningContainer = document.querySelector(".warningContainer")


function changeToRed(e) {
    e.target.closest("button").classList.toggle('filter')
};

function removeWarning() {
    warningContainer.style.display = "none"
};

function storeSong() {
    let songSelectionUpdate = [];
    for (let s of selectedItems) {
        console.log(s)
        songSelectionUpdate.push({
            songId: s.id,
            songTitle: s.querySelector(".selectedSongTitle").innerText,
            songArtist: s.querySelector(".selectedSongArtist").innerText,
            songImg: s.querySelector(".selectedItemImg").src
        });
    }

    sessionStorage.setItem("songlist", JSON.stringify(songSelectionUpdate));  
};

function removeItem(e) {
    var currentDiv = e.target.closest(".selectedItem")
    currentDiv.id = ""
    currentDiv.querySelector(".selectedSongTitle").innerText=""
    currentDiv.querySelector(".selectedSongArtist").innerText=""
    currentDiv.querySelector(".selectedItemImg").src=""
    storeSong()
};



function checkSelectionFull() {
    var full = false
    for (let i of selectedItems) {
        if (i.id != "") {
            full = true;
        } else {
            full = false;
            break;
        }   
    }
    return full
};

function checkSelection(toCheckItem) {
    var found = false;
    for (let i of selectedItems) {
        if (i.querySelector(".selectedSongTitle").innerText == toCheckItem.querySelector(".searchSongTitle").innerText && i.querySelector(".selectedSongArtist").innerText == toCheckItem.querySelector(".searchSongArtist").innerText) {
            //if checks songs' title and artist are the same
            found = true;
            return found;
        }

    }
    return found
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie != "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function sendSongs() {
    const csrftoken = getCookie("csrftoken");
    try {
        const url = "/account/get_selection/";
        const response = await fetch(url, {
            method: "POST",
            headers: {
                'Content-type' : 'application/json',
                "X-CSRFToken" : csrftoken
            },
            body: JSON.stringify({
                song_list: JSON.parse(sessionStorage.getItem("songlist"))
            })
        })

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        const data = await response.json();
        console.log(data.message);
    } catch (error) {
        console.log(error)
    }
}

async function submit() {
    var full = checkSelectionFull()
    if (full) {
        //basically pass data to view or model 
        console.log(sessionStorage);
        var songList = JSON.parse(window.sessionStorage.songlist);
        console.log(songList);
        await sendSongs();
        for (let i of selectedItems) {
            i.id = "";
            i.querySelector(".selectedSongTitle").innerText="";
            i.querySelector(".selectedSongArtist").innerText="";
            i.querySelector(".selectedItemImg").src="";
            storeSong();
            window.location.href = '/chat/find/'
        }

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
            if (i.querySelector(".selectedSongTitle").innerText != "") {
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

//fix two functions under then fix artist

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
                if (i.querySelector(".selectedSongTitle").innerText=="") {
                    i.id = item.id
                    i.querySelector(".selectedSongTitle").innerText = item.querySelector(".searchSongTitle").innerText;
                    i.querySelector(".selectedSongArtist").innerText = item.querySelector(".searchSongArtist").innerText;
                    i.querySelector(".selectedItemImg").src = item.querySelector(".searchItemImg").src;
                    warningContainer.style.display = "none"
                    storeSong();
                    break;
                }
            }

            
        }
    })
};



for (let i = 0; i < storedItems.length && i< selectedItems.length; i++) {
    selectedItems[i].id = storedItems[i].songId
    selectedItems[i].querySelector(".selectedSongTitle").innerText = storedItems[i].songTitle;
    selectedItems[i].querySelector(".selectedSongArtist").innerText = storedItems[i].songArtist;
    selectedItems[i].querySelector("img").src = storedItems[i].songImg;
}




