document.addEventListener('click', async function (event) {
	let row = event.target.closest('tr.clickable-row');
	if (!row) return;

	const id = row.dataset.id;
	window.location.href = `/entreprise/${id}`;
});


