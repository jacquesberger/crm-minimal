function showMessage(message, type = 'succes', title = 'Notification') {
    const container = document.getElementById('toast-container');

    const toastEl = document.createElement('div');
    toastEl.className = 'toast';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;

    if (type === TYPE.ERREUR ) {
        toastEl.classList.add('text-bg-danger');
    } else {
        toastEl.classList.add('text-bg-success');
    }

    toastEl.appendChild(body);
    container.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, {delay: 5000});
    bsToast.show();
}

const TYPE = {
    ERREUR: 'erreur',
    SUCCES: 'succes'
};

export {showMessage,TYPE};