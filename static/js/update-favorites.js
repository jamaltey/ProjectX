function updateFavorites(product_id) {
	const url = `/api/wishlist/toggle/${product_id}/`
	$.get(url, () => {
		$(`.product#${product_id} .fa-heart`).toggleClass('fa-regular fa-solid')
	})
	.fail(() => {
		location.replace('/accounts/login/')
	})
}