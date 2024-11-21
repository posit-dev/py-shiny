import { LitElement } from "lit";

function createElement(
  tag_name: string,
  attrs: { [key: string]: string | null }
): HTMLElement {
  const el = document.createElement(tag_name);
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== null) el.setAttribute(key, value);
  }
  return el;
}

function createSVGIcon(icon: string): HTMLElement {
  const parser = new DOMParser();
  const svgDoc = parser.parseFromString(icon, "image/svg+xml");
  return svgDoc.documentElement;
}

// https://lit.dev/docs/components/shadow-dom/#implementing-createrenderroot
class LightElement extends LitElement {
  createRenderRoot() {
    return this;
  }
}

export { LightElement, createElement, createSVGIcon };
