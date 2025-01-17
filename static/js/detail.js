// user is defined in base.html
// productId, initialPrice, initialOldPrice are defined in detail.html

const $wishlistBtn = $('#wishlist-btn');

$wishlistBtn.on('click', () => {
    const url = `/api/wishlist/toggle/${productId}/`;
    $.get(url, ({ is_favorite }) => {
        const text = is_favorite ? 'Remove from wishlist' : 'Add to wishlist';
        $wishlistBtn.find('span').text(text);
    }).fail((xhr) => {
        if (xhr.status === 403) {
            location.replace('/accounts/login/');
        } else {
            alert(`Failed to add product to wishlist. Please try again. Error: ${xhr.status}`);
        }
    });
});

const carousel = new bootstrap.Carousel('#carousel')
const $colors = $('.color');
const $storages = $('.storage');
const $quantity = $('#quantity span');

$colors.on('click', function(){
    selectColor($(this));
});
$storages.on('click', function(){
    selectStorage($(this));
});

const color = sessionStorage.getItem(`product-${productId}-color`);
let $color = $(`.color[data-color-name='${color}']`);
if (!$color.length) {
    $color = $colors.first();
}
const $carouselItems = $('#carousel .carousel-item');
$carouselItems.css('transition-duration', '0s');
selectColor($color);
$carouselItems.css('transition-duration', '.6s');

const storage = sessionStorage.getItem(`product-${productId}-storage`);
let $storage = $(`.storage[data-storage='${storage}']`);
if (!$storage.length) {
    $storage = $storages.first();   
}
selectStorage($storage);

function selectColor($color) {
    if (!$color.length) {
        return;
    }

    $('.color.active').removeClass("active");
    $color.addClass("active");

    const colorName = $color.attr('data-color-name');
    $('#color-name').text(colorName);
    $('input[name="color"]').val(colorName);
    sessionStorage.setItem(`product-${productId}-color`, colorName);

    const $img = $(`#carousel .carousel-item img[data-color-name="${colorName}"]`);

    if ($img.length) {
        const index = $img.parent().index();
        carousel.to(index);
        // $(".carousel-item.active").removeClass("active");
        // $img.parent().addClass("active");
    }
}

function selectStorage($storage) {
    if (!$storage.length) {
        return;
    }

    $('.storage.active').removeClass("active");
    $storage.addClass("active");

    const storage = $storage.attr('data-storage');
    $('input[name="storage"]').val(storage);
    sessionStorage.setItem(`product-${productId}-storage`, storage);

    const addPrice = parseInt($storage.attr('data-add-price'));
    const quantity = parseInt($quantity.text());

    const finalPrice = (initialPrice + addPrice) * quantity;
    $('#price').text(finalPrice);

    if ($('#old-price').length) {
        $('#old-price').text((initialOldPrice + addPrice) * quantity);
    }
}

function changeCount(count) {
    const prevCount = parseInt($quantity.text());
    const quantity = prevCount + count;
    if (quantity < 1) {
        return;
    }
    $quantity.text(quantity);
    $('input[name="quantity"]').val(quantity);

    const price = parseInt($('#price').text());
    const finalPrice = price/prevCount * quantity;
    $('#price').text(finalPrice);

    if ($('#old-price').length) {
        const oldPrice = parseInt($('#old-price').text());
        $('#old-price').text(oldPrice/prevCount * quantity);
    }
}

const $commentBtn = $('#comment-button');
const $infoBtn = $('#info-button');
const $commentPart = $('#comment-part');
const $infoPart = $('#info-part');

if (location.href.endsWith('#comment-part')) {
    showCommentsPart();
} else {
    showInfoPart();
}

function showCommentsPart() {
    $commentBtn.addClass('active');
    $infoBtn.removeClass('active');
    $infoPart.hide();
    $commentPart.show();
    history.pushState(null, null, '#comment-part');
}

function showInfoPart() {
    $commentBtn.removeClass('active');
    $infoBtn.addClass('active');
    $infoPart.show();
    $commentPart.hide();
    history.pushState(null, null, '#');
}

$commentBtn.on('click', showCommentsPart);
$infoBtn.on('click', showInfoPart);

function setRating(rating) {
    $('select#comment-rating').val(rating);
    const stars = $('#comment-form .stars i.fa-star');
    stars.each((i, star) => {
        $(star).toggleClass('fa-sharp fa-solid', i < rating);
    });
}

$('#comment-form').on('submit', (e) => {
    e.preventDefault();
    const text = $('#comment-text').val();
    const rating = $('#comment-rating').val();
    sendComment(rating, text);
});

function generateStars(ratingValue) {
    return '<i class="fa-sharp fa-solid fa-star"></i>\n'.repeat(ratingValue) +
            '<i class="fa-regular fa-star"></i>\n'.repeat(5 - ratingValue);
}

function renderComment(comment) {
    comment.created_at = new Date(comment.created_at).toLocaleString(
        'en-us',
        { month: 'short', day: 'numeric', year: 'numeric' }
    );

    const $comment = $(`
        <div class="comment row" id="${comment.id}">
            <div class="col-md-3 text-center">
                <h2>${comment.rating_value || 'No rating'}</h2>
                <div class="stars fs-5">${generateStars(comment.rating_value)}</div>
            </div>

            <div class="col-md-9">
                <div class="comment-info d-flex justify-content-between">
                    <h5>${comment.author}</h5>
                    <h6>${comment.created_at}</h6>
                </div>

                <p>${comment.text}</p>

                <button class="btn btn-dark">
                    Delete comment
                </button>
            </div>

            <hr class="w-100 my-4" />
        </div>
    `);

    $comment.find('button').on('click', () => {
        deleteComment(comment.id);
    });

    $('#comments').prepend($comment);
}

function sendComment(rating = 0, text) {
    $.post('/api/comment/', {
            'rating_value': rating,
            'text': text,
            'product': productId
        }, (data) => {
            $('#comment-text').val('');
            setRating(0);
            data.author = user.fullName;
            renderComment(data);
            $('#comments .no-items').hide();
        }
    ).fail(() => {
        alert('Failed to submit comment. Please try again.');
    });
}

function deleteComment(id) {
    $.ajax({
        url: `/api/comment/${id}/`,
        type: 'DELETE',
        success: () => {
            $(`.comment#${id}`).remove();
            if ($('.comment').length) {
                if ($('.comment').length == 1) {
                    $('#comments hr').remove();
                }
            } else {
                $('#comments .no-items').show();
            }
        },
        error: () => {
            alert('Failed to delete comment. Please try again.');
        }
    });
}
