import { l as languageMap } from "../index-CKRNGLIi.js";
import { b as bracketIndenting, c as clikeComment } from "../index-BZh6eCR8.js";
languageMap.css = bracketIndenting({
  block: ["/*", "*/"]
});
languageMap.less = languageMap.scss = bracketIndenting();
languageMap.sass = {
  comments: clikeComment
  // Let's not bother with auto-indenting for sass
};
//# sourceMappingURL=css.js.map
