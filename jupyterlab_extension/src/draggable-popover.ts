declare global {
  interface HTMLElement {
    showPopover: () => void;
    hidePopover: () => void;
  }
  interface Window {
    jQuery: any;
  }
}

export function makeDraggable(
  handle: HTMLElement,
  container: HTMLElement
): (e: { x: number; y: number; pointerId: number }) => void {
  let dragging = false;
  let offsetX = 0;
  let offsetY = 0;

  handle.addEventListener(
    'pointerdown',
    e => {
      e.preventDefault();
      e.stopPropagation();

      startDragging({ x: e.clientX, y: e.clientY, pointerId: e.pointerId });
    },
    { capture: false }
  );

  function startDragging(e: { x: number; y: number; pointerId: number }) {
    dragging = true;

    container.setPointerCapture(e.pointerId);

    offsetX = e.x - container.getBoundingClientRect().left;
    offsetY = e.y - container.getBoundingClientRect().top;

    // Attach event listeners
    container.addEventListener('pointermove', pointerMoveHandler);
    container.addEventListener('pointerup', pointerUpHandler);
  }

  function pointerMoveHandler(event: PointerEvent): void {
    if (!dragging) return;

    const target = event.target as HTMLElement;

    const x = event.clientX - offsetX;
    const y = event.clientY - offsetY;

    target.style.setProperty('--shinynotebook-popover-left', `${x}px`);
    target.style.setProperty('--shinynotebook-popover-top', `${y}px`);
  }

  function pointerUpHandler(event: PointerEvent): void {
    dragging = false;

    const target = event.target as HTMLElement;

    // Release the pointer capture
    target.releasePointerCapture(event.pointerId);

    target.removeEventListener('pointermove', pointerMoveHandler);
    target.removeEventListener('pointerup', pointerUpHandler);
  }

  return startDragging;
}

export function makePopover(
  container: HTMLElement,
  button: HTMLElement,
  dragStart?: (e: { x: number; y: number; pointerId: number }) => void
) {
  if (button) {
    button.addEventListener('pointerdown', e => {
      togglePopover(container);
    });
  }
  container.addEventListener('click', e => {
    if (e.detail === 3) {
      e.preventDefault();
      e.stopPropagation();
      togglePopover(container);
      window.getSelection()?.empty();
    }
  });

  if (dragStart) {
    let lastPointerId: number | null;

    container.addEventListener('pointerdown', e => {
      if (e.button === 0) {
        lastPointerId = e.pointerId;
      }
    });
    container.addEventListener('dragstart', e => {
      if (container.matches(':popover-open')) {
        // Dragging shouldn't dismiss the popover
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      togglePopover(container);
      if (lastPointerId) {
        dragStart({ x: e.clientX, y: e.clientY, pointerId: lastPointerId });
      }
    });
  }
}

export function togglePopover(container: HTMLElement) {
  if (container.hasAttribute('popover')) {
    container.classList.remove('shinynotebook-draggable-popover');
    container.hidePopover();
    container.removeAttribute('popover');
    window.jQuery(container).trigger('resize');
  } else {
    container.classList.add('shinynotebook-draggable-popover');
    const bounds = container.getBoundingClientRect();
    const width = container.offsetWidth;
    const height = container.offsetHeight;

    const style = container.style;
    style.setProperty('--shinynotebook-popover-left', `${bounds.left}px`);
    style.setProperty('--shinynotebook-popover-top', `${bounds.top}px`);
    style.setProperty('--shinynotebook-popover-width', `${width}px`);
    style.setProperty('--shinynotebook-popover-height', `${height}px`);

    container.setAttribute('popover', 'manual');
    container.showPopover();
    window.jQuery(container).trigger('resize');
  }
}
