"use strict";


function getLanguage() {
    const languageBlock = document.querySelector("div.set_language");
    const languagesArray = languageBlock.querySelectorAll("option");

    for(const lang of languagesArray) {
        if(lang.selected) {
            return lang.value;
        }
    }
}


function createAlert(text, fieldId) {
    let newElement = document.createElement("div");
    newElement.classList.add("alert", "alert-danger");
    newElement.innerHTML = text;
    newElement.id = fieldId;

    newElement.style.width = "300px";
    newElement.style.fontSize = "20px";
    newElement.style.fontWeight = "500";
    newElement.style.margin = "-20px 0 30px 0";
    return newElement;
}


function addAlert(element, alertBlock) {
    element.nextElementSibling.after(alertBlock);
}


class AccountValidation {
    constructor(form) {
        this.form = form;
        this.language = getLanguage();
    }

    removeAlert(fieldId) {
        this.findAlert(fieldId).remove();
    }

    changeAlertText(newText, fieldId) {
        let alertBlock = this.findAlert(fieldId);
        alertBlock.innerHTML = newText;
    }

    findAlert(fieldId) {
        return this.form.querySelector(`div#${fieldId}`);
    }

    isAlert(fieldId) {
        if(this.findAlert(fieldId)) {
            return true;
        }
        return false;
    }

    static verifyUserEmail(instance, event) {
        let alertText = "Fill in the field correctly";
        const emailId = "custom_id_email";
        
        if(event.target.value) {
            if(!/[\w._-]+@[\w]+\.[a-z]{2,4}$/.test(event.target.value)) {
                // поле email заполнено неправильно
                if(instance.language === "ru") alertText = "Введите правильный адрес электронной почты.";
                else alertText = "Enter a valid email address.";

                if(!instance.isAlert(emailId)) {
                    // создаём блок с сообщением об ошибке
                    addAlert(event.target, createAlert(alertText, emailId));
                }
                else {
                    // меняем текст ошибки
                    instance.changeAlertText(alertText, emailId);
                }
            }
            else {
                // нет ошибок при заполнении поля email
                if(instance.isAlert(emailId)) {
                    instance.removeAlert(emailId);
                }
            }
        }
        else {
            // пустое поле email
            if(instance.language === "ru") alertText = "Данное поле должно быть заполнено.";
            else alertText = "This field must be filled in.";

            if(!instance.isAlert(emailId)) {
                // создаём блок с сообщением об ошибке
                addAlert(event.target, createAlert(alertText, emailId));
            }
            else {
                // меняем текст ошибки
                instance.changeAlertText(alertText, emailId);
            }
        }
    }

    static verifyUserName(instance, event) {
        let alertText = "Fill in the field correctly.";
        const usernameId = "custom_id_username";

        if(event.target.value) {
            if(/[^\w@.+-_]+/.test(event.target.value)) {
                // поле username заполнено неправильно
                if(instance.language === "ru") 
                alertText = "Введите правильное имя пользователя. Оно может содержать только буквы, цифры и знаки @.+-_";
                else alertText = "Enter a correct username.It can contain only letters, numbers and signs @.+-_";

                if(!instance.isAlert(usernameId)) {
                    // создаём блок с сообщением об ошибке
                    addAlert(event.target, createAlert(alertText, usernameId));
                }
                else {
                    // меняем текст ошибки
                    instance.changeAlertText(alertText, usernameId);
                }
            }
            else {
                // нет ошибок при заполнении поля username
                if(instance.isAlert(usernameId)) {
                    instance.removeAlert(usernameId);
                }
            }
        }
        else {
            // пустое поле username
            if(instance.language === "ru") alertText = "Данное поле должно быть заполненно.";
            else alertText = alertText = "This field must be filled in.";

            if(!instance.isAlert(usernameId)) {
                // создаём блок с сообщением об ошибке
                addAlert(event.target, createAlert(alertText, usernameId));
            }
            else {
                // меняем текст ошибки
                instance.changeAlertText(alertText, usernameId);
            }
        }
    }

    initiateSignupFormValidation() {
        const userName = this.form.querySelector("#id_username");
        const userEmail = this.form.querySelector("#id_user_email");

        userName.addEventListener("blur", AccountValidation.verifyUserName.bind(userName, this));
        userEmail.addEventListener("blur", AccountValidation.verifyUserEmail.bind(userEmail, this));
    }

    initiateLoginFormValidation() {
        const login = this.form.querySelector("input#id_login");
        login.addEventListener("blur", AccountValidation.verifyUserName.bind(login, this));
    }

    initiatePasswordResetFormValidation() {
        const userEmail = this.form.querySelector("#id_user_email");
        
        userEmail.addEventListener("blur", this.verifyUserEmail.bind(userEmail, this));
    }
}


function getPasswordFields(form) {
    // Возвращает поля с типом password
    const allTagsInput = form.querySelectorAll("input");
    let passwordFields = [];

    for(const inp of allTagsInput) {
        if(inp.id.includes("password")) {
            passwordFields.push(inp);
        }
    }
    return passwordFields;
}


function changePasswordField(passwordField, event) {
    const currentType = passwordField.getAttribute("type");
    let newType = "password";

    if(currentType === "text") {
        newType = "password";
        event.target.classList.replace("account_hide-password", "account_show-password");
    }
    else {
        newType = "text";
        event.target.classList.replace("account_show-password", "account_hide-password");
    }
    passwordField.setAttribute("type", newType);
}


function initiateCheckboxShowPassword(form) {
    // переключение аттрибута type поля password
    const passwordFields = getPasswordFields(form);
    const passwordFieldHandlers = form.querySelectorAll("div.account_show-password");

    for(let count = 0; count < passwordFields.length; count++) {
        passwordFieldHandlers[count].addEventListener("click", changePasswordField.bind(passwordFieldHandlers[count], passwordFields[count]))
    }
}


function main() {
    window.scrollTo(0, 550);

    const loginForm = document.querySelector("form#account_form.login");
    const signupForm = document.querySelector("form#account_form.signup");
    const passwordResetForm = document.querySelector("form#account_form.password_reset");

    if(loginForm) {
        initiateCheckboxShowPassword(loginForm);

        const loginValidationInstance = new AccountValidation(loginForm);
        loginValidationInstance.initiateLoginFormValidation();
    }
    else if(signupForm) {
        initiateCheckboxShowPassword(signupForm);

        const accountValidationInstance = new AccountValidation(signupForm);
        accountValidationInstance.initiateSignupFormValidation();
    }
    else if(passwordResetForm) {
        const passwordResetValidationInstance = new AccountValidation(passwordResetForm);
        passwordResetValidationInstance.initiatePasswordResetFormValidation();
    }
}


document.addEventListener("DOMContentLoaded", main);
