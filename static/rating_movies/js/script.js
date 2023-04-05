"use strict";

import Hogan from 'hogan.js';


const HTML = '\
{{#movies}}\
    <div class="col-md-4 product-men">\
        <div class="product-shoe-info editContent text-center mt-lg-4">\
            <div class="men-thumb-item">\
                <img src="/media/{{ poster }}" class="img-fluid" alt="">\
            </div>\
            <div class="item-info-product">\
                <h4 class="">\
                    <a href="/movie/{{ url }}" class="editContent">{{ title }}</a>\
                </h4>\
                <div class="product_price">\
                    <div class="grid-price">\
                        <span class="money editContent">{{ tagline }}</span>\
                    </div>\
                </div>\
                <ul class="stars">\
                    <li><a href="#"><span class="fa fa-star" aria-hidden="true"></span></a></li>\
                    <li><a href="#"><span class="fa fa-star" aria-hidden="true"></span></a></li>\
                    <li><a href="#"><span class="fa fa-star-half-o" aria-hidden="true"></span></a></li>\
                    <li><a href="#"><span class="fa fa-star-half-o" aria-hidden="true"></span></a></li>\
                    <li><a href="#"><span class="fa fa-star-o" aria-hidden="true"></span></a></li>\
                </ul>\
            </div>\
        </div>\
    </div>\
{{/movies}}'


function renderMovies(data) {
    // Рендер шаблона
    let template = Hogan.compile(HTML);
    let output = template.render(data);

    const div = document.querySelector('.left-ads-display>.row');
    div.innerHTML = output;
}


function ajaxSend(url, params) {
    fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(json => renderMovies(json))
        .catch(error => console.error(error))
}


function deletePagination() {
    const pagination = document.getElementById("pagination");
    if (pagination) pagination.remove();
}


class JsonFilter {
    constructor(preferences) {
        this.preferences_block = preferences;
        this.form = document.getElementById("filter");
        this.main_page = document.getElementById("main_page");
    }

    initiateJsonFilter() {
        if(!this.main_page && this.preferences_block) {
            this.preferences_block.hidden = true;
        }
        else if(this.form) {
            this.genres = this.form.querySelectorAll("input#filter-genre");
            this.years = this.form.querySelectorAll("input#filter-year");

            this.setFilterFormHandlers();
        }
    }

    setFilterFormHandlers() {
        for (const genre of this.genres) {
            genre.addEventListener("change", this.handleCheckedCheckbox.bind(genre, this));
        }
        for (const year of this.years) {
            year.addEventListener("change", this.handleCheckedCheckbox.bind(year, this));
        }
    }

    handleCheckedCheckbox(obj) {
        if (!obj.isOneGenreFilled() && !obj.isOneYearFilled()) {
            window.location.reload(); // reload the page
        }
        let url = obj.form.action;
        let params = new URLSearchParams(new FormData(obj.form)).toString();

        if (!params) params = "genre=0&year=0";
        ajaxSend(url, params);
    
        deletePagination();
    }

    isOneGenreFilled() {
        for (const genre of this.genres) {
            if (genre.checked) return true;
        }
        return false;
    }

    isOneYearFilled() {
        for (const year of this.years) {
            if (year.checked) return true;
        }
        return false;
    }
}


class SortingMovies {
    constructor(preferences) {
        this.sortingForm = preferences.querySelector("form[name=sorting-movies]");
        this.sortingList = preferences.querySelector(".sorting-list");
        this.sortingItems = preferences.querySelectorAll(".sorting-list > li");

        this.sortingClassAsc = "sorting-list-item__ascending";
        this.sortingClassDesc = "sorting-list-item__descending";
    }

    setSortingHandlers() {
        for (const sortingItem of this.sortingItems) {
            sortingItem.addEventListener("click", this.handleSortingItem.bind(sortingItem, this));
        }
    }

    handleSortingItem(obj, event) {
        let url = obj.sortingForm.action;
        let params = `${event.target.dataset.sortingId}&sorting_order=${event.target.dataset.sortingOrder}`;
        ajaxSend(url, params);

        let itemNumber = params.split("=")[1];
        if (itemNumber !== "4") obj.changeSortingOrder(event.target);

        deletePagination();
    }

