"use strict";


class YearFiltration {
    constructor() {
        this.button = document.querySelector('button.btn.btn-info.filter-year');
        this.genres = document.querySelectorAll('input#filter-genre');
        this.years = document.querySelectorAll('input#filter-year');
    }

    handleChange(obj) {
        obj.button.click();
    }

    setAllHandlers() {
        for (let year of this.years) {
            year.addEventListener('change', this.handleChange.bind(year, this));
        }
        for (let genre of this.genres) {
            genre.addEventListener('change', this.handleChange.bind(genre, this));
        }
    }
}


function main() {
    let yearObj = new YearFiltration();
    yearObj.setAllHandlers();
}


document.addEventListener('DOMContentLoaded', main);
