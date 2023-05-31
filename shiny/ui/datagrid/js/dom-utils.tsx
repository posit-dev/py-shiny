// Find the first item whose top-left corner is fully inside the visible portion of the
// scroll container
export function findFirstItemInView(
  scrollContainer: HTMLElement,
  items: NodeList,
  extraPadding?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  }
) {
  const pad = Object.assign(
    { top: 0, right: 0, bottom: 0, left: 0 },
    extraPadding
  );
  const container = scrollContainer;
  const top = container.scrollTop + pad.top;
  const left = container.scrollLeft + pad.left;
  const bottom = top + container.clientHeight - pad.top - pad.bottom;
  const right = left + container.clientWidth - pad.left - pad.right;

  for (let i = 0; i < items.length; i++) {
    const el = items[i] as HTMLElement;
    const y = el.offsetTop,
      x = el.offsetLeft;
    if (y >= top && y <= bottom && x >= left && x <= right) {
      return el;
    }
  }
  return null;
}
