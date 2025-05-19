// user is defined in base.html
// productId, initialPrice, initialOldPrice are defined in detail.html

const swiper = new Swiper('#swiper', {
    effect: 'fade',
    speed: 500,
    navigation: {
        prevEl: '.swiper-button-prev',
        nextEl: '.swiper-button-next',
    },
    pagination: {
        el: '.swiper-pagination',
        type: 'bullets',
        dynamicBullets: true,
        clickable: true,
        renderBullet(index, className) {
            const src = $(`#swiper .swiper-slide img`).eq(index).attr('src');
            return `<button class="${className}" style="background-image: url('${src}')"></button>`;
        },
    },
    breakpoints: {
        768: {
            pagination: {
                dynamicBullets: false,
            },
        },
    },
    on: {
        slideChange() {
            const index = this.realIndex;
            const colorName = $(`#swiper .swiper-slide img`).eq(index).data('color-name');
            selectColor($(`.color[data-color-name="${colorName}"]`));
        },
    },
});

const $colors = $('.color');
const $storages = $('.storage');
const $quantity = $('#quantity span');

$colors.on('click', function () {
    selectColor($(this));
});
$storages.on('click', function () {
    selectStorage($(this));
});

const color = sessionStorage.getItem(`product#${productId}-color`);
const $color = $(`.color[data-color-name='${color}']`);
selectColor($color.length ? $color : $colors.first());

const storage = sessionStorage.getItem(`product#${productId}-storage`);
const $storage = $(`.storage[data-storage='${storage}']`);
selectStorage($storage.length ? $storage : $storages.first());

function selectColor($color) {
    if (!$color.length) return;

    $('.color.active').removeClass('active');
    $color.addClass('active');

    const colorName = $color.data('color-name');
    $('#color-name').text(colorName);
    $('input[name="color"]').val(colorName);
    sessionStorage.setItem(`product#${productId}-color`, colorName);

    const $slide = $(`#swiper .swiper-slide:has(img[data-color-name="${colorName}"])`);
    if ($slide.length) {
        const index = $slide.index();
        swiper.slideTo(index);
    }
}

function selectStorage($storage) {
    if (!$storage.length) return;

    $('.storage.active').removeClass('active');
    $storage.addClass('active');

    const storage = $storage.data('storage');
    $('input[name="storage"]').val(storage);
    sessionStorage.setItem(`product#${productId}-storage`, storage);

    const addPrice = parseInt($storage.data('add-price'));
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
    const finalPrice = (price / prevCount) * quantity;
    $('#price').text(finalPrice);

    if ($('#old-price').length) {
        const oldPrice = parseInt($('#old-price').text());
        $('#old-price').text((oldPrice / prevCount) * quantity);
    }
}

$('#wishlist-btn').on('click', function () {
    const url = `/api/wishlist/toggle/${productId}/`;
    $.get(url, ({ is_favorite }) => {
        const text = is_favorite ? 'Remove from wishlist' : 'Add to wishlist';
        $(this).find('span').text(text);
    }).fail(xhr => {
        if (xhr.status === 403) {
            location.replace('/accounts/login/');
        } else {
            alert(`Failed to add product to wishlist. Please try again. Error: ${xhr.status}`);
        }
    });
});

const $commentBtn = $('#comment-button');
const $infoBtn = $('#info-button');
const $commentPart = $('#comment-part');
const $infoPart = $('#info-part');

if (location.hash == '#comment-part') showCommentsPart();
else showInfoPart();

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

const $commentRatingSelect = $('#comment-rating-select');
const $commentText = $('#comment-text');
const $commentRatingStars = $('#comment-form .fa-star');

function setRating(ratingValue) {
    ratingValue = parseInt(ratingValue);
    const $star = $commentRatingStars.eq(ratingValue - 1);
    const currentValue = $commentRatingSelect.val();
    if (ratingValue == currentValue && $star.hasClass('fa-solid')) {
        $commentRatingSelect.val(ratingValue - 1);
        $star.removeClass('fa-solid');
        return 0;
    }
    $commentRatingSelect.val(ratingValue);
    $commentRatingStars.each((i, star) => {
        $(star).toggleClass('fa-solid', i < ratingValue);
    });
    return ratingValue;
}

$('#comment-form').on('submit', e => {
    e.preventDefault();
    const ratingValue = $commentRatingSelect.val();
    const text = $commentText.val();
    sendComment(ratingValue, text);
});

function renderStars(ratingValue) {
    return (
        '<i class="fa-sharp fa-solid fa-star"></i>\n'.repeat(ratingValue) + '<i class="fa-sharp fa-regular fa-star"></i>\n'.repeat(5 - ratingValue)
    );
}

function renderComment({ id, rating_value: ratingValue = 0, author, created_at: createdAt, text }) {
    createdAt = new Date(createdAt).toLocaleString('en-us', { month: 'short', day: 'numeric', year: 'numeric' });
    const $comment = $(`
		<div class="comment row gy-3" id="comment-${id}">
			<div class="col-md-3 text-center">
				<h2>${ratingValue || 'No rating'}</h2>
				<div class="stars fs-5">${renderStars(ratingValue)}</div>
			</div>
			<div class="col-md-9">
				<div class="comment-info d-flex justify-content-between">
					<h5>${author}</h5>
					<h6>${createdAt}</h6>
				</div>
				<p></p>
				<button class="btn btn-dark">
					Delete comment
				</button>
			</div>
			<hr class="w-100 my-4" />
		</div>
	`);
    $comment.find('p').text(text);
    $comment.find('.btn').on('click', () => deleteComment(id));
    $comment.prependTo('#comments');
}

function sendComment(ratingValue = 0, text) {
    $.post(
        '/api/comment/',
        {
            rating_value: ratingValue,
            text: text,
            product: productId,
        },
        data => {
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
        success() {
            $(`#comment-${id}`).remove();
            const commentsLength = $('.comment').length;
            if (!commentsLength) {
                $('#comments .no-items').show();
            } else if (commentsLength == 1) {
                $('#comments hr').remove();
            }
        },
        error() {
            alert('Failed to delete comment. Please try again.');
        },
    });
}
