export function createElement(
  tag_name: string,
  attrs: { [key: string]: string | boolean | null }
): HTMLElement {
  const el = document.createElement(tag_name);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null) continue;
    if (typeof value === "boolean") {
      if (value) el.setAttribute(key, "");
      continue;
    }
    el.setAttribute(key, value);
  }
  return el;
}
