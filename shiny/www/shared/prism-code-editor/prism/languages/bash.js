import { l as languages } from "../../index-C1_GGQ8y.js";
var envVars = "\\b(?:BASH(?:OPTS|_ALIASES|_ARG[CV]|_CMDS|_COMPLETION_COMPAT_DIR|_LINENO|_REMATCH|_SOURCE|_VERSINFO|_VERSION)?|COLORTERM|COLUMNS|COMP_WORDBREAKS|DBUS_SESSION_BUS_ADDRESS|DEFAULTS_PATH|DESKTOP_SESSION|DIRSTACK|DISPLAY|E?UID|GDMSESSION|GDM_LANG|GNOME_KEYRING_CONTROL|GNOME_KEYRING_PID|GPG_AGENT_INFO|GROUPS|HISTCONTROL|HISTFILE|HISTFILESIZE|HISTSIZE|HOME|HOSTNAME|HOSTTYPE|IFS|INSTANCE|JOB|LANG|LANGUAGE|LC_(?:ADDRESS|ALL|IDENTIFICATION|MEASUREMENT|MONETARY|NAME|NUMERIC|PAPER|TELEPHONE|TIME)|LESSCLOSE|LESSOPEN|LINES|LOGNAME|LS_COLORS|MACHTYPE|MAILCHECK|MANDATORY_PATH|NO_AT_BRIDGE|OLDPWD|OPTERR|OPTIND|ORBIT_SOCKETDIR|OSTYPE|PAPERSIZE|PATH|PIPESTATUS|PPID|PS[1-4]|PWD|RANDOM|REPLY|SECONDS|SELINUX_INIT|SESSION|SESSIONTYPE|SESSION_MANAGER|SHELL|SHELLOPTS|SHLVL|SSH_AUTH_SOCK|TERM|UPSTART_EVENTS|UPSTART_INSTANCE|UPSTART_JOB|UPSTART_SESSION|USER|WINDOWID|XAUTHORITY|XDG_(?:CONFIG_DIRS|CURRENT_DESKTOP|DATA_DIRS|GREETER_DATA_DIR|MENU_PREFIX|RUNTIME_DIR|SEAT|SEAT_PATH|SESSION_DESKTOP|SESSION_ID|SESSION_PATH|SESSION_TYPE|VTNR)|XMODIFIERS)\\b";
var commandAfterHeredoc = {
  pattern: /(^(["']?)\w+\2)[ 	]+\S.*/,
  lookbehind: true,
  alias: "punctuation"
  // this looks reasonably well in all themes
};
var variableInside = {
  "variable": /^\$\(|^`|\)$|`$/
};
var insideString = {
  "bash": commandAfterHeredoc,
  "environment": {
    pattern: RegExp("\\$" + envVars),
    alias: "constant"
  },
  "variable": [
    // [0]: Arithmetic Environment
    {
      pattern: /\$?\(\([^]*?\)\)/g,
      greedy: true,
      inside: {
        // If there is a $ sign at the beginning highlight $(( and )) as variable
        "variable": [
          {
            pattern: /(^\$[^]+)../,
            lookbehind: true
          },
          /^\$\(\(/
        ],
        "number": /\b0x[a-fA-F\d]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:[Ee]-?\d+)?/,
        // Operators according to https://www.gnu.org/software/bash/manual/bashref.html#Shell-Arithmetic
        "operator": /--|\+\+|&&|\|\||(?:\*\*|<<|>>|[%&|^!=<>/*+-])=?|[?:~]/,
        // If there is no $ sign at the beginning highlight (( and )) as punctuation
        "punctuation": /\(\(?|\)\)?|,|;/
      }
    },
    // [1]: Command Substitution
    {
      pattern: /\$\((?:[^()]|\([^)]*\))*\)|`[^`]+`/g,
      greedy: true,
      inside: variableInside
    },
    // [2]: Brace expansion
    {
      pattern: /\$\{[^}]*\}/g,
      greedy: true,
      inside: {
        "operator": /:[?=+-]?|[!/]|##?|%%?|\^\^?|,,?/,
        "punctuation": /[[\]]/,
        "environment": {
          pattern: RegExp("(\\{)" + envVars),
          lookbehind: true,
          alias: "constant"
        }
      }
    },
    /\$(?:\w+|[#?*!@$])/
  ],
  // Escape sequences from echo and printf's manuals, and escaped quotes.
  "entity": /\\(?:[abceEfnrtv\\"]|O?[0-7]{1,3}|U[a-fA-F\d]{8}|u[a-fA-F\d]{4}|x[a-fA-F\d]{1,2})/
};
var bash = commandAfterHeredoc.inside = languages.sh = languages.shell = languages.bash = {
  "shebang": {
    pattern: /^#!\s*\/.*/,
    alias: "important"
  },
  "comment": {
    pattern: /(^|[^\\"{$])#.*/,
    lookbehind: true
  },
  "function-name": [
    // a) function foo {
    // b) foo() {
    // c) function foo() {
    // but not “foo {”
    {
      // a) and c)
      pattern: /(\bfunction\s+)[\w-]+(?=(?:\s*\(?:\s*\))?\s*\{)/,
      lookbehind: true,
      alias: "function"
    },
    {
      // b)
      pattern: /\b[\w-]+(?=\s*\(\s*\)\s*\{)/,
      alias: "function"
    }
  ],
  // Highlight variable names as variables in for and select beginnings.
  "for-or-select": {
    pattern: /(\b(?:for|select)\s+)\w+(?=\s+in\s)/,
    lookbehind: true,
    alias: "variable"
  },
  // Highlight variable names as variables in the left-hand part
  // of assignments (“=” and “+=”).
  "assign-left": {
    pattern: /(^|[\s;|&]|[<>]\()\w+(?:\.\w+)*(?=\+?=)/,
    lookbehind: true,
    alias: "variable",
    inside: {
      "environment": {
        pattern: RegExp("(^|[\\s;|&]|[<>]\\()" + envVars),
        lookbehind: true,
        alias: "constant"
      }
    }
  },
  // Highlight parameter names as variables
  "parameter": {
    pattern: /(^|\s)-{1,2}(?:\w+:[+-]?)?\w+(?:\.\w+)*(?![^\s=])/,
    lookbehind: true,
    alias: "variable"
  },
  "string": [
    // Support for Here-documents https://en.wikipedia.org/wiki/Here_document
    {
      pattern: /((?:^|[^<])<<-?\s*)(\w+)\s[^]*?\n\2/g,
      lookbehind: true,
      greedy: true,
      inside: insideString
    },
    // Here-document with quotes around the tag
    // → No expansion (so no “inside”).
    {
      pattern: /((?:^|[^<])<<-?\s*)(["'])(\w+)\2\s[^]*?\n\3/g,
      lookbehind: true,
      greedy: true,
      inside: {
        "bash": commandAfterHeredoc
      }
    },
    // “Normal” string
    {
      // https://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html
      pattern: /(^|[^\\](?:\\\\)*)"(?:\\[^]|\$\([^)]+\)|\$(?!\()|`[^`]+`|[^\\"`$])*"/g,
      lookbehind: true,
      greedy: true,
      inside: insideString
    },
    {
      // https://www.gnu.org/software/bash/manual/html_node/Single-Quotes.html
      pattern: /(^|[^\\$])'[^']*'/g,
      lookbehind: true,
      greedy: true
    },
    {
      // https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html
      pattern: /\$'(?:\\[^]|[^\\'])*'/g,
      greedy: true,
      inside: {
        "entity": insideString.entity
      }
    }
  ],
  "environment": {
    pattern: RegExp("\\$?" + envVars),
    alias: "constant"
  },
  "variable": insideString.variable,
  "function": {
    pattern: /(^|[\s;|&]|[<>]\()(?:add|apropos|apt|apt-cache|apt-get|aptitude|aspell|automysqlbackup|basename|bash|bc|bconsole|bg|bzip2|cal|cargo|cat|c?fdisk|chgrp|chkconfig|chmod|chown|chroot|cksum|clear|cmp|column|comm|composer|cron|crontab|c?split|curl|cut|date|dc|dd|ddrescue|debootstrap|df|diff3?|dig|dircolors|dirname|dirs?|dmesg|docker|docker-compose|du|[ef]?grep|eject|env|ethtool|expand|expect|expr|fdformat|fg|file|find|fmt|fold|format|free|fsck|fuser|g?awk|git|g?parted|groupadd|groupdel|groupmod|groups|grub-mkconfig|halt|head|hg|history|host|hostname|iconv|id|ifconfig|ifdown|ifup|import|install|ip|java|jobs|join|killall|less|link|ln|logname|logrotate|look|lpc|lprint[dq]?|lprm?|ls|lsof|lynx|make|man|mc|mdadm|mkconfig|mkdir|mke2fs|mkfifo|mkfs|mkisofs|mknod|mkswap|mm?v|more|most|mtools|m?tr|mutt|nano|nc|netstat|nice|nl|node|nohup|notify-send|nslookup|op|open|passwd|paste|pathchk|ping|p?kill|p?npm|podman|podman-compose|popd|pr|printcap|printenv|ps|pushd|pv|quota|quotacheck|quotactl|ra[mr]|reboot|remsync|rename|renice|rev|rmdir|rp?m|r?sync|[sr]?cp|screen|sdiff|se[dq]|sendmail|service|s?ftp|shellcheck|shuf|shutdown|sleep|s?locate|[sz]?sh|stat|strace|sudo|sum?|suspend|swapon|sysctl|tac|tail|tar|tee|time|timeout|h?top|touch|traceroute|t?sort|tty|u?mount|uname|unexpand|uniq|units|unrar|unshar|unzip|update-grub|uptime|useradd|userdel|usermod|users|uudecode|uuencode|v|vcpkg|vdir|vim?|virsh|vmstat|wait|watch|wc|wget|whereis|which|who|whoami|write|xargs|xdg-open|yarn|yes|zenity|g?zip|zsh|zypper)(?=$|[)\s;|&])/,
    lookbehind: true
  },
  "keyword": {
    pattern: /(^|[\s;|&]|[<>]\()(?:case|do|done|elif|else|esac|fi|for|function|if|in|select|then|until|while)(?=$|[)\s;|&])/,
    lookbehind: true
  },
  // https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html
  "builtin": {
    pattern: /(^|[\s;|&]|[<>]\()(?:\.|:|alias|bind|break|builtin|caller|cd|command|continue|declare|echo|enable|eval|exec|exit|export|getopts|hash|help|[ls]et|local|logout|mapfile|printf|pwd|read|readarray|readonly|return|shift|shopt|source|test|times|trap|type|typeset|ulimit|umask|unalias|unset)(?=$|[)\s;|&])/,
    lookbehind: true,
    // Alias added to make those easier to distinguish from strings.
    alias: "class-name"
  },
  "boolean": {
    pattern: /(^|[\s;|&]|[<>]\()(?:false|true)(?=$|[)\s;|&])/,
    lookbehind: true
  },
  "file-descriptor": {
    pattern: /\B&\d\b/,
    alias: "important"
  },
  "operator": {
    // Lots of redirections here, but not just that.
    pattern: /\d?<>|>\||\+=|=[=~]?|!=?|<<[<-]?|[&\d]?>>|\d[<>]&?|[<>][&=]?|&[>&]?|\|[&|]?/,
    inside: {
      "file-descriptor": {
        pattern: /^\d/,
        alias: "important"
      }
    }
  },
  "punctuation": /\$?\(\(?|\)\)?|\.\.|[[\]{};\\]/,
  "number": {
    pattern: /(^|\s)(?:[1-9]\d*|0)(?:[.,]\d+)?\b/,
    lookbehind: true
  }
};
[
  "comment",
  "function-name",
  "for-or-select",
  "assign-left",
  "parameter",
  "string",
  "environment",
  "function",
  "keyword",
  "builtin",
  "boolean",
  "file-descriptor",
  "operator",
  "punctuation",
  "number"
].forEach((copied) => variableInside[copied] = bash[copied]);
//# sourceMappingURL=bash.js.map
