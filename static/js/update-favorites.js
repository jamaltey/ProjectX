function updateFavorites(product_id) {
    $.get(
      `/accounts/wishlist/update/${product_id}`,
      function(){
        $(`.product#${product_id} .heart-cont img`).each(function(index, element){
            if (/heart2\.svg$/.test(element.src)) {
                element.src = "/static/img/heart-red.svg"
            } else {
                element.src = "/static/img/heart2.svg"
            }
        })
      }
    )
}