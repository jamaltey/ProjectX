if (location.href.endsWith('#comments')) {
    showCommentsPart()
} else {
    showInfoPart()
}

function showCommentsPart(){
    $('#comment-button').css('color', 'inherit')
    $('#info-button').css('color', '#BDBDBD')
    $('#info-part').hide()
    $('#comment-part').show()
}

function showInfoPart(){
    $('#comment-button').css('color', '#BDBDBD')
    $('#info-button').css('color', 'inherit')
    $('#info-part').show()
    $('#comment-part').hide()
}

$('#comment-button').on('click', showCommentsPart)
$('#info-button').on('click', showInfoPart)

$('#wishlist-btn').on('click', function(){
    const url = `/api/wishlist/toggle/${productId}/`
    const $btnText = $(this).find('span')
    $.get(url, ({ is_favorite }) => {
        if (is_favorite) {
            $btnText.text('Remove from wishlist')
        } else {
            $btnText.text('Add to wishlist')
        }
    })
})

function selectColor(element){
    element = $(element)
    $('.color.active').removeClass("active")
    element.addClass("active")

    const colorName = element.attr('data-color-name')
    $('input[name="color"]').val(colorName)
    sessionStorage.setItem('color', colorName)

    const img = $(`.carousel-item img[data-color-name="${colorName}"]`)

    if (img.length) {
        $(".carousel-item.active").removeClass("active")
        img.parent().addClass("active")
    }
}

function selectStorage(element){
    element = $(element)
    $('.storage.active').removeClass("active")
    element.addClass("active")
    
    const storage = element.attr('data-storage')
    $('input[name="storage"]').val(storage)
    sessionStorage.setItem('storage', storage)
    
    const addPrice = parseInt(element.attr('data-add-price'))
    const quantity = parseInt( $('.quantity span').text() )

    const finalPrice = (initialPrice + addPrice) * quantity
    $('#price').text(`${ finalPrice } $`)

    if ($('#old-price').length) {
        $('#old-price').text(`${ (initialOldPrice + addPrice) * quantity } $`)
    }
}

function changeCount(count){
    const counter = $('.quantity span')
    const prevCount = parseInt(counter.text())
    const quantity = prevCount + count
    if (quantity < 1) {
        return
    }
    counter.text(quantity)
    $('input[name="quantity"]').val(quantity)

    const price = parseInt( $('#price').text() )
    const finalPrice = price/prevCount * quantity
    $('#price').text(`${ finalPrice } $`)

    if ($('#old-price').length) {
        const oldPrice = parseInt( $('#old-price').text() )
        $('#old-price').text(`${ oldPrice/prevCount * quantity } $`)
    }
}

function setRating(rating){
    $('select#comment-rating').val(rating)
    let stars = $('.comment-form .stars img')
    stars.each((index, star) => {
        if (index < rating) {
            star.src = "/static/img/star.svg"
        } else {
            star.src = "/static/img/star-empty.svg"
        }
    })
}

function renderComment(comment){
    comment.created_at = new Date(comment.created_at).toLocaleString(
        'en-us',
        { month: 'short', day: 'numeric', year: 'numeric' }
    )
    const $comment = $(`
        <div class="comment row" id="${comment.id}">
            <div class="col-md-3">
                <h2>${comment.rating_value ? comment.rating_value : 'No rating'}</h2>
                <div class="stars"> </div>
            </div>

            <div class="col-md-9">
                <div class="comment-info">
                    <h5>${comment.author}</h5>
                    <h6>${comment.created_at}</h6>
                </div>

                <p>${comment.text}</p>

                <button class="btn btn-dark">
                    Delete comment
                </button>
            </div>
        </div>
    `)

    $comment.find('.stars')
    .html( 
        '<img src="/static/img/star.svg">'.repeat(comment.rating_value) +
        '<img src="/static/img/star-empty.svg">'.repeat(5 - comment.rating_value)
    );

    $comment.find('button').on('click', () => {
        deleteComment(comment.id)
    })

    $('.comments').append($comment)
}

function sendComment(rating=0, text){
    $.post('/api/comment/', {
            'rating_value': rating,
            'text': text,
            'product': productId
        }, ( data ) => {
            $('#comment-text').val('')
            setRating(0)
            data.author = user.fullName
            renderComment( data )
        }
    )
}

function deleteComment(id){
    $.ajax({
        url: `${commentUrl + id}/`,
        type: 'DELETE',
        success: () => {
            $(`.comment#${id}`).remove()
        }
    })
}

$('#comment-form').on('submit', function(e){
    e.preventDefault()
    const text = $('#comment-text').val()
    const rating = $('#comment-rating').val()
    sendComment(rating, text)
})