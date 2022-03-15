// Don't allow keypresses that happen in the pyshiny editor
// bubble up to the parent since Sphinx will, in that case, want
// to navigate to another page on <- or ->.
$(".pyshiny-container").keydown(function(e) {
  e.stopPropagation();
});
