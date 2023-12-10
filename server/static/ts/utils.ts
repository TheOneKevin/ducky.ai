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
