
function showCommentsPart(){
    $('#comment-button').css('color', 'black')
    $('#info-button').css('color', '#BDBDBD')
    $('#info-part').hide()
    $('#comment-part').show()
}

function showInfoPart(){
    $('#comment-button').css('color', '#BDBDBD')
    $('#info-button').css('color', 'black')
    $('#info-part').show()
    $('#comment-part').hide()
}

$('button.wishlist-add').on('click', function(){
    const url = `/accounts/wishlist/update/${productId}`
    const btnText = $(this).find('span')
    $.get(url, function(data){
        if (data.is_favorite) {
            btnText.text('Remove from wishlist')
        } else {
            btnText.text('Add to wishlist')
        }
    })
})

function selectColor(element){
    element = $(element)
    $('.color.active').removeClass("active")
    element.addClass("active")

    const colorname = element.attr('colorname')
    $('input[name="color"]').val(colorname)
    sessionStorage.setItem('color', colorname)

    const img = $(`.carousel-item img[colorname="${colorname}"]`)

    if (img.length) {
        $(".carousel-item.active").removeClass("active")
        img.parent().addClass("active")
    }
}

function selectStorage(element){
    element = $(element)
    $('.storage.active').removeClass("active")
    element.addClass("active")
    
    const storage = element.attr('storage')
    $('input[name="storage"]').val(storage)
    sessionStorage.setItem('storage', storage)
    
    const addPrice = parseInt(element.attr('addprice'))
    const defaultPrice = parseInt( $('#price').attr('default') )
    const quantity = parseInt( $('.quantity span').text() )

    const finalPrice = (defaultPrice + addPrice) * quantity
    $('#price').text(`${ finalPrice } $`)

    if ($('#old-price').length) {
        const oldPrice = parseInt( $('#old-price').attr('default') )
        $('#old-price').text(`${ (oldPrice + addPrice) * quantity } $`)
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
    const commentElement = $(`
        <div class="comment row" id="${comment.id}">
            <div class="col-md-3">
                <h1>${comment.rating_value ? comment.rating_value : 'No rating'}</h1>
                <div class="stars">

                </div>
            </div>

            <div class="col-md-9">
                <div class="comment-info">
                    <h6>${comment.author}</h6>
                    <p>${comment.created_at}</p>
                </div>

                <p>${comment.text}</p>

                <button onclick="deleteComment(${comment.id})" class="btn-dark">
                    Delete comment
                </button>
            </div>
        </div>
    `)

    const stars = commentElement.find('.stars')

    for (let i = 0; i < comment.rating_value; i++) {
        $(stars).append('<img src="/static/img/star.svg">')
    }
    for (let i = comment.rating_value; i < 5; i++) {
        $(stars).append('<img src="/static/img/star-empty.svg">')
    }

    
    $('.comments').append(commentElement)
}

const commentUrl = '/api/comment/'

function sendComment(rating=0, text){
    $.post(
      commentUrl, {
        'rating_value': rating,
        'text': text,
        'product': productId
      }, ( data ) => {
        $('#comment-text').val('')
        setRating(0)
        
        data.author = user_full_name
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
