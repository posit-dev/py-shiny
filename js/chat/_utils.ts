function createElement(
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

function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function (this: unknown, ...args: Parameters<T>): void {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

export { createElement, throttle };
