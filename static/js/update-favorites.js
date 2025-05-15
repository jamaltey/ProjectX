function updateFavorites(productId) {
	if (!user.isAuthenticated) {
		location.replace(`/accounts/login/?next=${location.pathname}`);
		return;
	}
	$.get(`/api/wishlist/toggle/${productId}/`, () => {
		$(`#product-${productId} .fa-heart`).toggleClass('fa-regular fa-solid');
	});
}
