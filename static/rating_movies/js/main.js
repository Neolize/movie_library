"use strict";


function addReview(name, id, event) {
    let form = document.querySelector('form#formReview');
    let textarea = form.querySelector('textarea#contactcomment'); 

    form.querySelector('input#contactparent').value = id;
    textarea.value = `${name}, `;
    textarea.focus();
    event.preventDefault();
}



function askUserAboutDeleting(event) {
    let userAnswer = confirm('Are you sure that you want to delete this actor/director?');
    if (!userAnswer) {
        event.preventDefault();
    }
}


function setActiveHeader() {
    if(document.getElementById("main_page")) {  
        let mainOption = document.getElementById("main_option");
        mainOption.classList.add("active");
    }
}


class MenuPopup {
    constructor() {
        this.popupLink = document.getElementById("menu_popup-link");
        this.body = document.querySelector("body");
        this.lockedPadding = document.querySelectorAll(".locked-padding");

        this.unlock = true;
        this.timeout = 700;
    }

    openPopup(popup) {
        if (popup && this.unlock) {
            const popupActive = document.querySelector(".menu_popup.open");

            if (popupActive) {
                this.closePopup(popupActive);
            }
            else {
                this.blockBody();
            }

            popup.classList.add("open");
            popup.addEventListener("click", (event) => {
                if (!event.target.closest(".menu_popup__content")) {
                    this.closePopup(event.target.closest(".menu_popup"));
                }
            });
        }
    }

    closePopup(popup, doUnlock = true) {
        if (this.unlock) {
            popup.classList.remove("open");

            if (doUnlock) {
                this.unblockBody();
            }
        }
    }

    blockBody() {
        const lockedPaddingValue = window.innerWidth - document.querySelector("body").offsetWidth + "px";

        if (this.lockedPadding.length > 0) {
            for (const element of this.lockedPadding) {
                element.style.paddingRight = lockedPaddingValue;
            }
        }
        this.body.style.paddingRight = lockedPaddingValue;
        this.body.classList.add("lock");

        this.unlock = false;
        setTimeout(() => {
            this.unlock = true;
        }, this.timeout);
    }

    unblockBody() {
        setTimeout(() => {
            if (this.lockedPadding.length > 0) {
                for (const element of this.lockedPadding) {
                    element.style.paddingRight = "0px";
                }
            }
            this.body.style.paddingRight = "0px";
            this.body.classList.remove("lock");

        }, this.timeout);

        this.unlock = false;
        setTimeout(() => {
            this.unlock = true;
        }, this.timeout);
    }

    closeWithKeyboard() {
        document.addEventListener("keydown", (event) => {
            if (event.code === "Escape") {
                this.closePopup(document.querySelector(".menu_popup.open"));
            }
        });
    }

    initiateMenuPopup() {
        this.popupLink.addEventListener("click", (event) => {
            const popupName = this.popupLink.getAttribute("href").replace("#", "");

            this.openPopup(document.getElementById(popupName));
            event.preventDefault();
        });

        let popupClosingElements = document.querySelectorAll(".close-menu_popup");

        if (popupClosingElements.length > 0) {
            for (const closingElement of popupClosingElements) {
                closingElement.addEventListener("click", (event) => {
                    this.closePopup(closingElement.closest(".menu_popup"));
                    event.preventDefault();
                });
            }
        }
        this.closeWithKeyboard();
    }
}


class Scroll {
    constructor() {
        this.scroll = document.getElementById("page_scroll");
        this.scrollState = "up";
        this.scrollByUser = true;
        this.scrollTop = 0;
        this.topBorder = 350;

        this.scrollTime = 550;
        this.scrollDifference = 1000;

        this.nextScrollY = this.scrollTop;
        this.previousScrollY = this.scrollTop;

        this.classScrollUp = "scroll_block__up";
        this.classScrollDown = "scroll_block__down";
    }

    changeScrollToTop() {
        this.scrollState = "up";

        if (this.scroll.classList.contains(this.classScrollDown)) {
            this.scroll.classList.remove(this.classScrollDown);
            this.scroll.classList.add(this.classScrollUp);
        }
    }

    hideScroll(startHeight, endingHeight) {
        const differenceHeightIndex = Math.ceil(Math.abs(endingHeight - startHeight) / this.scrollDifference);

        this.scroll.style.display = "none";
        setTimeout(() => {
            this.scroll.style.display = "block";
        }, this.scrollTime * differenceHeightIndex);
    }

    moveToTop(scrollValue) {
        window.scrollTo(0, this.scrollTop);
        this.hideScroll(scrollValue, this.scrollTop);

        this.nextScrollY = this.scrollTop;
        this.previousScrollY = scrollValue;
        this.scrollState = "down";
        
        this.scroll.classList.remove(this.classScrollUp);
        this.scroll.classList.add(this.classScrollDown);
    }

    moveToBottom() {
        window.scrollTo(0, this.previousScrollY);
        this.hideScroll(this.scrollTop, this.previousScrollY);

        this.nextScrollY = this.previousScrollY;
        this.previousScrollY = this.scrollTop;
        this.scrollState = "up";

         this.scroll.classList.remove(this.classScrollDown);
         this.scroll.classList.add(this.classScrollUp);
    }

    static scrollPage(obj) {
        const currentScrollY = window.scrollY;

        if (currentScrollY === obj.nextScrollY) {
            obj.scrollByUser = true;
        }

        if (currentScrollY < obj.topBorder) {
            if (obj.scrollByUser === false && currentScrollY === 0) {
                obj.scrollByUser = true;
            }
            else if (obj.scrollByUser === true) {
                obj.scroll.style.display = "none";
            }
        }

        else if (currentScrollY >= obj.topBorder) {
            if (obj.scroll.style.display === "none" && obj.scrollByUser === true) {
                obj.scroll.style.display = "block";
            }
            if (obj.scrollState === "down" && obj.scrollByUser === true) {
                obj.changeScrollToTop();
            }
        }
    }

    static clickOnScroll(obj) {
        obj.scrollByUser = false;

        if (obj.scrollState === "up" && window.scrollY >= obj.topBorder) {
            obj.moveToTop(window.scrollY);
        }
        else if(obj.scrollState === "down") {
            obj.moveToBottom();
        }
    }

    initiateScroll() {
        this.scroll.addEventListener("click", Scroll.clickOnScroll.bind(this.scroll, this));
        window.addEventListener("scroll", Scroll.scrollPage.bind(window, this));
    }
}


function main() {
    setActiveHeader();

    let menuPopupInstance = new MenuPopup();
    menuPopupInstance.initiateMenuPopup();

    let pageScroll = new Scroll();
    pageScroll.initiateScroll();
}


document.addEventListener("DOMContentLoaded", main);


