function updateFavorites(product_id) {
	$.get(
		`/api/wishlist/toggle/${product_id}/`,
		success = () => {
			$(`.product#${product_id} .heart-cont img`).each((index, element) => {
				if (/heart2\.svg$/.test(element.src)) {
				element.src = "/static/img/heart-red.svg"
				} else {
				element.src = "/static/img/heart2.svg"
				}
			})
		}
	).fail(() => {
		location.replace('/accounts/login/')
	})
}