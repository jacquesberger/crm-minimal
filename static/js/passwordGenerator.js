import {showMessage} from "./toast.js";

const containerContent = document.getElementById('content-container');

containerContent.addEventListener('click', function (event) {
    if (event.target.closest('#btn-generate-password')) {

        const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+";
        let password = "";
        for (let i = 0; i < 15; i++) {
            const randomIndex = Math.floor(Math.random() * charset.length);
            password += charset[randomIndex];
        }

        const passwordField = document.getElementById('edit-password');
        if (passwordField) {
            passwordField.value = password;
        }
    }

    if (event.target.closest('#btn-copy-password')) {
        const passwordField = document.getElementById("edit-password");
        if (passwordField && passwordField.value) {
            navigator.clipboard.writeText(passwordField.value)
                .then(() => {
                    showMessage("Mot de passe copié dans le presse-papiers")
                })
                .catch(err => {
                    console.error("Erreur de copie : ", err);
                });
        }
    }
});

