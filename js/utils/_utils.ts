import { LitElement } from "lit";

import type { HtmlDep } from "rstudio-shiny/srcts/types/src/shiny/render";

////////////////////////////////////////////////
// Lit helpers
////////////////////////////////////////////////

function createElement(
  tag_name: string,
  attrs: { [key: string]: string | null }
): HTMLElement {
  const el = document.createElement(tag_name);
  for (const [key, value] of Object.entries(attrs)) {
    // Replace _ with - in attribute names
    const attrName = key.replace(/_/g, "-");
    if (value !== null) el.setAttribute(attrName, value);
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
////////////////////////////////////////////////
// Shiny helpers
////////////////////////////////////////////////

export type ShinyClientMessage = {
  message: string;
  headline?: string;
  status?: "error" | "info" | "warning";
};

function showShinyClientMessage({
  headline = "",
  message,
  status = "warning",
}: ShinyClientMessage): void {
  document.dispatchEvent(
    new CustomEvent("shiny:client-message", {
      detail: { headline: headline, message: message, status: status },
    })
  );
}

async function renderDependencies(deps: HtmlDep[]): Promise<void> {
  if (!window.Shiny) return;
  if (!deps) return;

  try {
    await Shiny.renderDependenciesAsync(deps);
  } catch (renderError) {
    showShinyClientMessage({
      status: "error",
      message: `Failed to render HTML dependencies: ${renderError}`,
    });
  }
}

////////////////////////////////////////////////
// General helpers
////////////////////////////////////////////////

/**
 * Creates a throttle decorator that ensures the decorated method isn't called more
 * frequently than the specified delay
 * @param delay The minimum time (in ms) that must pass between calls
 */
export function throttle(delay: number) {
  /* eslint-disable @typescript-eslint/no-explicit-any */
  return function (
    _target: any,
    _propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    let timeout: number | undefined;

    descriptor.value = function (...args: any[]) {
      if (timeout) {
        window.clearTimeout(timeout);
      }

      timeout = window.setTimeout(() => {
        originalMethod.apply(this, args);
        timeout = undefined;
      }, delay);
    };

    return descriptor;
  };
}

export {
  LightElement,
  createElement,
  createSVGIcon,
  renderDependencies,
  showShinyClientMessage,
};

export type { HtmlDep };