    changeSortingOrder(listItem) {
        if (listItem.classList.length === 0) {
            listItem.dataset.sortingOrder = "ascending";
            listItem.classList.add(this.sortingClassDesc);
            return;
        }
        if (listItem.dataset.sortingOrder === "ascending") {
            listItem.dataset.sortingOrder = "descending";

            listItem.classList.remove(this.sortingClassDesc);
            listItem.classList.add(this.sortingClassAsc);
        }
        else {
            listItem.dataset.sortingOrder = "ascending";

            listItem.classList.remove(this.sortingClassAsc);
            listItem.classList.add(this.sortingClassDesc);
        }
    }

    initiateSorting() {
        this.setSortingHandlers();
    }
}


function sendRating() {
    const rating = document.querySelector('form[name=rating]');

    if (rating) {

        rating.addEventListener('change', function(event) {
            let data = new FormData(this);
            fetch(`${this.action}`, {
                method: 'POST',
                body: data,
            })
            .then(response => alert('Рейтинг установлен'))
            .catch(error => alert('Произошла ошибка'))
        });
    }
}


function sendPassword() {
    const form = document.querySelector("form[name=generate_password]");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        let url = form.action;
        let params = new FormData(form);

        fetch(`${url}`, {
            method: "POST",
            body: params,
        })
        .then(response => response.json())
        .then(json => renderPassword(json))
        .catch(error => console.error(error))
    });
}


function renderPassword(data) {
    const html = '\
    {{#password}}\
        <div class="random_password_title">\
            Generated password:\
            <p style="color: black;">{{ password }}</p>\
        </div>\
    {{/password}}'
    let template = Hogan.compile(html);
    let output = template.render(data);

    const passwordBlock = document.getElementById("generated_password_block");

    if(passwordBlock.classList.length === 0) {
        passwordBlock.classList.add("generated_password_block");
    }
    passwordBlock.innerHTML = output;
}


function showRandomPasswordPage() {
    const randomPasswordBlock = document.getElementById("random_password");
    if (randomPasswordBlock) {
        window.scrollTo(0, 800);
        sendPassword();
    }
}


class UserEmail {

    verifyUserEmail(instance, event) {
        const emailInput = event.target.querySelector('input#id_email');
        let userEmail = emailInput.value;

        if(!/[\w._-]+@[\w]+\.[a-z]{2,4}$/.test(userEmail)) {
            event.preventDefault();

            if(!instance.isAlert()) {
                let alertBlock = instance.createAlert();
                event.target.after(alertBlock);
            }
        }
    }

    createAlert() {
        let newElement = document.createElement('div');
        newElement.classList.add('alert', 'alert-danger');
        newElement.innerHTML = 'Enter a valid email address.';
        newElement.style.width = '336px';
        return newElement;
    }

    isAlert() {
        if(document.getElementById('footer_block').querySelector('div.alert.alert-danger')) return true;
        return false;
    }

    initiateUserEmailHandler() {
        const form = document.getElementById('form_mailing');

        if(form) {
            form.addEventListener('submit', this.verifyUserEmail.bind(form, this));
        }
    }
}


function setLanguage() {
    const languageForm = document.querySelector('div.set_language > form');

    if(languageForm) {
        const languageSelection = document.querySelector('select.select_language');

        languageSelection.addEventListener('change', function() {
        languageForm.submit();
        });
    }
}


function main() {
    const preferences = document.getElementById("preferences");

    if (preferences) {
        let jsonFilterInstance = new JsonFilter(preferences);
        jsonFilterInstance.initiateJsonFilter();

        let sorting = new SortingMovies(preferences);
        sorting.initiateSorting();
    }

    sendRating();

    let userEmailInstance = new UserEmail();
    userEmailInstance.initiateUserEmailHandler();

    setLanguage();
    showRandomPasswordPage();
}


document.addEventListener('DOMContentLoaded', main);
