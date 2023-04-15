"use strict";


function createHintBlock(width, height) {
    let hintBlock = document.createElement("div");
    hintBlock.style.width = `${width}px`;
    hintBlock.style.height = `${height * 2}px`;
    hintBlock.id = "hint_block";
    return hintBlock;
}


function createHintElement(width, height, movies) {
    let newElement = document.createElement("div");
    newElement.style.width = `${width}px`;
    newElement.style.height = `${height}px`;

    if (movies) {
        newElement.classList.add("hint_element", "chosen-hint_element");
        newElement.id = "movies__hint";
        newElement.innerHTML = "Movies";
    }
    else {
        newElement.className = "hint_element";
        newElement.id = "actors_directors__hint";
        newElement.innerHTML = "Actors and directors";
    }
    return newElement;
}


function isHintBlock() {
    if (document.getElementById("hint_block")) return true;
    return false;
}


function setSearchHandlers(){
    const searchBlock = document.getElementById("search-block");
    const form = document.getElementById("search_form");
    if (form) {
        document.addEventListener("click", handleClick.bind(document, searchBlock));

        const inputTag = form.querySelector("input[name=q]");
        inputTag.addEventListener("focus", handleInputTag.bind(inputTag, form, inputTag));
    }
}


function handleInputTag(form, inputTag) {
    if (!isHintBlock()) {
        let hintBlock = createHintBlock(inputTag.offsetWidth, inputTag.offsetHeight);
        let movieElement = createHintElement(inputTag.offsetWidth, inputTag.offsetHeight, true);
        let actorDirectorElement = createHintElement(inputTag.offsetWidth, inputTag.offsetHeight, false);

        movieElement.addEventListener("click", handleHintElement.bind(movieElement, form, true));
        actorDirectorElement.addEventListener("click", handleHintElement.bind(actorDirectorElement, form, false));

        hintBlock.appendChild(movieElement);
        hintBlock.appendChild(actorDirectorElement);
        form.parentNode.append(hintBlock);
    }
}


function handleHintElement(form, movies, event) {
    let chosenElement = event.target.parentNode.querySelector(".chosen-hint_element");
    if (!chosenElement) {
        event.target.classList.add("chosen-hint_element");
    }
    else if (chosenElement != event.target) {
        chosenElement.classList.remove("chosen-hint_element");
        event.target.classList.add("chosen-hint_element");
    }

    let hiddenInput = form.querySelector("#hidden_search_input");
    if (movies) {
        hiddenInput.value = "Movies";
    }
    else {
        hiddenInput.value = "Actors/Directors";
    }
}


function deleteHintBlock() {
    if (isHintBlock()) {
        document.getElementById("hint_block").remove();
    }
}


function handleClick(searchBlock, event) {
    const rect = searchBlock.getBoundingClientRect();
    let coords = getClickPosition(event);

    if (!((rect.left <= coords.xPosition && coords.xPosition <= rect.right) && (rect.top <= coords.yPosition && coords.yPosition <= rect.bottom))) {
        // if user clicked outside the search block - hint block would be deleted
        deleteHintBlock();
    }
}


function getClickPosition(event) {
    return {
        xPosition: event.clientX,
        yPosition: event.clientY
    }
}


function main() {
    setSearchHandlers();
}


document.addEventListener("DOMContentLoaded", main);
