"use strict";


function main() {
    document.addEventListener('DOMContentLoaded', function () {
        let phoneInputs = document.querySelectorAll('input[data-tel-input]');

        let getInputNumbersValue = function(input) {
            return input.value.replace(/\D/g, '');
        }

        let  onPhoneInput = function(event) {
            let input = event.target,
                inputNumbersValue = getInputNumbersValue(input),
                formattedInputValue = '',
                selectionStart = input.selectionStart;
            
            if (!inputNumbersValue) {
                input.value = '';
                return;
            }

            if (input.value.length !== selectionStart) {
                if (event.data && /\D/g.test(event.data)) {
                    input.value = inputNumbersValue;
                }
                return;
            }

            if (['7', '8', '9'].indexOf(inputNumbersValue[0]) > -1) {
                // Russian phone number
                if (inputNumbersValue[0] === '9') inputNumbersValue = '7' + inputNumbersValue;
                let firstSymbols = (inputNumbersValue[0] === '8') ? '8' : '+7';
                formattedInputValue = firstSymbols + ' ';

                if (inputNumbersValue.length > 1) {
                    formattedInputValue += '(' + inputNumbersValue.substring(1, 4);
                }
                if (inputNumbersValue.length >= 5) {
                    formattedInputValue += ') ' + inputNumbersValue.substring(4, 7);
                }

                if (inputNumbersValue.length >= 8) {
                    formattedInputValue += '-' + inputNumbersValue.substring(7, 9);
                }
                
                if (inputNumbersValue.length >= 10) {
                    formattedInputValue += '-' + inputNumbersValue.substring(9, 11);
                }
            }
            else {
                // Not Russian phone number
                formattedInputValue = '+' + inputNumbersValue.substring(0, 15);
            }
            input.value = formattedInputValue;
        }

        let onPhoneKeyDown = function(event) {
            let input = event.target;
            if (event.keyCode === 8 && getInputNumbersValue(input).length === 1) {
                input.value = '';
            }
        }

        let onPhonePaste = function(event) {
            let pasted = event.clipboardData || window.clipboardData,
                input = event.target,
                inputNumbersValue = getInputNumbersValue(input);
            
            if (pasted) {
                let pastedText = pasted.getData('Text');
                
                if (/\D/g.test(pastedText)) {
                    input.value = inputNumbersValue;
                }
            }
        }
        
        for (let iter of phoneInputs) {
            iter.addEventListener('input', onPhoneInput);
            iter.addEventListener('keydown', onPhoneKeyDown);
            iter.addEventListener('paste', onPhonePaste);
        }

    });
}

main();
