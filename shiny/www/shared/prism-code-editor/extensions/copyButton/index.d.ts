import { BasicExtension } from '../../types.js';
/**
 * Creates a static copy button that can be added to the overlays of an editor or code
 * block. The `firstChild` of the element returned is the button itself.
 */
declare const createCopyButton: () => HTMLDivElement;
/**
 * Extension that adds a copy button to the editor.
 * Probably best used with a read-only editor.
 * You must also import styles from `prism-code-editor/copy-button.css`.
 */
declare const copyButton: () => BasicExtension;
export { copyButton, createCopyButton };
