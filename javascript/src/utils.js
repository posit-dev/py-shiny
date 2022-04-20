// similar to htmltools::tag()
// name: String
// attrs: {}
// children: any?
function tag(name, attrs, ...children) {
  let el = document.createElement(name);
  Object.entries(attrs || {}).forEach(([nm, val]) => {
    (nm.startsWith('on') && nm.toLowerCase() in window) 
    ? el.addEventListener(nm.toLowerCase().substr(2), val)
    : el.setAttribute(nm, val.toString());
  });
  if (!children) {
    return el;
  }
  tagAppendChild(el, children);
  return el;
}

// similar to htmltools::tagList()
function tagList(...children) {
  return tag("template", {}, children).children;
}

// similar to htmltools::HTML()
// x: String
function HTML(x) {
  let el = document.createElement("template");
  el.innerHTML = x;
  return el.content;
}

// similar to htmltools::tagAppendChild()
// x: https://developer.mozilla.org/en-US/docs/Web/API/Node
// y: any?
function tagAppendChild(x, y) {
  if (y instanceof HTMLCollection) {
    while (y.length > 0) x.append(y[0]);
  } else if (Array.isArray(y)) {
    y.forEach(z => tagAppendChild(x, z));
  } else {
    x.append(y);
  }
}

export {tag, tagList, HTML, tagAppendChild}