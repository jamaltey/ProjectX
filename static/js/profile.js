let icon = $(`.profile-main li a[href="${activeTab}"] img`)

icon.attr('src', icon.attr('src').replace(/.svg$/, '-green.svg'))
$(`.profile-main li a[href="${activeTab}"] span`).addClass('active')
