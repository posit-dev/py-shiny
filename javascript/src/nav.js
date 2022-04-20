// TODO:
// 1. should/can we get rid of bs3compat dependency?
// 2. selected attribute is great for using component directly, but does it make sense for qmd usage?

// Usage:
//
// Each <bslib-navs-*> component expects top-level <template>s with
// special classes:
//  * nav: title attr defines the nav item and contents are displayed when active
//  * nav-item: contents are displayed verbatim in the nav
//  * nav-spacer: for add spacing between nav items.
//  * nav-menu: a collection of .nav/.nav-items
//
// Example:
//
// <bslib-navs-* selected='two'>
//   <template class='nav' title='Tab 1' value='one'>
//     Tab 1 content
//   </template>
//   <template class='nav' title='Tab 2' value='two'>
//     Tab 2 content
//   </template>
//   <template class='nav-spacer'></template>
//   <template class='nav-item'>
//     <a href='https://google.com'> An external link </a>
//   </template>
//   <template class='nav-menu' title='Menu' value='menu'>
//     <template class='nav' title='Tab 3' value='three'>
//       Tab 3 content
//     </template>
//   </template>
// </bslib-navs-*>

import { tag } from './utils';

import {
  createTabFragment,
  buildTabset,
  getSelected,
  replaceChildren,
} from './nav-utils';

import { createCard } from './card';


class NavsTab extends HTMLElement {
  constructor() {
    self = super();

    debugger;

    const selected = getSelected(self);
    const tabset = buildTabset(self.children, selected);
    const tabs = createTabFragment(self, 'nav nav-tabs', tabset);

    replaceChildren(self, tabs);
  }
}

customElements.define('bslib-navs-tab', NavsTab);


class NavsPill extends HTMLElement {
  constructor() {
    self = super();

    const selected = getSelected(self);
    const tabset = buildTabset(self.children, selected);
    const pills = createTabFragment(self, 'nav nav-pills', tabset);

    replaceChildren(self, pills);
  }
}

customElements.define('bslib-navs-pill', NavsPill);


class NavsTabCard extends HTMLElement {
  constructor() {
    self = super();

    const selected = getSelected(self);
    const tabset = buildTabset(self.children, selected);
    const tabs = createTabFragment(self, 'nav nav-tabs', tabset);
    const nav = tabs[0];
    const content = tabs[1];
    // https://getbootstrap.com/docs/5.0/components/card/#navigation
    nav.classList.add('card-header-tabs');
    const card = createCard(content, nav);

    replaceChildren(self, card);
  }
}

customElements.define('bslib-navs-tab-card', NavsTabCard);


class NavsPillCard extends HTMLElement {
  constructor() {
    self = super();

    const selected = getSelected(self);
    const tabset = buildTabset(self.children, selected);
    const pills = createTabFragment(self, 'nav nav-pills', tabset);
    const nav = pills[0];
    const content = pills[1];
    const above = self.getAttribute('placement') !== 'below';
    if (above) nav.classList.add('card-header-pills');
    const card = above
      ? createCard(content, nav)
      : createCard(content, null, nav);
    replaceChildren(self, card);
  }
}

customElements.define('bslib-navs-pill-card', NavsPillCard);


class NavsPillList extends HTMLElement {
  constructor() {
    self = super();

    const selected = getSelected(self);
    // TODO: implement textFilter!
    const tabset = buildTabset(self.children, selected);
    const pills = createTabFragment(self, 'nav nav-pills nav-stacked', tabset);

    const nav = pills[0];
    const content = pills[1];

    let navClass = 'col-sm-' + self.getAttribute('widthNav');
    if (self.getAttribute('well')) {
      navClass = navClass + ' well';
    }

    let row = tag(
      'div', {class: 'row'},
      tag('div', {class: navClass}, nav),
      tag('div', {class: 'col-sm-' + self.getAttribute('widthContent')}, content),
    );

    replaceChildren(self, row);
  }
}

customElements.define('bslib-navs-pill-list', NavsPillList);


class NavsBar extends HTMLElement {
  constructor() {
    self = super();

    const selected = getSelected(self);
    const tabset = buildTabset(self.children, selected);
    const navbar = createTabFragment(self, 'nav navbar-nav', tabset);

    // TODO: implement!
    //const nav = tag('nav', {role: 'navigation', class: navbarClass});
    //replaceChildren(self, nav);
  }
}

customElements.define('bslib-navs-bar', NavsBar);
