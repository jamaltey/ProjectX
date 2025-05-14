const params = new URLSearchParams(location.search);

const $loading = $('#loading');
const $products = $('#products');
function updateContent() {
    const url = `${location.pathname}?${params}`;
    history.replaceState(null, '', url);
    $loading.show();
    $products.load(`${url} #products > *`);
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

// $search and $searchForm are defined in base.html
let searchTimeout;
$search.on('input', function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        updateParam('search', this.value.trim());
    }, 500);
});

$searchForm.on('submit', e => {
    e.preventDefault();
    updateParam('search', $search.val().trim());
});

$(':checkbox[name="brand"]').on('change', function () {
    const brand = this.value;
    if (params.has('brand', brand) == this.checked) return true;
    updateParam('brand', brand, true);
});

$('#reset-filter').on('click', () => {
    updateParam('brand', null);
    $brandCheckbox.prop('checked', false);
});
