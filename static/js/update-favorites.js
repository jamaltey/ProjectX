function updateFavorites(product_id) {
	if (!user.isAuthenticated) {
		location.replace(`/accounts/login/?next=${location.pathname}`);
		return;
	}
	$.get(`/api/wishlist/toggle/${product_id}/`, () => {
		$(`.product#${product_id} .fa-heart`).toggleClass('fa-regular fa-solid');
	})
}