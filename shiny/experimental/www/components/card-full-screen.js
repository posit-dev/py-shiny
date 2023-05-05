$(document).on('click', '.bslib-full-screen-enter', function(e) {
  const $card = $(e.target).parents('.card').last();
  // Re-size/position the card (and add an overlay behind it)
  $card.addClass("bslib-full-screen");
  const overlay = $("<div id='bslib-full-screen-overlay'><a class='bslib-full-screen-exit'>Close <svg width:'20' height='20' fill='currentColor' class='bi bi-x-lg' viewBox='0 0 16 16'><path d='M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z'/></svg></a></div>");
  $card[0].insertAdjacentElement("beforebegin", overlay[0]);
});

$(document).on('click', '.bslib-full-screen-exit', function(e) {
  exitFullScreen();
});

document.addEventListener('keyup', function(e) {
  if (e.key === 'Escape') exitFullScreen();
}, false);

function exitFullScreen() {
  const $card = $('.bslib-full-screen');
  if ($card) {
    $('#bslib-full-screen-overlay').remove();
    $card.removeClass('bslib-full-screen');
  }
}
