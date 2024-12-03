function removeItem(id) {
	$.ajax({
		url: `/api/cart/${id}/remove/`,
		type: 'DELETE',
		success: ( data ) => {
			if ( data.is_empty ) {
				$('.row, .card').remove()
				$('#cart-items-count').remove()
				$('#cart-clear-btn').remove()
				$('#cart-empty').show()
			} else {
				$(`.cart-item#${id}`).remove()
				$('#cart-items-count').text( parseInt($('#cart-items-count').text()) - 1 )
				$('.total-price .old-price').text(`–${ data.discount } $`)
				$('.total-price .price').text(`${ data.total_price } $`)
			}
		}
	})
}

function changeQuantity(id, count) {
	const counter = $(`.cart-item#${id} span.counter`)
	const quantity = parseInt(counter.text()) + count
	if (quantity < 1) {
		return
	}
	$.post(
		`/api/cart/${id}/change-quantity/`, { 'quantity': quantity },
		success = ( data ) => {
			counter.text(quantity)
			$(`.cart-item#${id} .price`).text(`${ data.price } $`)
			$('.total-price .old-price').text(`–${ data.discount } $`)
			$('.total-price .price').text(`${ data.total_price } $`)
		}
	)
} 