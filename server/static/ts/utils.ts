/**
 * Same as querySelector, but throws an error if the element is not found.
 * @param sel Selector string to query
 * @returns The element (never null).
 */
export function querySelectorSafe<E extends Element = Element>(sel: string): E {
    const element = document.querySelector<E>(sel);
    if (!element) {
        throw new Error(`Could not find: ${sel}`);
    }
    return element;
}

/**
 * Waits for two animation frames to pass.
 * @returns A promise that resolves when the DOM has been updated.
 */
export function waitForDomUpdate() {
    return new Promise(resolve => {
        window.requestAnimationFrame(() => {
            window.requestAnimationFrame(resolve);
        });
    });
}

/**
 * Replaces an element with a feather icon.
 * @param element The element to replace.
 */
export function replaceFeatherIcon(element: HTMLElement) {
   // @ts-ignore
   const svgString = feather.icons[element.dataset.feather].toSvg({
      'stroke-width': 2.5
   });
   const svgDocument = new DOMParser().parseFromString(
      svgString, 'image/svg+xml'
   );
   const svgElement = svgDocument.querySelector('svg');
   element.parentNode.replaceChild(svgElement, element);
}

/**
 * Replaces all feather icons in a template fragment.
 * @param template The template fragment clone to replace icons in.
 */
export function replaceFeatherIconsIn(template: DocumentFragment) {
   template.querySelectorAll("[data-feather]").forEach(element => {
      if (element instanceof HTMLElement)
         replaceFeatherIcon(element);
   });
}
