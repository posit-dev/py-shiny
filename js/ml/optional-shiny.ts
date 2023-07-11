/**
 * A safe Shiny object that reflects we may be in an environment without Shiny
 * e.g. a static quarto document.
 *
 */
// eslint-disable-next-line @typescript-eslint/naming-convention
export const Shiny: typeof window.Shiny | undefined = window.Shiny;
