"use strict";


function createSortTag(ascending = true) {
    let sortTag = document.createElement("span");
    sortTag.id = "sort";
    if(ascending === true) {
        sortTag.className = "crypto_currency_sort__ascending";
    }
    else {
        sortTag.className = "crypto_currency_sort__descending";
    }
    return sortTag;
}


class Sorting {
    constructor(form, hiddenInput) {
        this.form = form;
        this.hiddenInput = hiddenInput;
        this.table = document.querySelector("table.crypto_currency_table");
        this.allTitleTags = this.table.querySelectorAll("th");
        this.currentSortTag = null;
    }

    findSpanSortNumber(target) {
        for(let iter = 0; iter < this.allTitleTags.length; iter++) {
            const titleTag = this.allTitleTags[iter].querySelector("span");
            if(titleTag === this.getContentTag(target)) {
                return iter;
            }
        }
    }

    getContentTag(target) {
        if(target.className === "crypto_currency_table_column__block") {
            return target.querySelector("span");
        }
        else if(target.id === "sort") {
            return target.parentNode;
        }
        return target;
    }

    appendSortTag(tagNumber) {
        let currentTag = this.allTitleTags[tagNumber].querySelector("span");
        currentTag.className = "crypto_currency_table_column__content";
        currentTag.appendChild(this.currentSortTag);
    }

    static sendSort(obj, event) {
        let sortArr = obj.hiddenInput.value.split(":");
        if(sortArr[0] === "ascending") {
            sortArr[0] = "descending";
        }
        else {
            sortArr[0] = "ascending";
        }
        sortArr[1] = String(obj.findSpanSortNumber(event.target));
        obj.hiddenInput.value = sortArr.join(":");
        obj.form.submit();
    }

    setSortTag() {
        let sortArr = this.hiddenInput.value.split(":");
        if(sortArr[0] === "ascending") {
            this.currentSortTag = createSortTag();
        }
        else {
            this.currentSortTag = createSortTag(false);
        }
        this.appendSortTag(Number(sortArr[1]));
    }

    appendSort() {
        for(let titleTag of this.allTitleTags) {
            let titleBlock = titleTag.querySelector("div.crypto_currency_table_column__block");
            titleBlock.addEventListener("click", Sorting.sendSort.bind(titleBlock, this))
        }
    }

    initiateSort() {
        this.setSortTag();
        this.appendSort();
    }
}


function main() {
    window.scrollTo(0, 800);
    const form = document.getElementById("crypto_currency_form");

    if(form) {
        const hiddenInput = form.querySelector("input[name=sorting]");
        const tagSelect = form.querySelector("select.select_crypto_currency");

        tagSelect.addEventListener("change", () => {
            form.submit();
        });

        let instanceSorting = new Sorting(form, hiddenInput);
        instanceSorting.initiateSort();
    }
}


document.addEventListener("DOMContentLoaded", main);
