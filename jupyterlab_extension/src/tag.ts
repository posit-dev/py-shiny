export function tag(
  tagname: string,
  attrs: Record<string, string> = {},
  children: (string | Node)[] = []
) {
  const el = document.createElement(tagname);
  Object.entries(attrs).forEach(([k, v]) => {
    el.setAttribute(k, v);
  });
  el.append(...children);
  return el;
}
