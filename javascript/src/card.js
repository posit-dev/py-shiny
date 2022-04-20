import { tag } from './utils'

function createCard(body, header, footer) {
  let card = tag('div', {class: 'card'});
  if (header) {
    card.append(tag('div', {class: 'card-header'}, header));
  }
  card.append(tag('div', {class: 'card-body'}, body));
  if (footer) {
      card.append(tag('div', {class: 'card-footer'}, footer));
  }
  return card;
}

export { createCard };