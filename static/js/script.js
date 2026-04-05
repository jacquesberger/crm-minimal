// L'endroit où placer le code du front-end.


// https://getbootstrap.com/docs/5.0/forms/validation/

import { showMessage, TYPE } from "./toast.js";


(function () {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }

                form.classList.add('was-validated')
            }, false)
        })
})()

function verifierChampObligatoire(input, feedback, message = "Ce champ doit être rempli.") {
    if (input.value.length === 0) {
        input.setCustomValidity(message);
        feedback.textContent = message;
        return true;
    } else {
        input.setCustomValidity("");
        feedback.textContent = "";
        return false;
    }
}

function verifierAncienMdp(ancienMdp, feedbackAncien) {
    verifierChampObligatoire(ancienMdp, feedbackAncien);
}

function verifierNouveauMdp(nouveauMdp, feedbackNouveau, ancienMdp) {
    if (verifierChampObligatoire(nouveauMdp, feedbackNouveau)) return;

    if (nouveauMdp.validity.tooShort) {
        nouveauMdp.setCustomValidity("Le mot de passe doit contenir au moins 15 caractères.");
        feedbackNouveau.textContent = "Le mot de passe doit contenir au moins 15 caractères.";
    } else if (nouveauMdp.value === ancienMdp.value) {
        nouveauMdp.setCustomValidity("Le nouveau mot de passe doit être différent de l'ancien.");
        feedbackNouveau.textContent = "Le nouveau mot de passe doit être différent de l'ancien.";
    } else {
        nouveauMdp.setCustomValidity("");
        feedbackNouveau.textContent = "";
    }
}

function verifierConfirmeMdp(confirmeMdp, feedbackConfirme, nouveauMdp) {
    if (verifierChampObligatoire(confirmeMdp, feedbackConfirme)) return;
    if (nouveauMdp.value !== confirmeMdp.value) {
        confirmeMdp.setCustomValidity("Les mots de passe ne correspondent pas.");
        feedbackConfirme.textContent = "Les mots de passe ne correspondent pas.";
    } else {
        confirmeMdp.setCustomValidity("");
        feedbackConfirme.textContent = "";
    }
}

function validerChampsMotDePasse(form) {
    const ancienMdp = form.querySelector('#ancien-mot-de-passe');
    const nouveauMdp = form.querySelector('#nouveau-mot-de-passe');
    const confirmeMdp = form.querySelector('#confirme-mot-de-passe');
    const feedbackAncien = form.querySelector('#feedback-ancien-mdp');
    const feedbackNouveau = form.querySelector('#feedback-nouveau-mdp');
    const feedbackConfirme = form.querySelector('#feedback-confirme-mdp');

    ancienMdp.addEventListener('input', () => verifierAncienMdp(ancienMdp, feedbackAncien));
    nouveauMdp.addEventListener('input', () => verifierNouveauMdp(nouveauMdp, feedbackNouveau, ancienMdp));
    confirmeMdp.addEventListener('input', () => verifierConfirmeMdp(confirmeMdp, feedbackConfirme, nouveauMdp));

    verifierAncienMdp(ancienMdp, feedbackAncien);
    verifierNouveauMdp(nouveauMdp, feedbackNouveau, ancienMdp);
    verifierConfirmeMdp(confirmeMdp, feedbackConfirme, nouveauMdp);
    form.classList.add('was-validated');
}

async function fetchHtmlContent(url) {
    const response = await fetch(url);
    if (response.status === 401) {
        throw new Error(`Non autorisé.`);
    } else if (!response.ok) {
        throw new Error(`Une erreur est survenue côté serveur.`);
    }
    return await response.text();
}

function displayResponseMessage(messageBox, message, type = 'success') {
    const alertType = type === 'success' ? 'alert-success' : 'alert-danger';
    messageBox.innerHTML = `<div class="alert ${alertType}">${message}</div>`;
}

async function handleSubmitCompteForm(event, form, messageBox) {
    event.stopPropagation();
    validerChampsMotDePasse(form);

    if (!form.checkValidity()) {
        messageBox.innerHTML = '';
        return;
    }

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const url = '/api/utilisateur/moi/mot-de-passe';

    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)

        });

        const data = await response.json();

        if (response.ok) {
            showMessage("Le mot de passe a été modifié avec succès.", TYPE.SUCCES)
            form.reset();
            form.classList.remove('was-validated');
        } else if (response.status === 400) {
            displayResponseMessage(messageBox, data.Error, 'danger');
        } else {
            displayResponseMessage(messageBox, 'Une erreur est survenue côté serveur. Veuillez réessayer plus tard.', 'danger');
        }
    } catch (error) {
        console.error('Erreur lors de la requête :', error);
        displayResponseMessage(messageBox, 'Erreur réseau ou serveur inattendue.', 'danger');
    }
}

const container = document.getElementById('content-container');

async function loadContent(url) {
    try {
        const fullUrl = url + "?fragment=true";
        const response = await fetch(fullUrl);

        if (!response.ok) {
            showMessage("Une erreur est survenue.", TYPE.ERREUR);
            return;
        }

        const htmlContent = await response.text();
        container.innerHTML = htmlContent;
        window.history.pushState({}, "", url);

    } catch (error) {
        showMessage("Erreur lors du chargement du contenu.", TYPE.ERREUR);
    }
}



container.addEventListener('submit', function (event) {
    if (event.target.matches('.needs-validation')) {
        event.preventDefault();
        handleSubmitCompteForm(event, event.target, document.getElementById('response-message'));
    }
});


