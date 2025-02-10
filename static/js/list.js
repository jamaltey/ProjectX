const params = new URLSearchParams(location.search);

function updateContent() {
	const url = `${location.pathname}?${params.toString()}`;
	history.replaceState(null, '', url);
	$('#loading').show();
	$('#products').load(`${url} #products > *`);
}

function updateParam(name, value, multiple = false) {
	if (name != 'page') params.delete('page');
	if (multiple) {
		params.has(name, value) ? params.delete(name, value) : params.append(name, value);
	} else if (value && value != params.get(name)) {
		params.set(name, value);
	} else if (!value && params.has(name)) {
		params.delete(name);
	} else return;
	updateContent();
}

let searchTimeout;
$('#search').on('input', function () {
	clearTimeout(searchTimeout);
	searchTimeout = setTimeout(() => {
		updateParam('search', this.value.trim());
	}, 500);
});

$('#search-form').on('submit', function (e) {
	e.preventDefault();
	updateParam('search', $('#search').val().trim());
});

const $brandCheckbox = $(':checkbox[name="brand"]');
$brandCheckbox.on('change', function () {
	const brand = this.value;
	if (params.has('brand', brand) == this.checked) return true;
	updateParam('brand', brand, true);
});

$('#reset-filter').on('click', function () {
	updateParam('brand', null);
	$brandCheckbox.prop('checked', false);
});
