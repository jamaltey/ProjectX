
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

function selectColor(element){
    element = $(element)
    $('.color.active').removeClass("active")
    element.addClass("active")

    let colorname = element.attr('colorname')
    $('input[name="color"]').val(colorname)
    sessionStorage.setItem('color', colorname)

    let img = $(`.carousel-item img[colorname="${colorname}"]`)

    if (img.length) {
        $(".carousel-item.active").removeClass("active")
        img.parent().addClass("active")
    }
}

function selectStorage(element){
    element = $(element)
    $('.storage.active').removeClass("active")
    element.addClass("active")
    
    let storage = element.attr('storage')
    $('input[name="storage"]').val(storage)
    sessionStorage.setItem('storage', storage)
    
    let addPrice = parseInt(element.attr('addprice'))
    let defaultPrice = parseInt( $('#price').attr('default') )
    let quantity = parseInt( $('.quantity span').text() )

    let finalPrice = (defaultPrice + addPrice) * quantity
    $('#price').text(`${ finalPrice } $`)

    if ($('#old-price').length) {
        let oldPrice = parseInt( $('#old-price').attr('default') )
        $('#old-price').text(`${ (oldPrice + addPrice) * quantity } $`)
    }
}

function changeCount(count){
    let counter = $('.quantity span')
    prevCount = parseInt(counter.text())
    quantity = prevCount + count
    if (quantity < 1) {
        return
    }
    counter.text(quantity)
    $('input[name="quantity"]').val(quantity)

    let price = parseInt( $('#price').text() )
    let finalPrice = price/prevCount * quantity
    $('#price').text(`${ finalPrice } $`)

    if ($('#old-price').length) {
        let oldPrice = parseInt( $('#old-price').text() )
        $('#old-price').text(`${ oldPrice/prevCount * quantity } $`)
    }
}

function setRating(rating){
    $('select#comment-rating').val(rating)
    let stars = $('.comment-form .stars img')
    stars.each((index, star) => {
        if (index < rating) {
            star.src = "{% static 'img/star.svg' %}"
        } else {
            star.src = "{% static 'img/star-empty.svg' %}"
        }
    })
}

function sendComment(rating=0, text){
    let url = location.href
    $.post(
      url,
      {
        'csrfmiddlewaretoken': csrftoken,
        'comment-rating': rating,
        'text': text
      },
      function( data ){
        $('.product-rating').html( $(data).find('.product-rating > *') )
        $('.comments-div').html( $(data).find('.comments-div > *') )
      }
    )
}

function deleteComment(comment_id){
    $.get(
      `/delete-comment/${comment_id}`,
      function( data ){
        $('.product-rating').html( $(data).find('.product-rating > *') )
        $('.comments-div').html( $(data).find('.comments-div > *') )
        if ($('.comments-div .row').children().length == 0) {
            $('.comments-div div').remove()
        }
      }
    )
}
