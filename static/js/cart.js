function clearContent() {
	$('main .row, main .card').remove()
	$('.cart-items-count').remove()
	$('#cart-clear-btn').remove()
	$('#cart-empty').show()
}

$('#cart-clear-btn').on('click', () => {
	$.get(`/api/cart/clear/`, clearContent)
})

function removeItem(id) {
	$.ajax({
		url: `/api/cart/${id}/remove/`,
		type: 'DELETE',
		success: ( data ) => {
			if ( data.is_empty ) {
				clearContent()
			} else {
				$(`.cart-item#${id}`).remove()
				$('.cart-items-count').text( data.items_count )
				$('#total-price .old-price').text(`${ data.discount } $`)
				$('#total-price .price').text(`${ data.total_price } $`)
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
			console.log(data)
			$(`.cart-item#${id} .price`).text(data.price)
			$('#total-price .old-price').text(data.discount)
			$('#total-price .price').text(data.total_price)
		}
	)
}