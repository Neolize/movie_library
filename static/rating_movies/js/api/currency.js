"use strict";


function activate_calendar(calendar_input, text_input) {
    calendar_input.hidden = false;
    text_input.hidden = true;
    
    let date_split = text_input.value.split(".");
    calendar_input.value = `${date_split[2]}-${date_split[1]}-${date_split[0]}`;
}


function main() {
    window.scrollTo(0, 800);

    const form = document.getElementById("date_form");
    const calendar = form.querySelector("input#id_calendar");
    const text = form.querySelector("input#id_calendar_text");
    
    text.addEventListener("click", activate_calendar.bind(text, calendar, text));
    calendar.addEventListener("change", () => form.submit());
}


document.addEventListener("DOMContentLoaded", main);
