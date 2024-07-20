function changeQuantity(id, count) {
	let counter = $(`.cart-object#${id} span.counter`)
	if (parseInt(counter.text()) + count < 1) {
		return
	}
	let quantity = parseInt(counter.text()) + count
	$.get(
		`/accounts/cart/change-quantity/${id}/${quantity}/`,
		function( data ){
			counter.text(quantity)
			$('.total-price').html($(data).find('.total-price > *'))
			$(`.cart-object#${id} .info`).html($(data).find(`.cart-object#${id} .info > *`))
		}
	)
}