document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.nav-settings').forEach(link => {
        link.addEventListener('click', async function (event) {
            event.preventDefault();
            const url = this.getAttribute('href');
            await loadContent(url);
        });
    });
});


// Gestion du bouton back/forward du navigateur
window.addEventListener("popstate", (e) => {
    if (e.state) {
        container.innerHTML = e.state.html;
    }
});


container.addEventListener('click', async function (event) {
    let row = event.target.closest('tr');
    if (!row) return;

    const id = row.dataset.id;
    await loadContent(`/parametres/utilisateur/${id}`);
});

container.addEventListener('click', function (event) {
    if (event.target.matches('#btn-save-edit-user')) {
        handleSubmitEditUtilisateur(event);
    }
    if (event.target.matches('#btn-save-edit-password')) {
        handleSubmitModifyPassword(event);
    }
    if (event.target.matches('#btn-save-new-user')) {
        handleSubmitNewUtilisateurForm(event);
    }
});

async function handleSubmitNewUtilisateurForm(event) {
    event.preventDefault();
    const form = document.getElementById("form-nouvel-utilisateur");
    const errorContainer = document.getElementById("nouvel-utilisateur-errors");
    if (!form || !errorContainer) return;

    errorContainer.classList.add("d-none");
    errorContainer.innerHTML = "";

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    try {
        const url = '/api/utilisateur';
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)

        });
        const data = await response.json();

        if (!response.ok) {
            let message = 'Une erreur serveur est survenue. Veuillez réessayer plus tard.';
            if (response.status === 400) {
                message = data.Error.global_errors.join('<br>');
            } else if (response.status === 409) {
                message = data.Error;
            }

            errorContainer.innerHTML = message;
            errorContainer.classList.remove("d-none");
            return;
        }
        form.reset();
        const modalElement = document.getElementById('nouvelUtilisateur');
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.hide();

        showMessage("L'utilisateur a été créé avec succès.", TYPE.SUCCES);
        await updateListUtilisateur();

    } catch (error) {
        errorContainer.innerHTML = 'Une erreur serveur est survenue. Veuillez réessayer plus tard.';
        errorContainer.classList.remove("d-none");
    }
}

async function updateListUtilisateur() {
    const tableUtilisateur = document.getElementById('table-utilisateurs');
    const url = '/api/utilisateurs';

    try {
        const response = await fetch(url);
        const data = await response.json();

        const utilisateurs = Array.isArray(data) ? data : [];
        const tbody = tableUtilisateur.querySelector('tbody');
        tbody.innerHTML = "";

        for (const utilisateur of utilisateurs) {
            const tr = document.createElement("tr");
            tr.className = "user-row clickable-row";

            tr.dataset.id = utilisateur.id;
            tr.dataset.username = utilisateur.username;
            tr.dataset.role = utilisateur.role_id;
            tr.dataset.etat = utilisateur.etat_id;

            const roleLabel = Number(utilisateur.role_id) === 1 ? "Admin" : "Régulier";
            const etatLabel = Number(utilisateur.etat_id) === 1 ? "Actif" : "Suspendu";

            tr.innerHTML = `
            <td>${utilisateur.id}</td>
            <td>${utilisateur.username}</td>
            <td>${roleLabel}</td>
            <td>${etatLabel}</td> `;

            tbody.appendChild(tr);
        }

    } catch (error) {
        showMessage('Une erreur serveur est survenue. Veuillez réessayer plus tard.',TYPE.ERREUR);
    }
}

async function handleSubmitEditUtilisateur(event) {
    event.preventDefault();

    const form = document.getElementById("form-edit-utilisateur");
    if (!form) return;

    const userId = form.dataset.formUserId;
    const url = `/api/utilisateur/${userId}`;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (!response.ok) {
            let message = 'Une erreur serveur est survenue. Veuillez réessayer plus tard.';
            if (response.status === 400 && data.Error) {
                message = data.Error;
            }
            showMessage(message, TYPE.ERREUR);
            return;
        }
        showMessage("Les informations ont été modifiées avec succès.", TYPE.SUCCES);
    } catch (error) {
        showMessage('Une erreur serveur est survenue. Veuillez réessayer plus tard.', TYPE.ERREUR);
    }
}


async function handleSubmitModifyPassword(event) {
    console.log("Modifier mot de passe");
    event.preventDefault();
    const form = document.getElementById("form-edit-password");
    if (!form) {
        console.error("Une erreur est survenue côté client.");
        return;
    }

    const passwordField = document.getElementById("edit-password");
    if (!passwordField) {
        console.error("Une erreur est survenue côté client.");
        return;
    }
    const password = passwordField.value.trim();
    if (password.length < 15) {
        showMessage("Le mot de passe doit contenir au moins 15 caractères.", TYPE.ERREUR);
        return;
    }
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const userId = form.dataset.formUserId;
    const url = `/api/utilisateur/${userId}/mot-de-passe`;

    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            let message = 'Une erreur serveur est survenue. Veuillez réessayer plus tard.';
            if (response.status === 400 && data.Error) {
                message = data.Error;
            }
            showMessage(message,TYPE.ERREUR);
            return;
        }
        showMessage("Le mot de passe a été modifié avec succès.",TYPE.SUCCES);

    } catch (error) {
        showMessage('Une erreur serveur est survenue. Veuillez réessayer plus tard.', TYPE.ERREUR);
    }
}
