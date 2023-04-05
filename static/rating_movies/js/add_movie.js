"use strict";


function getInputNumbersValue(input) {
    return input.value.replace(/\D/g, '');
}


class WorldPremiereForm {
    constructor(field) {
        this.field = field;
        this.button = document.querySelector('div.add_form > form > button.btn.btn-success');
    }
    static handleInput(obj, event) {
        let inputNumbersValue = getInputNumbersValue(obj.field),
            input = obj.field,
            selectionStart = input.selectionStart;

        if (!inputNumbersValue) {
            input.value = '';
            return;
        }

        if (input.value.length !== selectionStart) {
            if (event.data && /\D/g.test(input.data)) {
                input.value = inputNumbersValue;
            }
            return;
        }

        WorldPremiereForm.formatDateInput(inputNumbersValue, input);
    }

    static formatDateInput(inputNumbersValue, input) {
        let formattedInputValue = '',
            inputLength = inputNumbersValue.length;

        if (inputLength < 5) {
            formattedInputValue += inputNumbersValue;
        }
        if (inputLength >= 5) {
            formattedInputValue += inputNumbersValue.substring(0, 4) + '-' + inputNumbersValue.substring(4, 6);
        }
        if (inputLength >= 7) {
            formattedInputValue += '-' + inputNumbersValue.substring(6, 8);
        }
        input.value = formattedInputValue;
    }

    static handlePaste(obj, event) {
        let pasted = event.clipboardData || window.clipboardData,
            input = obj.field,
            inputNumbersValue = getInputNumbersValue(input);
        
        if (pasted) {
            let pastedText = pasted.getData('Text');
            
            if(/\D/g.test(pastedText)) {
                input.value = inputNumbersValue;
            }
        }
    } 

    setAllHandlers() {
        this.field.addEventListener('input', WorldPremiereForm.handleInput.bind(this.field, this));
        this.field.addEventListener('paste', WorldPremiereForm.handlePaste.bind(this.field, this));
        this.field.addEventListener('blur', WorldPremiereForm.handleInput.bind(this.field, this));
    }
}


class MovieForm {
    constructor(form) {
        this.budget = form.querySelector('input#id_budget');
        this.feesInUSA = form.querySelector('input#id_fees_in_usa');
        this.feesInWorld = form.querySelector('input#id_fees_in_world');
        this.worldPremiereInput = new WorldPremiereForm(form.querySelector('input#id_world_premiere'));
        this.category = form.querySelector('select#id_category');

        this.button = form.querySelector('button.btn.btn-success.btn-block');
    }

    static handleInput(obj, field, event) {
        let inputNumbersValue = getInputNumbersValue(field),
            selectionStart = field.selectionStart;

        if (!inputNumbersValue) {
            field.value = '';
            return;
        }

        if (field.value.length !== selectionStart) {
            if(event.data && /\D/g.test(event.data)) {
                field.value = inputNumbersValue;
            }
            return;
        }

        obj.formatBigNumberInput(field);
    }

    formatBigNumberInput(field) {
        if (field.value.length >= 4) {
            let inputNumbersValue = getInputNumbersValue(field),
                sections = inputNumbersValue.length % 3,
                formattedInputValue = '';
            
            switch (sections) {
                case 1: 
                    formattedInputValue += inputNumbersValue[0];
                    for (let iter = 1; iter <= inputNumbersValue.length; iter += 3) {
                        const other = inputNumbersValue.substring(iter, iter + 3);  // берём три последующие цифры
                        if (other) {  // если цифры ещё есть - форматируем
                            formattedInputValue += ` ${inputNumbersValue.substring(iter, iter + 3)}`;
                        }
                        else break;
                    }
                    break;
                case 2: 
                    formattedInputValue += inputNumbersValue.substring(0, 2);
                    for (let iter = 2; iter <= inputNumbersValue.length; iter += 3) {
                        const other = inputNumbersValue.substring(iter, iter + 3);
                        if (other) {
                            formattedInputValue += ` ${inputNumbersValue.substring(iter, iter + 3)}`;
                        }
                        else break;
                    } 
                    break;
                case 0: 
                    formattedInputValue += inputNumbersValue.substring(0, 3);
                    for (let iter = 3; iter <= inputNumbersValue.length; iter += 3) {
                        const other = inputNumbersValue.substring(iter, iter + 3);
                        if (other) {
                            formattedInputValue += ` ${inputNumbersValue.substring(iter, iter + 3)}`;
                        }
                        else break;
                    }
                    break;
            }
            field.value = formattedInputValue;
        }
    }

    handlePaste(field, event) {
        let pasted = event.clipboardData || window.clipboardData,
            inputNumbersValue = getInputNumbersValue(field);

        if (pasted) {
            let pastedText = pasted.getData('Text');

            if (/\D/g.test(pastedText)) {
                field.value = inputNumbersValue;
            }
        }
    }

    setNumbersValue(fields) {
        for (const field of fields) {
            field.value = Number(field.value.replace(/\s/g, ''));
        }
    }

    handleChangeCategory(event) {
        let addCategory = document.getElementById('add_category');
        let categories = {
             1: 'фильм',
             4: 'сериал',
             5: 'аниме',
        }
        let category = categories[event.target.value];
        if (category) addCategory.innerHTML = category;
    }

    setAllHandlers() {
        const fields = [this.budget, this.feesInUSA, this.feesInWorld];

        for (const field of fields) {
            field.addEventListener('input', MovieForm.handleInput.bind(field, this, field));
            field.addEventListener('blur', this.formatBigNumberInput.bind(field, field));
            field.addEventListener('paste', this.handlePaste.bind(field, field));
        }
        this.category.addEventListener('change', this.handleChangeCategory);

        this.worldPremiereInput.setAllHandlers();
        this.button.addEventListener('click', this.setNumbersValue.bind(this.button, fields));
    }

}


function main() {
    let movieForm = document.querySelector('div.add_form');

    let movieFormObj = new MovieForm(movieForm);
    movieFormObj.setAllHandlers();
}


document.addEventListener('DOMContentLoaded', main);
