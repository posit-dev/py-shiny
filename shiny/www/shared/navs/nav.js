(function() {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __markAsModule = function(target) {
    return __defProp(target, "__esModule", { value: true });
  };
  var __commonJS = function(cb, mod) {
    return function __require() {
      return mod || (0, cb[Object.keys(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
    };
  };
  var __reExport = function(target, module, desc) {
    if (module && typeof module === "object" || typeof module === "function")
      for (var keys = __getOwnPropNames(module), i = 0, n = keys.length, key; i < n; i++) {
        key = keys[i];
        if (!__hasOwnProp.call(target, key) && key !== "default")
          __defProp(target, key, { get: function(k) {
            return module[k];
          }.bind(null, key), enumerable: !(desc = __getOwnPropDesc(module, key)) || desc.enumerable });
      }
    return target;
  };
  var __toModule = function(module) {
    return __reExport(__markAsModule(__defProp(module != null ? __create(__getProtoOf(module)) : {}, "default", module && module.__esModule && "default" in module ? { get: function() {
      return module.default;
    }, enumerable: true } : { value: module, enumerable: true })), module);
  };

  // node_modules/core-js/internals/global.js
  var require_global = __commonJS({
    "node_modules/core-js/internals/global.js": function(exports, module) {
      var check = function(it) {
        return it && it.Math == Math && it;
      };
      module.exports = check(typeof globalThis == "object" && globalThis) || check(typeof window == "object" && window) || check(typeof self == "object" && self) || check(typeof global == "object" && global) || function() {
        return this;
      }() || Function("return this")();
    }
  });

  // node_modules/core-js/internals/fails.js
  var require_fails = __commonJS({
    "node_modules/core-js/internals/fails.js": function(exports, module) {
      module.exports = function(exec) {
        try {
          return !!exec();
        } catch (error) {
          return true;
        }
      };
    }
  });

  // node_modules/core-js/internals/descriptors.js
  var require_descriptors = __commonJS({
    "node_modules/core-js/internals/descriptors.js": function(exports, module) {
      var fails6 = require_fails();
      module.exports = !fails6(function() {
        return Object.defineProperty({}, 1, { get: function() {
          return 7;
        } })[1] != 7;
      });
    }
  });

  // node_modules/core-js/internals/object-property-is-enumerable.js
  var require_object_property_is_enumerable = __commonJS({
    "node_modules/core-js/internals/object-property-is-enumerable.js": function(exports) {
      "use strict";
      var $propertyIsEnumerable2 = {}.propertyIsEnumerable;
      var getOwnPropertyDescriptor3 = Object.getOwnPropertyDescriptor;
      var NASHORN_BUG = getOwnPropertyDescriptor3 && !$propertyIsEnumerable2.call({ 1: 2 }, 1);
      exports.f = NASHORN_BUG ? function propertyIsEnumerable2(V) {
        var descriptor = getOwnPropertyDescriptor3(this, V);
        return !!descriptor && descriptor.enumerable;
      } : $propertyIsEnumerable2;
    }
  });

  // node_modules/core-js/internals/create-property-descriptor.js
  var require_create_property_descriptor = __commonJS({
    "node_modules/core-js/internals/create-property-descriptor.js": function(exports, module) {
      module.exports = function(bitmap, value) {
        return {
          enumerable: !(bitmap & 1),
          configurable: !(bitmap & 2),
          writable: !(bitmap & 4),
          value: value
        };
      };
    }
  });

  // node_modules/core-js/internals/classof-raw.js
  var require_classof_raw = __commonJS({
    "node_modules/core-js/internals/classof-raw.js": function(exports, module) {
      var toString2 = {}.toString;
      module.exports = function(it) {
        return toString2.call(it).slice(8, -1);
      };
    }
  });

  // node_modules/core-js/internals/indexed-object.js
  var require_indexed_object = __commonJS({
    "node_modules/core-js/internals/indexed-object.js": function(exports, module) {
      var fails6 = require_fails();
      var classof = require_classof_raw();
      var split = "".split;
      module.exports = fails6(function() {
        return !Object("z").propertyIsEnumerable(0);
      }) ? function(it) {
        return classof(it) == "String" ? split.call(it, "") : Object(it);
      } : Object;
    }
  });

  // node_modules/core-js/internals/require-object-coercible.js
  var require_require_object_coercible = __commonJS({
    "node_modules/core-js/internals/require-object-coercible.js": function(exports, module) {
      module.exports = function(it) {
        if (it == void 0)
          throw TypeError("Can't call method on " + it);
        return it;
      };
    }
  });

  // node_modules/core-js/internals/to-indexed-object.js
  var require_to_indexed_object = __commonJS({
    "node_modules/core-js/internals/to-indexed-object.js": function(exports, module) {
      var IndexedObject = require_indexed_object();
      var requireObjectCoercible2 = require_require_object_coercible();
      module.exports = function(it) {
        return IndexedObject(requireObjectCoercible2(it));
      };
    }
  });

  // node_modules/core-js/internals/is-object.js
  var require_is_object = __commonJS({
    "node_modules/core-js/internals/is-object.js": function(exports, module) {
      module.exports = function(it) {
        return typeof it === "object" ? it !== null : typeof it === "function";
      };
    }
  });

  // node_modules/core-js/internals/to-primitive.js
  var require_to_primitive = __commonJS({
    "node_modules/core-js/internals/to-primitive.js": function(exports, module) {
      var isObject6 = require_is_object();
      module.exports = function(input, PREFERRED_STRING) {
        if (!isObject6(input))
          return input;
        var fn, val;
        if (PREFERRED_STRING && typeof (fn = input.toString) == "function" && !isObject6(val = fn.call(input)))
          return val;
        if (typeof (fn = input.valueOf) == "function" && !isObject6(val = fn.call(input)))
          return val;
        if (!PREFERRED_STRING && typeof (fn = input.toString) == "function" && !isObject6(val = fn.call(input)))
          return val;
        throw TypeError("Can't convert object to primitive value");
      };
    }
  });

  // node_modules/core-js/internals/to-object.js
  var require_to_object = __commonJS({
    "node_modules/core-js/internals/to-object.js": function(exports, module) {
      var requireObjectCoercible2 = require_require_object_coercible();
      module.exports = function(argument) {
        return Object(requireObjectCoercible2(argument));
      };
    }
  });

  // node_modules/core-js/internals/has.js
  var require_has = __commonJS({
    "node_modules/core-js/internals/has.js": function(exports, module) {
      var toObject4 = require_to_object();
      var hasOwnProperty = {}.hasOwnProperty;
      module.exports = Object.hasOwn || function hasOwn(it, key) {
        return hasOwnProperty.call(toObject4(it), key);
      };
    }
  });

  // node_modules/core-js/internals/document-create-element.js
  var require_document_create_element = __commonJS({
    "node_modules/core-js/internals/document-create-element.js": function(exports, module) {
      var global6 = require_global();
      var isObject6 = require_is_object();
      var document2 = global6.document;
      var EXISTS = isObject6(document2) && isObject6(document2.createElement);
      module.exports = function(it) {
        return EXISTS ? document2.createElement(it) : {};
      };
    }
  });

  // node_modules/core-js/internals/ie8-dom-define.js
  var require_ie8_dom_define = __commonJS({
    "node_modules/core-js/internals/ie8-dom-define.js": function(exports, module) {
      var DESCRIPTORS5 = require_descriptors();
      var fails6 = require_fails();
      var createElement = require_document_create_element();
      module.exports = !DESCRIPTORS5 && !fails6(function() {
        return Object.defineProperty(createElement("div"), "a", {
          get: function() {
            return 7;
          }
        }).a != 7;
      });
    }
  });

  // node_modules/core-js/internals/object-get-own-property-descriptor.js
  var require_object_get_own_property_descriptor = __commonJS({
    "node_modules/core-js/internals/object-get-own-property-descriptor.js": function(exports) {
      var DESCRIPTORS5 = require_descriptors();
      var propertyIsEnumerableModule2 = require_object_property_is_enumerable();
      var createPropertyDescriptor2 = require_create_property_descriptor();
      var toIndexedObject3 = require_to_indexed_object();
      var toPrimitive2 = require_to_primitive();
      var has3 = require_has();
      var IE8_DOM_DEFINE = require_ie8_dom_define();
      var $getOwnPropertyDescriptor2 = Object.getOwnPropertyDescriptor;
      exports.f = DESCRIPTORS5 ? $getOwnPropertyDescriptor2 : function getOwnPropertyDescriptor3(O, P) {
        O = toIndexedObject3(O);
        P = toPrimitive2(P, true);
        if (IE8_DOM_DEFINE)
          try {
            return $getOwnPropertyDescriptor2(O, P);
          } catch (error) {
          }
        if (has3(O, P))
          return createPropertyDescriptor2(!propertyIsEnumerableModule2.f.call(O, P), O[P]);
      };
    }
  });

  // node_modules/core-js/internals/an-object.js
  var require_an_object = __commonJS({
    "node_modules/core-js/internals/an-object.js": function(exports, module) {
      var isObject6 = require_is_object();
      module.exports = function(it) {
        if (!isObject6(it)) {
          throw TypeError(String(it) + " is not an object");
        }
        return it;
      };
    }
  });

  // node_modules/core-js/internals/object-define-property.js
  var require_object_define_property = __commonJS({
    "node_modules/core-js/internals/object-define-property.js": function(exports) {
      var DESCRIPTORS5 = require_descriptors();
      var IE8_DOM_DEFINE = require_ie8_dom_define();
      var anObject4 = require_an_object();
      var toPrimitive2 = require_to_primitive();
      var $defineProperty2 = Object.defineProperty;
      exports.f = DESCRIPTORS5 ? $defineProperty2 : function defineProperty4(O, P, Attributes) {
        anObject4(O);
        P = toPrimitive2(P, true);
        anObject4(Attributes);
        if (IE8_DOM_DEFINE)
          try {
            return $defineProperty2(O, P, Attributes);
          } catch (error) {
          }
        if ("get" in Attributes || "set" in Attributes)
          throw TypeError("Accessors not supported");
        if ("value" in Attributes)
          O[P] = Attributes.value;
        return O;
      };
    }
  });

  // node_modules/core-js/internals/create-non-enumerable-property.js
  var require_create_non_enumerable_property = __commonJS({
    "node_modules/core-js/internals/create-non-enumerable-property.js": function(exports, module) {
      var DESCRIPTORS5 = require_descriptors();
      var definePropertyModule2 = require_object_define_property();
      var createPropertyDescriptor2 = require_create_property_descriptor();
      module.exports = DESCRIPTORS5 ? function(object, key, value) {
        return definePropertyModule2.f(object, key, createPropertyDescriptor2(1, value));
      } : function(object, key, value) {
        object[key] = value;
        return object;
      };
    }
  });

  // node_modules/core-js/internals/set-global.js
  var require_set_global = __commonJS({
    "node_modules/core-js/internals/set-global.js": function(exports, module) {
      var global6 = require_global();
      var createNonEnumerableProperty4 = require_create_non_enumerable_property();
      module.exports = function(key, value) {
        try {
          createNonEnumerableProperty4(global6, key, value);
        } catch (error) {
          global6[key] = value;
        }
        return value;
      };
    }
  });

  // node_modules/core-js/internals/shared-store.js
  var require_shared_store = __commonJS({
    "node_modules/core-js/internals/shared-store.js": function(exports, module) {
      var global6 = require_global();
      var setGlobal = require_set_global();
      var SHARED = "__core-js_shared__";
      var store = global6[SHARED] || setGlobal(SHARED, {});
      module.exports = store;
    }
  });

  // node_modules/core-js/internals/inspect-source.js
  var require_inspect_source = __commonJS({
    "node_modules/core-js/internals/inspect-source.js": function(exports, module) {
      var store = require_shared_store();
      var functionToString = Function.toString;
      if (typeof store.inspectSource != "function") {
        store.inspectSource = function(it) {
          return functionToString.call(it);
        };
      }
      module.exports = store.inspectSource;
    }
  });

  // node_modules/core-js/internals/native-weak-map.js
  var require_native_weak_map = __commonJS({
    "node_modules/core-js/internals/native-weak-map.js": function(exports, module) {
      var global6 = require_global();
      var inspectSource = require_inspect_source();
      var WeakMap = global6.WeakMap;
      module.exports = typeof WeakMap === "function" && /native code/.test(inspectSource(WeakMap));
    }
  });

  // node_modules/core-js/internals/is-pure.js
  var require_is_pure = __commonJS({
    "node_modules/core-js/internals/is-pure.js": function(exports, module) {
      module.exports = false;
    }
  });

  // node_modules/core-js/internals/shared.js
  var require_shared = __commonJS({
    "node_modules/core-js/internals/shared.js": function(exports, module) {
      var IS_PURE3 = require_is_pure();
      var store = require_shared_store();
      (module.exports = function(key, value) {
        return store[key] || (store[key] = value !== void 0 ? value : {});
      })("versions", []).push({
        version: "3.15.2",
        mode: IS_PURE3 ? "pure" : "global",
        copyright: "\xA9 2021 Denis Pushkarev (zloirock.ru)"
      });
    }
  });

  // node_modules/core-js/internals/uid.js
  var require_uid = __commonJS({
    "node_modules/core-js/internals/uid.js": function(exports, module) {
      var id = 0;
      var postfix = Math.random();
      module.exports = function(key) {
        return "Symbol(" + String(key === void 0 ? "" : key) + ")_" + (++id + postfix).toString(36);
      };
    }
  });

  // node_modules/core-js/internals/shared-key.js
  var require_shared_key = __commonJS({
    "node_modules/core-js/internals/shared-key.js": function(exports, module) {
      var shared2 = require_shared();
      var uid2 = require_uid();
      var keys = shared2("keys");
      module.exports = function(key) {
        return keys[key] || (keys[key] = uid2(key));
      };
    }
  });

  // node_modules/core-js/internals/hidden-keys.js
  var require_hidden_keys = __commonJS({
    "node_modules/core-js/internals/hidden-keys.js": function(exports, module) {
      module.exports = {};
    }
  });

  // node_modules/core-js/internals/internal-state.js
  var require_internal_state = __commonJS({
    "node_modules/core-js/internals/internal-state.js": function(exports, module) {
      var NATIVE_WEAK_MAP = require_native_weak_map();
      var global6 = require_global();
      var isObject6 = require_is_object();
      var createNonEnumerableProperty4 = require_create_non_enumerable_property();
      var objectHas = require_has();
      var shared2 = require_shared_store();
      var sharedKey2 = require_shared_key();
      var hiddenKeys2 = require_hidden_keys();
      var OBJECT_ALREADY_INITIALIZED = "Object already initialized";
      var WeakMap = global6.WeakMap;
      var set;
      var get;
      var has3;
      var enforce = function(it) {
        return has3(it) ? get(it) : set(it, {});
      };
      var getterFor = function(TYPE) {
        return function(it) {
          var state;
          if (!isObject6(it) || (state = get(it)).type !== TYPE) {
            throw TypeError("Incompatible receiver, " + TYPE + " required");
          }
          return state;
        };
      };
      if (NATIVE_WEAK_MAP || shared2.state) {
        store = shared2.state || (shared2.state = new WeakMap());
        wmget = store.get;
        wmhas = store.has;
        wmset = store.set;
        set = function(it, metadata) {
          if (wmhas.call(store, it))
            throw new TypeError(OBJECT_ALREADY_INITIALIZED);
          metadata.facade = it;
          wmset.call(store, it, metadata);
          return metadata;
        };
        get = function(it) {
          return wmget.call(store, it) || {};
        };
        has3 = function(it) {
          return wmhas.call(store, it);
        };
      } else {
        STATE = sharedKey2("state");
        hiddenKeys2[STATE] = true;
        set = function(it, metadata) {
          if (objectHas(it, STATE))
            throw new TypeError(OBJECT_ALREADY_INITIALIZED);
          metadata.facade = it;
          createNonEnumerableProperty4(it, STATE, metadata);
          return metadata;
        };
        get = function(it) {
          return objectHas(it, STATE) ? it[STATE] : {};
        };
        has3 = function(it) {
          return objectHas(it, STATE);
        };
      }
      var store;
      var wmget;
      var wmhas;
      var wmset;
      var STATE;
      module.exports = {
        set: set,
        get: get,
        has: has3,
        enforce: enforce,
        getterFor: getterFor
      };
    }
  });

  // node_modules/core-js/internals/redefine.js
  var require_redefine = __commonJS({
    "node_modules/core-js/internals/redefine.js": function(exports, module) {
      var global6 = require_global();
      var createNonEnumerableProperty4 = require_create_non_enumerable_property();
      var has3 = require_has();
      var setGlobal = require_set_global();
      var inspectSource = require_inspect_source();
      var InternalStateModule3 = require_internal_state();
      var getInternalState3 = InternalStateModule3.get;
      var enforceInternalState = InternalStateModule3.enforce;
      var TEMPLATE = String(String).split("String");
      (module.exports = function(O, key, value, options) {
        var unsafe = options ? !!options.unsafe : false;
        var simple = options ? !!options.enumerable : false;
        var noTargetGet = options ? !!options.noTargetGet : false;
        var state;
        if (typeof value == "function") {
          if (typeof key == "string" && !has3(value, "name")) {
            createNonEnumerableProperty4(value, "name", key);
          }
          state = enforceInternalState(value);
          if (!state.source) {
            state.source = TEMPLATE.join(typeof key == "string" ? key : "");
          }
        }
        if (O === global6) {
          if (simple)
            O[key] = value;
          else
            setGlobal(key, value);
          return;
        } else if (!unsafe) {
          delete O[key];
        } else if (!noTargetGet && O[key]) {
          simple = true;
        }
        if (simple)
          O[key] = value;
        else
          createNonEnumerableProperty4(O, key, value);
      })(Function.prototype, "toString", function toString2() {
        return typeof this == "function" && getInternalState3(this).source || inspectSource(this);
      });
    }
  });

  // node_modules/core-js/internals/path.js
  var require_path = __commonJS({
    "node_modules/core-js/internals/path.js": function(exports, module) {
      var global6 = require_global();
      module.exports = global6;
    }
  });

  // node_modules/core-js/internals/get-built-in.js
  var require_get_built_in = __commonJS({
    "node_modules/core-js/internals/get-built-in.js": function(exports, module) {
      var path = require_path();
      var global6 = require_global();
      var aFunction2 = function(variable) {
        return typeof variable == "function" ? variable : void 0;
      };
      module.exports = function(namespace, method) {
        return arguments.length < 2 ? aFunction2(path[namespace]) || aFunction2(global6[namespace]) : path[namespace] && path[namespace][method] || global6[namespace] && global6[namespace][method];
      };
    }
  });

  // node_modules/core-js/internals/to-integer.js
  var require_to_integer = __commonJS({
    "node_modules/core-js/internals/to-integer.js": function(exports, module) {
      var ceil = Math.ceil;
      var floor = Math.floor;
      module.exports = function(argument) {
        return isNaN(argument = +argument) ? 0 : (argument > 0 ? floor : ceil)(argument);
      };
    }
  });

  // node_modules/core-js/internals/to-length.js
  var require_to_length = __commonJS({
    "node_modules/core-js/internals/to-length.js": function(exports, module) {
      var toInteger = require_to_integer();
      var min2 = Math.min;
      module.exports = function(argument) {
        return argument > 0 ? min2(toInteger(argument), 9007199254740991) : 0;
      };
    }
  });

  // node_modules/core-js/internals/to-absolute-index.js
  var require_to_absolute_index = __commonJS({
    "node_modules/core-js/internals/to-absolute-index.js": function(exports, module) {
      var toInteger = require_to_integer();
      var max2 = Math.max;
      var min2 = Math.min;
      module.exports = function(index, length) {
        var integer = toInteger(index);
        return integer < 0 ? max2(integer + length, 0) : min2(integer, length);
      };
    }
  });

  // node_modules/core-js/internals/array-includes.js
  var require_array_includes = __commonJS({
    "node_modules/core-js/internals/array-includes.js": function(exports, module) {
      var toIndexedObject3 = require_to_indexed_object();
      var toLength4 = require_to_length();
      var toAbsoluteIndex2 = require_to_absolute_index();
      var createMethod = function(IS_INCLUDES) {
        return function($this, el, fromIndex) {
          var O = toIndexedObject3($this);
          var length = toLength4(O.length);
          var index = toAbsoluteIndex2(fromIndex, length);
          var value;
          if (IS_INCLUDES && el != el)
            while (length > index) {
              value = O[index++];
              if (value != value)
                return true;
            }
          else
            for (; length > index; index++) {
              if ((IS_INCLUDES || index in O) && O[index] === el)
                return IS_INCLUDES || index || 0;
            }
          return !IS_INCLUDES && -1;
        };
      };
      module.exports = {
        includes: createMethod(true),
        indexOf: createMethod(false)
      };
    }
  });

  // node_modules/core-js/internals/object-keys-internal.js
  var require_object_keys_internal = __commonJS({
    "node_modules/core-js/internals/object-keys-internal.js": function(exports, module) {
      var has3 = require_has();
      var toIndexedObject3 = require_to_indexed_object();
      var indexOf2 = require_array_includes().indexOf;
      var hiddenKeys2 = require_hidden_keys();
      module.exports = function(object, names) {
        var O = toIndexedObject3(object);
        var i = 0;
        var result = [];
        var key;
        for (key in O)
          !has3(hiddenKeys2, key) && has3(O, key) && result.push(key);
        while (names.length > i)
          if (has3(O, key = names[i++])) {
            ~indexOf2(result, key) || result.push(key);
          }
        return result;
      };
    }
  });

  // node_modules/core-js/internals/enum-bug-keys.js
  var require_enum_bug_keys = __commonJS({
    "node_modules/core-js/internals/enum-bug-keys.js": function(exports, module) {
      module.exports = [
        "constructor",
        "hasOwnProperty",
        "isPrototypeOf",
        "propertyIsEnumerable",
        "toLocaleString",
        "toString",
        "valueOf"
      ];
    }
  });

  // node_modules/core-js/internals/object-get-own-property-names.js
  var require_object_get_own_property_names = __commonJS({
    "node_modules/core-js/internals/object-get-own-property-names.js": function(exports) {
      var internalObjectKeys = require_object_keys_internal();
      var enumBugKeys = require_enum_bug_keys();
      var hiddenKeys2 = enumBugKeys.concat("length", "prototype");
      exports.f = Object.getOwnPropertyNames || function getOwnPropertyNames2(O) {
        return internalObjectKeys(O, hiddenKeys2);
      };
    }
  });

  // node_modules/core-js/internals/object-get-own-property-symbols.js
  var require_object_get_own_property_symbols = __commonJS({
    "node_modules/core-js/internals/object-get-own-property-symbols.js": function(exports) {
      exports.f = Object.getOwnPropertySymbols;
    }
  });

  // node_modules/core-js/internals/own-keys.js
  var require_own_keys = __commonJS({
    "node_modules/core-js/internals/own-keys.js": function(exports, module) {
      var getBuiltIn3 = require_get_built_in();
      var getOwnPropertyNamesModule2 = require_object_get_own_property_names();
      var getOwnPropertySymbolsModule2 = require_object_get_own_property_symbols();
      var anObject4 = require_an_object();
      module.exports = getBuiltIn3("Reflect", "ownKeys") || function ownKeys(it) {
        var keys = getOwnPropertyNamesModule2.f(anObject4(it));
        var getOwnPropertySymbols3 = getOwnPropertySymbolsModule2.f;
        return getOwnPropertySymbols3 ? keys.concat(getOwnPropertySymbols3(it)) : keys;
      };
    }
  });

  // node_modules/core-js/internals/copy-constructor-properties.js
  var require_copy_constructor_properties = __commonJS({
    "node_modules/core-js/internals/copy-constructor-properties.js": function(exports, module) {
      var has3 = require_has();
      var ownKeys = require_own_keys();
      var getOwnPropertyDescriptorModule2 = require_object_get_own_property_descriptor();
      var definePropertyModule2 = require_object_define_property();
      module.exports = function(target, source) {
        var keys = ownKeys(source);
        var defineProperty4 = definePropertyModule2.f;
        var getOwnPropertyDescriptor3 = getOwnPropertyDescriptorModule2.f;
        for (var i = 0; i < keys.length; i++) {
          var key = keys[i];
          if (!has3(target, key))
            defineProperty4(target, key, getOwnPropertyDescriptor3(source, key));
        }
      };
    }
  });

  // node_modules/core-js/internals/is-forced.js
  var require_is_forced = __commonJS({
    "node_modules/core-js/internals/is-forced.js": function(exports, module) {
      var fails6 = require_fails();
      var replacement = /#|\.prototype\./;
      var isForced = function(feature, detection) {
        var value = data[normalize(feature)];
        return value == POLYFILL ? true : value == NATIVE ? false : typeof detection == "function" ? fails6(detection) : !!detection;
      };
      var normalize = isForced.normalize = function(string) {
        return String(string).replace(replacement, ".").toLowerCase();
      };
      var data = isForced.data = {};
      var NATIVE = isForced.NATIVE = "N";
      var POLYFILL = isForced.POLYFILL = "P";
      module.exports = isForced;
    }
  });

  // node_modules/core-js/internals/export.js
  var require_export = __commonJS({
    "node_modules/core-js/internals/export.js": function(exports, module) {
      var global6 = require_global();
      var getOwnPropertyDescriptor3 = require_object_get_own_property_descriptor().f;
      var createNonEnumerableProperty4 = require_create_non_enumerable_property();
      var redefine5 = require_redefine();
      var setGlobal = require_set_global();
      var copyConstructorProperties2 = require_copy_constructor_properties();
      var isForced = require_is_forced();
      module.exports = function(options, source) {
        var TARGET = options.target;
        var GLOBAL = options.global;
        var STATIC = options.stat;
        var FORCED3, target, key, targetProperty, sourceProperty, descriptor;
        if (GLOBAL) {
          target = global6;
        } else if (STATIC) {
          target = global6[TARGET] || setGlobal(TARGET, {});
        } else {
          target = (global6[TARGET] || {}).prototype;
        }
        if (target)
          for (key in source) {
            sourceProperty = source[key];
            if (options.noTargetGet) {
              descriptor = getOwnPropertyDescriptor3(target, key);
              targetProperty = descriptor && descriptor.value;
            } else
              targetProperty = target[key];
            FORCED3 = isForced(GLOBAL ? key : TARGET + (STATIC ? "." : "#") + key, options.forced);
            if (!FORCED3 && targetProperty !== void 0) {
              if (typeof sourceProperty === typeof targetProperty)
                continue;
              copyConstructorProperties2(sourceProperty, targetProperty);
            }
            if (options.sham || targetProperty && targetProperty.sham) {
              createNonEnumerableProperty4(sourceProperty, "sham", true);
            }
            redefine5(target, key, sourceProperty, options);
          }
      };
    }
  });

  // node_modules/core-js/internals/a-possible-prototype.js
  var require_a_possible_prototype = __commonJS({
    "node_modules/core-js/internals/a-possible-prototype.js": function(exports, module) {
      var isObject6 = require_is_object();
      module.exports = function(it) {
        if (!isObject6(it) && it !== null) {
          throw TypeError("Can't set " + String(it) + " as a prototype");
        }
        return it;
      };
    }
  });

  // node_modules/core-js/internals/object-set-prototype-of.js
  var require_object_set_prototype_of = __commonJS({
    "node_modules/core-js/internals/object-set-prototype-of.js": function(exports, module) {
      var anObject4 = require_an_object();
      var aPossiblePrototype = require_a_possible_prototype();
      module.exports = Object.setPrototypeOf || ("__proto__" in {} ? function() {
        var CORRECT_SETTER = false;
        var test = {};
        var setter;
        try {
          setter = Object.getOwnPropertyDescriptor(Object.prototype, "__proto__").set;
          setter.call(test, []);
          CORRECT_SETTER = test instanceof Array;
        } catch (error) {
        }
        return function setPrototypeOf2(O, proto) {
          anObject4(O);
          aPossiblePrototype(proto);
          if (CORRECT_SETTER)
            setter.call(O, proto);
          else
            O.__proto__ = proto;
          return O;
        };
      }() : void 0);
    }
  });

  // node_modules/core-js/internals/correct-prototype-getter.js
  var require_correct_prototype_getter = __commonJS({
    "node_modules/core-js/internals/correct-prototype-getter.js": function(exports, module) {
      var fails6 = require_fails();
      module.exports = !fails6(function() {
        function F() {
        }
        F.prototype.constructor = null;
        return Object.getPrototypeOf(new F()) !== F.prototype;
      });
    }
  });

  // node_modules/core-js/internals/object-get-prototype-of.js
  var require_object_get_prototype_of = __commonJS({
    "node_modules/core-js/internals/object-get-prototype-of.js": function(exports, module) {
      var has3 = require_has();
      var toObject4 = require_to_object();
      var sharedKey2 = require_shared_key();
      var CORRECT_PROTOTYPE_GETTER2 = require_correct_prototype_getter();
      var IE_PROTO = sharedKey2("IE_PROTO");
      var ObjectPrototype2 = Object.prototype;
      module.exports = CORRECT_PROTOTYPE_GETTER2 ? Object.getPrototypeOf : function(O) {
        O = toObject4(O);
        if (has3(O, IE_PROTO))
          return O[IE_PROTO];
        if (typeof O.constructor == "function" && O instanceof O.constructor) {
          return O.constructor.prototype;
        }
        return O instanceof Object ? ObjectPrototype2 : null;
      };
    }
  });

  // node_modules/core-js/internals/array-method-is-strict.js
  var require_array_method_is_strict = __commonJS({
    "node_modules/core-js/internals/array-method-is-strict.js": function(exports, module) {
      "use strict";
      var fails6 = require_fails();
      module.exports = function(METHOD_NAME, argument) {
        var method = [][METHOD_NAME];
        return !!method && fails6(function() {
          method.call(null, argument || function() {
            throw 1;
          }, 1);
        });
      };
    }
  });

  // node_modules/core-js/internals/engine-user-agent.js
  var require_engine_user_agent = __commonJS({
    "node_modules/core-js/internals/engine-user-agent.js": function(exports, module) {
      var getBuiltIn3 = require_get_built_in();
      module.exports = getBuiltIn3("navigator", "userAgent") || "";
    }
  });

  // node_modules/core-js/internals/engine-v8-version.js
  var require_engine_v8_version = __commonJS({
    "node_modules/core-js/internals/engine-v8-version.js": function(exports, module) {
      var global6 = require_global();
      var userAgent = require_engine_user_agent();
      var process = global6.process;
      var versions = process && process.versions;
      var v8 = versions && versions.v8;
      var match;
      var version;
      if (v8) {
        match = v8.split(".");
        version = match[0] < 4 ? 1 : match[0] + match[1];
      } else if (userAgent) {
        match = userAgent.match(/Edge\/(\d+)/);
        if (!match || match[1] >= 74) {
          match = userAgent.match(/Chrome\/(\d+)/);
          if (match)
            version = match[1];
        }
      }
      module.exports = version && +version;
    }
  });

  // node_modules/core-js/internals/native-symbol.js
  var require_native_symbol = __commonJS({
    "node_modules/core-js/internals/native-symbol.js": function(exports, module) {
      var V8_VERSION2 = require_engine_v8_version();
      var fails6 = require_fails();
      module.exports = !!Object.getOwnPropertySymbols && !fails6(function() {
        var symbol = Symbol();
        return !String(symbol) || !(Object(symbol) instanceof Symbol) || !Symbol.sham && V8_VERSION2 && V8_VERSION2 < 41;
      });
    }
  });

  // node_modules/core-js/internals/use-symbol-as-uid.js
  var require_use_symbol_as_uid = __commonJS({
    "node_modules/core-js/internals/use-symbol-as-uid.js": function(exports, module) {
      var NATIVE_SYMBOL2 = require_native_symbol();
      module.exports = NATIVE_SYMBOL2 && !Symbol.sham && typeof Symbol.iterator == "symbol";
    }
  });

  // node_modules/core-js/internals/well-known-symbol.js
  var require_well_known_symbol = __commonJS({
    "node_modules/core-js/internals/well-known-symbol.js": function(exports, module) {
      var global6 = require_global();
      var shared2 = require_shared();
      var has3 = require_has();
      var uid2 = require_uid();
      var NATIVE_SYMBOL2 = require_native_symbol();
      var USE_SYMBOL_AS_UID2 = require_use_symbol_as_uid();
      var WellKnownSymbolsStore2 = shared2("wks");
      var Symbol2 = global6.Symbol;
      var createWellKnownSymbol = USE_SYMBOL_AS_UID2 ? Symbol2 : Symbol2 && Symbol2.withoutSetter || uid2;
      module.exports = function(name2) {
        if (!has3(WellKnownSymbolsStore2, name2) || !(NATIVE_SYMBOL2 || typeof WellKnownSymbolsStore2[name2] == "string")) {
          if (NATIVE_SYMBOL2 && has3(Symbol2, name2)) {
            WellKnownSymbolsStore2[name2] = Symbol2[name2];
          } else {
            WellKnownSymbolsStore2[name2] = createWellKnownSymbol("Symbol." + name2);
          }
        }
        return WellKnownSymbolsStore2[name2];
      };
    }
  });

  // node_modules/core-js/internals/to-string-tag-support.js
  var require_to_string_tag_support = __commonJS({
    "node_modules/core-js/internals/to-string-tag-support.js": function(exports, module) {
      var wellKnownSymbol5 = require_well_known_symbol();
      var TO_STRING_TAG2 = wellKnownSymbol5("toStringTag");
      var test = {};
      test[TO_STRING_TAG2] = "z";
      module.exports = String(test) === "[object z]";
    }
  });

  // node_modules/core-js/internals/classof.js
  var require_classof = __commonJS({
    "node_modules/core-js/internals/classof.js": function(exports, module) {
      var TO_STRING_TAG_SUPPORT2 = require_to_string_tag_support();
      var classofRaw = require_classof_raw();
      var wellKnownSymbol5 = require_well_known_symbol();
      var TO_STRING_TAG2 = wellKnownSymbol5("toStringTag");
      var CORRECT_ARGUMENTS = classofRaw(function() {
        return arguments;
      }()) == "Arguments";
      var tryGet = function(it, key) {
        try {
          return it[key];
        } catch (error) {
        }
      };
      module.exports = TO_STRING_TAG_SUPPORT2 ? classofRaw : function(it) {
        var O, tag2, result;
        return it === void 0 ? "Undefined" : it === null ? "Null" : typeof (tag2 = tryGet(O = Object(it), TO_STRING_TAG2)) == "string" ? tag2 : CORRECT_ARGUMENTS ? classofRaw(O) : (result = classofRaw(O)) == "Object" && typeof O.callee == "function" ? "Arguments" : result;
      };
    }
  });

  // node_modules/core-js/internals/object-to-string.js
  var require_object_to_string = __commonJS({
    "node_modules/core-js/internals/object-to-string.js": function(exports, module) {
      "use strict";
      var TO_STRING_TAG_SUPPORT2 = require_to_string_tag_support();
      var classof = require_classof();
      module.exports = TO_STRING_TAG_SUPPORT2 ? {}.toString : function toString2() {
        return "[object " + classof(this) + "]";
      };
    }
  });

  // node_modules/core-js/internals/regexp-flags.js
  var require_regexp_flags = __commonJS({
    "node_modules/core-js/internals/regexp-flags.js": function(exports, module) {
      "use strict";
      var anObject4 = require_an_object();
      module.exports = function() {
        var that = anObject4(this);
        var result = "";
        if (that.global)
          result += "g";
        if (that.ignoreCase)
          result += "i";
        if (that.multiline)
          result += "m";
        if (that.dotAll)
          result += "s";
        if (that.unicode)
          result += "u";
        if (that.sticky)
          result += "y";
        return result;
      };
    }
  });

  // node_modules/core-js/internals/a-function.js
  var require_a_function = __commonJS({
    "node_modules/core-js/internals/a-function.js": function(exports, module) {
      module.exports = function(it) {
        if (typeof it != "function") {
          throw TypeError(String(it) + " is not a function");
        }
        return it;
      };
    }
  });

  // node_modules/core-js/internals/object-keys.js
  var require_object_keys = __commonJS({
    "node_modules/core-js/internals/object-keys.js": function(exports, module) {
      var internalObjectKeys = require_object_keys_internal();
      var enumBugKeys = require_enum_bug_keys();
      module.exports = Object.keys || function keys(O) {
        return internalObjectKeys(O, enumBugKeys);
      };
    }
  });

  // node_modules/core-js/internals/object-define-properties.js
  var require_object_define_properties = __commonJS({
    "node_modules/core-js/internals/object-define-properties.js": function(exports, module) {
      var DESCRIPTORS5 = require_descriptors();
      var definePropertyModule2 = require_object_define_property();
      var anObject4 = require_an_object();
      var objectKeys2 = require_object_keys();
      module.exports = DESCRIPTORS5 ? Object.defineProperties : function defineProperties2(O, Properties) {
        anObject4(O);
        var keys = objectKeys2(Properties);
        var length = keys.length;
        var index = 0;
        var key;
        while (length > index)
          definePropertyModule2.f(O, key = keys[index++], Properties[key]);
        return O;
      };
    }
  });

  // node_modules/core-js/internals/html.js
  var require_html = __commonJS({
    "node_modules/core-js/internals/html.js": function(exports, module) {
      var getBuiltIn3 = require_get_built_in();
      module.exports = getBuiltIn3("document", "documentElement");
    }
  });

  // node_modules/core-js/internals/object-create.js
  var require_object_create = __commonJS({
    "node_modules/core-js/internals/object-create.js": function(exports, module) {
      var anObject4 = require_an_object();
      var defineProperties2 = require_object_define_properties();
      var enumBugKeys = require_enum_bug_keys();
      var hiddenKeys2 = require_hidden_keys();
      var html = require_html();
      var documentCreateElement = require_document_create_element();
      var sharedKey2 = require_shared_key();
      var GT = ">";
      var LT = "<";
      var PROTOTYPE2 = "prototype";
      var SCRIPT = "script";
      var IE_PROTO = sharedKey2("IE_PROTO");
      var EmptyConstructor = function() {
      };
      var scriptTag = function(content) {
        return LT + SCRIPT + GT + content + LT + "/" + SCRIPT + GT;
      };
      var NullProtoObjectViaActiveX = function(activeXDocument2) {
        activeXDocument2.write(scriptTag(""));
        activeXDocument2.close();
        var temp = activeXDocument2.parentWindow.Object;
        activeXDocument2 = null;
        return temp;
      };
      var NullProtoObjectViaIFrame = function() {
        var iframe = documentCreateElement("iframe");
        var JS = "java" + SCRIPT + ":";
        var iframeDocument;
        iframe.style.display = "none";
        html.appendChild(iframe);
        iframe.src = String(JS);
        iframeDocument = iframe.contentWindow.document;
        iframeDocument.open();
        iframeDocument.write(scriptTag("document.F=Object"));
        iframeDocument.close();
        return iframeDocument.F;
      };
      var activeXDocument;
      var NullProtoObject = function() {
        try {
          activeXDocument = document.domain && new ActiveXObject("htmlfile");
        } catch (error) {
        }
        NullProtoObject = activeXDocument ? NullProtoObjectViaActiveX(activeXDocument) : NullProtoObjectViaIFrame();
        var length = enumBugKeys.length;
        while (length--)
          delete NullProtoObject[PROTOTYPE2][enumBugKeys[length]];
        return NullProtoObject();
      };
      hiddenKeys2[IE_PROTO] = true;
      module.exports = Object.create || function create4(O, Properties) {
        var result;
        if (O !== null) {
          EmptyConstructor[PROTOTYPE2] = anObject4(O);
          result = new EmptyConstructor();
          EmptyConstructor[PROTOTYPE2] = null;
          result[IE_PROTO] = O;
        } else
          result = NullProtoObject();
        return Properties === void 0 ? result : defineProperties2(result, Properties);
      };
    }
  });

  // node_modules/core-js/internals/function-bind.js
  var require_function_bind = __commonJS({
    "node_modules/core-js/internals/function-bind.js": function(exports, module) {
      "use strict";
      var aFunction2 = require_a_function();
      var isObject6 = require_is_object();
      var slice2 = [].slice;
      var factories = {};
      var construct2 = function(C, argsLength, args) {
        if (!(argsLength in factories)) {
          for (var list = [], i = 0; i < argsLength; i++)
            list[i] = "a[" + i + "]";
          factories[argsLength] = Function("C,a", "return new C(" + list.join(",") + ")");
        }
        return factories[argsLength](C, args);
      };
      module.exports = Function.bind || function bind3(that) {
        var fn = aFunction2(this);
        var partArgs = slice2.call(arguments, 1);
        var boundFunction = function bound() {
          var args = partArgs.concat(slice2.call(arguments));
          return this instanceof boundFunction ? construct2(fn, args.length, args) : fn.apply(that, args);
        };
        if (isObject6(fn.prototype))
          boundFunction.prototype = fn.prototype;
        return boundFunction;
      };
    }
  });

  // node_modules/core-js/internals/add-to-unscopables.js
  var require_add_to_unscopables = __commonJS({
    "node_modules/core-js/internals/add-to-unscopables.js": function(exports, module) {
      var wellKnownSymbol5 = require_well_known_symbol();
      var create4 = require_object_create();
      var definePropertyModule2 = require_object_define_property();
      var UNSCOPABLES = wellKnownSymbol5("unscopables");
      var ArrayPrototype = Array.prototype;
      if (ArrayPrototype[UNSCOPABLES] == void 0) {
        definePropertyModule2.f(ArrayPrototype, UNSCOPABLES, {
          configurable: true,
          value: create4(null)
        });
      }
      module.exports = function(key) {
        ArrayPrototype[UNSCOPABLES][key] = true;
      };
    }
  });

  // node_modules/core-js/internals/iterators.js
  var require_iterators = __commonJS({
    "node_modules/core-js/internals/iterators.js": function(exports, module) {
      module.exports = {};
    }
  });

  // node_modules/core-js/internals/iterators-core.js
  var require_iterators_core = __commonJS({
    "node_modules/core-js/internals/iterators-core.js": function(exports, module) {
      "use strict";
      var fails6 = require_fails();
      var getPrototypeOf2 = require_object_get_prototype_of();
      var createNonEnumerableProperty4 = require_create_non_enumerable_property();
      var has3 = require_has();
      var wellKnownSymbol5 = require_well_known_symbol();
      var IS_PURE3 = require_is_pure();
      var ITERATOR2 = wellKnownSymbol5("iterator");
      var BUGGY_SAFARI_ITERATORS = false;
      var returnThis = function() {
        return this;
      };
      var IteratorPrototype;
      var PrototypeOfArrayIteratorPrototype;
      var arrayIterator;
      if ([].keys) {
        arrayIterator = [].keys();
        if (!("next" in arrayIterator))
          BUGGY_SAFARI_ITERATORS = true;
        else {
          PrototypeOfArrayIteratorPrototype = getPrototypeOf2(getPrototypeOf2(arrayIterator));
          if (PrototypeOfArrayIteratorPrototype !== Object.prototype)
            IteratorPrototype = PrototypeOfArrayIteratorPrototype;
        }
      }
      var NEW_ITERATOR_PROTOTYPE = IteratorPrototype == void 0 || fails6(function() {
        var test = {};
        return IteratorPrototype[ITERATOR2].call(test) !== test;
      });
      if (NEW_ITERATOR_PROTOTYPE)
        IteratorPrototype = {};
      if ((!IS_PURE3 || NEW_ITERATOR_PROTOTYPE) && !has3(IteratorPrototype, ITERATOR2)) {
        createNonEnumerableProperty4(IteratorPrototype, ITERATOR2, returnThis);
      }
      module.exports = {
        IteratorPrototype: IteratorPrototype,
        BUGGY_SAFARI_ITERATORS: BUGGY_SAFARI_ITERATORS
      };
    }
  });

  // node_modules/core-js/internals/set-to-string-tag.js
  var require_set_to_string_tag = __commonJS({
    "node_modules/core-js/internals/set-to-string-tag.js": function(exports, module) {
      var defineProperty4 = require_object_define_property().f;
      var has3 = require_has();
      var wellKnownSymbol5 = require_well_known_symbol();
      var TO_STRING_TAG2 = wellKnownSymbol5("toStringTag");
      module.exports = function(it, TAG, STATIC) {
        if (it && !has3(it = STATIC ? it : it.prototype, TO_STRING_TAG2)) {
          defineProperty4(it, TO_STRING_TAG2, { configurable: true, value: TAG });
        }
      };
    }
  });

  // node_modules/core-js/internals/create-iterator-constructor.js
  var require_create_iterator_constructor = __commonJS({
    "node_modules/core-js/internals/create-iterator-constructor.js": function(exports, module) {
      "use strict";
      var IteratorPrototype = require_iterators_core().IteratorPrototype;
      var create4 = require_object_create();
      var createPropertyDescriptor2 = require_create_property_descriptor();
      var setToStringTag2 = require_set_to_string_tag();
      var Iterators = require_iterators();
      var returnThis = function() {
        return this;
      };
      module.exports = function(IteratorConstructor, NAME2, next2) {
        var TO_STRING_TAG2 = NAME2 + " Iterator";
        IteratorConstructor.prototype = create4(IteratorPrototype, { next: createPropertyDescriptor2(1, next2) });
        setToStringTag2(IteratorConstructor, TO_STRING_TAG2, false, true);
        Iterators[TO_STRING_TAG2] = returnThis;
        return IteratorConstructor;
      };
    }
  });

  // node_modules/core-js/internals/define-iterator.js
  var require_define_iterator = __commonJS({
    "node_modules/core-js/internals/define-iterator.js": function(exports, module) {
      "use strict";
      var $16 = require_export();
      var createIteratorConstructor = require_create_iterator_constructor();
      var getPrototypeOf2 = require_object_get_prototype_of();
      var setPrototypeOf2 = require_object_set_prototype_of();
      var setToStringTag2 = require_set_to_string_tag();
      var createNonEnumerableProperty4 = require_create_non_enumerable_property();
      var redefine5 = require_redefine();
      var wellKnownSymbol5 = require_well_known_symbol();
      var IS_PURE3 = require_is_pure();
      var Iterators = require_iterators();
      var IteratorsCore = require_iterators_core();
      var IteratorPrototype = IteratorsCore.IteratorPrototype;
      var BUGGY_SAFARI_ITERATORS = IteratorsCore.BUGGY_SAFARI_ITERATORS;
      var ITERATOR2 = wellKnownSymbol5("iterator");
      var KEYS = "keys";
      var VALUES = "values";
      var ENTRIES = "entries";
      var returnThis = function() {
        return this;
      };
      module.exports = function(Iterable, NAME2, IteratorConstructor, next2, DEFAULT, IS_SET, FORCED3) {
        createIteratorConstructor(IteratorConstructor, NAME2, next2);
        var getIterationMethod = function(KIND) {
          if (KIND === DEFAULT && defaultIterator)
            return defaultIterator;
          if (!BUGGY_SAFARI_ITERATORS && KIND in IterablePrototype)
            return IterablePrototype[KIND];
          switch (KIND) {
            case KEYS:
              return function keys() {
                return new IteratorConstructor(this, KIND);
              };
            case VALUES:
              return function values() {
                return new IteratorConstructor(this, KIND);
              };
            case ENTRIES:
              return function entries2() {
                return new IteratorConstructor(this, KIND);
              };
          }
          return function() {
            return new IteratorConstructor(this);
          };
        };
        var TO_STRING_TAG2 = NAME2 + " Iterator";
        var INCORRECT_VALUES_NAME = false;
        var IterablePrototype = Iterable.prototype;
        var nativeIterator = IterablePrototype[ITERATOR2] || IterablePrototype["@@iterator"] || DEFAULT && IterablePrototype[DEFAULT];
        var defaultIterator = !BUGGY_SAFARI_ITERATORS && nativeIterator || getIterationMethod(DEFAULT);
        var anyNativeIterator = NAME2 == "Array" ? IterablePrototype.entries || nativeIterator : nativeIterator;
        var CurrentIteratorPrototype, methods, KEY;
        if (anyNativeIterator) {
          CurrentIteratorPrototype = getPrototypeOf2(anyNativeIterator.call(new Iterable()));
          if (IteratorPrototype !== Object.prototype && CurrentIteratorPrototype.next) {
            if (!IS_PURE3 && getPrototypeOf2(CurrentIteratorPrototype) !== IteratorPrototype) {
              if (setPrototypeOf2) {
                setPrototypeOf2(CurrentIteratorPrototype, IteratorPrototype);
              } else if (typeof CurrentIteratorPrototype[ITERATOR2] != "function") {
                createNonEnumerableProperty4(CurrentIteratorPrototype, ITERATOR2, returnThis);
              }
            }
            setToStringTag2(CurrentIteratorPrototype, TO_STRING_TAG2, true, true);
            if (IS_PURE3)
              Iterators[TO_STRING_TAG2] = returnThis;
          }
        }
        if (DEFAULT == VALUES && nativeIterator && nativeIterator.name !== VALUES) {
          INCORRECT_VALUES_NAME = true;
          defaultIterator = function values() {
            return nativeIterator.call(this);
          };
        }
        if ((!IS_PURE3 || FORCED3) && IterablePrototype[ITERATOR2] !== defaultIterator) {
          createNonEnumerableProperty4(IterablePrototype, ITERATOR2, defaultIterator);
        }
        Iterators[NAME2] = defaultIterator;
        if (DEFAULT) {
          methods = {
            values: getIterationMethod(VALUES),
            keys: IS_SET ? defaultIterator : getIterationMethod(KEYS),
            entries: getIterationMethod(ENTRIES)
          };
          if (FORCED3)
            for (KEY in methods) {
              if (BUGGY_SAFARI_ITERATORS || INCORRECT_VALUES_NAME || !(KEY in IterablePrototype)) {
                redefine5(IterablePrototype, KEY, methods[KEY]);
              }
            }
          else
            $16({ target: NAME2, proto: true, forced: BUGGY_SAFARI_ITERATORS || INCORRECT_VALUES_NAME }, methods);
        }
        return methods;
      };
    }
  });

  // node_modules/core-js/modules/es.array.iterator.js
  var require_es_array_iterator = __commonJS({
    "node_modules/core-js/modules/es.array.iterator.js": function(exports, module) {
      "use strict";
      var toIndexedObject3 = require_to_indexed_object();
      var addToUnscopables = require_add_to_unscopables();
      var Iterators = require_iterators();
      var InternalStateModule3 = require_internal_state();
      var defineIterator2 = require_define_iterator();
      var ARRAY_ITERATOR = "Array Iterator";
      var setInternalState3 = InternalStateModule3.set;
      var getInternalState3 = InternalStateModule3.getterFor(ARRAY_ITERATOR);
      module.exports = defineIterator2(Array, "Array", function(iterated, kind) {
        setInternalState3(this, {
          type: ARRAY_ITERATOR,
          target: toIndexedObject3(iterated),
          index: 0,
          kind: kind
        });
      }, function() {
        var state = getInternalState3(this);
        var target = state.target;
        var kind = state.kind;
        var index = state.index++;
        if (!target || index >= target.length) {
          state.target = void 0;
          return { value: void 0, done: true };
        }
        if (kind == "keys")
          return { value: index, done: false };
        if (kind == "values")
          return { value: target[index], done: false };
        return { value: [index, target[index]], done: false };
      }, "values");
      Iterators.Arguments = Iterators.Array;
      addToUnscopables("keys");
      addToUnscopables("values");
      addToUnscopables("entries");
    }
  });

  // node_modules/core-js/internals/freezing.js
  var require_freezing = __commonJS({
    "node_modules/core-js/internals/freezing.js": function(exports, module) {
      var fails6 = require_fails();
      module.exports = !fails6(function() {
        return Object.isExtensible(Object.preventExtensions({}));
      });
    }
  });

  // node_modules/core-js/internals/internal-metadata.js
  var require_internal_metadata = __commonJS({
    "node_modules/core-js/internals/internal-metadata.js": function(exports, module) {
      var hiddenKeys2 = require_hidden_keys();
      var isObject6 = require_is_object();
      var has3 = require_has();
      var defineProperty4 = require_object_define_property().f;
      var uid2 = require_uid();
      var FREEZING = require_freezing();
      var METADATA = uid2("meta");
      var id = 0;
      var isExtensible = Object.isExtensible || function() {
        return true;
      };
      var setMetadata = function(it) {
        defineProperty4(it, METADATA, { value: {
          objectID: "O" + id++,
          weakData: {}
        } });
      };
      var fastKey = function(it, create4) {
        if (!isObject6(it))
          return typeof it == "symbol" ? it : (typeof it == "string" ? "S" : "P") + it;
        if (!has3(it, METADATA)) {
          if (!isExtensible(it))
            return "F";
          if (!create4)
            return "E";
          setMetadata(it);
        }
        return it[METADATA].objectID;
      };
      var getWeakData = function(it, create4) {
        if (!has3(it, METADATA)) {
          if (!isExtensible(it))
            return true;
          if (!create4)
            return false;
          setMetadata(it);
        }
        return it[METADATA].weakData;
      };
      var onFreeze = function(it) {
        if (FREEZING && meta.REQUIRED && isExtensible(it) && !has3(it, METADATA))
          setMetadata(it);
        return it;
      };
      var meta = module.exports = {
        REQUIRED: false,
        fastKey: fastKey,
        getWeakData: getWeakData,
        onFreeze: onFreeze
      };
      hiddenKeys2[METADATA] = true;
    }
  });

  // node_modules/core-js/internals/is-array-iterator-method.js
  var require_is_array_iterator_method = __commonJS({
    "node_modules/core-js/internals/is-array-iterator-method.js": function(exports, module) {
      var wellKnownSymbol5 = require_well_known_symbol();
      var Iterators = require_iterators();
      var ITERATOR2 = wellKnownSymbol5("iterator");
      var ArrayPrototype = Array.prototype;
      module.exports = function(it) {
        return it !== void 0 && (Iterators.Array === it || ArrayPrototype[ITERATOR2] === it);
      };
    }
  });

  // node_modules/core-js/internals/function-bind-context.js
  var require_function_bind_context = __commonJS({
    "node_modules/core-js/internals/function-bind-context.js": function(exports, module) {
      var aFunction2 = require_a_function();
      module.exports = function(fn, that, length) {
        aFunction2(fn);
        if (that === void 0)
          return fn;
        switch (length) {
          case 0:
            return function() {
              return fn.call(that);
            };
          case 1:
            return function(a) {
              return fn.call(that, a);
            };
          case 2:
            return function(a, b) {
              return fn.call(that, a, b);
            };
          case 3:
            return function(a, b, c) {
              return fn.call(that, a, b, c);
            };
        }
        return function() {
          return fn.apply(that, arguments);
        };
      };
    }
  });

  // node_modules/core-js/internals/get-iterator-method.js
  var require_get_iterator_method = __commonJS({
    "node_modules/core-js/internals/get-iterator-method.js": function(exports, module) {
      var classof = require_classof();
      var Iterators = require_iterators();
      var wellKnownSymbol5 = require_well_known_symbol();
      var ITERATOR2 = wellKnownSymbol5("iterator");
      module.exports = function(it) {
        if (it != void 0)
          return it[ITERATOR2] || it["@@iterator"] || Iterators[classof(it)];
      };
    }
  });

  // node_modules/core-js/internals/iterator-close.js
  var require_iterator_close = __commonJS({
    "node_modules/core-js/internals/iterator-close.js": function(exports, module) {
      var anObject4 = require_an_object();
      module.exports = function(iterator) {
        var returnMethod = iterator["return"];
        if (returnMethod !== void 0) {
          return anObject4(returnMethod.call(iterator)).value;
        }
      };
    }
  });

  // node_modules/core-js/internals/iterate.js
  var require_iterate = __commonJS({
    "node_modules/core-js/internals/iterate.js": function(exports, module) {
      var anObject4 = require_an_object();
      var isArrayIteratorMethod = require_is_array_iterator_method();
      var toLength4 = require_to_length();
      var bind3 = require_function_bind_context();
      var getIteratorMethod = require_get_iterator_method();
      var iteratorClose = require_iterator_close();
      var Result = function(stopped, result) {
        this.stopped = stopped;
        this.result = result;
      };
      module.exports = function(iterable, unboundFunction, options) {
        var that = options && options.that;
        var AS_ENTRIES = !!(options && options.AS_ENTRIES);
        var IS_ITERATOR = !!(options && options.IS_ITERATOR);
        var INTERRUPTED = !!(options && options.INTERRUPTED);
        var fn = bind3(unboundFunction, that, 1 + AS_ENTRIES + INTERRUPTED);
        var iterator, iterFn, index, length, result, next2, step;
        var stop = function(condition) {
          if (iterator)
            iteratorClose(iterator);
          return new Result(true, condition);
        };
        var callFn = function(value) {
          if (AS_ENTRIES) {
            anObject4(value);
            return INTERRUPTED ? fn(value[0], value[1], stop) : fn(value[0], value[1]);
          }
          return INTERRUPTED ? fn(value, stop) : fn(value);
        };
        if (IS_ITERATOR) {
          iterator = iterable;
        } else {
          iterFn = getIteratorMethod(iterable);
          if (typeof iterFn != "function")
            throw TypeError("Target is not iterable");
          if (isArrayIteratorMethod(iterFn)) {
            for (index = 0, length = toLength4(iterable.length); length > index; index++) {
              result = callFn(iterable[index]);
              if (result && result instanceof Result)
                return result;
            }
            return new Result(false);
          }
          iterator = iterFn.call(iterable);
        }
        next2 = iterator.next;
        while (!(step = next2.call(iterator)).done) {
          try {
            result = callFn(step.value);
          } catch (error) {
            iteratorClose(iterator);
            throw error;
          }
          if (typeof result == "object" && result && result instanceof Result)
            return result;
        }
        return new Result(false);
      };
    }
  });

  // node_modules/core-js/internals/an-instance.js
  var require_an_instance = __commonJS({
    "node_modules/core-js/internals/an-instance.js": function(exports, module) {
      module.exports = function(it, Constructor, name2) {
        if (!(it instanceof Constructor)) {
          throw TypeError("Incorrect " + (name2 ? name2 + " " : "") + "invocation");
        }
        return it;
      };
    }
  });

  // node_modules/core-js/internals/check-correctness-of-iteration.js
  var require_check_correctness_of_iteration = __commonJS({
    "node_modules/core-js/internals/check-correctness-of-iteration.js": function(exports, module) {
      var wellKnownSymbol5 = require_well_known_symbol();
      var ITERATOR2 = wellKnownSymbol5("iterator");
      var SAFE_CLOSING = false;
      try {
        called = 0;
        iteratorWithReturn = {
          next: function() {
            return { done: !!called++ };
          },
          "return": function() {
            SAFE_CLOSING = true;
          }
        };
        iteratorWithReturn[ITERATOR2] = function() {
          return this;
        };
        Array.from(iteratorWithReturn, function() {
          throw 2;
        });
      } catch (error) {
      }
      var called;
      var iteratorWithReturn;
      module.exports = function(exec, SKIP_CLOSING) {
        if (!SKIP_CLOSING && !SAFE_CLOSING)
          return false;
        var ITERATION_SUPPORT = false;
        try {
          var object = {};
          object[ITERATOR2] = function() {
            return {
              next: function() {
                return { done: ITERATION_SUPPORT = true };
              }
            };
          };
          exec(object);
        } catch (error) {
        }
        return ITERATION_SUPPORT;
      };
    }
  });

  // node_modules/core-js/internals/inherit-if-required.js
  var require_inherit_if_required = __commonJS({
    "node_modules/core-js/internals/inherit-if-required.js": function(exports, module) {
      var isObject6 = require_is_object();
      var setPrototypeOf2 = require_object_set_prototype_of();
      module.exports = function($this, dummy, Wrapper) {
        var NewTarget, NewTargetPrototype;
        if (setPrototypeOf2 && typeof (NewTarget = dummy.constructor) == "function" && NewTarget !== Wrapper && isObject6(NewTargetPrototype = NewTarget.prototype) && NewTargetPrototype !== Wrapper.prototype)
          setPrototypeOf2($this, NewTargetPrototype);
        return $this;
      };
    }
  });

  // node_modules/core-js/internals/collection.js
  var require_collection = __commonJS({
    "node_modules/core-js/internals/collection.js": function(exports, module) {
      "use strict";
      var $16 = require_export();
      var global6 = require_global();
      var isForced = require_is_forced();
      var redefine5 = require_redefine();
      var InternalMetadataModule = require_internal_metadata();
      var iterate = require_iterate();
      var anInstance = require_an_instance();
      var isObject6 = require_is_object();
      var fails6 = require_fails();
      var checkCorrectnessOfIteration2 = require_check_correctness_of_iteration();
      var setToStringTag2 = require_set_to_string_tag();
      var inheritIfRequired = require_inherit_if_required();
      module.exports = function(CONSTRUCTOR_NAME, wrapper, common) {
        var IS_MAP = CONSTRUCTOR_NAME.indexOf("Map") !== -1;
        var IS_WEAK = CONSTRUCTOR_NAME.indexOf("Weak") !== -1;
        var ADDER = IS_MAP ? "set" : "add";
        var NativeConstructor = global6[CONSTRUCTOR_NAME];
        var NativePrototype = NativeConstructor && NativeConstructor.prototype;
        var Constructor = NativeConstructor;
        var exported = {};
        var fixMethod = function(KEY) {
          var nativeMethod = NativePrototype[KEY];
          redefine5(NativePrototype, KEY, KEY == "add" ? function add(value) {
            nativeMethod.call(this, value === 0 ? 0 : value);
            return this;
          } : KEY == "delete" ? function(key) {
            return IS_WEAK && !isObject6(key) ? false : nativeMethod.call(this, key === 0 ? 0 : key);
          } : KEY == "get" ? function get(key) {
            return IS_WEAK && !isObject6(key) ? void 0 : nativeMethod.call(this, key === 0 ? 0 : key);
          } : KEY == "has" ? function has3(key) {
            return IS_WEAK && !isObject6(key) ? false : nativeMethod.call(this, key === 0 ? 0 : key);
          } : function set(key, value) {
            nativeMethod.call(this, key === 0 ? 0 : key, value);
            return this;
          });
        };
        var REPLACE = isForced(CONSTRUCTOR_NAME, typeof NativeConstructor != "function" || !(IS_WEAK || NativePrototype.forEach && !fails6(function() {
          new NativeConstructor().entries().next();
        })));
        if (REPLACE) {
          Constructor = common.getConstructor(wrapper, CONSTRUCTOR_NAME, IS_MAP, ADDER);
          InternalMetadataModule.REQUIRED = true;
        } else if (isForced(CONSTRUCTOR_NAME, true)) {
          var instance = new Constructor();
          var HASNT_CHAINING = instance[ADDER](IS_WEAK ? {} : -0, 1) != instance;
          var THROWS_ON_PRIMITIVES = fails6(function() {
            instance.has(1);
          });
          var ACCEPT_ITERABLES = checkCorrectnessOfIteration2(function(iterable) {
            new NativeConstructor(iterable);
          });
          var BUGGY_ZERO = !IS_WEAK && fails6(function() {
            var $instance = new NativeConstructor();
            var index = 5;
            while (index--)
              $instance[ADDER](index, index);
            return !$instance.has(-0);
          });
          if (!ACCEPT_ITERABLES) {
            Constructor = wrapper(function(dummy, iterable) {
              anInstance(dummy, Constructor, CONSTRUCTOR_NAME);
              var that = inheritIfRequired(new NativeConstructor(), dummy, Constructor);
              if (iterable != void 0)
                iterate(iterable, that[ADDER], { that: that, AS_ENTRIES: IS_MAP });
              return that;
            });
            Constructor.prototype = NativePrototype;
            NativePrototype.constructor = Constructor;
          }
          if (THROWS_ON_PRIMITIVES || BUGGY_ZERO) {
            fixMethod("delete");
            fixMethod("has");
            IS_MAP && fixMethod("get");
          }
          if (BUGGY_ZERO || HASNT_CHAINING)
            fixMethod(ADDER);
          if (IS_WEAK && NativePrototype.clear)
            delete NativePrototype.clear;
        }
        exported[CONSTRUCTOR_NAME] = Constructor;
        $16({ global: true, forced: Constructor != NativeConstructor }, exported);
        setToStringTag2(Constructor, CONSTRUCTOR_NAME);
        if (!IS_WEAK)
          common.setStrong(Constructor, CONSTRUCTOR_NAME, IS_MAP);
        return Constructor;
      };
    }
  });

  // node_modules/core-js/internals/redefine-all.js
  var require_redefine_all = __commonJS({
    "node_modules/core-js/internals/redefine-all.js": function(exports, module) {
      var redefine5 = require_redefine();
      module.exports = function(target, src, options) {
        for (var key in src)
          redefine5(target, key, src[key], options);
        return target;
      };
    }
  });

  // node_modules/core-js/internals/set-species.js
  var require_set_species = __commonJS({
    "node_modules/core-js/internals/set-species.js": function(exports, module) {
      "use strict";
      var getBuiltIn3 = require_get_built_in();
      var definePropertyModule2 = require_object_define_property();
      var wellKnownSymbol5 = require_well_known_symbol();
      var DESCRIPTORS5 = require_descriptors();
      var SPECIES2 = wellKnownSymbol5("species");
      module.exports = function(CONSTRUCTOR_NAME) {
        var Constructor = getBuiltIn3(CONSTRUCTOR_NAME);
        var defineProperty4 = definePropertyModule2.f;
        if (DESCRIPTORS5 && Constructor && !Constructor[SPECIES2]) {
          defineProperty4(Constructor, SPECIES2, {
            configurable: true,
            get: function() {
              return this;
            }
          });
        }
      };
    }
  });

  // node_modules/core-js/internals/collection-strong.js
  var require_collection_strong = __commonJS({
    "node_modules/core-js/internals/collection-strong.js": function(exports, module) {
      "use strict";
      var defineProperty4 = require_object_define_property().f;
      var create4 = require_object_create();
      var redefineAll = require_redefine_all();
      var bind3 = require_function_bind_context();
      var anInstance = require_an_instance();
      var iterate = require_iterate();
      var defineIterator2 = require_define_iterator();
      var setSpecies = require_set_species();
      var DESCRIPTORS5 = require_descriptors();
      var fastKey = require_internal_metadata().fastKey;
      var InternalStateModule3 = require_internal_state();
      var setInternalState3 = InternalStateModule3.set;
      var internalStateGetterFor = InternalStateModule3.getterFor;
      module.exports = {
        getConstructor: function(wrapper, CONSTRUCTOR_NAME, IS_MAP, ADDER) {
          var C = wrapper(function(that, iterable) {
            anInstance(that, C, CONSTRUCTOR_NAME);
            setInternalState3(that, {
              type: CONSTRUCTOR_NAME,
              index: create4(null),
              first: void 0,
              last: void 0,
              size: 0
            });
            if (!DESCRIPTORS5)
              that.size = 0;
            if (iterable != void 0)
              iterate(iterable, that[ADDER], { that: that, AS_ENTRIES: IS_MAP });
          });
          var getInternalState3 = internalStateGetterFor(CONSTRUCTOR_NAME);
          var define = function(that, key, value) {
            var state = getInternalState3(that);
            var entry = getEntry(that, key);
            var previous, index;
            if (entry) {
              entry.value = value;
            } else {
              state.last = entry = {
                index: index = fastKey(key, true),
                key: key,
                value: value,
                previous: previous = state.last,
                next: void 0,
                removed: false
              };
              if (!state.first)
                state.first = entry;
              if (previous)
                previous.next = entry;
              if (DESCRIPTORS5)
                state.size++;
              else
                that.size++;
              if (index !== "F")
                state.index[index] = entry;
            }
            return that;
          };
          var getEntry = function(that, key) {
            var state = getInternalState3(that);
            var index = fastKey(key);
            var entry;
            if (index !== "F")
              return state.index[index];
            for (entry = state.first; entry; entry = entry.next) {
              if (entry.key == key)
                return entry;
            }
          };
          redefineAll(C.prototype, {
            clear: function clear() {
              var that = this;
              var state = getInternalState3(that);
              var data = state.index;
              var entry = state.first;
              while (entry) {
                entry.removed = true;
                if (entry.previous)
                  entry.previous = entry.previous.next = void 0;
                delete data[entry.index];
                entry = entry.next;
              }
              state.first = state.last = void 0;
              if (DESCRIPTORS5)
                state.size = 0;
              else
                that.size = 0;
            },
            "delete": function(key) {
              var that = this;
              var state = getInternalState3(that);
              var entry = getEntry(that, key);
              if (entry) {
                var next2 = entry.next;
                var prev = entry.previous;
                delete state.index[entry.index];
                entry.removed = true;
                if (prev)
                  prev.next = next2;
                if (next2)
                  next2.previous = prev;
                if (state.first == entry)
                  state.first = next2;
                if (state.last == entry)
                  state.last = prev;
                if (DESCRIPTORS5)
                  state.size--;
                else
                  that.size--;
              }
              return !!entry;
            },
            forEach: function forEach3(callbackfn) {
              var state = getInternalState3(this);
              var boundFunction = bind3(callbackfn, arguments.length > 1 ? arguments[1] : void 0, 3);
              var entry;
              while (entry = entry ? entry.next : state.first) {
                boundFunction(entry.value, entry.key, this);
                while (entry && entry.removed)
                  entry = entry.previous;
              }
            },
            has: function has3(key) {
              return !!getEntry(this, key);
            }
          });
          redefineAll(C.prototype, IS_MAP ? {
            get: function get(key) {
              var entry = getEntry(this, key);
              return entry && entry.value;
            },
            set: function set(key, value) {
              return define(this, key === 0 ? 0 : key, value);
            }
          } : {
            add: function add(value) {
              return define(this, value = value === 0 ? 0 : value, value);
            }
          });
          if (DESCRIPTORS5)
            defineProperty4(C.prototype, "size", {
              get: function() {
                return getInternalState3(this).size;
              }
            });
          return C;
        },
        setStrong: function(C, CONSTRUCTOR_NAME, IS_MAP) {
          var ITERATOR_NAME = CONSTRUCTOR_NAME + " Iterator";
          var getInternalCollectionState = internalStateGetterFor(CONSTRUCTOR_NAME);
          var getInternalIteratorState = internalStateGetterFor(ITERATOR_NAME);
          defineIterator2(C, CONSTRUCTOR_NAME, function(iterated, kind) {
            setInternalState3(this, {
              type: ITERATOR_NAME,
              target: iterated,
              state: getInternalCollectionState(iterated),
              kind: kind,
              last: void 0
            });
          }, function() {
            var state = getInternalIteratorState(this);
            var kind = state.kind;
            var entry = state.last;
            while (entry && entry.removed)
              entry = entry.previous;
            if (!state.target || !(state.last = entry = entry ? entry.next : state.state.first)) {
              state.target = void 0;
              return { value: void 0, done: true };
            }
            if (kind == "keys")
              return { value: entry.key, done: false };
            if (kind == "values")
              return { value: entry.value, done: false };
            return { value: [entry.key, entry.value], done: false };
          }, IS_MAP ? "entries" : "values", !IS_MAP, true);
          setSpecies(CONSTRUCTOR_NAME);
        }
      };
    }
  });

  // node_modules/core-js/modules/es.map.js
  var require_es_map = __commonJS({
    "node_modules/core-js/modules/es.map.js": function(exports, module) {
      "use strict";
      var collection = require_collection();
      var collectionStrong = require_collection_strong();
      module.exports = collection("Map", function(init) {
        return function Map2() {
          return init(this, arguments.length ? arguments[0] : void 0);
        };
      }, collectionStrong);
    }
  });

  // node_modules/core-js/internals/string-multibyte.js
  var require_string_multibyte = __commonJS({
    "node_modules/core-js/internals/string-multibyte.js": function(exports, module) {
      var toInteger = require_to_integer();
      var requireObjectCoercible2 = require_require_object_coercible();
      var createMethod = function(CONVERT_TO_STRING) {
        return function($this, pos) {
          var S = String(requireObjectCoercible2($this));
          var position = toInteger(pos);
          var size = S.length;
          var first, second;
          if (position < 0 || position >= size)
            return CONVERT_TO_STRING ? "" : void 0;
          first = S.charCodeAt(position);
          return first < 55296 || first > 56319 || position + 1 === size || (second = S.charCodeAt(position + 1)) < 56320 || second > 57343 ? CONVERT_TO_STRING ? S.charAt(position) : first : CONVERT_TO_STRING ? S.slice(position, position + 2) : (first - 55296 << 10) + (second - 56320) + 65536;
        };
      };
      module.exports = {
        codeAt: createMethod(false),
        charAt: createMethod(true)
      };
    }
  });

  // node_modules/core-js/internals/dom-iterables.js
  var require_dom_iterables = __commonJS({
    "node_modules/core-js/internals/dom-iterables.js": function(exports, module) {
      module.exports = {
        CSSRuleList: 0,
        CSSStyleDeclaration: 0,
        CSSValueList: 0,
        ClientRectList: 0,
        DOMRectList: 0,
        DOMStringList: 0,
        DOMTokenList: 1,
        DataTransferItemList: 0,
        FileList: 0,
        HTMLAllCollection: 0,
        HTMLCollection: 0,
        HTMLFormElement: 0,
        HTMLSelectElement: 0,
        MediaList: 0,
        MimeTypeArray: 0,
        NamedNodeMap: 0,
        NodeList: 1,
        PaintRequestList: 0,
        Plugin: 0,
        PluginArray: 0,
        SVGLengthList: 0,
        SVGNumberList: 0,
        SVGPathSegList: 0,
        SVGPointList: 0,
        SVGStringList: 0,
        SVGTransformList: 0,
        SourceBufferList: 0,
        StyleSheetList: 0,
        TextTrackCueList: 0,
        TextTrackList: 0,
        TouchList: 0
      };
    }
  });

  // node_modules/core-js/internals/is-array.js
  var require_is_array = __commonJS({
    "node_modules/core-js/internals/is-array.js": function(exports, module) {
      var classof = require_classof_raw();
      module.exports = Array.isArray || function isArray5(arg) {
        return classof(arg) == "Array";
      };
    }
  });

  // node_modules/core-js/internals/object-get-own-property-names-external.js
  var require_object_get_own_property_names_external = __commonJS({
    "node_modules/core-js/internals/object-get-own-property-names-external.js": function(exports, module) {
      var toIndexedObject3 = require_to_indexed_object();
      var $getOwnPropertyNames2 = require_object_get_own_property_names().f;
      var toString2 = {}.toString;
      var windowNames = typeof window == "object" && window && Object.getOwnPropertyNames ? Object.getOwnPropertyNames(window) : [];
      var getWindowNames = function(it) {
        try {
          return $getOwnPropertyNames2(it);
        } catch (error) {
          return windowNames.slice();
        }
      };
      module.exports.f = function getOwnPropertyNames2(it) {
        return windowNames && toString2.call(it) == "[object Window]" ? getWindowNames(it) : $getOwnPropertyNames2(toIndexedObject3(it));
      };
    }
  });

  // node_modules/core-js/internals/well-known-symbol-wrapped.js
  var require_well_known_symbol_wrapped = __commonJS({
    "node_modules/core-js/internals/well-known-symbol-wrapped.js": function(exports) {
      var wellKnownSymbol5 = require_well_known_symbol();
      exports.f = wellKnownSymbol5;
    }
  });

  // node_modules/core-js/internals/define-well-known-symbol.js
  var require_define_well_known_symbol = __commonJS({
    "node_modules/core-js/internals/define-well-known-symbol.js": function(exports, module) {
      var path = require_path();
      var has3 = require_has();
      var wrappedWellKnownSymbolModule2 = require_well_known_symbol_wrapped();
      var defineProperty4 = require_object_define_property().f;
      module.exports = function(NAME2) {
        var Symbol2 = path.Symbol || (path.Symbol = {});
        if (!has3(Symbol2, NAME2))
          defineProperty4(Symbol2, NAME2, {
            value: wrappedWellKnownSymbolModule2.f(NAME2)
          });
      };
    }
  });

  // node_modules/core-js/internals/array-species-create.js
  var require_array_species_create = __commonJS({
    "node_modules/core-js/internals/array-species-create.js": function(exports, module) {
      var isObject6 = require_is_object();
      var isArray5 = require_is_array();
      var wellKnownSymbol5 = require_well_known_symbol();
      var SPECIES2 = wellKnownSymbol5("species");
      module.exports = function(originalArray, length) {
        var C;
        if (isArray5(originalArray)) {
          C = originalArray.constructor;
          if (typeof C == "function" && (C === Array || isArray5(C.prototype)))
            C = void 0;
          else if (isObject6(C)) {
            C = C[SPECIES2];
            if (C === null)
              C = void 0;
          }
        }
        return new (C === void 0 ? Array : C)(length === 0 ? 0 : length);
      };
    }
  });

  // node_modules/core-js/internals/array-iteration.js
  var require_array_iteration = __commonJS({
    "node_modules/core-js/internals/array-iteration.js": function(exports, module) {
      var bind3 = require_function_bind_context();
      var IndexedObject = require_indexed_object();
      var toObject4 = require_to_object();
      var toLength4 = require_to_length();
      var arraySpeciesCreate2 = require_array_species_create();
      var push = [].push;
      var createMethod = function(TYPE) {
        var IS_MAP = TYPE == 1;
        var IS_FILTER = TYPE == 2;
        var IS_SOME = TYPE == 3;
        var IS_EVERY = TYPE == 4;
        var IS_FIND_INDEX = TYPE == 6;
        var IS_FILTER_OUT = TYPE == 7;
        var NO_HOLES = TYPE == 5 || IS_FIND_INDEX;
        return function($this, callbackfn, that, specificCreate) {
          var O = toObject4($this);
          var self2 = IndexedObject(O);
          var boundFunction = bind3(callbackfn, that, 3);
          var length = toLength4(self2.length);
          var index = 0;
          var create4 = specificCreate || arraySpeciesCreate2;
          var target = IS_MAP ? create4($this, length) : IS_FILTER || IS_FILTER_OUT ? create4($this, 0) : void 0;
          var value, result;
          for (; length > index; index++)
            if (NO_HOLES || index in self2) {
              value = self2[index];
              result = boundFunction(value, index, O);
              if (TYPE) {
                if (IS_MAP)
                  target[index] = result;
                else if (result)
                  switch (TYPE) {
                    case 3:
                      return true;
                    case 5:
                      return value;
                    case 6:
                      return index;
                    case 2:
                      push.call(target, value);
                  }
                else
                  switch (TYPE) {
                    case 4:
                      return false;
                    case 7:
                      push.call(target, value);
                  }
              }
            }
          return IS_FIND_INDEX ? -1 : IS_SOME || IS_EVERY ? IS_EVERY : target;
        };
      };
      module.exports = {
        forEach: createMethod(0),
        map: createMethod(1),
        filter: createMethod(2),
        some: createMethod(3),
        every: createMethod(4),
        find: createMethod(5),
        findIndex: createMethod(6),
        filterOut: createMethod(7)
      };
    }
  });

  // node_modules/core-js/internals/array-for-each.js
  var require_array_for_each = __commonJS({
    "node_modules/core-js/internals/array-for-each.js": function(exports, module) {
      "use strict";
      var $forEach2 = require_array_iteration().forEach;
      var arrayMethodIsStrict2 = require_array_method_is_strict();
      var STRICT_METHOD2 = arrayMethodIsStrict2("forEach");
      module.exports = !STRICT_METHOD2 ? function forEach3(callbackfn) {
        return $forEach2(this, callbackfn, arguments.length > 1 ? arguments[1] : void 0);
      } : [].forEach;
    }
  });

  // node_modules/core-js/internals/object-to-array.js
  var require_object_to_array = __commonJS({
    "node_modules/core-js/internals/object-to-array.js": function(exports, module) {
      var DESCRIPTORS5 = require_descriptors();
      var objectKeys2 = require_object_keys();
      var toIndexedObject3 = require_to_indexed_object();
      var propertyIsEnumerable2 = require_object_property_is_enumerable().f;
      var createMethod = function(TO_ENTRIES) {
        return function(it) {
          var O = toIndexedObject3(it);
          var keys = objectKeys2(O);
          var length = keys.length;
          var i = 0;
          var result = [];
          var key;
          while (length > i) {
            key = keys[i++];
            if (!DESCRIPTORS5 || propertyIsEnumerable2.call(O, key)) {
              result.push(TO_ENTRIES ? [key, O[key]] : O[key]);
            }
          }
          return result;
        };
      };
      module.exports = {
        entries: createMethod(true),
        values: createMethod(false)
      };
    }
  });

  // node_modules/core-js/internals/is-regexp.js
  var require_is_regexp = __commonJS({
    "node_modules/core-js/internals/is-regexp.js": function(exports, module) {
      var isObject6 = require_is_object();
      var classof = require_classof_raw();
      var wellKnownSymbol5 = require_well_known_symbol();
      var MATCH = wellKnownSymbol5("match");
      module.exports = function(it) {
        var isRegExp;
        return isObject6(it) && ((isRegExp = it[MATCH]) !== void 0 ? !!isRegExp : classof(it) == "RegExp");
      };
    }
  });

  // node_modules/core-js/internals/not-a-regexp.js
  var require_not_a_regexp = __commonJS({
    "node_modules/core-js/internals/not-a-regexp.js": function(exports, module) {
      var isRegExp = require_is_regexp();
      module.exports = function(it) {
        if (isRegExp(it)) {
          throw TypeError("The method doesn't accept regular expressions");
        }
        return it;
      };
    }
  });

  // node_modules/core-js/internals/correct-is-regexp-logic.js
  var require_correct_is_regexp_logic = __commonJS({
    "node_modules/core-js/internals/correct-is-regexp-logic.js": function(exports, module) {
      var wellKnownSymbol5 = require_well_known_symbol();
      var MATCH = wellKnownSymbol5("match");
      module.exports = function(METHOD_NAME) {
        var regexp = /./;
        try {
          "/./"[METHOD_NAME](regexp);
        } catch (error1) {
          try {
            regexp[MATCH] = false;
            return "/./"[METHOD_NAME](regexp);
          } catch (error2) {
          }
        }
        return false;
      };
    }
  });

  // node_modules/core-js/internals/create-property.js
  var require_create_property = __commonJS({
    "node_modules/core-js/internals/create-property.js": function(exports, module) {
      "use strict";
      var toPrimitive2 = require_to_primitive();
      var definePropertyModule2 = require_object_define_property();
      var createPropertyDescriptor2 = require_create_property_descriptor();
      module.exports = function(object, key, value) {
        var propertyKey = toPrimitive2(key);
        if (propertyKey in object)
          definePropertyModule2.f(object, propertyKey, createPropertyDescriptor2(0, value));
        else
          object[propertyKey] = value;
      };
    }
  });

  // node_modules/core-js/internals/array-method-has-species-support.js
  var require_array_method_has_species_support = __commonJS({
    "node_modules/core-js/internals/array-method-has-species-support.js": function(exports, module) {
      var fails6 = require_fails();
      var wellKnownSymbol5 = require_well_known_symbol();
      var V8_VERSION2 = require_engine_v8_version();
      var SPECIES2 = wellKnownSymbol5("species");
      module.exports = function(METHOD_NAME) {
        return V8_VERSION2 >= 51 || !fails6(function() {
          var array = [];
          var constructor = array.constructor = {};
          constructor[SPECIES2] = function() {
            return { foo: 1 };
          };
          return array[METHOD_NAME](Boolean).foo !== 1;
        });
      };
    }
  });

  // node_modules/core-js/internals/call-with-safe-iteration-closing.js
  var require_call_with_safe_iteration_closing = __commonJS({
    "node_modules/core-js/internals/call-with-safe-iteration-closing.js": function(exports, module) {
      var anObject4 = require_an_object();
      var iteratorClose = require_iterator_close();
      module.exports = function(iterator, fn, value, ENTRIES) {
        try {
          return ENTRIES ? fn(anObject4(value)[0], value[1]) : fn(value);
        } catch (error) {
          iteratorClose(iterator);
          throw error;
        }
      };
    }
  });

  // node_modules/core-js/internals/array-from.js
  var require_array_from = __commonJS({
    "node_modules/core-js/internals/array-from.js": function(exports, module) {
      "use strict";
      var bind3 = require_function_bind_context();
      var toObject4 = require_to_object();
      var callWithSafeIterationClosing = require_call_with_safe_iteration_closing();
      var isArrayIteratorMethod = require_is_array_iterator_method();
      var toLength4 = require_to_length();
      var createProperty3 = require_create_property();
      var getIteratorMethod = require_get_iterator_method();
      module.exports = function from2(arrayLike) {
        var O = toObject4(arrayLike);
        var C = typeof this == "function" ? this : Array;
        var argumentsLength = arguments.length;
        var mapfn = argumentsLength > 1 ? arguments[1] : void 0;
        var mapping = mapfn !== void 0;
        var iteratorMethod = getIteratorMethod(O);
        var index = 0;
        var length, result, step, iterator, next2, value;
        if (mapping)
          mapfn = bind3(mapfn, argumentsLength > 2 ? arguments[2] : void 0, 2);
        if (iteratorMethod != void 0 && !(C == Array && isArrayIteratorMethod(iteratorMethod))) {
          iterator = iteratorMethod.call(O);
          next2 = iterator.next;
          result = new C();
          for (; !(step = next2.call(iterator)).done; index++) {
            value = mapping ? callWithSafeIterationClosing(iterator, mapfn, [step.value, index], true) : step.value;
            createProperty3(result, index, value);
          }
        } else {
          length = toLength4(O.length);
          result = new C(length);
          for (; length > index; index++) {
            value = mapping ? mapfn(O[index], index) : O[index];
            createProperty3(result, index, value);
          }
        }
        result.length = index;
        return result;
      };
    }
  });

  // node_modules/core-js/modules/es.object.set-prototype-of.js
  var $ = require_export();
  var setPrototypeOf = require_object_set_prototype_of();
  $({ target: "Object", stat: true }, {
    setPrototypeOf: setPrototypeOf
  });

  // node_modules/core-js/modules/es.object.get-prototype-of.js
  var $2 = require_export();
  var fails = require_fails();
  var toObject = require_to_object();
  var nativeGetPrototypeOf = require_object_get_prototype_of();
  var CORRECT_PROTOTYPE_GETTER = require_correct_prototype_getter();
  var FAILS_ON_PRIMITIVES = fails(function() {
    nativeGetPrototypeOf(1);
  });
  $2({ target: "Object", stat: true, forced: FAILS_ON_PRIMITIVES, sham: !CORRECT_PROTOTYPE_GETTER }, {
    getPrototypeOf: function getPrototypeOf(it) {
      return nativeGetPrototypeOf(toObject(it));
    }
  });

  // node_modules/core-js/modules/es.array.index-of.js
  "use strict";
  var $3 = require_export();
  var $indexOf = require_array_includes().indexOf;
  var arrayMethodIsStrict = require_array_method_is_strict();
  var nativeIndexOf = [].indexOf;
  var NEGATIVE_ZERO = !!nativeIndexOf && 1 / [1].indexOf(1, -0) < 0;
  var STRICT_METHOD = arrayMethodIsStrict("indexOf");
  $3({ target: "Array", proto: true, forced: NEGATIVE_ZERO || !STRICT_METHOD }, {
    indexOf: function indexOf(searchElement) {
      return NEGATIVE_ZERO ? nativeIndexOf.apply(this, arguments) || 0 : $indexOf(this, searchElement, arguments.length > 1 ? arguments[1] : void 0);
    }
  });

  // node_modules/core-js/modules/es.date.to-string.js
  var redefine = require_redefine();
  var DatePrototype = Date.prototype;
  var INVALID_DATE = "Invalid Date";
  var TO_STRING = "toString";
  var nativeDateToString = DatePrototype[TO_STRING];
  var getTime = DatePrototype.getTime;
  if (new Date(NaN) + "" != INVALID_DATE) {
    redefine(DatePrototype, TO_STRING, function toString2() {
      var value = getTime.call(this);
      return value === value ? nativeDateToString.call(this) : INVALID_DATE;
    });
  }

  // node_modules/core-js/modules/es.object.to-string.js
  var TO_STRING_TAG_SUPPORT = require_to_string_tag_support();
  var redefine2 = require_redefine();
  var toString = require_object_to_string();
  if (!TO_STRING_TAG_SUPPORT) {
    redefine2(Object.prototype, "toString", toString, { unsafe: true });
  }

  // node_modules/core-js/modules/es.regexp.to-string.js
  "use strict";
  var redefine3 = require_redefine();
  var anObject = require_an_object();
  var fails2 = require_fails();
  var flags = require_regexp_flags();
  var TO_STRING2 = "toString";
  var RegExpPrototype = RegExp.prototype;
  var nativeToString = RegExpPrototype[TO_STRING2];
  var NOT_GENERIC = fails2(function() {
    return nativeToString.call({ source: "a", flags: "b" }) != "/a/b";
  });
  var INCORRECT_NAME = nativeToString.name != TO_STRING2;
  if (NOT_GENERIC || INCORRECT_NAME) {
    redefine3(RegExp.prototype, TO_STRING2, function toString2() {
      var R = anObject(this);
      var p = String(R.source);
      var rf = R.flags;
      var f = String(rf === void 0 && R instanceof RegExp && !("flags" in RegExpPrototype) ? flags.call(R) : rf);
      return "/" + p + "/" + f;
    }, { unsafe: true });
  }

  // node_modules/core-js/modules/es.reflect.construct.js
  var $4 = require_export();
  var getBuiltIn = require_get_built_in();
  var aFunction = require_a_function();
  var anObject2 = require_an_object();
  var isObject = require_is_object();
  var create = require_object_create();
  var bind = require_function_bind();
  var fails3 = require_fails();
  var nativeConstruct = getBuiltIn("Reflect", "construct");
  var NEW_TARGET_BUG = fails3(function() {
    function F() {
    }
    return !(nativeConstruct(function() {
    }, [], F) instanceof F);
  });
  var ARGS_BUG = !fails3(function() {
    nativeConstruct(function() {
    });
  });
  var FORCED = NEW_TARGET_BUG || ARGS_BUG;
  $4({ target: "Reflect", stat: true, forced: FORCED, sham: FORCED }, {
    construct: function construct(Target, args) {
      aFunction(Target);
      anObject2(args);
      var newTarget = arguments.length < 3 ? Target : aFunction(arguments[2]);
      if (ARGS_BUG && !NEW_TARGET_BUG)
        return nativeConstruct(Target, args, newTarget);
      if (Target == newTarget) {
        switch (args.length) {
          case 0:
            return new Target();
          case 1:
            return new Target(args[0]);
          case 2:
            return new Target(args[0], args[1]);
          case 3:
            return new Target(args[0], args[1], args[2]);
          case 4:
            return new Target(args[0], args[1], args[2], args[3]);
        }
        var $args = [null];
        $args.push.apply($args, args);
        return new (bind.apply(Target, $args))();
      }
      var proto = newTarget.prototype;
      var instance = create(isObject(proto) ? proto : Object.prototype);
      var result = Function.apply.call(Target, instance, args);
      return isObject(result) ? result : instance;
    }
  });

  // node_modules/core-js/modules/es.function.bind.js
  var $5 = require_export();
  var bind2 = require_function_bind();
  $5({ target: "Function", proto: true }, {
    bind: bind2
  });

  // src/nav.js
  var import_es_array_iterator2 = __toModule(require_es_array_iterator());
  var import_es_map = __toModule(require_es_map());

  // node_modules/core-js/modules/es.string.iterator.js
  "use strict";
  var charAt = require_string_multibyte().charAt;
  var InternalStateModule = require_internal_state();
  var defineIterator = require_define_iterator();
  var STRING_ITERATOR = "String Iterator";
  var setInternalState = InternalStateModule.set;
  var getInternalState = InternalStateModule.getterFor(STRING_ITERATOR);
  defineIterator(String, "String", function(iterated) {
    setInternalState(this, {
      type: STRING_ITERATOR,
      string: String(iterated),
      index: 0
    });
  }, function next() {
    var state = getInternalState(this);
    var string = state.string;
    var index = state.index;
    var point;
    if (index >= string.length)
      return { value: void 0, done: true };
    point = charAt(string, index);
    state.index += point.length;
    return { value: point, done: false };
  });

  // node_modules/core-js/modules/web.dom-collections.iterator.js
  var global2 = require_global();
  var DOMIterables = require_dom_iterables();
  var ArrayIteratorMethods = require_es_array_iterator();
  var createNonEnumerableProperty = require_create_non_enumerable_property();
  var wellKnownSymbol = require_well_known_symbol();
  var ITERATOR = wellKnownSymbol("iterator");
  var TO_STRING_TAG = wellKnownSymbol("toStringTag");
  var ArrayValues = ArrayIteratorMethods.values;
  for (var COLLECTION_NAME in DOMIterables) {
    Collection = global2[COLLECTION_NAME];
    CollectionPrototype = Collection && Collection.prototype;
    if (CollectionPrototype) {
      if (CollectionPrototype[ITERATOR] !== ArrayValues)
        try {
          createNonEnumerableProperty(CollectionPrototype, ITERATOR, ArrayValues);
        } catch (error) {
          CollectionPrototype[ITERATOR] = ArrayValues;
        }
      if (!CollectionPrototype[TO_STRING_TAG]) {
        createNonEnumerableProperty(CollectionPrototype, TO_STRING_TAG, COLLECTION_NAME);
      }
      if (DOMIterables[COLLECTION_NAME])
        for (METHOD_NAME in ArrayIteratorMethods) {
          if (CollectionPrototype[METHOD_NAME] !== ArrayIteratorMethods[METHOD_NAME])
            try {
              createNonEnumerableProperty(CollectionPrototype, METHOD_NAME, ArrayIteratorMethods[METHOD_NAME]);
            } catch (error) {
              CollectionPrototype[METHOD_NAME] = ArrayIteratorMethods[METHOD_NAME];
            }
        }
    }
  }
  var Collection;
  var CollectionPrototype;
  var METHOD_NAME;

  // node_modules/core-js/modules/es.object.create.js
  var $6 = require_export();
  var DESCRIPTORS = require_descriptors();
  var create2 = require_object_create();
  $6({ target: "Object", stat: true, sham: !DESCRIPTORS }, {
    create: create2
  });

  // node_modules/core-js/modules/es.symbol.js
  "use strict";
  var $7 = require_export();
  var global3 = require_global();
  var getBuiltIn2 = require_get_built_in();
  var IS_PURE = require_is_pure();
  var DESCRIPTORS2 = require_descriptors();
  var NATIVE_SYMBOL = require_native_symbol();
  var USE_SYMBOL_AS_UID = require_use_symbol_as_uid();
  var fails4 = require_fails();
  var has = require_has();
  var isArray = require_is_array();
  var isObject2 = require_is_object();
  var anObject3 = require_an_object();
  var toObject2 = require_to_object();
  var toIndexedObject = require_to_indexed_object();
  var toPrimitive = require_to_primitive();
  var createPropertyDescriptor = require_create_property_descriptor();
  var nativeObjectCreate = require_object_create();
  var objectKeys = require_object_keys();
  var getOwnPropertyNamesModule = require_object_get_own_property_names();
  var getOwnPropertyNamesExternal = require_object_get_own_property_names_external();
  var getOwnPropertySymbolsModule = require_object_get_own_property_symbols();
  var getOwnPropertyDescriptorModule = require_object_get_own_property_descriptor();
  var definePropertyModule = require_object_define_property();
  var propertyIsEnumerableModule = require_object_property_is_enumerable();
  var createNonEnumerableProperty2 = require_create_non_enumerable_property();
  var redefine4 = require_redefine();
  var shared = require_shared();
  var sharedKey = require_shared_key();
  var hiddenKeys = require_hidden_keys();
  var uid = require_uid();
  var wellKnownSymbol2 = require_well_known_symbol();
  var wrappedWellKnownSymbolModule = require_well_known_symbol_wrapped();
  var defineWellKnownSymbol = require_define_well_known_symbol();
  var setToStringTag = require_set_to_string_tag();
  var InternalStateModule2 = require_internal_state();
  var $forEach = require_array_iteration().forEach;
  var HIDDEN = sharedKey("hidden");
  var SYMBOL = "Symbol";
  var PROTOTYPE = "prototype";
  var TO_PRIMITIVE = wellKnownSymbol2("toPrimitive");
  var setInternalState2 = InternalStateModule2.set;
  var getInternalState2 = InternalStateModule2.getterFor(SYMBOL);
  var ObjectPrototype = Object[PROTOTYPE];
  var $Symbol = global3.Symbol;
  var $stringify = getBuiltIn2("JSON", "stringify");
  var nativeGetOwnPropertyDescriptor = getOwnPropertyDescriptorModule.f;
  var nativeDefineProperty = definePropertyModule.f;
  var nativeGetOwnPropertyNames = getOwnPropertyNamesExternal.f;
  var nativePropertyIsEnumerable = propertyIsEnumerableModule.f;
  var AllSymbols = shared("symbols");
  var ObjectPrototypeSymbols = shared("op-symbols");
  var StringToSymbolRegistry = shared("string-to-symbol-registry");
  var SymbolToStringRegistry = shared("symbol-to-string-registry");
  var WellKnownSymbolsStore = shared("wks");
  var QObject = global3.QObject;
  var USE_SETTER = !QObject || !QObject[PROTOTYPE] || !QObject[PROTOTYPE].findChild;
  var setSymbolDescriptor = DESCRIPTORS2 && fails4(function() {
    return nativeObjectCreate(nativeDefineProperty({}, "a", {
      get: function() {
        return nativeDefineProperty(this, "a", { value: 7 }).a;
      }
    })).a != 7;
  }) ? function(O, P, Attributes) {
    var ObjectPrototypeDescriptor = nativeGetOwnPropertyDescriptor(ObjectPrototype, P);
    if (ObjectPrototypeDescriptor)
      delete ObjectPrototype[P];
    nativeDefineProperty(O, P, Attributes);
    if (ObjectPrototypeDescriptor && O !== ObjectPrototype) {
      nativeDefineProperty(ObjectPrototype, P, ObjectPrototypeDescriptor);
    }
  } : nativeDefineProperty;
  var wrap = function(tag2, description) {
    var symbol = AllSymbols[tag2] = nativeObjectCreate($Symbol[PROTOTYPE]);
    setInternalState2(symbol, {
      type: SYMBOL,
      tag: tag2,
      description: description
    });
    if (!DESCRIPTORS2)
      symbol.description = description;
    return symbol;
  };
  var isSymbol = USE_SYMBOL_AS_UID ? function(it) {
    return typeof it == "symbol";
  } : function(it) {
    return Object(it) instanceof $Symbol;
  };
  var $defineProperty = function defineProperty(O, P, Attributes) {
    if (O === ObjectPrototype)
      $defineProperty(ObjectPrototypeSymbols, P, Attributes);
    anObject3(O);
    var key = toPrimitive(P, true);
    anObject3(Attributes);
    if (has(AllSymbols, key)) {
      if (!Attributes.enumerable) {
        if (!has(O, HIDDEN))
          nativeDefineProperty(O, HIDDEN, createPropertyDescriptor(1, {}));
        O[HIDDEN][key] = true;
      } else {
        if (has(O, HIDDEN) && O[HIDDEN][key])
          O[HIDDEN][key] = false;
        Attributes = nativeObjectCreate(Attributes, { enumerable: createPropertyDescriptor(0, false) });
      }
      return setSymbolDescriptor(O, key, Attributes);
    }
    return nativeDefineProperty(O, key, Attributes);
  };
  var $defineProperties = function defineProperties(O, Properties) {
    anObject3(O);
    var properties = toIndexedObject(Properties);
    var keys = objectKeys(properties).concat($getOwnPropertySymbols(properties));
    $forEach(keys, function(key) {
      if (!DESCRIPTORS2 || $propertyIsEnumerable.call(properties, key))
        $defineProperty(O, key, properties[key]);
    });
    return O;
  };
  var $create = function create3(O, Properties) {
    return Properties === void 0 ? nativeObjectCreate(O) : $defineProperties(nativeObjectCreate(O), Properties);
  };
  var $propertyIsEnumerable = function propertyIsEnumerable(V) {
    var P = toPrimitive(V, true);
    var enumerable = nativePropertyIsEnumerable.call(this, P);
    if (this === ObjectPrototype && has(AllSymbols, P) && !has(ObjectPrototypeSymbols, P))
      return false;
    return enumerable || !has(this, P) || !has(AllSymbols, P) || has(this, HIDDEN) && this[HIDDEN][P] ? enumerable : true;
  };
  var $getOwnPropertyDescriptor = function getOwnPropertyDescriptor(O, P) {
    var it = toIndexedObject(O);
    var key = toPrimitive(P, true);
    if (it === ObjectPrototype && has(AllSymbols, key) && !has(ObjectPrototypeSymbols, key))
      return;
    var descriptor = nativeGetOwnPropertyDescriptor(it, key);
    if (descriptor && has(AllSymbols, key) && !(has(it, HIDDEN) && it[HIDDEN][key])) {
      descriptor.enumerable = true;
    }
    return descriptor;
  };
  var $getOwnPropertyNames = function getOwnPropertyNames(O) {
    var names = nativeGetOwnPropertyNames(toIndexedObject(O));
    var result = [];
    $forEach(names, function(key) {
      if (!has(AllSymbols, key) && !has(hiddenKeys, key))
        result.push(key);
    });
    return result;
  };
  var $getOwnPropertySymbols = function getOwnPropertySymbols(O) {
    var IS_OBJECT_PROTOTYPE = O === ObjectPrototype;
    var names = nativeGetOwnPropertyNames(IS_OBJECT_PROTOTYPE ? ObjectPrototypeSymbols : toIndexedObject(O));
    var result = [];
    $forEach(names, function(key) {
      if (has(AllSymbols, key) && (!IS_OBJECT_PROTOTYPE || has(ObjectPrototype, key))) {
        result.push(AllSymbols[key]);
      }
    });
    return result;
  };
  if (!NATIVE_SYMBOL) {
    $Symbol = function Symbol2() {
      if (this instanceof $Symbol)
        throw TypeError("Symbol is not a constructor");
      var description = !arguments.length || arguments[0] === void 0 ? void 0 : String(arguments[0]);
      var tag2 = uid(description);
      var setter = function(value) {
        if (this === ObjectPrototype)
          setter.call(ObjectPrototypeSymbols, value);
        if (has(this, HIDDEN) && has(this[HIDDEN], tag2))
          this[HIDDEN][tag2] = false;
        setSymbolDescriptor(this, tag2, createPropertyDescriptor(1, value));
      };
      if (DESCRIPTORS2 && USE_SETTER)
        setSymbolDescriptor(ObjectPrototype, tag2, { configurable: true, set: setter });
      return wrap(tag2, description);
    };
    redefine4($Symbol[PROTOTYPE], "toString", function toString2() {
      return getInternalState2(this).tag;
    });
    redefine4($Symbol, "withoutSetter", function(description) {
      return wrap(uid(description), description);
    });
    propertyIsEnumerableModule.f = $propertyIsEnumerable;
    definePropertyModule.f = $defineProperty;
    getOwnPropertyDescriptorModule.f = $getOwnPropertyDescriptor;
    getOwnPropertyNamesModule.f = getOwnPropertyNamesExternal.f = $getOwnPropertyNames;
    getOwnPropertySymbolsModule.f = $getOwnPropertySymbols;
    wrappedWellKnownSymbolModule.f = function(name2) {
      return wrap(wellKnownSymbol2(name2), name2);
    };
    if (DESCRIPTORS2) {
      nativeDefineProperty($Symbol[PROTOTYPE], "description", {
        configurable: true,
        get: function description() {
          return getInternalState2(this).description;
        }
      });
      if (!IS_PURE) {
        redefine4(ObjectPrototype, "propertyIsEnumerable", $propertyIsEnumerable, { unsafe: true });
      }
    }
  }
  $7({ global: true, wrap: true, forced: !NATIVE_SYMBOL, sham: !NATIVE_SYMBOL }, {
    Symbol: $Symbol
  });
  $forEach(objectKeys(WellKnownSymbolsStore), function(name2) {
    defineWellKnownSymbol(name2);
  });
  $7({ target: SYMBOL, stat: true, forced: !NATIVE_SYMBOL }, {
    "for": function(key) {
      var string = String(key);
      if (has(StringToSymbolRegistry, string))
        return StringToSymbolRegistry[string];
      var symbol = $Symbol(string);
      StringToSymbolRegistry[string] = symbol;
      SymbolToStringRegistry[symbol] = string;
      return symbol;
    },
    keyFor: function keyFor(sym) {
      if (!isSymbol(sym))
        throw TypeError(sym + " is not a symbol");
      if (has(SymbolToStringRegistry, sym))
        return SymbolToStringRegistry[sym];
    },
    useSetter: function() {
      USE_SETTER = true;
    },
    useSimple: function() {
      USE_SETTER = false;
    }
  });
  $7({ target: "Object", stat: true, forced: !NATIVE_SYMBOL, sham: !DESCRIPTORS2 }, {
    create: $create,
    defineProperty: $defineProperty,
    defineProperties: $defineProperties,
    getOwnPropertyDescriptor: $getOwnPropertyDescriptor
  });
  $7({ target: "Object", stat: true, forced: !NATIVE_SYMBOL }, {
    getOwnPropertyNames: $getOwnPropertyNames,
    getOwnPropertySymbols: $getOwnPropertySymbols
  });
  $7({ target: "Object", stat: true, forced: fails4(function() {
    getOwnPropertySymbolsModule.f(1);
  }) }, {
    getOwnPropertySymbols: function getOwnPropertySymbols2(it) {
      return getOwnPropertySymbolsModule.f(toObject2(it));
    }
  });
  if ($stringify) {
    FORCED_JSON_STRINGIFY = !NATIVE_SYMBOL || fails4(function() {
      var symbol = $Symbol();
      return $stringify([symbol]) != "[null]" || $stringify({ a: symbol }) != "{}" || $stringify(Object(symbol)) != "{}";
    });
    $7({ target: "JSON", stat: true, forced: FORCED_JSON_STRINGIFY }, {
      stringify: function stringify(it, replacer, space) {
        var args = [it];
        var index = 1;
        var $replacer;
        while (arguments.length > index)
          args.push(arguments[index++]);
        $replacer = replacer;
        if (!isObject2(replacer) && it === void 0 || isSymbol(it))
          return;
        if (!isArray(replacer))
          replacer = function(key, value) {
            if (typeof $replacer == "function")
              value = $replacer.call(this, key, value);
            if (!isSymbol(value))
              return value;
          };
        args[1] = replacer;
        return $stringify.apply(null, args);
      }
    });
  }
  var FORCED_JSON_STRINGIFY;
  if (!$Symbol[PROTOTYPE][TO_PRIMITIVE]) {
    createNonEnumerableProperty2($Symbol[PROTOTYPE], TO_PRIMITIVE, $Symbol[PROTOTYPE].valueOf);
  }
  setToStringTag($Symbol, SYMBOL);
  hiddenKeys[HIDDEN] = true;

  // node_modules/core-js/modules/es.symbol.description.js
  "use strict";
  var $8 = require_export();
  var DESCRIPTORS3 = require_descriptors();
  var global4 = require_global();
  var has2 = require_has();
  var isObject3 = require_is_object();
  var defineProperty2 = require_object_define_property().f;
  var copyConstructorProperties = require_copy_constructor_properties();
  var NativeSymbol = global4.Symbol;
  if (DESCRIPTORS3 && typeof NativeSymbol == "function" && (!("description" in NativeSymbol.prototype) || NativeSymbol().description !== void 0)) {
    EmptyStringDescriptionStore = {};
    SymbolWrapper = function Symbol2() {
      var description = arguments.length < 1 || arguments[0] === void 0 ? void 0 : String(arguments[0]);
      var result = this instanceof SymbolWrapper ? new NativeSymbol(description) : description === void 0 ? NativeSymbol() : NativeSymbol(description);
      if (description === "")
        EmptyStringDescriptionStore[result] = true;
      return result;
    };
    copyConstructorProperties(SymbolWrapper, NativeSymbol);
    symbolPrototype = SymbolWrapper.prototype = NativeSymbol.prototype;
    symbolPrototype.constructor = SymbolWrapper;
    symbolToString = symbolPrototype.toString;
    native = String(NativeSymbol("test")) == "Symbol(test)";
    regexp = /^Symbol\((.*)\)[^)]+$/;
    defineProperty2(symbolPrototype, "description", {
      configurable: true,
      get: function description() {
        var symbol = isObject3(this) ? this.valueOf() : this;
        var string = symbolToString.call(symbol);
        if (has2(EmptyStringDescriptionStore, symbol))
          return "";
        var desc = native ? string.slice(7, -1) : string.replace(regexp, "$1");
        return desc === "" ? void 0 : desc;
      }
    });
    $8({ global: true, forced: true }, {
      Symbol: SymbolWrapper
    });
  }
  var EmptyStringDescriptionStore;
  var SymbolWrapper;
  var symbolPrototype;
  var symbolToString;
  var native;
  var regexp;

  // node_modules/core-js/modules/es.symbol.iterator.js
  var defineWellKnownSymbol2 = require_define_well_known_symbol();
  defineWellKnownSymbol2("iterator");

  // node_modules/core-js/modules/es.array.for-each.js
  "use strict";
  var $9 = require_export();
  var forEach = require_array_for_each();
  $9({ target: "Array", proto: true, forced: [].forEach != forEach }, {
    forEach: forEach
  });

  // node_modules/core-js/modules/web.dom-collections.for-each.js
  var global5 = require_global();
  var DOMIterables2 = require_dom_iterables();
  var forEach2 = require_array_for_each();
  var createNonEnumerableProperty3 = require_create_non_enumerable_property();
  for (var COLLECTION_NAME in DOMIterables2) {
    Collection = global5[COLLECTION_NAME];
    CollectionPrototype = Collection && Collection.prototype;
    if (CollectionPrototype && CollectionPrototype.forEach !== forEach2)
      try {
        createNonEnumerableProperty3(CollectionPrototype, "forEach", forEach2);
      } catch (error) {
        CollectionPrototype.forEach = forEach2;
      }
  }
  var Collection;
  var CollectionPrototype;

  // node_modules/core-js/modules/es.object.entries.js
  var $10 = require_export();
  var $entries = require_object_to_array().entries;
  $10({ target: "Object", stat: true }, {
    entries: function entries(O) {
      return $entries(O);
    }
  });

  // node_modules/core-js/modules/es.string.starts-with.js
  "use strict";
  var $11 = require_export();
  var getOwnPropertyDescriptor2 = require_object_get_own_property_descriptor().f;
  var toLength = require_to_length();
  var notARegExp = require_not_a_regexp();
  var requireObjectCoercible = require_require_object_coercible();
  var correctIsRegExpLogic = require_correct_is_regexp_logic();
  var IS_PURE2 = require_is_pure();
  var $startsWith = "".startsWith;
  var min = Math.min;
  var CORRECT_IS_REGEXP_LOGIC = correctIsRegExpLogic("startsWith");
  var MDN_POLYFILL_BUG = !IS_PURE2 && !CORRECT_IS_REGEXP_LOGIC && !!function() {
    var descriptor = getOwnPropertyDescriptor2(String.prototype, "startsWith");
    return descriptor && !descriptor.writable;
  }();
  $11({ target: "String", proto: true, forced: !MDN_POLYFILL_BUG && !CORRECT_IS_REGEXP_LOGIC }, {
    startsWith: function startsWith(searchString) {
      var that = String(requireObjectCoercible(this));
      notARegExp(searchString);
      var index = toLength(min(arguments.length > 1 ? arguments[1] : void 0, that.length));
      var search = String(searchString);
      return $startsWith ? $startsWith.call(that, search, index) : that.slice(index, index + search.length) === search;
    }
  });

  // node_modules/core-js/modules/es.array.is-array.js
  var $12 = require_export();
  var isArray2 = require_is_array();
  $12({ target: "Array", stat: true }, {
    isArray: isArray2
  });

  // src/utils.js
  var import_es_array_iterator = __toModule(require_es_array_iterator());

  // node_modules/core-js/modules/es.array.slice.js
  "use strict";
  var $13 = require_export();
  var isObject4 = require_is_object();
  var isArray3 = require_is_array();
  var toAbsoluteIndex = require_to_absolute_index();
  var toLength2 = require_to_length();
  var toIndexedObject2 = require_to_indexed_object();
  var createProperty = require_create_property();
  var wellKnownSymbol3 = require_well_known_symbol();
  var arrayMethodHasSpeciesSupport = require_array_method_has_species_support();
  var HAS_SPECIES_SUPPORT = arrayMethodHasSpeciesSupport("slice");
  var SPECIES = wellKnownSymbol3("species");
  var nativeSlice = [].slice;
  var max = Math.max;
  $13({ target: "Array", proto: true, forced: !HAS_SPECIES_SUPPORT }, {
    slice: function slice(start, end) {
      var O = toIndexedObject2(this);
      var length = toLength2(O.length);
      var k = toAbsoluteIndex(start, length);
      var fin = toAbsoluteIndex(end === void 0 ? length : end, length);
      var Constructor, result, n;
      if (isArray3(O)) {
        Constructor = O.constructor;
        if (typeof Constructor == "function" && (Constructor === Array || isArray3(Constructor.prototype))) {
          Constructor = void 0;
        } else if (isObject4(Constructor)) {
          Constructor = Constructor[SPECIES];
          if (Constructor === null)
            Constructor = void 0;
        }
        if (Constructor === Array || Constructor === void 0) {
          return nativeSlice.call(O, k, fin);
        }
      }
      result = new (Constructor === void 0 ? Array : Constructor)(max(fin - k, 0));
      for (n = 0; k < fin; k++, n++)
        if (k in O)
          createProperty(result, n, O[k]);
      result.length = n;
      return result;
    }
  });

  // node_modules/core-js/modules/es.function.name.js
  var DESCRIPTORS4 = require_descriptors();
  var defineProperty3 = require_object_define_property().f;
  var FunctionPrototype = Function.prototype;
  var FunctionPrototypeToString = FunctionPrototype.toString;
  var nameRE = /^\s*function ([^ (]*)/;
  var NAME = "name";
  if (DESCRIPTORS4 && !(NAME in FunctionPrototype)) {
    defineProperty3(FunctionPrototype, NAME, {
      configurable: true,
      get: function() {
        try {
          return FunctionPrototypeToString.call(this).match(nameRE)[1];
        } catch (error) {
          return "";
        }
      }
    });
  }

  // node_modules/core-js/modules/es.array.from.js
  var $14 = require_export();
  var from = require_array_from();
  var checkCorrectnessOfIteration = require_check_correctness_of_iteration();
  var INCORRECT_ITERATION = !checkCorrectnessOfIteration(function(iterable) {
    Array.from(iterable);
  });
  $14({ target: "Array", stat: true, forced: INCORRECT_ITERATION }, {
    from: from
  });

  // src/utils.js
  function _slicedToArray(arr, i) {
    return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest();
  }
  function _nonIterableRest() {
    throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
  }
  function _unsupportedIterableToArray(o, minLen) {
    if (!o)
      return;
    if (typeof o === "string")
      return _arrayLikeToArray(o, minLen);
    var n = Object.prototype.toString.call(o).slice(8, -1);
    if (n === "Object" && o.constructor)
      n = o.constructor.name;
    if (n === "Map" || n === "Set")
      return Array.from(o);
    if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n))
      return _arrayLikeToArray(o, minLen);
  }
  function _arrayLikeToArray(arr, len) {
    if (len == null || len > arr.length)
      len = arr.length;
    for (var i = 0, arr2 = new Array(len); i < len; i++) {
      arr2[i] = arr[i];
    }
    return arr2;
  }
  function _iterableToArrayLimit(arr, i) {
    var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"];
    if (_i == null)
      return;
    var _arr = [];
    var _n = true;
    var _d = false;
    var _s, _e;
    try {
      for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) {
        _arr.push(_s.value);
        if (i && _arr.length === i)
          break;
      }
    } catch (err) {
      _d = true;
      _e = err;
    } finally {
      try {
        if (!_n && _i["return"] != null)
          _i["return"]();
      } finally {
        if (_d)
          throw _e;
      }
    }
    return _arr;
  }
  function _arrayWithHoles(arr) {
    if (Array.isArray(arr))
      return arr;
  }
  function tag(name2, attrs) {
    for (var _len = arguments.length, children = new Array(_len > 2 ? _len - 2 : 0), _key = 2; _key < _len; _key++) {
      children[_key - 2] = arguments[_key];
    }
    var el = document.createElement(name2);
    Object.entries(attrs || {}).forEach(function(_ref) {
      var _ref2 = _slicedToArray(_ref, 2), nm = _ref2[0], val = _ref2[1];
      nm.startsWith("on") && nm.toLowerCase() in window ? el.addEventListener(nm.toLowerCase().substr(2), val) : el.setAttribute(nm, val.toString());
    });
    if (!children) {
      return el;
    }
    tagAppendChild(el, children);
    return el;
  }
  function tagList() {
    for (var _len2 = arguments.length, children = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
      children[_key2] = arguments[_key2];
    }
    return tag("template", {}, children).children;
  }
  function HTML(x) {
    var el = document.createElement("template");
    el.innerHTML = x;
    return el.content;
  }
  function tagAppendChild(x, y) {
    if (y instanceof HTMLCollection) {
      while (y.length > 0) {
        x.append(y[0]);
      }
    } else if (Array.isArray(y)) {
      y.forEach(function(z) {
        return tagAppendChild(x, z);
      });
    } else {
      x.append(y);
    }
  }

  // node_modules/core-js/modules/es.array.concat.js
  "use strict";
  var $15 = require_export();
  var fails5 = require_fails();
  var isArray4 = require_is_array();
  var isObject5 = require_is_object();
  var toObject3 = require_to_object();
  var toLength3 = require_to_length();
  var createProperty2 = require_create_property();
  var arraySpeciesCreate = require_array_species_create();
  var arrayMethodHasSpeciesSupport2 = require_array_method_has_species_support();
  var wellKnownSymbol4 = require_well_known_symbol();
  var V8_VERSION = require_engine_v8_version();
  var IS_CONCAT_SPREADABLE = wellKnownSymbol4("isConcatSpreadable");
  var MAX_SAFE_INTEGER = 9007199254740991;
  var MAXIMUM_ALLOWED_INDEX_EXCEEDED = "Maximum allowed index exceeded";
  var IS_CONCAT_SPREADABLE_SUPPORT = V8_VERSION >= 51 || !fails5(function() {
    var array = [];
    array[IS_CONCAT_SPREADABLE] = false;
    return array.concat()[0] !== array;
  });
  var SPECIES_SUPPORT = arrayMethodHasSpeciesSupport2("concat");
  var isConcatSpreadable = function(O) {
    if (!isObject5(O))
      return false;
    var spreadable = O[IS_CONCAT_SPREADABLE];
    return spreadable !== void 0 ? !!spreadable : isArray4(O);
  };
  var FORCED2 = !IS_CONCAT_SPREADABLE_SUPPORT || !SPECIES_SUPPORT;
  $15({ target: "Array", proto: true, forced: FORCED2 }, {
    concat: function concat(arg) {
      var O = toObject3(this);
      var A = arraySpeciesCreate(O, 0);
      var n = 0;
      var i, k, length, len, E;
      for (i = -1, length = arguments.length; i < length; i++) {
        E = i === -1 ? O : arguments[i];
        if (isConcatSpreadable(E)) {
          len = toLength3(E.length);
          if (n + len > MAX_SAFE_INTEGER)
            throw TypeError(MAXIMUM_ALLOWED_INDEX_EXCEEDED);
          for (k = 0; k < len; k++, n++)
            if (k in E)
              createProperty2(A, n, E[k]);
        } else {
          if (n >= MAX_SAFE_INTEGER)
            throw TypeError(MAXIMUM_ALLOWED_INDEX_EXCEEDED);
          createProperty2(A, n++, E);
        }
      }
      A.length = n;
      return A;
    }
  });

  // src/nav-utils.js
  function createTabFragment(self2, className, tabset) {
    var ulAttrs = {
      "class": className,
      role: "tablist",
      "data-tabsetid": tabset.id
    };
    var id = self2.getAttribute("id");
    if (id) {
      ulAttrs.id = id;
      ulAttrs["class"] = ulAttrs["class"] + " shiny-tab-input";
    }
    var ulTag = tag("ul", ulAttrs, tabset.tabList);
    var contents = [];
    var header = self2.getAttribute("header");
    if (header)
      contents.push(HTML(header));
    contents.push(tabset.tabContent);
    var footer = self2.getAttribute("footer");
    if (footer)
      contents.push(HTML(footer));
    var divTag = tag("div", {
      "class": "tab-content",
      "data-tabsetid": tabset.id
    }, contents);
    return tagList(ulTag, divTag);
  }
  function buildTabset(navs, selected) {
    var tabList = new DocumentFragment();
    var tabContent = new DocumentFragment();
    var id = Math.floor(1e3 + Math.random() * 9e3);
    for (var i = 0; i < navs.length; i++) {
      var item = buildTabItem(navs[i], selected, id, i + 1);
      tabList.append(item.liTag);
      if (item.divTag)
        tabContent.append(item.divTag);
    }
    return {
      tabList: tabList,
      tabContent: tabContent,
      id: id
    };
  }
  function buildTabItem(nav, selected, id, index) {
    var liTag = document.createElement("li");
    if (nav.classList.contains("nav-spacer")) {
      liTag.classList.add("bslib-nav-spacer");
      return {
        liTag: liTag,
        divTag: void 0
      };
    }
    if (nav.classList.contains("nav-item")) {
      liTag.classList.add("form-inline");
      liTag.append(nav.content);
      return {
        liTag: liTag,
        divTag: void 0
      };
    }
    if (nav.classList.contains("nav-menu")) {
      liTag.classList.add("dropdown");
      var attrs = {
        href: "#",
        "class": "dropdown-toggle",
        "data-toggle": "dropdown",
        "data-value": nav.getAttribute("value")
      };
      var toggle = tag("a", attrs, HTML(nav.getAttribute("title")));
      var menu = tag("ul", {
        "data-tabsetid": id,
        "class": "dropdown-menu"
      });
      if (nav.getAttribute("align") === "right") {
        menu.classList.add("dropdown-menu-right");
      }
      var navMenu = buildTabset(nav.content.children, selected);
      menu.append(navMenu.tabList);
      liTag.append(toggle);
      liTag.append(menu);
      return {
        liTag: liTag,
        divTag: navMenu.tabContent
      };
    }
    if (nav.classList.contains("nav")) {
      var tabId = "tab-".concat(id, "-").concat(index);
      var aTag = tag("a", {
        href: "#" + tabId,
        role: "tab",
        "data-toggle": "tab",
        "data-value": nav.getAttribute("value")
      }, HTML(nav.getAttribute("title")));
      liTag.append(aTag);
      var divTag = tag("div", {
        id: tabId,
        "class": "tab-pane",
        role: "tabpanel"
      }, nav.content);
      if (selected === nav.getAttribute("value")) {
        liTag.classList.add("active");
        divTag.classList.add("active");
      }
      return {
        liTag: liTag,
        divTag: divTag
      };
    }
    throw new Error("A 'top-level' <".concat(name, "> tag within <bslib-navs-tab> is not supported"));
  }
  function getSelected(self2) {
    var selected = self2.getAttribute("selected");
    if (!selected && self2.children.length > 0) {
      selected = findFirstNav(self2.children).getAttribute("value");
    }
    return selected;
  }
  function findFirstNav(navs) {
    for (var i = 0; i < navs.length; i++) {
      var nav = navs[i];
      if (nav.classList.contains("nav")) {
        return nav;
      }
      if (nav.classList.contains("nav-menu")) {
        findFirstNav(nav);
      }
    }
  }
  function replaceChildren(x, y) {
    while (x.firstChild) {
      x.removeChild(x.lastChild);
    }
    tagAppendChild(x, y);
  }

  // src/card.js
  function createCard(body, header, footer) {
    var card = tag("div", {
      "class": "card"
    });
    if (header) {
      card.append(tag("div", {
        "class": "card-header"
      }, header));
    }
    card.append(tag("div", {
      "class": "card-body"
    }, body));
    if (footer) {
      card.append(tag("div", {
        "class": "card-footer"
      }, footer));
    }
    return card;
  }

  // src/nav.js
  function _typeof(obj) {
    "@babel/helpers - typeof";
    if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") {
      _typeof = function _typeof2(obj2) {
        return typeof obj2;
      };
    } else {
      _typeof = function _typeof2(obj2) {
        return obj2 && typeof Symbol === "function" && obj2.constructor === Symbol && obj2 !== Symbol.prototype ? "symbol" : typeof obj2;
      };
    }
    return _typeof(obj);
  }
  function _classCallCheck(instance, Constructor) {
    if (!(instance instanceof Constructor)) {
      throw new TypeError("Cannot call a class as a function");
    }
  }
  function _inherits(subClass, superClass) {
    if (typeof superClass !== "function" && superClass !== null) {
      throw new TypeError("Super expression must either be null or a function");
    }
    subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } });
    if (superClass)
      _setPrototypeOf(subClass, superClass);
  }
  function _createSuper(Derived) {
    var hasNativeReflectConstruct = _isNativeReflectConstruct();
    return function _createSuperInternal() {
      var Super = _getPrototypeOf(Derived), result;
      if (hasNativeReflectConstruct) {
        var NewTarget = _getPrototypeOf(this).constructor;
        result = Reflect.construct(Super, arguments, NewTarget);
      } else {
        result = Super.apply(this, arguments);
      }
      return _possibleConstructorReturn(this, result);
    };
  }
  function _possibleConstructorReturn(self2, call) {
    if (call && (_typeof(call) === "object" || typeof call === "function")) {
      return call;
    }
    return _assertThisInitialized(self2);
  }
  function _assertThisInitialized(self2) {
    if (self2 === void 0) {
      throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
    }
    return self2;
  }
  function _wrapNativeSuper(Class) {
    var _cache = typeof Map === "function" ? new Map() : void 0;
    _wrapNativeSuper = function _wrapNativeSuper2(Class2) {
      if (Class2 === null || !_isNativeFunction(Class2))
        return Class2;
      if (typeof Class2 !== "function") {
        throw new TypeError("Super expression must either be null or a function");
      }
      if (typeof _cache !== "undefined") {
        if (_cache.has(Class2))
          return _cache.get(Class2);
        _cache.set(Class2, Wrapper);
      }
      function Wrapper() {
        return _construct(Class2, arguments, _getPrototypeOf(this).constructor);
      }
      Wrapper.prototype = Object.create(Class2.prototype, { constructor: { value: Wrapper, enumerable: false, writable: true, configurable: true } });
      return _setPrototypeOf(Wrapper, Class2);
    };
    return _wrapNativeSuper(Class);
  }
  function _construct(Parent, args, Class) {
    if (_isNativeReflectConstruct()) {
      _construct = Reflect.construct;
    } else {
      _construct = function _construct2(Parent2, args2, Class2) {
        var a = [null];
        a.push.apply(a, args2);
        var Constructor = Function.bind.apply(Parent2, a);
        var instance = new Constructor();
        if (Class2)
          _setPrototypeOf(instance, Class2.prototype);
        return instance;
      };
    }
    return _construct.apply(null, arguments);
  }
  function _isNativeReflectConstruct() {
    if (typeof Reflect === "undefined" || !Reflect.construct)
      return false;
    if (Reflect.construct.sham)
      return false;
    if (typeof Proxy === "function")
      return true;
    try {
      Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
      }));
      return true;
    } catch (e) {
      return false;
    }
  }
  function _isNativeFunction(fn) {
    return Function.toString.call(fn).indexOf("[native code]") !== -1;
  }
  function _setPrototypeOf(o, p) {
    _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf2(o2, p2) {
      o2.__proto__ = p2;
      return o2;
    };
    return _setPrototypeOf(o, p);
  }
  function _getPrototypeOf(o) {
    _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf2(o2) {
      return o2.__proto__ || Object.getPrototypeOf(o2);
    };
    return _getPrototypeOf(o);
  }
  var NavsTab = /* @__PURE__ */ function(_HTMLElement) {
    _inherits(NavsTab2, _HTMLElement);
    var _super = _createSuper(NavsTab2);
    function NavsTab2() {
      var _this;
      _classCallCheck(this, NavsTab2);
      self = _this = _super.call(this);
      debugger;
      var selected = getSelected(self);
      var tabset = buildTabset(self.children, selected);
      var tabs = createTabFragment(self, "nav nav-tabs", tabset);
      replaceChildren(self, tabs);
      return _this;
    }
    return NavsTab2;
  }(/* @__PURE__ */ _wrapNativeSuper(HTMLElement));
  customElements.define("bslib-navs-tab", NavsTab);
  var NavsPill = /* @__PURE__ */ function(_HTMLElement2) {
    _inherits(NavsPill2, _HTMLElement2);
    var _super2 = _createSuper(NavsPill2);
    function NavsPill2() {
      var _this2;
      _classCallCheck(this, NavsPill2);
      self = _this2 = _super2.call(this);
      var selected = getSelected(self);
      var tabset = buildTabset(self.children, selected);
      var pills = createTabFragment(self, "nav nav-pills", tabset);
      replaceChildren(self, pills);
      return _this2;
    }
    return NavsPill2;
  }(/* @__PURE__ */ _wrapNativeSuper(HTMLElement));
  customElements.define("bslib-navs-pill", NavsPill);
  var NavsTabCard = /* @__PURE__ */ function(_HTMLElement3) {
    _inherits(NavsTabCard2, _HTMLElement3);
    var _super3 = _createSuper(NavsTabCard2);
    function NavsTabCard2() {
      var _this3;
      _classCallCheck(this, NavsTabCard2);
      self = _this3 = _super3.call(this);
      var selected = getSelected(self);
      var tabset = buildTabset(self.children, selected);
      var tabs = createTabFragment(self, "nav nav-tabs", tabset);
      var nav = tabs[0];
      var content = tabs[1];
      nav.classList.add("card-header-tabs");
      var card = createCard(content, nav);
      replaceChildren(self, card);
      return _this3;
    }
    return NavsTabCard2;
  }(/* @__PURE__ */ _wrapNativeSuper(HTMLElement));
  customElements.define("bslib-navs-tab-card", NavsTabCard);
  var NavsPillCard = /* @__PURE__ */ function(_HTMLElement4) {
    _inherits(NavsPillCard2, _HTMLElement4);
    var _super4 = _createSuper(NavsPillCard2);
    function NavsPillCard2() {
      var _this4;
      _classCallCheck(this, NavsPillCard2);
      self = _this4 = _super4.call(this);
      var selected = getSelected(self);
      var tabset = buildTabset(self.children, selected);
      var pills = createTabFragment(self, "nav nav-pills", tabset);
      var nav = pills[0];
      var content = pills[1];
      var above = self.getAttribute("placement") !== "below";
      if (above)
        nav.classList.add("card-header-pills");
      var card = above ? createCard(content, nav) : createCard(content, null, nav);
      replaceChildren(self, card);
      return _this4;
    }
    return NavsPillCard2;
  }(/* @__PURE__ */ _wrapNativeSuper(HTMLElement));
  customElements.define("bslib-navs-pill-card", NavsPillCard);
  var NavsPillList = /* @__PURE__ */ function(_HTMLElement5) {
    _inherits(NavsPillList2, _HTMLElement5);
    var _super5 = _createSuper(NavsPillList2);
    function NavsPillList2() {
      var _this5;
      _classCallCheck(this, NavsPillList2);
      self = _this5 = _super5.call(this);
      var selected = getSelected(self);
      var tabset = buildTabset(self.children, selected);
      var pills = createTabFragment(self, "nav nav-pills nav-stacked", tabset);
      var nav = pills[0];
      var content = pills[1];
      var navClass = "col-sm-" + self.getAttribute("widthNav");
      if (self.getAttribute("well")) {
        navClass = navClass + " well";
      }
      var row = tag("div", {
        "class": "row"
      }, tag("div", {
        "class": navClass
      }, nav), tag("div", {
        "class": "col-sm-" + self.getAttribute("widthContent")
      }, content));
      replaceChildren(self, row);
      return _this5;
    }
    return NavsPillList2;
  }(/* @__PURE__ */ _wrapNativeSuper(HTMLElement));
  customElements.define("bslib-navs-pill-list", NavsPillList);
  var NavsBar = /* @__PURE__ */ function(_HTMLElement6) {
    _inherits(NavsBar2, _HTMLElement6);
    var _super6 = _createSuper(NavsBar2);
    function NavsBar2() {
      var _this6;
      _classCallCheck(this, NavsBar2);
      self = _this6 = _super6.call(this);
      var selected = getSelected(self);
      var tabset = buildTabset(self.children, selected);
      var navbar = createTabFragment(self, "nav navbar-nav", tabset);
      return _this6;
    }
    return NavsBar2;
  }(/* @__PURE__ */ _wrapNativeSuper(HTMLElement));
  customElements.define("bslib-navs-bar", NavsBar);
})();
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvZ2xvYmFsLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2ZhaWxzLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2Rlc2NyaXB0b3JzLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL29iamVjdC1wcm9wZXJ0eS1pcy1lbnVtZXJhYmxlLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2NyZWF0ZS1wcm9wZXJ0eS1kZXNjcmlwdG9yLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2NsYXNzb2YtcmF3LmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2luZGV4ZWQtb2JqZWN0LmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3JlcXVpcmUtb2JqZWN0LWNvZXJjaWJsZS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy90by1pbmRleGVkLW9iamVjdC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9pcy1vYmplY3QuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvdG8tcHJpbWl0aXZlLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3RvLW9iamVjdC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9oYXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvZG9jdW1lbnQtY3JlYXRlLWVsZW1lbnQuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaWU4LWRvbS1kZWZpbmUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWdldC1vd24tcHJvcGVydHktZGVzY3JpcHRvci5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9hbi1vYmplY3QuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0eS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9jcmVhdGUtbm9uLWVudW1lcmFibGUtcHJvcGVydHkuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvc2V0LWdsb2JhbC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9zaGFyZWQtc3RvcmUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaW5zcGVjdC1zb3VyY2UuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvbmF0aXZlLXdlYWstbWFwLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2lzLXB1cmUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvc2hhcmVkLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3VpZC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9zaGFyZWQta2V5LmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2hpZGRlbi1rZXlzLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2ludGVybmFsLXN0YXRlLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3JlZGVmaW5lLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3BhdGguanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvZ2V0LWJ1aWx0LWluLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3RvLWludGVnZXIuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvdG8tbGVuZ3RoLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3RvLWFic29sdXRlLWluZGV4LmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2FycmF5LWluY2x1ZGVzLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL29iamVjdC1rZXlzLWludGVybmFsLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2VudW0tYnVnLWtleXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWdldC1vd24tcHJvcGVydHktbmFtZXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWdldC1vd24tcHJvcGVydHktc3ltYm9scy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9vd24ta2V5cy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9jb3B5LWNvbnN0cnVjdG9yLXByb3BlcnRpZXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaXMtZm9yY2VkLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2V4cG9ydC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9hLXBvc3NpYmxlLXByb3RvdHlwZS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9vYmplY3Qtc2V0LXByb3RvdHlwZS1vZi5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9jb3JyZWN0LXByb3RvdHlwZS1nZXR0ZXIuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWdldC1wcm90b3R5cGUtb2YuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvYXJyYXktbWV0aG9kLWlzLXN0cmljdC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9lbmdpbmUtdXNlci1hZ2VudC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9lbmdpbmUtdjgtdmVyc2lvbi5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9uYXRpdmUtc3ltYm9sLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3VzZS1zeW1ib2wtYXMtdWlkLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3dlbGwta25vd24tc3ltYm9sLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL3RvLXN0cmluZy10YWctc3VwcG9ydC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9jbGFzc29mLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL29iamVjdC10by1zdHJpbmcuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvcmVnZXhwLWZsYWdzLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2EtZnVuY3Rpb24uanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWtleXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0aWVzLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2h0bWwuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWNyZWF0ZS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9mdW5jdGlvbi1iaW5kLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2FkZC10by11bnNjb3BhYmxlcy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9pdGVyYXRvcnMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaXRlcmF0b3JzLWNvcmUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvc2V0LXRvLXN0cmluZy10YWcuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvY3JlYXRlLWl0ZXJhdG9yLWNvbnN0cnVjdG9yLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2RlZmluZS1pdGVyYXRvci5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMuYXJyYXkuaXRlcmF0b3IuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvZnJlZXppbmcuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaW50ZXJuYWwtbWV0YWRhdGEuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaXMtYXJyYXktaXRlcmF0b3ItbWV0aG9kLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2Z1bmN0aW9uLWJpbmQtY29udGV4dC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9nZXQtaXRlcmF0b3ItbWV0aG9kLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2l0ZXJhdG9yLWNsb3NlLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2l0ZXJhdGUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvYW4taW5zdGFuY2UuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvY2hlY2stY29ycmVjdG5lc3Mtb2YtaXRlcmF0aW9uLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2luaGVyaXQtaWYtcmVxdWlyZWQuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvY29sbGVjdGlvbi5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9yZWRlZmluZS1hbGwuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvc2V0LXNwZWNpZXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvY29sbGVjdGlvbi1zdHJvbmcuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLm1hcC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9zdHJpbmctbXVsdGlieXRlLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2RvbS1pdGVyYWJsZXMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvaXMtYXJyYXkuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvb2JqZWN0LWdldC1vd24tcHJvcGVydHktbmFtZXMtZXh0ZXJuYWwuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wtd3JhcHBlZC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9kZWZpbmUtd2VsbC1rbm93bi1zeW1ib2wuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvYXJyYXktc3BlY2llcy1jcmVhdGUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvYXJyYXktaXRlcmF0aW9uLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2FycmF5LWZvci1lYWNoLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL29iamVjdC10by1hcnJheS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9pcy1yZWdleHAuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9pbnRlcm5hbHMvbm90LWEtcmVnZXhwLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2NvcnJlY3QtaXMtcmVnZXhwLWxvZ2ljLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvaW50ZXJuYWxzL2NyZWF0ZS1wcm9wZXJ0eS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9hcnJheS1tZXRob2QtaGFzLXNwZWNpZXMtc3VwcG9ydC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9jYWxsLXdpdGgtc2FmZS1pdGVyYXRpb24tY2xvc2luZy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL2ludGVybmFscy9hcnJheS1mcm9tLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy9lcy5vYmplY3Quc2V0LXByb3RvdHlwZS1vZi5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMub2JqZWN0LmdldC1wcm90b3R5cGUtb2YuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5LmluZGV4LW9mLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy9lcy5kYXRlLnRvLXN0cmluZy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMub2JqZWN0LnRvLXN0cmluZy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMucmVnZXhwLnRvLXN0cmluZy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMucmVmbGVjdC5jb25zdHJ1Y3QuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLmZ1bmN0aW9uLmJpbmQuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9zcmMvbmF2LmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy9lcy5zdHJpbmcuaXRlcmF0b3IuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL3dlYi5kb20tY29sbGVjdGlvbnMuaXRlcmF0b3IuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLm9iamVjdC5jcmVhdGUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMuc3ltYm9sLmRlc2NyaXB0aW9uLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy9lcy5zeW1ib2wuaXRlcmF0b3IuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5LmZvci1lYWNoLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy93ZWIuZG9tLWNvbGxlY3Rpb25zLmZvci1lYWNoLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy9lcy5vYmplY3QuZW50cmllcy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMuc3RyaW5nLnN0YXJ0cy13aXRoLmpzIiwgIi4uLy4uLy4uLy4uL2phdmFzY3JpcHQvbm9kZV9tb2R1bGVzL2NvcmUtanMvbW9kdWxlcy9lcy5hcnJheS5pcy1hcnJheS5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L3NyYy91dGlscy5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L25vZGVfbW9kdWxlcy9jb3JlLWpzL21vZHVsZXMvZXMuYXJyYXkuc2xpY2UuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLmZ1bmN0aW9uLm5hbWUuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5LmZyb20uanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9ub2RlX21vZHVsZXMvY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5LmNvbmNhdC5qcyIsICIuLi8uLi8uLi8uLi9qYXZhc2NyaXB0L3NyYy9uYXYtdXRpbHMuanMiLCAiLi4vLi4vLi4vLi4vamF2YXNjcmlwdC9zcmMvY2FyZC5qcyJdLAogICJzb3VyY2VzQ29udGVudCI6IFsidmFyIGNoZWNrID0gZnVuY3Rpb24gKGl0KSB7XG4gIHJldHVybiBpdCAmJiBpdC5NYXRoID09IE1hdGggJiYgaXQ7XG59O1xuXG4vLyBodHRwczovL2dpdGh1Yi5jb20vemxvaXJvY2svY29yZS1qcy9pc3N1ZXMvODYjaXNzdWVjb21tZW50LTExNTc1OTAyOFxubW9kdWxlLmV4cG9ydHMgPVxuICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tZ2xvYmFsLXRoaXMgLS0gc2FmZVxuICBjaGVjayh0eXBlb2YgZ2xvYmFsVGhpcyA9PSAnb2JqZWN0JyAmJiBnbG9iYWxUaGlzKSB8fFxuICBjaGVjayh0eXBlb2Ygd2luZG93ID09ICdvYmplY3QnICYmIHdpbmRvdykgfHxcbiAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIG5vLXJlc3RyaWN0ZWQtZ2xvYmFscyAtLSBzYWZlXG4gIGNoZWNrKHR5cGVvZiBzZWxmID09ICdvYmplY3QnICYmIHNlbGYpIHx8XG4gIGNoZWNrKHR5cGVvZiBnbG9iYWwgPT0gJ29iamVjdCcgJiYgZ2xvYmFsKSB8fFxuICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgbm8tbmV3LWZ1bmMgLS0gZmFsbGJhY2tcbiAgKGZ1bmN0aW9uICgpIHsgcmV0dXJuIHRoaXM7IH0pKCkgfHwgRnVuY3Rpb24oJ3JldHVybiB0aGlzJykoKTtcbiIsICJtb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChleGVjKSB7XG4gIHRyeSB7XG4gICAgcmV0dXJuICEhZXhlYygpO1xuICB9IGNhdGNoIChlcnJvcikge1xuICAgIHJldHVybiB0cnVlO1xuICB9XG59O1xuIiwgInZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xuXG4vLyBEZXRlY3QgSUU4J3MgaW5jb21wbGV0ZSBkZWZpbmVQcm9wZXJ0eSBpbXBsZW1lbnRhdGlvblxubW9kdWxlLmV4cG9ydHMgPSAhZmFpbHMoZnVuY3Rpb24gKCkge1xuICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tb2JqZWN0LWRlZmluZXByb3BlcnR5IC0tIHJlcXVpcmVkIGZvciB0ZXN0aW5nXG4gIHJldHVybiBPYmplY3QuZGVmaW5lUHJvcGVydHkoe30sIDEsIHsgZ2V0OiBmdW5jdGlvbiAoKSB7IHJldHVybiA3OyB9IH0pWzFdICE9IDc7XG59KTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgJHByb3BlcnR5SXNFbnVtZXJhYmxlID0ge30ucHJvcGVydHlJc0VudW1lcmFibGU7XG4vLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tb2JqZWN0LWdldG93bnByb3BlcnR5ZGVzY3JpcHRvciAtLSBzYWZlXG52YXIgZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yID0gT2JqZWN0LmdldE93blByb3BlcnR5RGVzY3JpcHRvcjtcblxuLy8gTmFzaG9ybiB+IEpESzggYnVnXG52YXIgTkFTSE9STl9CVUcgPSBnZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IgJiYgISRwcm9wZXJ0eUlzRW51bWVyYWJsZS5jYWxsKHsgMTogMiB9LCAxKTtcblxuLy8gYE9iamVjdC5wcm90b3R5cGUucHJvcGVydHlJc0VudW1lcmFibGVgIG1ldGhvZCBpbXBsZW1lbnRhdGlvblxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1vYmplY3QucHJvdG90eXBlLnByb3BlcnR5aXNlbnVtZXJhYmxlXG5leHBvcnRzLmYgPSBOQVNIT1JOX0JVRyA/IGZ1bmN0aW9uIHByb3BlcnR5SXNFbnVtZXJhYmxlKFYpIHtcbiAgdmFyIGRlc2NyaXB0b3IgPSBnZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IodGhpcywgVik7XG4gIHJldHVybiAhIWRlc2NyaXB0b3IgJiYgZGVzY3JpcHRvci5lbnVtZXJhYmxlO1xufSA6ICRwcm9wZXJ0eUlzRW51bWVyYWJsZTtcbiIsICJtb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChiaXRtYXAsIHZhbHVlKSB7XG4gIHJldHVybiB7XG4gICAgZW51bWVyYWJsZTogIShiaXRtYXAgJiAxKSxcbiAgICBjb25maWd1cmFibGU6ICEoYml0bWFwICYgMiksXG4gICAgd3JpdGFibGU6ICEoYml0bWFwICYgNCksXG4gICAgdmFsdWU6IHZhbHVlXG4gIH07XG59O1xuIiwgInZhciB0b1N0cmluZyA9IHt9LnRvU3RyaW5nO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChpdCkge1xuICByZXR1cm4gdG9TdHJpbmcuY2FsbChpdCkuc2xpY2UoOCwgLTEpO1xufTtcbiIsICJ2YXIgZmFpbHMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZmFpbHMnKTtcbnZhciBjbGFzc29mID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NsYXNzb2YtcmF3Jyk7XG5cbnZhciBzcGxpdCA9ICcnLnNwbGl0O1xuXG4vLyBmYWxsYmFjayBmb3Igbm9uLWFycmF5LWxpa2UgRVMzIGFuZCBub24tZW51bWVyYWJsZSBvbGQgVjggc3RyaW5nc1xubW9kdWxlLmV4cG9ydHMgPSBmYWlscyhmdW5jdGlvbiAoKSB7XG4gIC8vIHRocm93cyBhbiBlcnJvciBpbiByaGlubywgc2VlIGh0dHBzOi8vZ2l0aHViLmNvbS9tb3ppbGxhL3JoaW5vL2lzc3Vlcy8zNDZcbiAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIG5vLXByb3RvdHlwZS1idWlsdGlucyAtLSBzYWZlXG4gIHJldHVybiAhT2JqZWN0KCd6JykucHJvcGVydHlJc0VudW1lcmFibGUoMCk7XG59KSA/IGZ1bmN0aW9uIChpdCkge1xuICByZXR1cm4gY2xhc3NvZihpdCkgPT0gJ1N0cmluZycgPyBzcGxpdC5jYWxsKGl0LCAnJykgOiBPYmplY3QoaXQpO1xufSA6IE9iamVjdDtcbiIsICIvLyBgUmVxdWlyZU9iamVjdENvZXJjaWJsZWAgYWJzdHJhY3Qgb3BlcmF0aW9uXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXJlcXVpcmVvYmplY3Rjb2VyY2libGVcbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGl0KSB7XG4gIGlmIChpdCA9PSB1bmRlZmluZWQpIHRocm93IFR5cGVFcnJvcihcIkNhbid0IGNhbGwgbWV0aG9kIG9uIFwiICsgaXQpO1xuICByZXR1cm4gaXQ7XG59O1xuIiwgIi8vIHRvT2JqZWN0IHdpdGggZmFsbGJhY2sgZm9yIG5vbi1hcnJheS1saWtlIEVTMyBzdHJpbmdzXG52YXIgSW5kZXhlZE9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pbmRleGVkLW9iamVjdCcpO1xudmFyIHJlcXVpcmVPYmplY3RDb2VyY2libGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVxdWlyZS1vYmplY3QtY29lcmNpYmxlJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGl0KSB7XG4gIHJldHVybiBJbmRleGVkT2JqZWN0KHJlcXVpcmVPYmplY3RDb2VyY2libGUoaXQpKTtcbn07XG4iLCAibW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaXQpIHtcbiAgcmV0dXJuIHR5cGVvZiBpdCA9PT0gJ29iamVjdCcgPyBpdCAhPT0gbnVsbCA6IHR5cGVvZiBpdCA9PT0gJ2Z1bmN0aW9uJztcbn07XG4iLCAidmFyIGlzT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLW9iamVjdCcpO1xuXG4vLyBgVG9QcmltaXRpdmVgIGFic3RyYWN0IG9wZXJhdGlvblxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy10b3ByaW1pdGl2ZVxuLy8gaW5zdGVhZCBvZiB0aGUgRVM2IHNwZWMgdmVyc2lvbiwgd2UgZGlkbid0IGltcGxlbWVudCBAQHRvUHJpbWl0aXZlIGNhc2Vcbi8vIGFuZCB0aGUgc2Vjb25kIGFyZ3VtZW50IC0gZmxhZyAtIHByZWZlcnJlZCB0eXBlIGlzIGEgc3RyaW5nXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChpbnB1dCwgUFJFRkVSUkVEX1NUUklORykge1xuICBpZiAoIWlzT2JqZWN0KGlucHV0KSkgcmV0dXJuIGlucHV0O1xuICB2YXIgZm4sIHZhbDtcbiAgaWYgKFBSRUZFUlJFRF9TVFJJTkcgJiYgdHlwZW9mIChmbiA9IGlucHV0LnRvU3RyaW5nKSA9PSAnZnVuY3Rpb24nICYmICFpc09iamVjdCh2YWwgPSBmbi5jYWxsKGlucHV0KSkpIHJldHVybiB2YWw7XG4gIGlmICh0eXBlb2YgKGZuID0gaW5wdXQudmFsdWVPZikgPT0gJ2Z1bmN0aW9uJyAmJiAhaXNPYmplY3QodmFsID0gZm4uY2FsbChpbnB1dCkpKSByZXR1cm4gdmFsO1xuICBpZiAoIVBSRUZFUlJFRF9TVFJJTkcgJiYgdHlwZW9mIChmbiA9IGlucHV0LnRvU3RyaW5nKSA9PSAnZnVuY3Rpb24nICYmICFpc09iamVjdCh2YWwgPSBmbi5jYWxsKGlucHV0KSkpIHJldHVybiB2YWw7XG4gIHRocm93IFR5cGVFcnJvcihcIkNhbid0IGNvbnZlcnQgb2JqZWN0IHRvIHByaW1pdGl2ZSB2YWx1ZVwiKTtcbn07XG4iLCAidmFyIHJlcXVpcmVPYmplY3RDb2VyY2libGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVxdWlyZS1vYmplY3QtY29lcmNpYmxlJyk7XG5cbi8vIGBUb09iamVjdGAgYWJzdHJhY3Qgb3BlcmF0aW9uXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXRvb2JqZWN0XG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChhcmd1bWVudCkge1xuICByZXR1cm4gT2JqZWN0KHJlcXVpcmVPYmplY3RDb2VyY2libGUoYXJndW1lbnQpKTtcbn07XG4iLCAidmFyIHRvT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLW9iamVjdCcpO1xuXG52YXIgaGFzT3duUHJvcGVydHkgPSB7fS5oYXNPd25Qcm9wZXJ0eTtcblxubW9kdWxlLmV4cG9ydHMgPSBPYmplY3QuaGFzT3duIHx8IGZ1bmN0aW9uIGhhc093bihpdCwga2V5KSB7XG4gIHJldHVybiBoYXNPd25Qcm9wZXJ0eS5jYWxsKHRvT2JqZWN0KGl0KSwga2V5KTtcbn07XG4iLCAidmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcbnZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcblxudmFyIGRvY3VtZW50ID0gZ2xvYmFsLmRvY3VtZW50O1xuLy8gdHlwZW9mIGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQgaXMgJ29iamVjdCcgaW4gb2xkIElFXG52YXIgRVhJU1RTID0gaXNPYmplY3QoZG9jdW1lbnQpICYmIGlzT2JqZWN0KGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChpdCkge1xuICByZXR1cm4gRVhJU1RTID8gZG9jdW1lbnQuY3JlYXRlRWxlbWVudChpdCkgOiB7fTtcbn07XG4iLCAidmFyIERFU0NSSVBUT1JTID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Rlc2NyaXB0b3JzJyk7XG52YXIgZmFpbHMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZmFpbHMnKTtcbnZhciBjcmVhdGVFbGVtZW50ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2RvY3VtZW50LWNyZWF0ZS1lbGVtZW50Jyk7XG5cbi8vIFRoYW5rJ3MgSUU4IGZvciBoaXMgZnVubnkgZGVmaW5lUHJvcGVydHlcbm1vZHVsZS5leHBvcnRzID0gIURFU0NSSVBUT1JTICYmICFmYWlscyhmdW5jdGlvbiAoKSB7XG4gIC8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBlcy9uby1vYmplY3QtZGVmaW5lcHJvcGVydHkgLS0gcmVxdWllZCBmb3IgdGVzdGluZ1xuICByZXR1cm4gT2JqZWN0LmRlZmluZVByb3BlcnR5KGNyZWF0ZUVsZW1lbnQoJ2RpdicpLCAnYScsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHsgcmV0dXJuIDc7IH1cbiAgfSkuYSAhPSA3O1xufSk7XG4iLCAidmFyIERFU0NSSVBUT1JTID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Rlc2NyaXB0b3JzJyk7XG52YXIgcHJvcGVydHlJc0VudW1lcmFibGVNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LXByb3BlcnR5LWlzLWVudW1lcmFibGUnKTtcbnZhciBjcmVhdGVQcm9wZXJ0eURlc2NyaXB0b3IgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY3JlYXRlLXByb3BlcnR5LWRlc2NyaXB0b3InKTtcbnZhciB0b0luZGV4ZWRPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8taW5kZXhlZC1vYmplY3QnKTtcbnZhciB0b1ByaW1pdGl2ZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1wcmltaXRpdmUnKTtcbnZhciBoYXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGFzJyk7XG52YXIgSUU4X0RPTV9ERUZJTkUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaWU4LWRvbS1kZWZpbmUnKTtcblxuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLW9iamVjdC1nZXRvd25wcm9wZXJ0eWRlc2NyaXB0b3IgLS0gc2FmZVxudmFyICRnZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IgPSBPYmplY3QuZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yO1xuXG4vLyBgT2JqZWN0LmdldE93blByb3BlcnR5RGVzY3JpcHRvcmAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5nZXRvd25wcm9wZXJ0eWRlc2NyaXB0b3JcbmV4cG9ydHMuZiA9IERFU0NSSVBUT1JTID8gJGdldE93blByb3BlcnR5RGVzY3JpcHRvciA6IGZ1bmN0aW9uIGdldE93blByb3BlcnR5RGVzY3JpcHRvcihPLCBQKSB7XG4gIE8gPSB0b0luZGV4ZWRPYmplY3QoTyk7XG4gIFAgPSB0b1ByaW1pdGl2ZShQLCB0cnVlKTtcbiAgaWYgKElFOF9ET01fREVGSU5FKSB0cnkge1xuICAgIHJldHVybiAkZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yKE8sIFApO1xuICB9IGNhdGNoIChlcnJvcikgeyAvKiBlbXB0eSAqLyB9XG4gIGlmIChoYXMoTywgUCkpIHJldHVybiBjcmVhdGVQcm9wZXJ0eURlc2NyaXB0b3IoIXByb3BlcnR5SXNFbnVtZXJhYmxlTW9kdWxlLmYuY2FsbChPLCBQKSwgT1tQXSk7XG59O1xuIiwgInZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcblxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaXQpIHtcbiAgaWYgKCFpc09iamVjdChpdCkpIHtcbiAgICB0aHJvdyBUeXBlRXJyb3IoU3RyaW5nKGl0KSArICcgaXMgbm90IGFuIG9iamVjdCcpO1xuICB9IHJldHVybiBpdDtcbn07XG4iLCAidmFyIERFU0NSSVBUT1JTID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Rlc2NyaXB0b3JzJyk7XG52YXIgSUU4X0RPTV9ERUZJTkUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaWU4LWRvbS1kZWZpbmUnKTtcbnZhciBhbk9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hbi1vYmplY3QnKTtcbnZhciB0b1ByaW1pdGl2ZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1wcmltaXRpdmUnKTtcblxuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLW9iamVjdC1kZWZpbmVwcm9wZXJ0eSAtLSBzYWZlXG52YXIgJGRlZmluZVByb3BlcnR5ID0gT2JqZWN0LmRlZmluZVByb3BlcnR5O1xuXG4vLyBgT2JqZWN0LmRlZmluZVByb3BlcnR5YCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtb2JqZWN0LmRlZmluZXByb3BlcnR5XG5leHBvcnRzLmYgPSBERVNDUklQVE9SUyA/ICRkZWZpbmVQcm9wZXJ0eSA6IGZ1bmN0aW9uIGRlZmluZVByb3BlcnR5KE8sIFAsIEF0dHJpYnV0ZXMpIHtcbiAgYW5PYmplY3QoTyk7XG4gIFAgPSB0b1ByaW1pdGl2ZShQLCB0cnVlKTtcbiAgYW5PYmplY3QoQXR0cmlidXRlcyk7XG4gIGlmIChJRThfRE9NX0RFRklORSkgdHJ5IHtcbiAgICByZXR1cm4gJGRlZmluZVByb3BlcnR5KE8sIFAsIEF0dHJpYnV0ZXMpO1xuICB9IGNhdGNoIChlcnJvcikgeyAvKiBlbXB0eSAqLyB9XG4gIGlmICgnZ2V0JyBpbiBBdHRyaWJ1dGVzIHx8ICdzZXQnIGluIEF0dHJpYnV0ZXMpIHRocm93IFR5cGVFcnJvcignQWNjZXNzb3JzIG5vdCBzdXBwb3J0ZWQnKTtcbiAgaWYgKCd2YWx1ZScgaW4gQXR0cmlidXRlcykgT1tQXSA9IEF0dHJpYnV0ZXMudmFsdWU7XG4gIHJldHVybiBPO1xufTtcbiIsICJ2YXIgREVTQ1JJUFRPUlMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZGVzY3JpcHRvcnMnKTtcbnZhciBkZWZpbmVQcm9wZXJ0eU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZGVmaW5lLXByb3BlcnR5Jyk7XG52YXIgY3JlYXRlUHJvcGVydHlEZXNjcmlwdG9yID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1wcm9wZXJ0eS1kZXNjcmlwdG9yJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gREVTQ1JJUFRPUlMgPyBmdW5jdGlvbiAob2JqZWN0LCBrZXksIHZhbHVlKSB7XG4gIHJldHVybiBkZWZpbmVQcm9wZXJ0eU1vZHVsZS5mKG9iamVjdCwga2V5LCBjcmVhdGVQcm9wZXJ0eURlc2NyaXB0b3IoMSwgdmFsdWUpKTtcbn0gOiBmdW5jdGlvbiAob2JqZWN0LCBrZXksIHZhbHVlKSB7XG4gIG9iamVjdFtrZXldID0gdmFsdWU7XG4gIHJldHVybiBvYmplY3Q7XG59O1xuIiwgInZhciBnbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2xvYmFsJyk7XG52YXIgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1ub24tZW51bWVyYWJsZS1wcm9wZXJ0eScpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChrZXksIHZhbHVlKSB7XG4gIHRyeSB7XG4gICAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KGdsb2JhbCwga2V5LCB2YWx1ZSk7XG4gIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgZ2xvYmFsW2tleV0gPSB2YWx1ZTtcbiAgfSByZXR1cm4gdmFsdWU7XG59O1xuIiwgInZhciBnbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2xvYmFsJyk7XG52YXIgc2V0R2xvYmFsID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NldC1nbG9iYWwnKTtcblxudmFyIFNIQVJFRCA9ICdfX2NvcmUtanNfc2hhcmVkX18nO1xudmFyIHN0b3JlID0gZ2xvYmFsW1NIQVJFRF0gfHwgc2V0R2xvYmFsKFNIQVJFRCwge30pO1xuXG5tb2R1bGUuZXhwb3J0cyA9IHN0b3JlO1xuIiwgInZhciBzdG9yZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9zaGFyZWQtc3RvcmUnKTtcblxudmFyIGZ1bmN0aW9uVG9TdHJpbmcgPSBGdW5jdGlvbi50b1N0cmluZztcblxuLy8gdGhpcyBoZWxwZXIgYnJva2VuIGluIGBjb3JlLWpzQDMuNC4xLTMuNC40YCwgc28gd2UgY2FuJ3QgdXNlIGBzaGFyZWRgIGhlbHBlclxuaWYgKHR5cGVvZiBzdG9yZS5pbnNwZWN0U291cmNlICE9ICdmdW5jdGlvbicpIHtcbiAgc3RvcmUuaW5zcGVjdFNvdXJjZSA9IGZ1bmN0aW9uIChpdCkge1xuICAgIHJldHVybiBmdW5jdGlvblRvU3RyaW5nLmNhbGwoaXQpO1xuICB9O1xufVxuXG5tb2R1bGUuZXhwb3J0cyA9IHN0b3JlLmluc3BlY3RTb3VyY2U7XG4iLCAidmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcbnZhciBpbnNwZWN0U291cmNlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2luc3BlY3Qtc291cmNlJyk7XG5cbnZhciBXZWFrTWFwID0gZ2xvYmFsLldlYWtNYXA7XG5cbm1vZHVsZS5leHBvcnRzID0gdHlwZW9mIFdlYWtNYXAgPT09ICdmdW5jdGlvbicgJiYgL25hdGl2ZSBjb2RlLy50ZXN0KGluc3BlY3RTb3VyY2UoV2Vha01hcCkpO1xuIiwgIm1vZHVsZS5leHBvcnRzID0gZmFsc2U7XG4iLCAidmFyIElTX1BVUkUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtcHVyZScpO1xudmFyIHN0b3JlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NoYXJlZC1zdG9yZScpO1xuXG4obW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoa2V5LCB2YWx1ZSkge1xuICByZXR1cm4gc3RvcmVba2V5XSB8fCAoc3RvcmVba2V5XSA9IHZhbHVlICE9PSB1bmRlZmluZWQgPyB2YWx1ZSA6IHt9KTtcbn0pKCd2ZXJzaW9ucycsIFtdKS5wdXNoKHtcbiAgdmVyc2lvbjogJzMuMTUuMicsXG4gIG1vZGU6IElTX1BVUkUgPyAncHVyZScgOiAnZ2xvYmFsJyxcbiAgY29weXJpZ2h0OiAnXHUwMEE5IDIwMjEgRGVuaXMgUHVzaGthcmV2ICh6bG9pcm9jay5ydSknXG59KTtcbiIsICJ2YXIgaWQgPSAwO1xudmFyIHBvc3RmaXggPSBNYXRoLnJhbmRvbSgpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChrZXkpIHtcbiAgcmV0dXJuICdTeW1ib2woJyArIFN0cmluZyhrZXkgPT09IHVuZGVmaW5lZCA/ICcnIDoga2V5KSArICcpXycgKyAoKytpZCArIHBvc3RmaXgpLnRvU3RyaW5nKDM2KTtcbn07XG4iLCAidmFyIHNoYXJlZCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9zaGFyZWQnKTtcbnZhciB1aWQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdWlkJyk7XG5cbnZhciBrZXlzID0gc2hhcmVkKCdrZXlzJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGtleSkge1xuICByZXR1cm4ga2V5c1trZXldIHx8IChrZXlzW2tleV0gPSB1aWQoa2V5KSk7XG59O1xuIiwgIm1vZHVsZS5leHBvcnRzID0ge307XG4iLCAidmFyIE5BVElWRV9XRUFLX01BUCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9uYXRpdmUtd2Vhay1tYXAnKTtcbnZhciBnbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2xvYmFsJyk7XG52YXIgaXNPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtb2JqZWN0Jyk7XG52YXIgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1ub24tZW51bWVyYWJsZS1wcm9wZXJ0eScpO1xudmFyIG9iamVjdEhhcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oYXMnKTtcbnZhciBzaGFyZWQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2hhcmVkLXN0b3JlJyk7XG52YXIgc2hhcmVkS2V5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NoYXJlZC1rZXknKTtcbnZhciBoaWRkZW5LZXlzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2hpZGRlbi1rZXlzJyk7XG5cbnZhciBPQkpFQ1RfQUxSRUFEWV9JTklUSUFMSVpFRCA9ICdPYmplY3QgYWxyZWFkeSBpbml0aWFsaXplZCc7XG52YXIgV2Vha01hcCA9IGdsb2JhbC5XZWFrTWFwO1xudmFyIHNldCwgZ2V0LCBoYXM7XG5cbnZhciBlbmZvcmNlID0gZnVuY3Rpb24gKGl0KSB7XG4gIHJldHVybiBoYXMoaXQpID8gZ2V0KGl0KSA6IHNldChpdCwge30pO1xufTtcblxudmFyIGdldHRlckZvciA9IGZ1bmN0aW9uIChUWVBFKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoaXQpIHtcbiAgICB2YXIgc3RhdGU7XG4gICAgaWYgKCFpc09iamVjdChpdCkgfHwgKHN0YXRlID0gZ2V0KGl0KSkudHlwZSAhPT0gVFlQRSkge1xuICAgICAgdGhyb3cgVHlwZUVycm9yKCdJbmNvbXBhdGlibGUgcmVjZWl2ZXIsICcgKyBUWVBFICsgJyByZXF1aXJlZCcpO1xuICAgIH0gcmV0dXJuIHN0YXRlO1xuICB9O1xufTtcblxuaWYgKE5BVElWRV9XRUFLX01BUCB8fCBzaGFyZWQuc3RhdGUpIHtcbiAgdmFyIHN0b3JlID0gc2hhcmVkLnN0YXRlIHx8IChzaGFyZWQuc3RhdGUgPSBuZXcgV2Vha01hcCgpKTtcbiAgdmFyIHdtZ2V0ID0gc3RvcmUuZ2V0O1xuICB2YXIgd21oYXMgPSBzdG9yZS5oYXM7XG4gIHZhciB3bXNldCA9IHN0b3JlLnNldDtcbiAgc2V0ID0gZnVuY3Rpb24gKGl0LCBtZXRhZGF0YSkge1xuICAgIGlmICh3bWhhcy5jYWxsKHN0b3JlLCBpdCkpIHRocm93IG5ldyBUeXBlRXJyb3IoT0JKRUNUX0FMUkVBRFlfSU5JVElBTElaRUQpO1xuICAgIG1ldGFkYXRhLmZhY2FkZSA9IGl0O1xuICAgIHdtc2V0LmNhbGwoc3RvcmUsIGl0LCBtZXRhZGF0YSk7XG4gICAgcmV0dXJuIG1ldGFkYXRhO1xuICB9O1xuICBnZXQgPSBmdW5jdGlvbiAoaXQpIHtcbiAgICByZXR1cm4gd21nZXQuY2FsbChzdG9yZSwgaXQpIHx8IHt9O1xuICB9O1xuICBoYXMgPSBmdW5jdGlvbiAoaXQpIHtcbiAgICByZXR1cm4gd21oYXMuY2FsbChzdG9yZSwgaXQpO1xuICB9O1xufSBlbHNlIHtcbiAgdmFyIFNUQVRFID0gc2hhcmVkS2V5KCdzdGF0ZScpO1xuICBoaWRkZW5LZXlzW1NUQVRFXSA9IHRydWU7XG4gIHNldCA9IGZ1bmN0aW9uIChpdCwgbWV0YWRhdGEpIHtcbiAgICBpZiAob2JqZWN0SGFzKGl0LCBTVEFURSkpIHRocm93IG5ldyBUeXBlRXJyb3IoT0JKRUNUX0FMUkVBRFlfSU5JVElBTElaRUQpO1xuICAgIG1ldGFkYXRhLmZhY2FkZSA9IGl0O1xuICAgIGNyZWF0ZU5vbkVudW1lcmFibGVQcm9wZXJ0eShpdCwgU1RBVEUsIG1ldGFkYXRhKTtcbiAgICByZXR1cm4gbWV0YWRhdGE7XG4gIH07XG4gIGdldCA9IGZ1bmN0aW9uIChpdCkge1xuICAgIHJldHVybiBvYmplY3RIYXMoaXQsIFNUQVRFKSA/IGl0W1NUQVRFXSA6IHt9O1xuICB9O1xuICBoYXMgPSBmdW5jdGlvbiAoaXQpIHtcbiAgICByZXR1cm4gb2JqZWN0SGFzKGl0LCBTVEFURSk7XG4gIH07XG59XG5cbm1vZHVsZS5leHBvcnRzID0ge1xuICBzZXQ6IHNldCxcbiAgZ2V0OiBnZXQsXG4gIGhhczogaGFzLFxuICBlbmZvcmNlOiBlbmZvcmNlLFxuICBnZXR0ZXJGb3I6IGdldHRlckZvclxufTtcbiIsICJ2YXIgZ2xvYmFsID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2dsb2JhbCcpO1xudmFyIGNyZWF0ZU5vbkVudW1lcmFibGVQcm9wZXJ0eSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jcmVhdGUtbm9uLWVudW1lcmFibGUtcHJvcGVydHknKTtcbnZhciBoYXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGFzJyk7XG52YXIgc2V0R2xvYmFsID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NldC1nbG9iYWwnKTtcbnZhciBpbnNwZWN0U291cmNlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2luc3BlY3Qtc291cmNlJyk7XG52YXIgSW50ZXJuYWxTdGF0ZU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pbnRlcm5hbC1zdGF0ZScpO1xuXG52YXIgZ2V0SW50ZXJuYWxTdGF0ZSA9IEludGVybmFsU3RhdGVNb2R1bGUuZ2V0O1xudmFyIGVuZm9yY2VJbnRlcm5hbFN0YXRlID0gSW50ZXJuYWxTdGF0ZU1vZHVsZS5lbmZvcmNlO1xudmFyIFRFTVBMQVRFID0gU3RyaW5nKFN0cmluZykuc3BsaXQoJ1N0cmluZycpO1xuXG4obW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoTywga2V5LCB2YWx1ZSwgb3B0aW9ucykge1xuICB2YXIgdW5zYWZlID0gb3B0aW9ucyA/ICEhb3B0aW9ucy51bnNhZmUgOiBmYWxzZTtcbiAgdmFyIHNpbXBsZSA9IG9wdGlvbnMgPyAhIW9wdGlvbnMuZW51bWVyYWJsZSA6IGZhbHNlO1xuICB2YXIgbm9UYXJnZXRHZXQgPSBvcHRpb25zID8gISFvcHRpb25zLm5vVGFyZ2V0R2V0IDogZmFsc2U7XG4gIHZhciBzdGF0ZTtcbiAgaWYgKHR5cGVvZiB2YWx1ZSA9PSAnZnVuY3Rpb24nKSB7XG4gICAgaWYgKHR5cGVvZiBrZXkgPT0gJ3N0cmluZycgJiYgIWhhcyh2YWx1ZSwgJ25hbWUnKSkge1xuICAgICAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KHZhbHVlLCAnbmFtZScsIGtleSk7XG4gICAgfVxuICAgIHN0YXRlID0gZW5mb3JjZUludGVybmFsU3RhdGUodmFsdWUpO1xuICAgIGlmICghc3RhdGUuc291cmNlKSB7XG4gICAgICBzdGF0ZS5zb3VyY2UgPSBURU1QTEFURS5qb2luKHR5cGVvZiBrZXkgPT0gJ3N0cmluZycgPyBrZXkgOiAnJyk7XG4gICAgfVxuICB9XG4gIGlmIChPID09PSBnbG9iYWwpIHtcbiAgICBpZiAoc2ltcGxlKSBPW2tleV0gPSB2YWx1ZTtcbiAgICBlbHNlIHNldEdsb2JhbChrZXksIHZhbHVlKTtcbiAgICByZXR1cm47XG4gIH0gZWxzZSBpZiAoIXVuc2FmZSkge1xuICAgIGRlbGV0ZSBPW2tleV07XG4gIH0gZWxzZSBpZiAoIW5vVGFyZ2V0R2V0ICYmIE9ba2V5XSkge1xuICAgIHNpbXBsZSA9IHRydWU7XG4gIH1cbiAgaWYgKHNpbXBsZSkgT1trZXldID0gdmFsdWU7XG4gIGVsc2UgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KE8sIGtleSwgdmFsdWUpO1xuLy8gYWRkIGZha2UgRnVuY3Rpb24jdG9TdHJpbmcgZm9yIGNvcnJlY3Qgd29yayB3cmFwcGVkIG1ldGhvZHMgLyBjb25zdHJ1Y3RvcnMgd2l0aCBtZXRob2RzIGxpa2UgTG9EYXNoIGlzTmF0aXZlXG59KShGdW5jdGlvbi5wcm90b3R5cGUsICd0b1N0cmluZycsIGZ1bmN0aW9uIHRvU3RyaW5nKCkge1xuICByZXR1cm4gdHlwZW9mIHRoaXMgPT0gJ2Z1bmN0aW9uJyAmJiBnZXRJbnRlcm5hbFN0YXRlKHRoaXMpLnNvdXJjZSB8fCBpbnNwZWN0U291cmNlKHRoaXMpO1xufSk7XG4iLCAidmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcblxubW9kdWxlLmV4cG9ydHMgPSBnbG9iYWw7XG4iLCAidmFyIHBhdGggPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcGF0aCcpO1xudmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcblxudmFyIGFGdW5jdGlvbiA9IGZ1bmN0aW9uICh2YXJpYWJsZSkge1xuICByZXR1cm4gdHlwZW9mIHZhcmlhYmxlID09ICdmdW5jdGlvbicgPyB2YXJpYWJsZSA6IHVuZGVmaW5lZDtcbn07XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKG5hbWVzcGFjZSwgbWV0aG9kKSB7XG4gIHJldHVybiBhcmd1bWVudHMubGVuZ3RoIDwgMiA/IGFGdW5jdGlvbihwYXRoW25hbWVzcGFjZV0pIHx8IGFGdW5jdGlvbihnbG9iYWxbbmFtZXNwYWNlXSlcbiAgICA6IHBhdGhbbmFtZXNwYWNlXSAmJiBwYXRoW25hbWVzcGFjZV1bbWV0aG9kXSB8fCBnbG9iYWxbbmFtZXNwYWNlXSAmJiBnbG9iYWxbbmFtZXNwYWNlXVttZXRob2RdO1xufTtcbiIsICJ2YXIgY2VpbCA9IE1hdGguY2VpbDtcbnZhciBmbG9vciA9IE1hdGguZmxvb3I7XG5cbi8vIGBUb0ludGVnZXJgIGFic3RyYWN0IG9wZXJhdGlvblxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy10b2ludGVnZXJcbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGFyZ3VtZW50KSB7XG4gIHJldHVybiBpc05hTihhcmd1bWVudCA9ICthcmd1bWVudCkgPyAwIDogKGFyZ3VtZW50ID4gMCA/IGZsb29yIDogY2VpbCkoYXJndW1lbnQpO1xufTtcbiIsICJ2YXIgdG9JbnRlZ2VyID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWludGVnZXInKTtcblxudmFyIG1pbiA9IE1hdGgubWluO1xuXG4vLyBgVG9MZW5ndGhgIGFic3RyYWN0IG9wZXJhdGlvblxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy10b2xlbmd0aFxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoYXJndW1lbnQpIHtcbiAgcmV0dXJuIGFyZ3VtZW50ID4gMCA/IG1pbih0b0ludGVnZXIoYXJndW1lbnQpLCAweDFGRkZGRkZGRkZGRkZGKSA6IDA7IC8vIDIgKiogNTMgLSAxID09IDkwMDcxOTkyNTQ3NDA5OTFcbn07XG4iLCAidmFyIHRvSW50ZWdlciA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1pbnRlZ2VyJyk7XG5cbnZhciBtYXggPSBNYXRoLm1heDtcbnZhciBtaW4gPSBNYXRoLm1pbjtcblxuLy8gSGVscGVyIGZvciBhIHBvcHVsYXIgcmVwZWF0aW5nIGNhc2Ugb2YgdGhlIHNwZWM6XG4vLyBMZXQgaW50ZWdlciBiZSA/IFRvSW50ZWdlcihpbmRleCkuXG4vLyBJZiBpbnRlZ2VyIDwgMCwgbGV0IHJlc3VsdCBiZSBtYXgoKGxlbmd0aCArIGludGVnZXIpLCAwKTsgZWxzZSBsZXQgcmVzdWx0IGJlIG1pbihpbnRlZ2VyLCBsZW5ndGgpLlxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaW5kZXgsIGxlbmd0aCkge1xuICB2YXIgaW50ZWdlciA9IHRvSW50ZWdlcihpbmRleCk7XG4gIHJldHVybiBpbnRlZ2VyIDwgMCA/IG1heChpbnRlZ2VyICsgbGVuZ3RoLCAwKSA6IG1pbihpbnRlZ2VyLCBsZW5ndGgpO1xufTtcbiIsICJ2YXIgdG9JbmRleGVkT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWluZGV4ZWQtb2JqZWN0Jyk7XG52YXIgdG9MZW5ndGggPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tbGVuZ3RoJyk7XG52YXIgdG9BYnNvbHV0ZUluZGV4ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWFic29sdXRlLWluZGV4Jyk7XG5cbi8vIGBBcnJheS5wcm90b3R5cGUueyBpbmRleE9mLCBpbmNsdWRlcyB9YCBtZXRob2RzIGltcGxlbWVudGF0aW9uXG52YXIgY3JlYXRlTWV0aG9kID0gZnVuY3Rpb24gKElTX0lOQ0xVREVTKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoJHRoaXMsIGVsLCBmcm9tSW5kZXgpIHtcbiAgICB2YXIgTyA9IHRvSW5kZXhlZE9iamVjdCgkdGhpcyk7XG4gICAgdmFyIGxlbmd0aCA9IHRvTGVuZ3RoKE8ubGVuZ3RoKTtcbiAgICB2YXIgaW5kZXggPSB0b0Fic29sdXRlSW5kZXgoZnJvbUluZGV4LCBsZW5ndGgpO1xuICAgIHZhciB2YWx1ZTtcbiAgICAvLyBBcnJheSNpbmNsdWRlcyB1c2VzIFNhbWVWYWx1ZVplcm8gZXF1YWxpdHkgYWxnb3JpdGhtXG4gICAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIG5vLXNlbGYtY29tcGFyZSAtLSBOYU4gY2hlY2tcbiAgICBpZiAoSVNfSU5DTFVERVMgJiYgZWwgIT0gZWwpIHdoaWxlIChsZW5ndGggPiBpbmRleCkge1xuICAgICAgdmFsdWUgPSBPW2luZGV4KytdO1xuICAgICAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIG5vLXNlbGYtY29tcGFyZSAtLSBOYU4gY2hlY2tcbiAgICAgIGlmICh2YWx1ZSAhPSB2YWx1ZSkgcmV0dXJuIHRydWU7XG4gICAgLy8gQXJyYXkjaW5kZXhPZiBpZ25vcmVzIGhvbGVzLCBBcnJheSNpbmNsdWRlcyAtIG5vdFxuICAgIH0gZWxzZSBmb3IgKDtsZW5ndGggPiBpbmRleDsgaW5kZXgrKykge1xuICAgICAgaWYgKChJU19JTkNMVURFUyB8fCBpbmRleCBpbiBPKSAmJiBPW2luZGV4XSA9PT0gZWwpIHJldHVybiBJU19JTkNMVURFUyB8fCBpbmRleCB8fCAwO1xuICAgIH0gcmV0dXJuICFJU19JTkNMVURFUyAmJiAtMTtcbiAgfTtcbn07XG5cbm1vZHVsZS5leHBvcnRzID0ge1xuICAvLyBgQXJyYXkucHJvdG90eXBlLmluY2x1ZGVzYCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuaW5jbHVkZXNcbiAgaW5jbHVkZXM6IGNyZWF0ZU1ldGhvZCh0cnVlKSxcbiAgLy8gYEFycmF5LnByb3RvdHlwZS5pbmRleE9mYCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuaW5kZXhvZlxuICBpbmRleE9mOiBjcmVhdGVNZXRob2QoZmFsc2UpXG59O1xuIiwgInZhciBoYXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGFzJyk7XG52YXIgdG9JbmRleGVkT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWluZGV4ZWQtb2JqZWN0Jyk7XG52YXIgaW5kZXhPZiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hcnJheS1pbmNsdWRlcycpLmluZGV4T2Y7XG52YXIgaGlkZGVuS2V5cyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oaWRkZW4ta2V5cycpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChvYmplY3QsIG5hbWVzKSB7XG4gIHZhciBPID0gdG9JbmRleGVkT2JqZWN0KG9iamVjdCk7XG4gIHZhciBpID0gMDtcbiAgdmFyIHJlc3VsdCA9IFtdO1xuICB2YXIga2V5O1xuICBmb3IgKGtleSBpbiBPKSAhaGFzKGhpZGRlbktleXMsIGtleSkgJiYgaGFzKE8sIGtleSkgJiYgcmVzdWx0LnB1c2goa2V5KTtcbiAgLy8gRG9uJ3QgZW51bSBidWcgJiBoaWRkZW4ga2V5c1xuICB3aGlsZSAobmFtZXMubGVuZ3RoID4gaSkgaWYgKGhhcyhPLCBrZXkgPSBuYW1lc1tpKytdKSkge1xuICAgIH5pbmRleE9mKHJlc3VsdCwga2V5KSB8fCByZXN1bHQucHVzaChrZXkpO1xuICB9XG4gIHJldHVybiByZXN1bHQ7XG59O1xuIiwgIi8vIElFOC0gZG9uJ3QgZW51bSBidWcga2V5c1xubW9kdWxlLmV4cG9ydHMgPSBbXG4gICdjb25zdHJ1Y3RvcicsXG4gICdoYXNPd25Qcm9wZXJ0eScsXG4gICdpc1Byb3RvdHlwZU9mJyxcbiAgJ3Byb3BlcnR5SXNFbnVtZXJhYmxlJyxcbiAgJ3RvTG9jYWxlU3RyaW5nJyxcbiAgJ3RvU3RyaW5nJyxcbiAgJ3ZhbHVlT2YnXG5dO1xuIiwgInZhciBpbnRlcm5hbE9iamVjdEtleXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWtleXMtaW50ZXJuYWwnKTtcbnZhciBlbnVtQnVnS2V5cyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9lbnVtLWJ1Zy1rZXlzJyk7XG5cbnZhciBoaWRkZW5LZXlzID0gZW51bUJ1Z0tleXMuY29uY2F0KCdsZW5ndGgnLCAncHJvdG90eXBlJyk7XG5cbi8vIGBPYmplY3QuZ2V0T3duUHJvcGVydHlOYW1lc2AgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5nZXRvd25wcm9wZXJ0eW5hbWVzXG4vLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tb2JqZWN0LWdldG93bnByb3BlcnR5bmFtZXMgLS0gc2FmZVxuZXhwb3J0cy5mID0gT2JqZWN0LmdldE93blByb3BlcnR5TmFtZXMgfHwgZnVuY3Rpb24gZ2V0T3duUHJvcGVydHlOYW1lcyhPKSB7XG4gIHJldHVybiBpbnRlcm5hbE9iamVjdEtleXMoTywgaGlkZGVuS2V5cyk7XG59O1xuIiwgIi8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBlcy9uby1vYmplY3QtZ2V0b3ducHJvcGVydHlzeW1ib2xzIC0tIHNhZmVcbmV4cG9ydHMuZiA9IE9iamVjdC5nZXRPd25Qcm9wZXJ0eVN5bWJvbHM7XG4iLCAidmFyIGdldEJ1aWx0SW4gPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2V0LWJ1aWx0LWluJyk7XG52YXIgZ2V0T3duUHJvcGVydHlOYW1lc01vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1uYW1lcycpO1xudmFyIGdldE93blByb3BlcnR5U3ltYm9sc01vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1zeW1ib2xzJyk7XG52YXIgYW5PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYW4tb2JqZWN0Jyk7XG5cbi8vIGFsbCBvYmplY3Qga2V5cywgaW5jbHVkZXMgbm9uLWVudW1lcmFibGUgYW5kIHN5bWJvbHNcbm1vZHVsZS5leHBvcnRzID0gZ2V0QnVpbHRJbignUmVmbGVjdCcsICdvd25LZXlzJykgfHwgZnVuY3Rpb24gb3duS2V5cyhpdCkge1xuICB2YXIga2V5cyA9IGdldE93blByb3BlcnR5TmFtZXNNb2R1bGUuZihhbk9iamVjdChpdCkpO1xuICB2YXIgZ2V0T3duUHJvcGVydHlTeW1ib2xzID0gZ2V0T3duUHJvcGVydHlTeW1ib2xzTW9kdWxlLmY7XG4gIHJldHVybiBnZXRPd25Qcm9wZXJ0eVN5bWJvbHMgPyBrZXlzLmNvbmNhdChnZXRPd25Qcm9wZXJ0eVN5bWJvbHMoaXQpKSA6IGtleXM7XG59O1xuIiwgInZhciBoYXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGFzJyk7XG52YXIgb3duS2V5cyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vd24ta2V5cycpO1xudmFyIGdldE93blByb3BlcnR5RGVzY3JpcHRvck1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1kZXNjcmlwdG9yJyk7XG52YXIgZGVmaW5lUHJvcGVydHlNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0eScpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uICh0YXJnZXQsIHNvdXJjZSkge1xuICB2YXIga2V5cyA9IG93bktleXMoc291cmNlKTtcbiAgdmFyIGRlZmluZVByb3BlcnR5ID0gZGVmaW5lUHJvcGVydHlNb2R1bGUuZjtcbiAgdmFyIGdldE93blByb3BlcnR5RGVzY3JpcHRvciA9IGdldE93blByb3BlcnR5RGVzY3JpcHRvck1vZHVsZS5mO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IGtleXMubGVuZ3RoOyBpKyspIHtcbiAgICB2YXIga2V5ID0ga2V5c1tpXTtcbiAgICBpZiAoIWhhcyh0YXJnZXQsIGtleSkpIGRlZmluZVByb3BlcnR5KHRhcmdldCwga2V5LCBnZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3Ioc291cmNlLCBrZXkpKTtcbiAgfVxufTtcbiIsICJ2YXIgZmFpbHMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZmFpbHMnKTtcblxudmFyIHJlcGxhY2VtZW50ID0gLyN8XFwucHJvdG90eXBlXFwuLztcblxudmFyIGlzRm9yY2VkID0gZnVuY3Rpb24gKGZlYXR1cmUsIGRldGVjdGlvbikge1xuICB2YXIgdmFsdWUgPSBkYXRhW25vcm1hbGl6ZShmZWF0dXJlKV07XG4gIHJldHVybiB2YWx1ZSA9PSBQT0xZRklMTCA/IHRydWVcbiAgICA6IHZhbHVlID09IE5BVElWRSA/IGZhbHNlXG4gICAgOiB0eXBlb2YgZGV0ZWN0aW9uID09ICdmdW5jdGlvbicgPyBmYWlscyhkZXRlY3Rpb24pXG4gICAgOiAhIWRldGVjdGlvbjtcbn07XG5cbnZhciBub3JtYWxpemUgPSBpc0ZvcmNlZC5ub3JtYWxpemUgPSBmdW5jdGlvbiAoc3RyaW5nKSB7XG4gIHJldHVybiBTdHJpbmcoc3RyaW5nKS5yZXBsYWNlKHJlcGxhY2VtZW50LCAnLicpLnRvTG93ZXJDYXNlKCk7XG59O1xuXG52YXIgZGF0YSA9IGlzRm9yY2VkLmRhdGEgPSB7fTtcbnZhciBOQVRJVkUgPSBpc0ZvcmNlZC5OQVRJVkUgPSAnTic7XG52YXIgUE9MWUZJTEwgPSBpc0ZvcmNlZC5QT0xZRklMTCA9ICdQJztcblxubW9kdWxlLmV4cG9ydHMgPSBpc0ZvcmNlZDtcbiIsICJ2YXIgZ2xvYmFsID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2dsb2JhbCcpO1xudmFyIGdldE93blByb3BlcnR5RGVzY3JpcHRvciA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1kZXNjcmlwdG9yJykuZjtcbnZhciBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY3JlYXRlLW5vbi1lbnVtZXJhYmxlLXByb3BlcnR5Jyk7XG52YXIgcmVkZWZpbmUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVkZWZpbmUnKTtcbnZhciBzZXRHbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2V0LWdsb2JhbCcpO1xudmFyIGNvcHlDb25zdHJ1Y3RvclByb3BlcnRpZXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY29weS1jb25zdHJ1Y3Rvci1wcm9wZXJ0aWVzJyk7XG52YXIgaXNGb3JjZWQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtZm9yY2VkJyk7XG5cbi8qXG4gIG9wdGlvbnMudGFyZ2V0ICAgICAgLSBuYW1lIG9mIHRoZSB0YXJnZXQgb2JqZWN0XG4gIG9wdGlvbnMuZ2xvYmFsICAgICAgLSB0YXJnZXQgaXMgdGhlIGdsb2JhbCBvYmplY3RcbiAgb3B0aW9ucy5zdGF0ICAgICAgICAtIGV4cG9ydCBhcyBzdGF0aWMgbWV0aG9kcyBvZiB0YXJnZXRcbiAgb3B0aW9ucy5wcm90byAgICAgICAtIGV4cG9ydCBhcyBwcm90b3R5cGUgbWV0aG9kcyBvZiB0YXJnZXRcbiAgb3B0aW9ucy5yZWFsICAgICAgICAtIHJlYWwgcHJvdG90eXBlIG1ldGhvZCBmb3IgdGhlIGBwdXJlYCB2ZXJzaW9uXG4gIG9wdGlvbnMuZm9yY2VkICAgICAgLSBleHBvcnQgZXZlbiBpZiB0aGUgbmF0aXZlIGZlYXR1cmUgaXMgYXZhaWxhYmxlXG4gIG9wdGlvbnMuYmluZCAgICAgICAgLSBiaW5kIG1ldGhvZHMgdG8gdGhlIHRhcmdldCwgcmVxdWlyZWQgZm9yIHRoZSBgcHVyZWAgdmVyc2lvblxuICBvcHRpb25zLndyYXAgICAgICAgIC0gd3JhcCBjb25zdHJ1Y3RvcnMgdG8gcHJldmVudGluZyBnbG9iYWwgcG9sbHV0aW9uLCByZXF1aXJlZCBmb3IgdGhlIGBwdXJlYCB2ZXJzaW9uXG4gIG9wdGlvbnMudW5zYWZlICAgICAgLSB1c2UgdGhlIHNpbXBsZSBhc3NpZ25tZW50IG9mIHByb3BlcnR5IGluc3RlYWQgb2YgZGVsZXRlICsgZGVmaW5lUHJvcGVydHlcbiAgb3B0aW9ucy5zaGFtICAgICAgICAtIGFkZCBhIGZsYWcgdG8gbm90IGNvbXBsZXRlbHkgZnVsbCBwb2x5ZmlsbHNcbiAgb3B0aW9ucy5lbnVtZXJhYmxlICAtIGV4cG9ydCBhcyBlbnVtZXJhYmxlIHByb3BlcnR5XG4gIG9wdGlvbnMubm9UYXJnZXRHZXQgLSBwcmV2ZW50IGNhbGxpbmcgYSBnZXR0ZXIgb24gdGFyZ2V0XG4qL1xubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAob3B0aW9ucywgc291cmNlKSB7XG4gIHZhciBUQVJHRVQgPSBvcHRpb25zLnRhcmdldDtcbiAgdmFyIEdMT0JBTCA9IG9wdGlvbnMuZ2xvYmFsO1xuICB2YXIgU1RBVElDID0gb3B0aW9ucy5zdGF0O1xuICB2YXIgRk9SQ0VELCB0YXJnZXQsIGtleSwgdGFyZ2V0UHJvcGVydHksIHNvdXJjZVByb3BlcnR5LCBkZXNjcmlwdG9yO1xuICBpZiAoR0xPQkFMKSB7XG4gICAgdGFyZ2V0ID0gZ2xvYmFsO1xuICB9IGVsc2UgaWYgKFNUQVRJQykge1xuICAgIHRhcmdldCA9IGdsb2JhbFtUQVJHRVRdIHx8IHNldEdsb2JhbChUQVJHRVQsIHt9KTtcbiAgfSBlbHNlIHtcbiAgICB0YXJnZXQgPSAoZ2xvYmFsW1RBUkdFVF0gfHwge30pLnByb3RvdHlwZTtcbiAgfVxuICBpZiAodGFyZ2V0KSBmb3IgKGtleSBpbiBzb3VyY2UpIHtcbiAgICBzb3VyY2VQcm9wZXJ0eSA9IHNvdXJjZVtrZXldO1xuICAgIGlmIChvcHRpb25zLm5vVGFyZ2V0R2V0KSB7XG4gICAgICBkZXNjcmlwdG9yID0gZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yKHRhcmdldCwga2V5KTtcbiAgICAgIHRhcmdldFByb3BlcnR5ID0gZGVzY3JpcHRvciAmJiBkZXNjcmlwdG9yLnZhbHVlO1xuICAgIH0gZWxzZSB0YXJnZXRQcm9wZXJ0eSA9IHRhcmdldFtrZXldO1xuICAgIEZPUkNFRCA9IGlzRm9yY2VkKEdMT0JBTCA/IGtleSA6IFRBUkdFVCArIChTVEFUSUMgPyAnLicgOiAnIycpICsga2V5LCBvcHRpb25zLmZvcmNlZCk7XG4gICAgLy8gY29udGFpbmVkIGluIHRhcmdldFxuICAgIGlmICghRk9SQ0VEICYmIHRhcmdldFByb3BlcnR5ICE9PSB1bmRlZmluZWQpIHtcbiAgICAgIGlmICh0eXBlb2Ygc291cmNlUHJvcGVydHkgPT09IHR5cGVvZiB0YXJnZXRQcm9wZXJ0eSkgY29udGludWU7XG4gICAgICBjb3B5Q29uc3RydWN0b3JQcm9wZXJ0aWVzKHNvdXJjZVByb3BlcnR5LCB0YXJnZXRQcm9wZXJ0eSk7XG4gICAgfVxuICAgIC8vIGFkZCBhIGZsYWcgdG8gbm90IGNvbXBsZXRlbHkgZnVsbCBwb2x5ZmlsbHNcbiAgICBpZiAob3B0aW9ucy5zaGFtIHx8ICh0YXJnZXRQcm9wZXJ0eSAmJiB0YXJnZXRQcm9wZXJ0eS5zaGFtKSkge1xuICAgICAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KHNvdXJjZVByb3BlcnR5LCAnc2hhbScsIHRydWUpO1xuICAgIH1cbiAgICAvLyBleHRlbmQgZ2xvYmFsXG4gICAgcmVkZWZpbmUodGFyZ2V0LCBrZXksIHNvdXJjZVByb3BlcnR5LCBvcHRpb25zKTtcbiAgfVxufTtcbiIsICJ2YXIgaXNPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtb2JqZWN0Jyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGl0KSB7XG4gIGlmICghaXNPYmplY3QoaXQpICYmIGl0ICE9PSBudWxsKSB7XG4gICAgdGhyb3cgVHlwZUVycm9yKFwiQ2FuJ3Qgc2V0IFwiICsgU3RyaW5nKGl0KSArICcgYXMgYSBwcm90b3R5cGUnKTtcbiAgfSByZXR1cm4gaXQ7XG59O1xuIiwgIi8qIGVzbGludC1kaXNhYmxlIG5vLXByb3RvIC0tIHNhZmUgKi9cbnZhciBhbk9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hbi1vYmplY3QnKTtcbnZhciBhUG9zc2libGVQcm90b3R5cGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYS1wb3NzaWJsZS1wcm90b3R5cGUnKTtcblxuLy8gYE9iamVjdC5zZXRQcm90b3R5cGVPZmAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5zZXRwcm90b3R5cGVvZlxuLy8gV29ya3Mgd2l0aCBfX3Byb3RvX18gb25seS4gT2xkIHY4IGNhbid0IHdvcmsgd2l0aCBudWxsIHByb3RvIG9iamVjdHMuXG4vLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tb2JqZWN0LXNldHByb3RvdHlwZW9mIC0tIHNhZmVcbm1vZHVsZS5leHBvcnRzID0gT2JqZWN0LnNldFByb3RvdHlwZU9mIHx8ICgnX19wcm90b19fJyBpbiB7fSA/IGZ1bmN0aW9uICgpIHtcbiAgdmFyIENPUlJFQ1RfU0VUVEVSID0gZmFsc2U7XG4gIHZhciB0ZXN0ID0ge307XG4gIHZhciBzZXR0ZXI7XG4gIHRyeSB7XG4gICAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLW9iamVjdC1nZXRvd25wcm9wZXJ0eWRlc2NyaXB0b3IgLS0gc2FmZVxuICAgIHNldHRlciA9IE9iamVjdC5nZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IoT2JqZWN0LnByb3RvdHlwZSwgJ19fcHJvdG9fXycpLnNldDtcbiAgICBzZXR0ZXIuY2FsbCh0ZXN0LCBbXSk7XG4gICAgQ09SUkVDVF9TRVRURVIgPSB0ZXN0IGluc3RhbmNlb2YgQXJyYXk7XG4gIH0gY2F0Y2ggKGVycm9yKSB7IC8qIGVtcHR5ICovIH1cbiAgcmV0dXJuIGZ1bmN0aW9uIHNldFByb3RvdHlwZU9mKE8sIHByb3RvKSB7XG4gICAgYW5PYmplY3QoTyk7XG4gICAgYVBvc3NpYmxlUHJvdG90eXBlKHByb3RvKTtcbiAgICBpZiAoQ09SUkVDVF9TRVRURVIpIHNldHRlci5jYWxsKE8sIHByb3RvKTtcbiAgICBlbHNlIE8uX19wcm90b19fID0gcHJvdG87XG4gICAgcmV0dXJuIE87XG4gIH07XG59KCkgOiB1bmRlZmluZWQpO1xuIiwgInZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xuXG5tb2R1bGUuZXhwb3J0cyA9ICFmYWlscyhmdW5jdGlvbiAoKSB7XG4gIGZ1bmN0aW9uIEYoKSB7IC8qIGVtcHR5ICovIH1cbiAgRi5wcm90b3R5cGUuY29uc3RydWN0b3IgPSBudWxsO1xuICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tb2JqZWN0LWdldHByb3RvdHlwZW9mIC0tIHJlcXVpcmVkIGZvciB0ZXN0aW5nXG4gIHJldHVybiBPYmplY3QuZ2V0UHJvdG90eXBlT2YobmV3IEYoKSkgIT09IEYucHJvdG90eXBlO1xufSk7XG4iLCAidmFyIGhhcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oYXMnKTtcbnZhciB0b09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1vYmplY3QnKTtcbnZhciBzaGFyZWRLZXkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2hhcmVkLWtleScpO1xudmFyIENPUlJFQ1RfUFJPVE9UWVBFX0dFVFRFUiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jb3JyZWN0LXByb3RvdHlwZS1nZXR0ZXInKTtcblxudmFyIElFX1BST1RPID0gc2hhcmVkS2V5KCdJRV9QUk9UTycpO1xudmFyIE9iamVjdFByb3RvdHlwZSA9IE9iamVjdC5wcm90b3R5cGU7XG5cbi8vIGBPYmplY3QuZ2V0UHJvdG90eXBlT2ZgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1vYmplY3QuZ2V0cHJvdG90eXBlb2Zcbi8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBlcy9uby1vYmplY3QtZ2V0cHJvdG90eXBlb2YgLS0gc2FmZVxubW9kdWxlLmV4cG9ydHMgPSBDT1JSRUNUX1BST1RPVFlQRV9HRVRURVIgPyBPYmplY3QuZ2V0UHJvdG90eXBlT2YgOiBmdW5jdGlvbiAoTykge1xuICBPID0gdG9PYmplY3QoTyk7XG4gIGlmIChoYXMoTywgSUVfUFJPVE8pKSByZXR1cm4gT1tJRV9QUk9UT107XG4gIGlmICh0eXBlb2YgTy5jb25zdHJ1Y3RvciA9PSAnZnVuY3Rpb24nICYmIE8gaW5zdGFuY2VvZiBPLmNvbnN0cnVjdG9yKSB7XG4gICAgcmV0dXJuIE8uY29uc3RydWN0b3IucHJvdG90eXBlO1xuICB9IHJldHVybiBPIGluc3RhbmNlb2YgT2JqZWN0ID8gT2JqZWN0UHJvdG90eXBlIDogbnVsbDtcbn07XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyIGZhaWxzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2ZhaWxzJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKE1FVEhPRF9OQU1FLCBhcmd1bWVudCkge1xuICB2YXIgbWV0aG9kID0gW11bTUVUSE9EX05BTUVdO1xuICByZXR1cm4gISFtZXRob2QgJiYgZmFpbHMoZnVuY3Rpb24gKCkge1xuICAgIC8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBuby11c2VsZXNzLWNhbGwsbm8tdGhyb3ctbGl0ZXJhbCAtLSByZXF1aXJlZCBmb3IgdGVzdGluZ1xuICAgIG1ldGhvZC5jYWxsKG51bGwsIGFyZ3VtZW50IHx8IGZ1bmN0aW9uICgpIHsgdGhyb3cgMTsgfSwgMSk7XG4gIH0pO1xufTtcbiIsICJ2YXIgZ2V0QnVpbHRJbiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nZXQtYnVpbHQtaW4nKTtcblxubW9kdWxlLmV4cG9ydHMgPSBnZXRCdWlsdEluKCduYXZpZ2F0b3InLCAndXNlckFnZW50JykgfHwgJyc7XG4iLCAidmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcbnZhciB1c2VyQWdlbnQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZW5naW5lLXVzZXItYWdlbnQnKTtcblxudmFyIHByb2Nlc3MgPSBnbG9iYWwucHJvY2VzcztcbnZhciB2ZXJzaW9ucyA9IHByb2Nlc3MgJiYgcHJvY2Vzcy52ZXJzaW9ucztcbnZhciB2OCA9IHZlcnNpb25zICYmIHZlcnNpb25zLnY4O1xudmFyIG1hdGNoLCB2ZXJzaW9uO1xuXG5pZiAodjgpIHtcbiAgbWF0Y2ggPSB2OC5zcGxpdCgnLicpO1xuICB2ZXJzaW9uID0gbWF0Y2hbMF0gPCA0ID8gMSA6IG1hdGNoWzBdICsgbWF0Y2hbMV07XG59IGVsc2UgaWYgKHVzZXJBZ2VudCkge1xuICBtYXRjaCA9IHVzZXJBZ2VudC5tYXRjaCgvRWRnZVxcLyhcXGQrKS8pO1xuICBpZiAoIW1hdGNoIHx8IG1hdGNoWzFdID49IDc0KSB7XG4gICAgbWF0Y2ggPSB1c2VyQWdlbnQubWF0Y2goL0Nocm9tZVxcLyhcXGQrKS8pO1xuICAgIGlmIChtYXRjaCkgdmVyc2lvbiA9IG1hdGNoWzFdO1xuICB9XG59XG5cbm1vZHVsZS5leHBvcnRzID0gdmVyc2lvbiAmJiArdmVyc2lvbjtcbiIsICIvKiBlc2xpbnQtZGlzYWJsZSBlcy9uby1zeW1ib2wgLS0gcmVxdWlyZWQgZm9yIHRlc3RpbmcgKi9cbnZhciBWOF9WRVJTSU9OID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2VuZ2luZS12OC12ZXJzaW9uJyk7XG52YXIgZmFpbHMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZmFpbHMnKTtcblxuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLW9iamVjdC1nZXRvd25wcm9wZXJ0eXN5bWJvbHMgLS0gcmVxdWlyZWQgZm9yIHRlc3Rpbmdcbm1vZHVsZS5leHBvcnRzID0gISFPYmplY3QuZ2V0T3duUHJvcGVydHlTeW1ib2xzICYmICFmYWlscyhmdW5jdGlvbiAoKSB7XG4gIHZhciBzeW1ib2wgPSBTeW1ib2woKTtcbiAgLy8gQ2hyb21lIDM4IFN5bWJvbCBoYXMgaW5jb3JyZWN0IHRvU3RyaW5nIGNvbnZlcnNpb25cbiAgLy8gYGdldC1vd24tcHJvcGVydHktc3ltYm9sc2AgcG9seWZpbGwgc3ltYm9scyBjb252ZXJ0ZWQgdG8gb2JqZWN0IGFyZSBub3QgU3ltYm9sIGluc3RhbmNlc1xuICByZXR1cm4gIVN0cmluZyhzeW1ib2wpIHx8ICEoT2JqZWN0KHN5bWJvbCkgaW5zdGFuY2VvZiBTeW1ib2wpIHx8XG4gICAgLy8gQ2hyb21lIDM4LTQwIHN5bWJvbHMgYXJlIG5vdCBpbmhlcml0ZWQgZnJvbSBET00gY29sbGVjdGlvbnMgcHJvdG90eXBlcyB0byBpbnN0YW5jZXNcbiAgICAhU3ltYm9sLnNoYW0gJiYgVjhfVkVSU0lPTiAmJiBWOF9WRVJTSU9OIDwgNDE7XG59KTtcbiIsICIvKiBlc2xpbnQtZGlzYWJsZSBlcy9uby1zeW1ib2wgLS0gcmVxdWlyZWQgZm9yIHRlc3RpbmcgKi9cbnZhciBOQVRJVkVfU1lNQk9MID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL25hdGl2ZS1zeW1ib2wnKTtcblxubW9kdWxlLmV4cG9ydHMgPSBOQVRJVkVfU1lNQk9MXG4gICYmICFTeW1ib2wuc2hhbVxuICAmJiB0eXBlb2YgU3ltYm9sLml0ZXJhdG9yID09ICdzeW1ib2wnO1xuIiwgInZhciBnbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2xvYmFsJyk7XG52YXIgc2hhcmVkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NoYXJlZCcpO1xudmFyIGhhcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oYXMnKTtcbnZhciB1aWQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdWlkJyk7XG52YXIgTkFUSVZFX1NZTUJPTCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9uYXRpdmUtc3ltYm9sJyk7XG52YXIgVVNFX1NZTUJPTF9BU19VSUQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdXNlLXN5bWJvbC1hcy11aWQnKTtcblxudmFyIFdlbGxLbm93blN5bWJvbHNTdG9yZSA9IHNoYXJlZCgnd2tzJyk7XG52YXIgU3ltYm9sID0gZ2xvYmFsLlN5bWJvbDtcbnZhciBjcmVhdGVXZWxsS25vd25TeW1ib2wgPSBVU0VfU1lNQk9MX0FTX1VJRCA/IFN5bWJvbCA6IFN5bWJvbCAmJiBTeW1ib2wud2l0aG91dFNldHRlciB8fCB1aWQ7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKG5hbWUpIHtcbiAgaWYgKCFoYXMoV2VsbEtub3duU3ltYm9sc1N0b3JlLCBuYW1lKSB8fCAhKE5BVElWRV9TWU1CT0wgfHwgdHlwZW9mIFdlbGxLbm93blN5bWJvbHNTdG9yZVtuYW1lXSA9PSAnc3RyaW5nJykpIHtcbiAgICBpZiAoTkFUSVZFX1NZTUJPTCAmJiBoYXMoU3ltYm9sLCBuYW1lKSkge1xuICAgICAgV2VsbEtub3duU3ltYm9sc1N0b3JlW25hbWVdID0gU3ltYm9sW25hbWVdO1xuICAgIH0gZWxzZSB7XG4gICAgICBXZWxsS25vd25TeW1ib2xzU3RvcmVbbmFtZV0gPSBjcmVhdGVXZWxsS25vd25TeW1ib2woJ1N5bWJvbC4nICsgbmFtZSk7XG4gICAgfVxuICB9IHJldHVybiBXZWxsS25vd25TeW1ib2xzU3RvcmVbbmFtZV07XG59O1xuIiwgInZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcblxudmFyIFRPX1NUUklOR19UQUcgPSB3ZWxsS25vd25TeW1ib2woJ3RvU3RyaW5nVGFnJyk7XG52YXIgdGVzdCA9IHt9O1xuXG50ZXN0W1RPX1NUUklOR19UQUddID0gJ3onO1xuXG5tb2R1bGUuZXhwb3J0cyA9IFN0cmluZyh0ZXN0KSA9PT0gJ1tvYmplY3Qgel0nO1xuIiwgInZhciBUT19TVFJJTkdfVEFHX1NVUFBPUlQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tc3RyaW5nLXRhZy1zdXBwb3J0Jyk7XG52YXIgY2xhc3NvZlJhdyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jbGFzc29mLXJhdycpO1xudmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xuXG52YXIgVE9fU1RSSU5HX1RBRyA9IHdlbGxLbm93blN5bWJvbCgndG9TdHJpbmdUYWcnKTtcbi8vIEVTMyB3cm9uZyBoZXJlXG52YXIgQ09SUkVDVF9BUkdVTUVOVFMgPSBjbGFzc29mUmF3KGZ1bmN0aW9uICgpIHsgcmV0dXJuIGFyZ3VtZW50czsgfSgpKSA9PSAnQXJndW1lbnRzJztcblxuLy8gZmFsbGJhY2sgZm9yIElFMTEgU2NyaXB0IEFjY2VzcyBEZW5pZWQgZXJyb3JcbnZhciB0cnlHZXQgPSBmdW5jdGlvbiAoaXQsIGtleSkge1xuICB0cnkge1xuICAgIHJldHVybiBpdFtrZXldO1xuICB9IGNhdGNoIChlcnJvcikgeyAvKiBlbXB0eSAqLyB9XG59O1xuXG4vLyBnZXR0aW5nIHRhZyBmcm9tIEVTNisgYE9iamVjdC5wcm90b3R5cGUudG9TdHJpbmdgXG5tb2R1bGUuZXhwb3J0cyA9IFRPX1NUUklOR19UQUdfU1VQUE9SVCA/IGNsYXNzb2ZSYXcgOiBmdW5jdGlvbiAoaXQpIHtcbiAgdmFyIE8sIHRhZywgcmVzdWx0O1xuICByZXR1cm4gaXQgPT09IHVuZGVmaW5lZCA/ICdVbmRlZmluZWQnIDogaXQgPT09IG51bGwgPyAnTnVsbCdcbiAgICAvLyBAQHRvU3RyaW5nVGFnIGNhc2VcbiAgICA6IHR5cGVvZiAodGFnID0gdHJ5R2V0KE8gPSBPYmplY3QoaXQpLCBUT19TVFJJTkdfVEFHKSkgPT0gJ3N0cmluZycgPyB0YWdcbiAgICAvLyBidWlsdGluVGFnIGNhc2VcbiAgICA6IENPUlJFQ1RfQVJHVU1FTlRTID8gY2xhc3NvZlJhdyhPKVxuICAgIC8vIEVTMyBhcmd1bWVudHMgZmFsbGJhY2tcbiAgICA6IChyZXN1bHQgPSBjbGFzc29mUmF3KE8pKSA9PSAnT2JqZWN0JyAmJiB0eXBlb2YgTy5jYWxsZWUgPT0gJ2Z1bmN0aW9uJyA/ICdBcmd1bWVudHMnIDogcmVzdWx0O1xufTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgVE9fU1RSSU5HX1RBR19TVVBQT1JUID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLXN0cmluZy10YWctc3VwcG9ydCcpO1xudmFyIGNsYXNzb2YgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY2xhc3NvZicpO1xuXG4vLyBgT2JqZWN0LnByb3RvdHlwZS50b1N0cmluZ2AgbWV0aG9kIGltcGxlbWVudGF0aW9uXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5wcm90b3R5cGUudG9zdHJpbmdcbm1vZHVsZS5leHBvcnRzID0gVE9fU1RSSU5HX1RBR19TVVBQT1JUID8ge30udG9TdHJpbmcgOiBmdW5jdGlvbiB0b1N0cmluZygpIHtcbiAgcmV0dXJuICdbb2JqZWN0ICcgKyBjbGFzc29mKHRoaXMpICsgJ10nO1xufTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgYW5PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYW4tb2JqZWN0Jyk7XG5cbi8vIGBSZWdFeHAucHJvdG90eXBlLmZsYWdzYCBnZXR0ZXIgaW1wbGVtZW50YXRpb25cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtZ2V0LXJlZ2V4cC5wcm90b3R5cGUuZmxhZ3Ncbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKCkge1xuICB2YXIgdGhhdCA9IGFuT2JqZWN0KHRoaXMpO1xuICB2YXIgcmVzdWx0ID0gJyc7XG4gIGlmICh0aGF0Lmdsb2JhbCkgcmVzdWx0ICs9ICdnJztcbiAgaWYgKHRoYXQuaWdub3JlQ2FzZSkgcmVzdWx0ICs9ICdpJztcbiAgaWYgKHRoYXQubXVsdGlsaW5lKSByZXN1bHQgKz0gJ20nO1xuICBpZiAodGhhdC5kb3RBbGwpIHJlc3VsdCArPSAncyc7XG4gIGlmICh0aGF0LnVuaWNvZGUpIHJlc3VsdCArPSAndSc7XG4gIGlmICh0aGF0LnN0aWNreSkgcmVzdWx0ICs9ICd5JztcbiAgcmV0dXJuIHJlc3VsdDtcbn07XG4iLCAibW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaXQpIHtcbiAgaWYgKHR5cGVvZiBpdCAhPSAnZnVuY3Rpb24nKSB7XG4gICAgdGhyb3cgVHlwZUVycm9yKFN0cmluZyhpdCkgKyAnIGlzIG5vdCBhIGZ1bmN0aW9uJyk7XG4gIH0gcmV0dXJuIGl0O1xufTtcbiIsICJ2YXIgaW50ZXJuYWxPYmplY3RLZXlzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1rZXlzLWludGVybmFsJyk7XG52YXIgZW51bUJ1Z0tleXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZW51bS1idWcta2V5cycpO1xuXG4vLyBgT2JqZWN0LmtleXNgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1vYmplY3Qua2V5c1xuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLW9iamVjdC1rZXlzIC0tIHNhZmVcbm1vZHVsZS5leHBvcnRzID0gT2JqZWN0LmtleXMgfHwgZnVuY3Rpb24ga2V5cyhPKSB7XG4gIHJldHVybiBpbnRlcm5hbE9iamVjdEtleXMoTywgZW51bUJ1Z0tleXMpO1xufTtcbiIsICJ2YXIgREVTQ1JJUFRPUlMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZGVzY3JpcHRvcnMnKTtcbnZhciBkZWZpbmVQcm9wZXJ0eU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZGVmaW5lLXByb3BlcnR5Jyk7XG52YXIgYW5PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYW4tb2JqZWN0Jyk7XG52YXIgb2JqZWN0S2V5cyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3Qta2V5cycpO1xuXG4vLyBgT2JqZWN0LmRlZmluZVByb3BlcnRpZXNgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1vYmplY3QuZGVmaW5lcHJvcGVydGllc1xuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLW9iamVjdC1kZWZpbmVwcm9wZXJ0aWVzIC0tIHNhZmVcbm1vZHVsZS5leHBvcnRzID0gREVTQ1JJUFRPUlMgPyBPYmplY3QuZGVmaW5lUHJvcGVydGllcyA6IGZ1bmN0aW9uIGRlZmluZVByb3BlcnRpZXMoTywgUHJvcGVydGllcykge1xuICBhbk9iamVjdChPKTtcbiAgdmFyIGtleXMgPSBvYmplY3RLZXlzKFByb3BlcnRpZXMpO1xuICB2YXIgbGVuZ3RoID0ga2V5cy5sZW5ndGg7XG4gIHZhciBpbmRleCA9IDA7XG4gIHZhciBrZXk7XG4gIHdoaWxlIChsZW5ndGggPiBpbmRleCkgZGVmaW5lUHJvcGVydHlNb2R1bGUuZihPLCBrZXkgPSBrZXlzW2luZGV4KytdLCBQcm9wZXJ0aWVzW2tleV0pO1xuICByZXR1cm4gTztcbn07XG4iLCAidmFyIGdldEJ1aWx0SW4gPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2V0LWJ1aWx0LWluJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZ2V0QnVpbHRJbignZG9jdW1lbnQnLCAnZG9jdW1lbnRFbGVtZW50Jyk7XG4iLCAidmFyIGFuT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FuLW9iamVjdCcpO1xudmFyIGRlZmluZVByb3BlcnRpZXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0aWVzJyk7XG52YXIgZW51bUJ1Z0tleXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZW51bS1idWcta2V5cycpO1xudmFyIGhpZGRlbktleXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGlkZGVuLWtleXMnKTtcbnZhciBodG1sID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2h0bWwnKTtcbnZhciBkb2N1bWVudENyZWF0ZUVsZW1lbnQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZG9jdW1lbnQtY3JlYXRlLWVsZW1lbnQnKTtcbnZhciBzaGFyZWRLZXkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2hhcmVkLWtleScpO1xuXG52YXIgR1QgPSAnPic7XG52YXIgTFQgPSAnPCc7XG52YXIgUFJPVE9UWVBFID0gJ3Byb3RvdHlwZSc7XG52YXIgU0NSSVBUID0gJ3NjcmlwdCc7XG52YXIgSUVfUFJPVE8gPSBzaGFyZWRLZXkoJ0lFX1BST1RPJyk7XG5cbnZhciBFbXB0eUNvbnN0cnVjdG9yID0gZnVuY3Rpb24gKCkgeyAvKiBlbXB0eSAqLyB9O1xuXG52YXIgc2NyaXB0VGFnID0gZnVuY3Rpb24gKGNvbnRlbnQpIHtcbiAgcmV0dXJuIExUICsgU0NSSVBUICsgR1QgKyBjb250ZW50ICsgTFQgKyAnLycgKyBTQ1JJUFQgKyBHVDtcbn07XG5cbi8vIENyZWF0ZSBvYmplY3Qgd2l0aCBmYWtlIGBudWxsYCBwcm90b3R5cGU6IHVzZSBBY3RpdmVYIE9iamVjdCB3aXRoIGNsZWFyZWQgcHJvdG90eXBlXG52YXIgTnVsbFByb3RvT2JqZWN0VmlhQWN0aXZlWCA9IGZ1bmN0aW9uIChhY3RpdmVYRG9jdW1lbnQpIHtcbiAgYWN0aXZlWERvY3VtZW50LndyaXRlKHNjcmlwdFRhZygnJykpO1xuICBhY3RpdmVYRG9jdW1lbnQuY2xvc2UoKTtcbiAgdmFyIHRlbXAgPSBhY3RpdmVYRG9jdW1lbnQucGFyZW50V2luZG93Lk9iamVjdDtcbiAgYWN0aXZlWERvY3VtZW50ID0gbnVsbDsgLy8gYXZvaWQgbWVtb3J5IGxlYWtcbiAgcmV0dXJuIHRlbXA7XG59O1xuXG4vLyBDcmVhdGUgb2JqZWN0IHdpdGggZmFrZSBgbnVsbGAgcHJvdG90eXBlOiB1c2UgaWZyYW1lIE9iamVjdCB3aXRoIGNsZWFyZWQgcHJvdG90eXBlXG52YXIgTnVsbFByb3RvT2JqZWN0VmlhSUZyYW1lID0gZnVuY3Rpb24gKCkge1xuICAvLyBUaHJhc2gsIHdhc3RlIGFuZCBzb2RvbXk6IElFIEdDIGJ1Z1xuICB2YXIgaWZyYW1lID0gZG9jdW1lbnRDcmVhdGVFbGVtZW50KCdpZnJhbWUnKTtcbiAgdmFyIEpTID0gJ2phdmEnICsgU0NSSVBUICsgJzonO1xuICB2YXIgaWZyYW1lRG9jdW1lbnQ7XG4gIGlmcmFtZS5zdHlsZS5kaXNwbGF5ID0gJ25vbmUnO1xuICBodG1sLmFwcGVuZENoaWxkKGlmcmFtZSk7XG4gIC8vIGh0dHBzOi8vZ2l0aHViLmNvbS96bG9pcm9jay9jb3JlLWpzL2lzc3Vlcy80NzVcbiAgaWZyYW1lLnNyYyA9IFN0cmluZyhKUyk7XG4gIGlmcmFtZURvY3VtZW50ID0gaWZyYW1lLmNvbnRlbnRXaW5kb3cuZG9jdW1lbnQ7XG4gIGlmcmFtZURvY3VtZW50Lm9wZW4oKTtcbiAgaWZyYW1lRG9jdW1lbnQud3JpdGUoc2NyaXB0VGFnKCdkb2N1bWVudC5GPU9iamVjdCcpKTtcbiAgaWZyYW1lRG9jdW1lbnQuY2xvc2UoKTtcbiAgcmV0dXJuIGlmcmFtZURvY3VtZW50LkY7XG59O1xuXG4vLyBDaGVjayBmb3IgZG9jdW1lbnQuZG9tYWluIGFuZCBhY3RpdmUgeCBzdXBwb3J0XG4vLyBObyBuZWVkIHRvIHVzZSBhY3RpdmUgeCBhcHByb2FjaCB3aGVuIGRvY3VtZW50LmRvbWFpbiBpcyBub3Qgc2V0XG4vLyBzZWUgaHR0cHM6Ly9naXRodWIuY29tL2VzLXNoaW1zL2VzNS1zaGltL2lzc3Vlcy8xNTBcbi8vIHZhcmlhdGlvbiBvZiBodHRwczovL2dpdGh1Yi5jb20va2l0Y2FtYnJpZGdlL2VzNS1zaGltL2NvbW1pdC80ZjczOGFjMDY2MzQ2XG4vLyBhdm9pZCBJRSBHQyBidWdcbnZhciBhY3RpdmVYRG9jdW1lbnQ7XG52YXIgTnVsbFByb3RvT2JqZWN0ID0gZnVuY3Rpb24gKCkge1xuICB0cnkge1xuICAgIC8qIGdsb2JhbCBBY3RpdmVYT2JqZWN0IC0tIG9sZCBJRSAqL1xuICAgIGFjdGl2ZVhEb2N1bWVudCA9IGRvY3VtZW50LmRvbWFpbiAmJiBuZXcgQWN0aXZlWE9iamVjdCgnaHRtbGZpbGUnKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHsgLyogaWdub3JlICovIH1cbiAgTnVsbFByb3RvT2JqZWN0ID0gYWN0aXZlWERvY3VtZW50ID8gTnVsbFByb3RvT2JqZWN0VmlhQWN0aXZlWChhY3RpdmVYRG9jdW1lbnQpIDogTnVsbFByb3RvT2JqZWN0VmlhSUZyYW1lKCk7XG4gIHZhciBsZW5ndGggPSBlbnVtQnVnS2V5cy5sZW5ndGg7XG4gIHdoaWxlIChsZW5ndGgtLSkgZGVsZXRlIE51bGxQcm90b09iamVjdFtQUk9UT1RZUEVdW2VudW1CdWdLZXlzW2xlbmd0aF1dO1xuICByZXR1cm4gTnVsbFByb3RvT2JqZWN0KCk7XG59O1xuXG5oaWRkZW5LZXlzW0lFX1BST1RPXSA9IHRydWU7XG5cbi8vIGBPYmplY3QuY3JlYXRlYCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtb2JqZWN0LmNyZWF0ZVxubW9kdWxlLmV4cG9ydHMgPSBPYmplY3QuY3JlYXRlIHx8IGZ1bmN0aW9uIGNyZWF0ZShPLCBQcm9wZXJ0aWVzKSB7XG4gIHZhciByZXN1bHQ7XG4gIGlmIChPICE9PSBudWxsKSB7XG4gICAgRW1wdHlDb25zdHJ1Y3RvcltQUk9UT1RZUEVdID0gYW5PYmplY3QoTyk7XG4gICAgcmVzdWx0ID0gbmV3IEVtcHR5Q29uc3RydWN0b3IoKTtcbiAgICBFbXB0eUNvbnN0cnVjdG9yW1BST1RPVFlQRV0gPSBudWxsO1xuICAgIC8vIGFkZCBcIl9fcHJvdG9fX1wiIGZvciBPYmplY3QuZ2V0UHJvdG90eXBlT2YgcG9seWZpbGxcbiAgICByZXN1bHRbSUVfUFJPVE9dID0gTztcbiAgfSBlbHNlIHJlc3VsdCA9IE51bGxQcm90b09iamVjdCgpO1xuICByZXR1cm4gUHJvcGVydGllcyA9PT0gdW5kZWZpbmVkID8gcmVzdWx0IDogZGVmaW5lUHJvcGVydGllcyhyZXN1bHQsIFByb3BlcnRpZXMpO1xufTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgYUZ1bmN0aW9uID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2EtZnVuY3Rpb24nKTtcbnZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcblxudmFyIHNsaWNlID0gW10uc2xpY2U7XG52YXIgZmFjdG9yaWVzID0ge307XG5cbnZhciBjb25zdHJ1Y3QgPSBmdW5jdGlvbiAoQywgYXJnc0xlbmd0aCwgYXJncykge1xuICBpZiAoIShhcmdzTGVuZ3RoIGluIGZhY3RvcmllcykpIHtcbiAgICBmb3IgKHZhciBsaXN0ID0gW10sIGkgPSAwOyBpIDwgYXJnc0xlbmd0aDsgaSsrKSBsaXN0W2ldID0gJ2FbJyArIGkgKyAnXSc7XG4gICAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIG5vLW5ldy1mdW5jIC0tIHdlIGhhdmUgbm8gcHJvcGVyIGFsdGVybmF0aXZlcywgSUU4LSBvbmx5XG4gICAgZmFjdG9yaWVzW2FyZ3NMZW5ndGhdID0gRnVuY3Rpb24oJ0MsYScsICdyZXR1cm4gbmV3IEMoJyArIGxpc3Quam9pbignLCcpICsgJyknKTtcbiAgfSByZXR1cm4gZmFjdG9yaWVzW2FyZ3NMZW5ndGhdKEMsIGFyZ3MpO1xufTtcblxuLy8gYEZ1bmN0aW9uLnByb3RvdHlwZS5iaW5kYCBtZXRob2QgaW1wbGVtZW50YXRpb25cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtZnVuY3Rpb24ucHJvdG90eXBlLmJpbmRcbm1vZHVsZS5leHBvcnRzID0gRnVuY3Rpb24uYmluZCB8fCBmdW5jdGlvbiBiaW5kKHRoYXQgLyogLCAuLi5hcmdzICovKSB7XG4gIHZhciBmbiA9IGFGdW5jdGlvbih0aGlzKTtcbiAgdmFyIHBhcnRBcmdzID0gc2xpY2UuY2FsbChhcmd1bWVudHMsIDEpO1xuICB2YXIgYm91bmRGdW5jdGlvbiA9IGZ1bmN0aW9uIGJvdW5kKC8qIGFyZ3MuLi4gKi8pIHtcbiAgICB2YXIgYXJncyA9IHBhcnRBcmdzLmNvbmNhdChzbGljZS5jYWxsKGFyZ3VtZW50cykpO1xuICAgIHJldHVybiB0aGlzIGluc3RhbmNlb2YgYm91bmRGdW5jdGlvbiA/IGNvbnN0cnVjdChmbiwgYXJncy5sZW5ndGgsIGFyZ3MpIDogZm4uYXBwbHkodGhhdCwgYXJncyk7XG4gIH07XG4gIGlmIChpc09iamVjdChmbi5wcm90b3R5cGUpKSBib3VuZEZ1bmN0aW9uLnByb3RvdHlwZSA9IGZuLnByb3RvdHlwZTtcbiAgcmV0dXJuIGJvdW5kRnVuY3Rpb247XG59O1xuIiwgInZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcbnZhciBjcmVhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWNyZWF0ZScpO1xudmFyIGRlZmluZVByb3BlcnR5TW9kdWxlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1kZWZpbmUtcHJvcGVydHknKTtcblxudmFyIFVOU0NPUEFCTEVTID0gd2VsbEtub3duU3ltYm9sKCd1bnNjb3BhYmxlcycpO1xudmFyIEFycmF5UHJvdG90eXBlID0gQXJyYXkucHJvdG90eXBlO1xuXG4vLyBBcnJheS5wcm90b3R5cGVbQEB1bnNjb3BhYmxlc11cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLUBAdW5zY29wYWJsZXNcbmlmIChBcnJheVByb3RvdHlwZVtVTlNDT1BBQkxFU10gPT0gdW5kZWZpbmVkKSB7XG4gIGRlZmluZVByb3BlcnR5TW9kdWxlLmYoQXJyYXlQcm90b3R5cGUsIFVOU0NPUEFCTEVTLCB7XG4gICAgY29uZmlndXJhYmxlOiB0cnVlLFxuICAgIHZhbHVlOiBjcmVhdGUobnVsbClcbiAgfSk7XG59XG5cbi8vIGFkZCBhIGtleSB0byBBcnJheS5wcm90b3R5cGVbQEB1bnNjb3BhYmxlc11cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGtleSkge1xuICBBcnJheVByb3RvdHlwZVtVTlNDT1BBQkxFU11ba2V5XSA9IHRydWU7XG59O1xuIiwgIm1vZHVsZS5leHBvcnRzID0ge307XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyIGZhaWxzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2ZhaWxzJyk7XG52YXIgZ2V0UHJvdG90eXBlT2YgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWdldC1wcm90b3R5cGUtb2YnKTtcbnZhciBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY3JlYXRlLW5vbi1lbnVtZXJhYmxlLXByb3BlcnR5Jyk7XG52YXIgaGFzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2hhcycpO1xudmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xudmFyIElTX1BVUkUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtcHVyZScpO1xuXG52YXIgSVRFUkFUT1IgPSB3ZWxsS25vd25TeW1ib2woJ2l0ZXJhdG9yJyk7XG52YXIgQlVHR1lfU0FGQVJJX0lURVJBVE9SUyA9IGZhbHNlO1xuXG52YXIgcmV0dXJuVGhpcyA9IGZ1bmN0aW9uICgpIHsgcmV0dXJuIHRoaXM7IH07XG5cbi8vIGAlSXRlcmF0b3JQcm90b3R5cGUlYCBvYmplY3Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtJWl0ZXJhdG9ycHJvdG90eXBlJS1vYmplY3RcbnZhciBJdGVyYXRvclByb3RvdHlwZSwgUHJvdG90eXBlT2ZBcnJheUl0ZXJhdG9yUHJvdG90eXBlLCBhcnJheUl0ZXJhdG9yO1xuXG4vKiBlc2xpbnQtZGlzYWJsZSBlcy9uby1hcnJheS1wcm90b3R5cGUta2V5cyAtLSBzYWZlICovXG5pZiAoW10ua2V5cykge1xuICBhcnJheUl0ZXJhdG9yID0gW10ua2V5cygpO1xuICAvLyBTYWZhcmkgOCBoYXMgYnVnZ3kgaXRlcmF0b3JzIHcvbyBgbmV4dGBcbiAgaWYgKCEoJ25leHQnIGluIGFycmF5SXRlcmF0b3IpKSBCVUdHWV9TQUZBUklfSVRFUkFUT1JTID0gdHJ1ZTtcbiAgZWxzZSB7XG4gICAgUHJvdG90eXBlT2ZBcnJheUl0ZXJhdG9yUHJvdG90eXBlID0gZ2V0UHJvdG90eXBlT2YoZ2V0UHJvdG90eXBlT2YoYXJyYXlJdGVyYXRvcikpO1xuICAgIGlmIChQcm90b3R5cGVPZkFycmF5SXRlcmF0b3JQcm90b3R5cGUgIT09IE9iamVjdC5wcm90b3R5cGUpIEl0ZXJhdG9yUHJvdG90eXBlID0gUHJvdG90eXBlT2ZBcnJheUl0ZXJhdG9yUHJvdG90eXBlO1xuICB9XG59XG5cbnZhciBORVdfSVRFUkFUT1JfUFJPVE9UWVBFID0gSXRlcmF0b3JQcm90b3R5cGUgPT0gdW5kZWZpbmVkIHx8IGZhaWxzKGZ1bmN0aW9uICgpIHtcbiAgdmFyIHRlc3QgPSB7fTtcbiAgLy8gRkY0NC0gbGVnYWN5IGl0ZXJhdG9ycyBjYXNlXG4gIHJldHVybiBJdGVyYXRvclByb3RvdHlwZVtJVEVSQVRPUl0uY2FsbCh0ZXN0KSAhPT0gdGVzdDtcbn0pO1xuXG5pZiAoTkVXX0lURVJBVE9SX1BST1RPVFlQRSkgSXRlcmF0b3JQcm90b3R5cGUgPSB7fTtcblxuLy8gYCVJdGVyYXRvclByb3RvdHlwZSVbQEBpdGVyYXRvcl0oKWAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLSVpdGVyYXRvcnByb3RvdHlwZSUtQEBpdGVyYXRvclxuaWYgKCghSVNfUFVSRSB8fCBORVdfSVRFUkFUT1JfUFJPVE9UWVBFKSAmJiAhaGFzKEl0ZXJhdG9yUHJvdG90eXBlLCBJVEVSQVRPUikpIHtcbiAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KEl0ZXJhdG9yUHJvdG90eXBlLCBJVEVSQVRPUiwgcmV0dXJuVGhpcyk7XG59XG5cbm1vZHVsZS5leHBvcnRzID0ge1xuICBJdGVyYXRvclByb3RvdHlwZTogSXRlcmF0b3JQcm90b3R5cGUsXG4gIEJVR0dZX1NBRkFSSV9JVEVSQVRPUlM6IEJVR0dZX1NBRkFSSV9JVEVSQVRPUlNcbn07XG4iLCAidmFyIGRlZmluZVByb3BlcnR5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1kZWZpbmUtcHJvcGVydHknKS5mO1xudmFyIGhhcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oYXMnKTtcbnZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcblxudmFyIFRPX1NUUklOR19UQUcgPSB3ZWxsS25vd25TeW1ib2woJ3RvU3RyaW5nVGFnJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGl0LCBUQUcsIFNUQVRJQykge1xuICBpZiAoaXQgJiYgIWhhcyhpdCA9IFNUQVRJQyA/IGl0IDogaXQucHJvdG90eXBlLCBUT19TVFJJTkdfVEFHKSkge1xuICAgIGRlZmluZVByb3BlcnR5KGl0LCBUT19TVFJJTkdfVEFHLCB7IGNvbmZpZ3VyYWJsZTogdHJ1ZSwgdmFsdWU6IFRBRyB9KTtcbiAgfVxufTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgSXRlcmF0b3JQcm90b3R5cGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXRlcmF0b3JzLWNvcmUnKS5JdGVyYXRvclByb3RvdHlwZTtcbnZhciBjcmVhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWNyZWF0ZScpO1xudmFyIGNyZWF0ZVByb3BlcnR5RGVzY3JpcHRvciA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jcmVhdGUtcHJvcGVydHktZGVzY3JpcHRvcicpO1xudmFyIHNldFRvU3RyaW5nVGFnID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NldC10by1zdHJpbmctdGFnJyk7XG52YXIgSXRlcmF0b3JzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2l0ZXJhdG9ycycpO1xuXG52YXIgcmV0dXJuVGhpcyA9IGZ1bmN0aW9uICgpIHsgcmV0dXJuIHRoaXM7IH07XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKEl0ZXJhdG9yQ29uc3RydWN0b3IsIE5BTUUsIG5leHQpIHtcbiAgdmFyIFRPX1NUUklOR19UQUcgPSBOQU1FICsgJyBJdGVyYXRvcic7XG4gIEl0ZXJhdG9yQ29uc3RydWN0b3IucHJvdG90eXBlID0gY3JlYXRlKEl0ZXJhdG9yUHJvdG90eXBlLCB7IG5leHQ6IGNyZWF0ZVByb3BlcnR5RGVzY3JpcHRvcigxLCBuZXh0KSB9KTtcbiAgc2V0VG9TdHJpbmdUYWcoSXRlcmF0b3JDb25zdHJ1Y3RvciwgVE9fU1RSSU5HX1RBRywgZmFsc2UsIHRydWUpO1xuICBJdGVyYXRvcnNbVE9fU1RSSU5HX1RBR10gPSByZXR1cm5UaGlzO1xuICByZXR1cm4gSXRlcmF0b3JDb25zdHJ1Y3Rvcjtcbn07XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgY3JlYXRlSXRlcmF0b3JDb25zdHJ1Y3RvciA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jcmVhdGUtaXRlcmF0b3ItY29uc3RydWN0b3InKTtcbnZhciBnZXRQcm90b3R5cGVPZiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LXByb3RvdHlwZS1vZicpO1xudmFyIHNldFByb3RvdHlwZU9mID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1zZXQtcHJvdG90eXBlLW9mJyk7XG52YXIgc2V0VG9TdHJpbmdUYWcgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2V0LXRvLXN0cmluZy10YWcnKTtcbnZhciBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY3JlYXRlLW5vbi1lbnVtZXJhYmxlLXByb3BlcnR5Jyk7XG52YXIgcmVkZWZpbmUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVkZWZpbmUnKTtcbnZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcbnZhciBJU19QVVJFID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLXB1cmUnKTtcbnZhciBJdGVyYXRvcnMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXRlcmF0b3JzJyk7XG52YXIgSXRlcmF0b3JzQ29yZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pdGVyYXRvcnMtY29yZScpO1xuXG52YXIgSXRlcmF0b3JQcm90b3R5cGUgPSBJdGVyYXRvcnNDb3JlLkl0ZXJhdG9yUHJvdG90eXBlO1xudmFyIEJVR0dZX1NBRkFSSV9JVEVSQVRPUlMgPSBJdGVyYXRvcnNDb3JlLkJVR0dZX1NBRkFSSV9JVEVSQVRPUlM7XG52YXIgSVRFUkFUT1IgPSB3ZWxsS25vd25TeW1ib2woJ2l0ZXJhdG9yJyk7XG52YXIgS0VZUyA9ICdrZXlzJztcbnZhciBWQUxVRVMgPSAndmFsdWVzJztcbnZhciBFTlRSSUVTID0gJ2VudHJpZXMnO1xuXG52YXIgcmV0dXJuVGhpcyA9IGZ1bmN0aW9uICgpIHsgcmV0dXJuIHRoaXM7IH07XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKEl0ZXJhYmxlLCBOQU1FLCBJdGVyYXRvckNvbnN0cnVjdG9yLCBuZXh0LCBERUZBVUxULCBJU19TRVQsIEZPUkNFRCkge1xuICBjcmVhdGVJdGVyYXRvckNvbnN0cnVjdG9yKEl0ZXJhdG9yQ29uc3RydWN0b3IsIE5BTUUsIG5leHQpO1xuXG4gIHZhciBnZXRJdGVyYXRpb25NZXRob2QgPSBmdW5jdGlvbiAoS0lORCkge1xuICAgIGlmIChLSU5EID09PSBERUZBVUxUICYmIGRlZmF1bHRJdGVyYXRvcikgcmV0dXJuIGRlZmF1bHRJdGVyYXRvcjtcbiAgICBpZiAoIUJVR0dZX1NBRkFSSV9JVEVSQVRPUlMgJiYgS0lORCBpbiBJdGVyYWJsZVByb3RvdHlwZSkgcmV0dXJuIEl0ZXJhYmxlUHJvdG90eXBlW0tJTkRdO1xuICAgIHN3aXRjaCAoS0lORCkge1xuICAgICAgY2FzZSBLRVlTOiByZXR1cm4gZnVuY3Rpb24ga2V5cygpIHsgcmV0dXJuIG5ldyBJdGVyYXRvckNvbnN0cnVjdG9yKHRoaXMsIEtJTkQpOyB9O1xuICAgICAgY2FzZSBWQUxVRVM6IHJldHVybiBmdW5jdGlvbiB2YWx1ZXMoKSB7IHJldHVybiBuZXcgSXRlcmF0b3JDb25zdHJ1Y3Rvcih0aGlzLCBLSU5EKTsgfTtcbiAgICAgIGNhc2UgRU5UUklFUzogcmV0dXJuIGZ1bmN0aW9uIGVudHJpZXMoKSB7IHJldHVybiBuZXcgSXRlcmF0b3JDb25zdHJ1Y3Rvcih0aGlzLCBLSU5EKTsgfTtcbiAgICB9IHJldHVybiBmdW5jdGlvbiAoKSB7IHJldHVybiBuZXcgSXRlcmF0b3JDb25zdHJ1Y3Rvcih0aGlzKTsgfTtcbiAgfTtcblxuICB2YXIgVE9fU1RSSU5HX1RBRyA9IE5BTUUgKyAnIEl0ZXJhdG9yJztcbiAgdmFyIElOQ09SUkVDVF9WQUxVRVNfTkFNRSA9IGZhbHNlO1xuICB2YXIgSXRlcmFibGVQcm90b3R5cGUgPSBJdGVyYWJsZS5wcm90b3R5cGU7XG4gIHZhciBuYXRpdmVJdGVyYXRvciA9IEl0ZXJhYmxlUHJvdG90eXBlW0lURVJBVE9SXVxuICAgIHx8IEl0ZXJhYmxlUHJvdG90eXBlWydAQGl0ZXJhdG9yJ11cbiAgICB8fCBERUZBVUxUICYmIEl0ZXJhYmxlUHJvdG90eXBlW0RFRkFVTFRdO1xuICB2YXIgZGVmYXVsdEl0ZXJhdG9yID0gIUJVR0dZX1NBRkFSSV9JVEVSQVRPUlMgJiYgbmF0aXZlSXRlcmF0b3IgfHwgZ2V0SXRlcmF0aW9uTWV0aG9kKERFRkFVTFQpO1xuICB2YXIgYW55TmF0aXZlSXRlcmF0b3IgPSBOQU1FID09ICdBcnJheScgPyBJdGVyYWJsZVByb3RvdHlwZS5lbnRyaWVzIHx8IG5hdGl2ZUl0ZXJhdG9yIDogbmF0aXZlSXRlcmF0b3I7XG4gIHZhciBDdXJyZW50SXRlcmF0b3JQcm90b3R5cGUsIG1ldGhvZHMsIEtFWTtcblxuICAvLyBmaXggbmF0aXZlXG4gIGlmIChhbnlOYXRpdmVJdGVyYXRvcikge1xuICAgIEN1cnJlbnRJdGVyYXRvclByb3RvdHlwZSA9IGdldFByb3RvdHlwZU9mKGFueU5hdGl2ZUl0ZXJhdG9yLmNhbGwobmV3IEl0ZXJhYmxlKCkpKTtcbiAgICBpZiAoSXRlcmF0b3JQcm90b3R5cGUgIT09IE9iamVjdC5wcm90b3R5cGUgJiYgQ3VycmVudEl0ZXJhdG9yUHJvdG90eXBlLm5leHQpIHtcbiAgICAgIGlmICghSVNfUFVSRSAmJiBnZXRQcm90b3R5cGVPZihDdXJyZW50SXRlcmF0b3JQcm90b3R5cGUpICE9PSBJdGVyYXRvclByb3RvdHlwZSkge1xuICAgICAgICBpZiAoc2V0UHJvdG90eXBlT2YpIHtcbiAgICAgICAgICBzZXRQcm90b3R5cGVPZihDdXJyZW50SXRlcmF0b3JQcm90b3R5cGUsIEl0ZXJhdG9yUHJvdG90eXBlKTtcbiAgICAgICAgfSBlbHNlIGlmICh0eXBlb2YgQ3VycmVudEl0ZXJhdG9yUHJvdG90eXBlW0lURVJBVE9SXSAhPSAnZnVuY3Rpb24nKSB7XG4gICAgICAgICAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KEN1cnJlbnRJdGVyYXRvclByb3RvdHlwZSwgSVRFUkFUT1IsIHJldHVyblRoaXMpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICAvLyBTZXQgQEB0b1N0cmluZ1RhZyB0byBuYXRpdmUgaXRlcmF0b3JzXG4gICAgICBzZXRUb1N0cmluZ1RhZyhDdXJyZW50SXRlcmF0b3JQcm90b3R5cGUsIFRPX1NUUklOR19UQUcsIHRydWUsIHRydWUpO1xuICAgICAgaWYgKElTX1BVUkUpIEl0ZXJhdG9yc1tUT19TVFJJTkdfVEFHXSA9IHJldHVyblRoaXM7XG4gICAgfVxuICB9XG5cbiAgLy8gZml4IEFycmF5LnByb3RvdHlwZS57IHZhbHVlcywgQEBpdGVyYXRvciB9Lm5hbWUgaW4gVjggLyBGRlxuICBpZiAoREVGQVVMVCA9PSBWQUxVRVMgJiYgbmF0aXZlSXRlcmF0b3IgJiYgbmF0aXZlSXRlcmF0b3IubmFtZSAhPT0gVkFMVUVTKSB7XG4gICAgSU5DT1JSRUNUX1ZBTFVFU19OQU1FID0gdHJ1ZTtcbiAgICBkZWZhdWx0SXRlcmF0b3IgPSBmdW5jdGlvbiB2YWx1ZXMoKSB7IHJldHVybiBuYXRpdmVJdGVyYXRvci5jYWxsKHRoaXMpOyB9O1xuICB9XG5cbiAgLy8gZGVmaW5lIGl0ZXJhdG9yXG4gIGlmICgoIUlTX1BVUkUgfHwgRk9SQ0VEKSAmJiBJdGVyYWJsZVByb3RvdHlwZVtJVEVSQVRPUl0gIT09IGRlZmF1bHRJdGVyYXRvcikge1xuICAgIGNyZWF0ZU5vbkVudW1lcmFibGVQcm9wZXJ0eShJdGVyYWJsZVByb3RvdHlwZSwgSVRFUkFUT1IsIGRlZmF1bHRJdGVyYXRvcik7XG4gIH1cbiAgSXRlcmF0b3JzW05BTUVdID0gZGVmYXVsdEl0ZXJhdG9yO1xuXG4gIC8vIGV4cG9ydCBhZGRpdGlvbmFsIG1ldGhvZHNcbiAgaWYgKERFRkFVTFQpIHtcbiAgICBtZXRob2RzID0ge1xuICAgICAgdmFsdWVzOiBnZXRJdGVyYXRpb25NZXRob2QoVkFMVUVTKSxcbiAgICAgIGtleXM6IElTX1NFVCA/IGRlZmF1bHRJdGVyYXRvciA6IGdldEl0ZXJhdGlvbk1ldGhvZChLRVlTKSxcbiAgICAgIGVudHJpZXM6IGdldEl0ZXJhdGlvbk1ldGhvZChFTlRSSUVTKVxuICAgIH07XG4gICAgaWYgKEZPUkNFRCkgZm9yIChLRVkgaW4gbWV0aG9kcykge1xuICAgICAgaWYgKEJVR0dZX1NBRkFSSV9JVEVSQVRPUlMgfHwgSU5DT1JSRUNUX1ZBTFVFU19OQU1FIHx8ICEoS0VZIGluIEl0ZXJhYmxlUHJvdG90eXBlKSkge1xuICAgICAgICByZWRlZmluZShJdGVyYWJsZVByb3RvdHlwZSwgS0VZLCBtZXRob2RzW0tFWV0pO1xuICAgICAgfVxuICAgIH0gZWxzZSAkKHsgdGFyZ2V0OiBOQU1FLCBwcm90bzogdHJ1ZSwgZm9yY2VkOiBCVUdHWV9TQUZBUklfSVRFUkFUT1JTIHx8IElOQ09SUkVDVF9WQUxVRVNfTkFNRSB9LCBtZXRob2RzKTtcbiAgfVxuXG4gIHJldHVybiBtZXRob2RzO1xufTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgdG9JbmRleGVkT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWluZGV4ZWQtb2JqZWN0Jyk7XG52YXIgYWRkVG9VbnNjb3BhYmxlcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hZGQtdG8tdW5zY29wYWJsZXMnKTtcbnZhciBJdGVyYXRvcnMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXRlcmF0b3JzJyk7XG52YXIgSW50ZXJuYWxTdGF0ZU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pbnRlcm5hbC1zdGF0ZScpO1xudmFyIGRlZmluZUl0ZXJhdG9yID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2RlZmluZS1pdGVyYXRvcicpO1xuXG52YXIgQVJSQVlfSVRFUkFUT1IgPSAnQXJyYXkgSXRlcmF0b3InO1xudmFyIHNldEludGVybmFsU3RhdGUgPSBJbnRlcm5hbFN0YXRlTW9kdWxlLnNldDtcbnZhciBnZXRJbnRlcm5hbFN0YXRlID0gSW50ZXJuYWxTdGF0ZU1vZHVsZS5nZXR0ZXJGb3IoQVJSQVlfSVRFUkFUT1IpO1xuXG4vLyBgQXJyYXkucHJvdG90eXBlLmVudHJpZXNgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuZW50cmllc1xuLy8gYEFycmF5LnByb3RvdHlwZS5rZXlzYCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLmtleXNcbi8vIGBBcnJheS5wcm90b3R5cGUudmFsdWVzYCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLnZhbHVlc1xuLy8gYEFycmF5LnByb3RvdHlwZVtAQGl0ZXJhdG9yXWAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWFycmF5LnByb3RvdHlwZS1AQGl0ZXJhdG9yXG4vLyBgQ3JlYXRlQXJyYXlJdGVyYXRvcmAgaW50ZXJuYWwgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWNyZWF0ZWFycmF5aXRlcmF0b3Jcbm1vZHVsZS5leHBvcnRzID0gZGVmaW5lSXRlcmF0b3IoQXJyYXksICdBcnJheScsIGZ1bmN0aW9uIChpdGVyYXRlZCwga2luZCkge1xuICBzZXRJbnRlcm5hbFN0YXRlKHRoaXMsIHtcbiAgICB0eXBlOiBBUlJBWV9JVEVSQVRPUixcbiAgICB0YXJnZXQ6IHRvSW5kZXhlZE9iamVjdChpdGVyYXRlZCksIC8vIHRhcmdldFxuICAgIGluZGV4OiAwLCAgICAgICAgICAgICAgICAgICAgICAgICAgLy8gbmV4dCBpbmRleFxuICAgIGtpbmQ6IGtpbmQgICAgICAgICAgICAgICAgICAgICAgICAgLy8ga2luZFxuICB9KTtcbi8vIGAlQXJyYXlJdGVyYXRvclByb3RvdHlwZSUubmV4dGAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLSVhcnJheWl0ZXJhdG9ycHJvdG90eXBlJS5uZXh0XG59LCBmdW5jdGlvbiAoKSB7XG4gIHZhciBzdGF0ZSA9IGdldEludGVybmFsU3RhdGUodGhpcyk7XG4gIHZhciB0YXJnZXQgPSBzdGF0ZS50YXJnZXQ7XG4gIHZhciBraW5kID0gc3RhdGUua2luZDtcbiAgdmFyIGluZGV4ID0gc3RhdGUuaW5kZXgrKztcbiAgaWYgKCF0YXJnZXQgfHwgaW5kZXggPj0gdGFyZ2V0Lmxlbmd0aCkge1xuICAgIHN0YXRlLnRhcmdldCA9IHVuZGVmaW5lZDtcbiAgICByZXR1cm4geyB2YWx1ZTogdW5kZWZpbmVkLCBkb25lOiB0cnVlIH07XG4gIH1cbiAgaWYgKGtpbmQgPT0gJ2tleXMnKSByZXR1cm4geyB2YWx1ZTogaW5kZXgsIGRvbmU6IGZhbHNlIH07XG4gIGlmIChraW5kID09ICd2YWx1ZXMnKSByZXR1cm4geyB2YWx1ZTogdGFyZ2V0W2luZGV4XSwgZG9uZTogZmFsc2UgfTtcbiAgcmV0dXJuIHsgdmFsdWU6IFtpbmRleCwgdGFyZ2V0W2luZGV4XV0sIGRvbmU6IGZhbHNlIH07XG59LCAndmFsdWVzJyk7XG5cbi8vIGFyZ3VtZW50c0xpc3RbQEBpdGVyYXRvcl0gaXMgJUFycmF5UHJvdG9fdmFsdWVzJVxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1jcmVhdGV1bm1hcHBlZGFyZ3VtZW50c29iamVjdFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1jcmVhdGVtYXBwZWRhcmd1bWVudHNvYmplY3Rcbkl0ZXJhdG9ycy5Bcmd1bWVudHMgPSBJdGVyYXRvcnMuQXJyYXk7XG5cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLUBAdW5zY29wYWJsZXNcbmFkZFRvVW5zY29wYWJsZXMoJ2tleXMnKTtcbmFkZFRvVW5zY29wYWJsZXMoJ3ZhbHVlcycpO1xuYWRkVG9VbnNjb3BhYmxlcygnZW50cmllcycpO1xuIiwgInZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xuXG5tb2R1bGUuZXhwb3J0cyA9ICFmYWlscyhmdW5jdGlvbiAoKSB7XG4gIC8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBlcy9uby1vYmplY3QtaXNleHRlbnNpYmxlLCBlcy9uby1vYmplY3QtcHJldmVudGV4dGVuc2lvbnMgLS0gcmVxdWlyZWQgZm9yIHRlc3RpbmdcbiAgcmV0dXJuIE9iamVjdC5pc0V4dGVuc2libGUoT2JqZWN0LnByZXZlbnRFeHRlbnNpb25zKHt9KSk7XG59KTtcbiIsICJ2YXIgaGlkZGVuS2V5cyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oaWRkZW4ta2V5cycpO1xudmFyIGlzT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLW9iamVjdCcpO1xudmFyIGhhcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oYXMnKTtcbnZhciBkZWZpbmVQcm9wZXJ0eSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZGVmaW5lLXByb3BlcnR5JykuZjtcbnZhciB1aWQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdWlkJyk7XG52YXIgRlJFRVpJTkcgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZnJlZXppbmcnKTtcblxudmFyIE1FVEFEQVRBID0gdWlkKCdtZXRhJyk7XG52YXIgaWQgPSAwO1xuXG4vLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgZXMvbm8tb2JqZWN0LWlzZXh0ZW5zaWJsZSAtLSBzYWZlXG52YXIgaXNFeHRlbnNpYmxlID0gT2JqZWN0LmlzRXh0ZW5zaWJsZSB8fCBmdW5jdGlvbiAoKSB7XG4gIHJldHVybiB0cnVlO1xufTtcblxudmFyIHNldE1ldGFkYXRhID0gZnVuY3Rpb24gKGl0KSB7XG4gIGRlZmluZVByb3BlcnR5KGl0LCBNRVRBREFUQSwgeyB2YWx1ZToge1xuICAgIG9iamVjdElEOiAnTycgKyBpZCsrLCAvLyBvYmplY3QgSURcbiAgICB3ZWFrRGF0YToge30gICAgICAgICAgLy8gd2VhayBjb2xsZWN0aW9ucyBJRHNcbiAgfSB9KTtcbn07XG5cbnZhciBmYXN0S2V5ID0gZnVuY3Rpb24gKGl0LCBjcmVhdGUpIHtcbiAgLy8gcmV0dXJuIGEgcHJpbWl0aXZlIHdpdGggcHJlZml4XG4gIGlmICghaXNPYmplY3QoaXQpKSByZXR1cm4gdHlwZW9mIGl0ID09ICdzeW1ib2wnID8gaXQgOiAodHlwZW9mIGl0ID09ICdzdHJpbmcnID8gJ1MnIDogJ1AnKSArIGl0O1xuICBpZiAoIWhhcyhpdCwgTUVUQURBVEEpKSB7XG4gICAgLy8gY2FuJ3Qgc2V0IG1ldGFkYXRhIHRvIHVuY2F1Z2h0IGZyb3plbiBvYmplY3RcbiAgICBpZiAoIWlzRXh0ZW5zaWJsZShpdCkpIHJldHVybiAnRic7XG4gICAgLy8gbm90IG5lY2Vzc2FyeSB0byBhZGQgbWV0YWRhdGFcbiAgICBpZiAoIWNyZWF0ZSkgcmV0dXJuICdFJztcbiAgICAvLyBhZGQgbWlzc2luZyBtZXRhZGF0YVxuICAgIHNldE1ldGFkYXRhKGl0KTtcbiAgLy8gcmV0dXJuIG9iamVjdCBJRFxuICB9IHJldHVybiBpdFtNRVRBREFUQV0ub2JqZWN0SUQ7XG59O1xuXG52YXIgZ2V0V2Vha0RhdGEgPSBmdW5jdGlvbiAoaXQsIGNyZWF0ZSkge1xuICBpZiAoIWhhcyhpdCwgTUVUQURBVEEpKSB7XG4gICAgLy8gY2FuJ3Qgc2V0IG1ldGFkYXRhIHRvIHVuY2F1Z2h0IGZyb3plbiBvYmplY3RcbiAgICBpZiAoIWlzRXh0ZW5zaWJsZShpdCkpIHJldHVybiB0cnVlO1xuICAgIC8vIG5vdCBuZWNlc3NhcnkgdG8gYWRkIG1ldGFkYXRhXG4gICAgaWYgKCFjcmVhdGUpIHJldHVybiBmYWxzZTtcbiAgICAvLyBhZGQgbWlzc2luZyBtZXRhZGF0YVxuICAgIHNldE1ldGFkYXRhKGl0KTtcbiAgLy8gcmV0dXJuIHRoZSBzdG9yZSBvZiB3ZWFrIGNvbGxlY3Rpb25zIElEc1xuICB9IHJldHVybiBpdFtNRVRBREFUQV0ud2Vha0RhdGE7XG59O1xuXG4vLyBhZGQgbWV0YWRhdGEgb24gZnJlZXplLWZhbWlseSBtZXRob2RzIGNhbGxpbmdcbnZhciBvbkZyZWV6ZSA9IGZ1bmN0aW9uIChpdCkge1xuICBpZiAoRlJFRVpJTkcgJiYgbWV0YS5SRVFVSVJFRCAmJiBpc0V4dGVuc2libGUoaXQpICYmICFoYXMoaXQsIE1FVEFEQVRBKSkgc2V0TWV0YWRhdGEoaXQpO1xuICByZXR1cm4gaXQ7XG59O1xuXG52YXIgbWV0YSA9IG1vZHVsZS5leHBvcnRzID0ge1xuICBSRVFVSVJFRDogZmFsc2UsXG4gIGZhc3RLZXk6IGZhc3RLZXksXG4gIGdldFdlYWtEYXRhOiBnZXRXZWFrRGF0YSxcbiAgb25GcmVlemU6IG9uRnJlZXplXG59O1xuXG5oaWRkZW5LZXlzW01FVEFEQVRBXSA9IHRydWU7XG4iLCAidmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xudmFyIEl0ZXJhdG9ycyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pdGVyYXRvcnMnKTtcblxudmFyIElURVJBVE9SID0gd2VsbEtub3duU3ltYm9sKCdpdGVyYXRvcicpO1xudmFyIEFycmF5UHJvdG90eXBlID0gQXJyYXkucHJvdG90eXBlO1xuXG4vLyBjaGVjayBvbiBkZWZhdWx0IEFycmF5IGl0ZXJhdG9yXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChpdCkge1xuICByZXR1cm4gaXQgIT09IHVuZGVmaW5lZCAmJiAoSXRlcmF0b3JzLkFycmF5ID09PSBpdCB8fCBBcnJheVByb3RvdHlwZVtJVEVSQVRPUl0gPT09IGl0KTtcbn07XG4iLCAidmFyIGFGdW5jdGlvbiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hLWZ1bmN0aW9uJyk7XG5cbi8vIG9wdGlvbmFsIC8gc2ltcGxlIGNvbnRleHQgYmluZGluZ1xubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoZm4sIHRoYXQsIGxlbmd0aCkge1xuICBhRnVuY3Rpb24oZm4pO1xuICBpZiAodGhhdCA9PT0gdW5kZWZpbmVkKSByZXR1cm4gZm47XG4gIHN3aXRjaCAobGVuZ3RoKSB7XG4gICAgY2FzZSAwOiByZXR1cm4gZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIGZuLmNhbGwodGhhdCk7XG4gICAgfTtcbiAgICBjYXNlIDE6IHJldHVybiBmdW5jdGlvbiAoYSkge1xuICAgICAgcmV0dXJuIGZuLmNhbGwodGhhdCwgYSk7XG4gICAgfTtcbiAgICBjYXNlIDI6IHJldHVybiBmdW5jdGlvbiAoYSwgYikge1xuICAgICAgcmV0dXJuIGZuLmNhbGwodGhhdCwgYSwgYik7XG4gICAgfTtcbiAgICBjYXNlIDM6IHJldHVybiBmdW5jdGlvbiAoYSwgYiwgYykge1xuICAgICAgcmV0dXJuIGZuLmNhbGwodGhhdCwgYSwgYiwgYyk7XG4gICAgfTtcbiAgfVxuICByZXR1cm4gZnVuY3Rpb24gKC8qIC4uLmFyZ3MgKi8pIHtcbiAgICByZXR1cm4gZm4uYXBwbHkodGhhdCwgYXJndW1lbnRzKTtcbiAgfTtcbn07XG4iLCAidmFyIGNsYXNzb2YgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY2xhc3NvZicpO1xudmFyIEl0ZXJhdG9ycyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pdGVyYXRvcnMnKTtcbnZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcblxudmFyIElURVJBVE9SID0gd2VsbEtub3duU3ltYm9sKCdpdGVyYXRvcicpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChpdCkge1xuICBpZiAoaXQgIT0gdW5kZWZpbmVkKSByZXR1cm4gaXRbSVRFUkFUT1JdXG4gICAgfHwgaXRbJ0BAaXRlcmF0b3InXVxuICAgIHx8IEl0ZXJhdG9yc1tjbGFzc29mKGl0KV07XG59O1xuIiwgInZhciBhbk9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hbi1vYmplY3QnKTtcblxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaXRlcmF0b3IpIHtcbiAgdmFyIHJldHVybk1ldGhvZCA9IGl0ZXJhdG9yWydyZXR1cm4nXTtcbiAgaWYgKHJldHVybk1ldGhvZCAhPT0gdW5kZWZpbmVkKSB7XG4gICAgcmV0dXJuIGFuT2JqZWN0KHJldHVybk1ldGhvZC5jYWxsKGl0ZXJhdG9yKSkudmFsdWU7XG4gIH1cbn07XG4iLCAidmFyIGFuT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FuLW9iamVjdCcpO1xudmFyIGlzQXJyYXlJdGVyYXRvck1ldGhvZCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1hcnJheS1pdGVyYXRvci1tZXRob2QnKTtcbnZhciB0b0xlbmd0aCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1sZW5ndGgnKTtcbnZhciBiaW5kID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Z1bmN0aW9uLWJpbmQtY29udGV4dCcpO1xudmFyIGdldEl0ZXJhdG9yTWV0aG9kID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2dldC1pdGVyYXRvci1tZXRob2QnKTtcbnZhciBpdGVyYXRvckNsb3NlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2l0ZXJhdG9yLWNsb3NlJyk7XG5cbnZhciBSZXN1bHQgPSBmdW5jdGlvbiAoc3RvcHBlZCwgcmVzdWx0KSB7XG4gIHRoaXMuc3RvcHBlZCA9IHN0b3BwZWQ7XG4gIHRoaXMucmVzdWx0ID0gcmVzdWx0O1xufTtcblxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaXRlcmFibGUsIHVuYm91bmRGdW5jdGlvbiwgb3B0aW9ucykge1xuICB2YXIgdGhhdCA9IG9wdGlvbnMgJiYgb3B0aW9ucy50aGF0O1xuICB2YXIgQVNfRU5UUklFUyA9ICEhKG9wdGlvbnMgJiYgb3B0aW9ucy5BU19FTlRSSUVTKTtcbiAgdmFyIElTX0lURVJBVE9SID0gISEob3B0aW9ucyAmJiBvcHRpb25zLklTX0lURVJBVE9SKTtcbiAgdmFyIElOVEVSUlVQVEVEID0gISEob3B0aW9ucyAmJiBvcHRpb25zLklOVEVSUlVQVEVEKTtcbiAgdmFyIGZuID0gYmluZCh1bmJvdW5kRnVuY3Rpb24sIHRoYXQsIDEgKyBBU19FTlRSSUVTICsgSU5URVJSVVBURUQpO1xuICB2YXIgaXRlcmF0b3IsIGl0ZXJGbiwgaW5kZXgsIGxlbmd0aCwgcmVzdWx0LCBuZXh0LCBzdGVwO1xuXG4gIHZhciBzdG9wID0gZnVuY3Rpb24gKGNvbmRpdGlvbikge1xuICAgIGlmIChpdGVyYXRvcikgaXRlcmF0b3JDbG9zZShpdGVyYXRvcik7XG4gICAgcmV0dXJuIG5ldyBSZXN1bHQodHJ1ZSwgY29uZGl0aW9uKTtcbiAgfTtcblxuICB2YXIgY2FsbEZuID0gZnVuY3Rpb24gKHZhbHVlKSB7XG4gICAgaWYgKEFTX0VOVFJJRVMpIHtcbiAgICAgIGFuT2JqZWN0KHZhbHVlKTtcbiAgICAgIHJldHVybiBJTlRFUlJVUFRFRCA/IGZuKHZhbHVlWzBdLCB2YWx1ZVsxXSwgc3RvcCkgOiBmbih2YWx1ZVswXSwgdmFsdWVbMV0pO1xuICAgIH0gcmV0dXJuIElOVEVSUlVQVEVEID8gZm4odmFsdWUsIHN0b3ApIDogZm4odmFsdWUpO1xuICB9O1xuXG4gIGlmIChJU19JVEVSQVRPUikge1xuICAgIGl0ZXJhdG9yID0gaXRlcmFibGU7XG4gIH0gZWxzZSB7XG4gICAgaXRlckZuID0gZ2V0SXRlcmF0b3JNZXRob2QoaXRlcmFibGUpO1xuICAgIGlmICh0eXBlb2YgaXRlckZuICE9ICdmdW5jdGlvbicpIHRocm93IFR5cGVFcnJvcignVGFyZ2V0IGlzIG5vdCBpdGVyYWJsZScpO1xuICAgIC8vIG9wdGltaXNhdGlvbiBmb3IgYXJyYXkgaXRlcmF0b3JzXG4gICAgaWYgKGlzQXJyYXlJdGVyYXRvck1ldGhvZChpdGVyRm4pKSB7XG4gICAgICBmb3IgKGluZGV4ID0gMCwgbGVuZ3RoID0gdG9MZW5ndGgoaXRlcmFibGUubGVuZ3RoKTsgbGVuZ3RoID4gaW5kZXg7IGluZGV4KyspIHtcbiAgICAgICAgcmVzdWx0ID0gY2FsbEZuKGl0ZXJhYmxlW2luZGV4XSk7XG4gICAgICAgIGlmIChyZXN1bHQgJiYgcmVzdWx0IGluc3RhbmNlb2YgUmVzdWx0KSByZXR1cm4gcmVzdWx0O1xuICAgICAgfSByZXR1cm4gbmV3IFJlc3VsdChmYWxzZSk7XG4gICAgfVxuICAgIGl0ZXJhdG9yID0gaXRlckZuLmNhbGwoaXRlcmFibGUpO1xuICB9XG5cbiAgbmV4dCA9IGl0ZXJhdG9yLm5leHQ7XG4gIHdoaWxlICghKHN0ZXAgPSBuZXh0LmNhbGwoaXRlcmF0b3IpKS5kb25lKSB7XG4gICAgdHJ5IHtcbiAgICAgIHJlc3VsdCA9IGNhbGxGbihzdGVwLnZhbHVlKTtcbiAgICB9IGNhdGNoIChlcnJvcikge1xuICAgICAgaXRlcmF0b3JDbG9zZShpdGVyYXRvcik7XG4gICAgICB0aHJvdyBlcnJvcjtcbiAgICB9XG4gICAgaWYgKHR5cGVvZiByZXN1bHQgPT0gJ29iamVjdCcgJiYgcmVzdWx0ICYmIHJlc3VsdCBpbnN0YW5jZW9mIFJlc3VsdCkgcmV0dXJuIHJlc3VsdDtcbiAgfSByZXR1cm4gbmV3IFJlc3VsdChmYWxzZSk7XG59O1xuIiwgIm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGl0LCBDb25zdHJ1Y3RvciwgbmFtZSkge1xuICBpZiAoIShpdCBpbnN0YW5jZW9mIENvbnN0cnVjdG9yKSkge1xuICAgIHRocm93IFR5cGVFcnJvcignSW5jb3JyZWN0ICcgKyAobmFtZSA/IG5hbWUgKyAnICcgOiAnJykgKyAnaW52b2NhdGlvbicpO1xuICB9IHJldHVybiBpdDtcbn07XG4iLCAidmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xuXG52YXIgSVRFUkFUT1IgPSB3ZWxsS25vd25TeW1ib2woJ2l0ZXJhdG9yJyk7XG52YXIgU0FGRV9DTE9TSU5HID0gZmFsc2U7XG5cbnRyeSB7XG4gIHZhciBjYWxsZWQgPSAwO1xuICB2YXIgaXRlcmF0b3JXaXRoUmV0dXJuID0ge1xuICAgIG5leHQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB7IGRvbmU6ICEhY2FsbGVkKysgfTtcbiAgICB9LFxuICAgICdyZXR1cm4nOiBmdW5jdGlvbiAoKSB7XG4gICAgICBTQUZFX0NMT1NJTkcgPSB0cnVlO1xuICAgIH1cbiAgfTtcbiAgaXRlcmF0b3JXaXRoUmV0dXJuW0lURVJBVE9SXSA9IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4gdGhpcztcbiAgfTtcbiAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLWFycmF5LWZyb20sIG5vLXRocm93LWxpdGVyYWwgLS0gcmVxdWlyZWQgZm9yIHRlc3RpbmdcbiAgQXJyYXkuZnJvbShpdGVyYXRvcldpdGhSZXR1cm4sIGZ1bmN0aW9uICgpIHsgdGhyb3cgMjsgfSk7XG59IGNhdGNoIChlcnJvcikgeyAvKiBlbXB0eSAqLyB9XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGV4ZWMsIFNLSVBfQ0xPU0lORykge1xuICBpZiAoIVNLSVBfQ0xPU0lORyAmJiAhU0FGRV9DTE9TSU5HKSByZXR1cm4gZmFsc2U7XG4gIHZhciBJVEVSQVRJT05fU1VQUE9SVCA9IGZhbHNlO1xuICB0cnkge1xuICAgIHZhciBvYmplY3QgPSB7fTtcbiAgICBvYmplY3RbSVRFUkFUT1JdID0gZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgICAgIHJldHVybiB7IGRvbmU6IElURVJBVElPTl9TVVBQT1JUID0gdHJ1ZSB9O1xuICAgICAgICB9XG4gICAgICB9O1xuICAgIH07XG4gICAgZXhlYyhvYmplY3QpO1xuICB9IGNhdGNoIChlcnJvcikgeyAvKiBlbXB0eSAqLyB9XG4gIHJldHVybiBJVEVSQVRJT05fU1VQUE9SVDtcbn07XG4iLCAidmFyIGlzT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLW9iamVjdCcpO1xudmFyIHNldFByb3RvdHlwZU9mID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1zZXQtcHJvdG90eXBlLW9mJyk7XG5cbi8vIG1ha2VzIHN1YmNsYXNzaW5nIHdvcmsgY29ycmVjdCBmb3Igd3JhcHBlZCBidWlsdC1pbnNcbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKCR0aGlzLCBkdW1teSwgV3JhcHBlcikge1xuICB2YXIgTmV3VGFyZ2V0LCBOZXdUYXJnZXRQcm90b3R5cGU7XG4gIGlmIChcbiAgICAvLyBpdCBjYW4gd29yayBvbmx5IHdpdGggbmF0aXZlIGBzZXRQcm90b3R5cGVPZmBcbiAgICBzZXRQcm90b3R5cGVPZiAmJlxuICAgIC8vIHdlIGhhdmVuJ3QgY29tcGxldGVseSBjb3JyZWN0IHByZS1FUzYgd2F5IGZvciBnZXR0aW5nIGBuZXcudGFyZ2V0YCwgc28gdXNlIHRoaXNcbiAgICB0eXBlb2YgKE5ld1RhcmdldCA9IGR1bW15LmNvbnN0cnVjdG9yKSA9PSAnZnVuY3Rpb24nICYmXG4gICAgTmV3VGFyZ2V0ICE9PSBXcmFwcGVyICYmXG4gICAgaXNPYmplY3QoTmV3VGFyZ2V0UHJvdG90eXBlID0gTmV3VGFyZ2V0LnByb3RvdHlwZSkgJiZcbiAgICBOZXdUYXJnZXRQcm90b3R5cGUgIT09IFdyYXBwZXIucHJvdG90eXBlXG4gICkgc2V0UHJvdG90eXBlT2YoJHRoaXMsIE5ld1RhcmdldFByb3RvdHlwZSk7XG4gIHJldHVybiAkdGhpcztcbn07XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgZ2xvYmFsID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2dsb2JhbCcpO1xudmFyIGlzRm9yY2VkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLWZvcmNlZCcpO1xudmFyIHJlZGVmaW5lID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3JlZGVmaW5lJyk7XG52YXIgSW50ZXJuYWxNZXRhZGF0YU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pbnRlcm5hbC1tZXRhZGF0YScpO1xudmFyIGl0ZXJhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXRlcmF0ZScpO1xudmFyIGFuSW5zdGFuY2UgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYW4taW5zdGFuY2UnKTtcbnZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcbnZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xudmFyIGNoZWNrQ29ycmVjdG5lc3NPZkl0ZXJhdGlvbiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jaGVjay1jb3JyZWN0bmVzcy1vZi1pdGVyYXRpb24nKTtcbnZhciBzZXRUb1N0cmluZ1RhZyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9zZXQtdG8tc3RyaW5nLXRhZycpO1xudmFyIGluaGVyaXRJZlJlcXVpcmVkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2luaGVyaXQtaWYtcmVxdWlyZWQnKTtcblxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoQ09OU1RSVUNUT1JfTkFNRSwgd3JhcHBlciwgY29tbW9uKSB7XG4gIHZhciBJU19NQVAgPSBDT05TVFJVQ1RPUl9OQU1FLmluZGV4T2YoJ01hcCcpICE9PSAtMTtcbiAgdmFyIElTX1dFQUsgPSBDT05TVFJVQ1RPUl9OQU1FLmluZGV4T2YoJ1dlYWsnKSAhPT0gLTE7XG4gIHZhciBBRERFUiA9IElTX01BUCA/ICdzZXQnIDogJ2FkZCc7XG4gIHZhciBOYXRpdmVDb25zdHJ1Y3RvciA9IGdsb2JhbFtDT05TVFJVQ1RPUl9OQU1FXTtcbiAgdmFyIE5hdGl2ZVByb3RvdHlwZSA9IE5hdGl2ZUNvbnN0cnVjdG9yICYmIE5hdGl2ZUNvbnN0cnVjdG9yLnByb3RvdHlwZTtcbiAgdmFyIENvbnN0cnVjdG9yID0gTmF0aXZlQ29uc3RydWN0b3I7XG4gIHZhciBleHBvcnRlZCA9IHt9O1xuXG4gIHZhciBmaXhNZXRob2QgPSBmdW5jdGlvbiAoS0VZKSB7XG4gICAgdmFyIG5hdGl2ZU1ldGhvZCA9IE5hdGl2ZVByb3RvdHlwZVtLRVldO1xuICAgIHJlZGVmaW5lKE5hdGl2ZVByb3RvdHlwZSwgS0VZLFxuICAgICAgS0VZID09ICdhZGQnID8gZnVuY3Rpb24gYWRkKHZhbHVlKSB7XG4gICAgICAgIG5hdGl2ZU1ldGhvZC5jYWxsKHRoaXMsIHZhbHVlID09PSAwID8gMCA6IHZhbHVlKTtcbiAgICAgICAgcmV0dXJuIHRoaXM7XG4gICAgICB9IDogS0VZID09ICdkZWxldGUnID8gZnVuY3Rpb24gKGtleSkge1xuICAgICAgICByZXR1cm4gSVNfV0VBSyAmJiAhaXNPYmplY3Qoa2V5KSA/IGZhbHNlIDogbmF0aXZlTWV0aG9kLmNhbGwodGhpcywga2V5ID09PSAwID8gMCA6IGtleSk7XG4gICAgICB9IDogS0VZID09ICdnZXQnID8gZnVuY3Rpb24gZ2V0KGtleSkge1xuICAgICAgICByZXR1cm4gSVNfV0VBSyAmJiAhaXNPYmplY3Qoa2V5KSA/IHVuZGVmaW5lZCA6IG5hdGl2ZU1ldGhvZC5jYWxsKHRoaXMsIGtleSA9PT0gMCA/IDAgOiBrZXkpO1xuICAgICAgfSA6IEtFWSA9PSAnaGFzJyA/IGZ1bmN0aW9uIGhhcyhrZXkpIHtcbiAgICAgICAgcmV0dXJuIElTX1dFQUsgJiYgIWlzT2JqZWN0KGtleSkgPyBmYWxzZSA6IG5hdGl2ZU1ldGhvZC5jYWxsKHRoaXMsIGtleSA9PT0gMCA/IDAgOiBrZXkpO1xuICAgICAgfSA6IGZ1bmN0aW9uIHNldChrZXksIHZhbHVlKSB7XG4gICAgICAgIG5hdGl2ZU1ldGhvZC5jYWxsKHRoaXMsIGtleSA9PT0gMCA/IDAgOiBrZXksIHZhbHVlKTtcbiAgICAgICAgcmV0dXJuIHRoaXM7XG4gICAgICB9XG4gICAgKTtcbiAgfTtcblxuICB2YXIgUkVQTEFDRSA9IGlzRm9yY2VkKFxuICAgIENPTlNUUlVDVE9SX05BTUUsXG4gICAgdHlwZW9mIE5hdGl2ZUNvbnN0cnVjdG9yICE9ICdmdW5jdGlvbicgfHwgIShJU19XRUFLIHx8IE5hdGl2ZVByb3RvdHlwZS5mb3JFYWNoICYmICFmYWlscyhmdW5jdGlvbiAoKSB7XG4gICAgICBuZXcgTmF0aXZlQ29uc3RydWN0b3IoKS5lbnRyaWVzKCkubmV4dCgpO1xuICAgIH0pKVxuICApO1xuXG4gIGlmIChSRVBMQUNFKSB7XG4gICAgLy8gY3JlYXRlIGNvbGxlY3Rpb24gY29uc3RydWN0b3JcbiAgICBDb25zdHJ1Y3RvciA9IGNvbW1vbi5nZXRDb25zdHJ1Y3Rvcih3cmFwcGVyLCBDT05TVFJVQ1RPUl9OQU1FLCBJU19NQVAsIEFEREVSKTtcbiAgICBJbnRlcm5hbE1ldGFkYXRhTW9kdWxlLlJFUVVJUkVEID0gdHJ1ZTtcbiAgfSBlbHNlIGlmIChpc0ZvcmNlZChDT05TVFJVQ1RPUl9OQU1FLCB0cnVlKSkge1xuICAgIHZhciBpbnN0YW5jZSA9IG5ldyBDb25zdHJ1Y3RvcigpO1xuICAgIC8vIGVhcmx5IGltcGxlbWVudGF0aW9ucyBub3Qgc3VwcG9ydHMgY2hhaW5pbmdcbiAgICB2YXIgSEFTTlRfQ0hBSU5JTkcgPSBpbnN0YW5jZVtBRERFUl0oSVNfV0VBSyA/IHt9IDogLTAsIDEpICE9IGluc3RhbmNlO1xuICAgIC8vIFY4IH4gQ2hyb21pdW0gNDAtIHdlYWstY29sbGVjdGlvbnMgdGhyb3dzIG9uIHByaW1pdGl2ZXMsIGJ1dCBzaG91bGQgcmV0dXJuIGZhbHNlXG4gICAgdmFyIFRIUk9XU19PTl9QUklNSVRJVkVTID0gZmFpbHMoZnVuY3Rpb24gKCkgeyBpbnN0YW5jZS5oYXMoMSk7IH0pO1xuICAgIC8vIG1vc3QgZWFybHkgaW1wbGVtZW50YXRpb25zIGRvZXNuJ3Qgc3VwcG9ydHMgaXRlcmFibGVzLCBtb3N0IG1vZGVybiAtIG5vdCBjbG9zZSBpdCBjb3JyZWN0bHlcbiAgICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgbm8tbmV3IC0tIHJlcXVpcmVkIGZvciB0ZXN0aW5nXG4gICAgdmFyIEFDQ0VQVF9JVEVSQUJMRVMgPSBjaGVja0NvcnJlY3RuZXNzT2ZJdGVyYXRpb24oZnVuY3Rpb24gKGl0ZXJhYmxlKSB7IG5ldyBOYXRpdmVDb25zdHJ1Y3RvcihpdGVyYWJsZSk7IH0pO1xuICAgIC8vIGZvciBlYXJseSBpbXBsZW1lbnRhdGlvbnMgLTAgYW5kICswIG5vdCB0aGUgc2FtZVxuICAgIHZhciBCVUdHWV9aRVJPID0gIUlTX1dFQUsgJiYgZmFpbHMoZnVuY3Rpb24gKCkge1xuICAgICAgLy8gVjggfiBDaHJvbWl1bSA0Mi0gZmFpbHMgb25seSB3aXRoIDUrIGVsZW1lbnRzXG4gICAgICB2YXIgJGluc3RhbmNlID0gbmV3IE5hdGl2ZUNvbnN0cnVjdG9yKCk7XG4gICAgICB2YXIgaW5kZXggPSA1O1xuICAgICAgd2hpbGUgKGluZGV4LS0pICRpbnN0YW5jZVtBRERFUl0oaW5kZXgsIGluZGV4KTtcbiAgICAgIHJldHVybiAhJGluc3RhbmNlLmhhcygtMCk7XG4gICAgfSk7XG5cbiAgICBpZiAoIUFDQ0VQVF9JVEVSQUJMRVMpIHtcbiAgICAgIENvbnN0cnVjdG9yID0gd3JhcHBlcihmdW5jdGlvbiAoZHVtbXksIGl0ZXJhYmxlKSB7XG4gICAgICAgIGFuSW5zdGFuY2UoZHVtbXksIENvbnN0cnVjdG9yLCBDT05TVFJVQ1RPUl9OQU1FKTtcbiAgICAgICAgdmFyIHRoYXQgPSBpbmhlcml0SWZSZXF1aXJlZChuZXcgTmF0aXZlQ29uc3RydWN0b3IoKSwgZHVtbXksIENvbnN0cnVjdG9yKTtcbiAgICAgICAgaWYgKGl0ZXJhYmxlICE9IHVuZGVmaW5lZCkgaXRlcmF0ZShpdGVyYWJsZSwgdGhhdFtBRERFUl0sIHsgdGhhdDogdGhhdCwgQVNfRU5UUklFUzogSVNfTUFQIH0pO1xuICAgICAgICByZXR1cm4gdGhhdDtcbiAgICAgIH0pO1xuICAgICAgQ29uc3RydWN0b3IucHJvdG90eXBlID0gTmF0aXZlUHJvdG90eXBlO1xuICAgICAgTmF0aXZlUHJvdG90eXBlLmNvbnN0cnVjdG9yID0gQ29uc3RydWN0b3I7XG4gICAgfVxuXG4gICAgaWYgKFRIUk9XU19PTl9QUklNSVRJVkVTIHx8IEJVR0dZX1pFUk8pIHtcbiAgICAgIGZpeE1ldGhvZCgnZGVsZXRlJyk7XG4gICAgICBmaXhNZXRob2QoJ2hhcycpO1xuICAgICAgSVNfTUFQICYmIGZpeE1ldGhvZCgnZ2V0Jyk7XG4gICAgfVxuXG4gICAgaWYgKEJVR0dZX1pFUk8gfHwgSEFTTlRfQ0hBSU5JTkcpIGZpeE1ldGhvZChBRERFUik7XG5cbiAgICAvLyB3ZWFrIGNvbGxlY3Rpb25zIHNob3VsZCBub3QgY29udGFpbnMgLmNsZWFyIG1ldGhvZFxuICAgIGlmIChJU19XRUFLICYmIE5hdGl2ZVByb3RvdHlwZS5jbGVhcikgZGVsZXRlIE5hdGl2ZVByb3RvdHlwZS5jbGVhcjtcbiAgfVxuXG4gIGV4cG9ydGVkW0NPTlNUUlVDVE9SX05BTUVdID0gQ29uc3RydWN0b3I7XG4gICQoeyBnbG9iYWw6IHRydWUsIGZvcmNlZDogQ29uc3RydWN0b3IgIT0gTmF0aXZlQ29uc3RydWN0b3IgfSwgZXhwb3J0ZWQpO1xuXG4gIHNldFRvU3RyaW5nVGFnKENvbnN0cnVjdG9yLCBDT05TVFJVQ1RPUl9OQU1FKTtcblxuICBpZiAoIUlTX1dFQUspIGNvbW1vbi5zZXRTdHJvbmcoQ29uc3RydWN0b3IsIENPTlNUUlVDVE9SX05BTUUsIElTX01BUCk7XG5cbiAgcmV0dXJuIENvbnN0cnVjdG9yO1xufTtcbiIsICJ2YXIgcmVkZWZpbmUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVkZWZpbmUnKTtcblxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAodGFyZ2V0LCBzcmMsIG9wdGlvbnMpIHtcbiAgZm9yICh2YXIga2V5IGluIHNyYykgcmVkZWZpbmUodGFyZ2V0LCBrZXksIHNyY1trZXldLCBvcHRpb25zKTtcbiAgcmV0dXJuIHRhcmdldDtcbn07XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyIGdldEJ1aWx0SW4gPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2V0LWJ1aWx0LWluJyk7XG52YXIgZGVmaW5lUHJvcGVydHlNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0eScpO1xudmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xudmFyIERFU0NSSVBUT1JTID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Rlc2NyaXB0b3JzJyk7XG5cbnZhciBTUEVDSUVTID0gd2VsbEtub3duU3ltYm9sKCdzcGVjaWVzJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKENPTlNUUlVDVE9SX05BTUUpIHtcbiAgdmFyIENvbnN0cnVjdG9yID0gZ2V0QnVpbHRJbihDT05TVFJVQ1RPUl9OQU1FKTtcbiAgdmFyIGRlZmluZVByb3BlcnR5ID0gZGVmaW5lUHJvcGVydHlNb2R1bGUuZjtcblxuICBpZiAoREVTQ1JJUFRPUlMgJiYgQ29uc3RydWN0b3IgJiYgIUNvbnN0cnVjdG9yW1NQRUNJRVNdKSB7XG4gICAgZGVmaW5lUHJvcGVydHkoQ29uc3RydWN0b3IsIFNQRUNJRVMsIHtcbiAgICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZSxcbiAgICAgIGdldDogZnVuY3Rpb24gKCkgeyByZXR1cm4gdGhpczsgfVxuICAgIH0pO1xuICB9XG59O1xuIiwgIid1c2Ugc3RyaWN0JztcbnZhciBkZWZpbmVQcm9wZXJ0eSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZGVmaW5lLXByb3BlcnR5JykuZjtcbnZhciBjcmVhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWNyZWF0ZScpO1xudmFyIHJlZGVmaW5lQWxsID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3JlZGVmaW5lLWFsbCcpO1xudmFyIGJpbmQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZnVuY3Rpb24tYmluZC1jb250ZXh0Jyk7XG52YXIgYW5JbnN0YW5jZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hbi1pbnN0YW5jZScpO1xudmFyIGl0ZXJhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXRlcmF0ZScpO1xudmFyIGRlZmluZUl0ZXJhdG9yID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2RlZmluZS1pdGVyYXRvcicpO1xudmFyIHNldFNwZWNpZXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2V0LXNwZWNpZXMnKTtcbnZhciBERVNDUklQVE9SUyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9kZXNjcmlwdG9ycycpO1xudmFyIGZhc3RLZXkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaW50ZXJuYWwtbWV0YWRhdGEnKS5mYXN0S2V5O1xudmFyIEludGVybmFsU3RhdGVNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaW50ZXJuYWwtc3RhdGUnKTtcblxudmFyIHNldEludGVybmFsU3RhdGUgPSBJbnRlcm5hbFN0YXRlTW9kdWxlLnNldDtcbnZhciBpbnRlcm5hbFN0YXRlR2V0dGVyRm9yID0gSW50ZXJuYWxTdGF0ZU1vZHVsZS5nZXR0ZXJGb3I7XG5cbm1vZHVsZS5leHBvcnRzID0ge1xuICBnZXRDb25zdHJ1Y3RvcjogZnVuY3Rpb24gKHdyYXBwZXIsIENPTlNUUlVDVE9SX05BTUUsIElTX01BUCwgQURERVIpIHtcbiAgICB2YXIgQyA9IHdyYXBwZXIoZnVuY3Rpb24gKHRoYXQsIGl0ZXJhYmxlKSB7XG4gICAgICBhbkluc3RhbmNlKHRoYXQsIEMsIENPTlNUUlVDVE9SX05BTUUpO1xuICAgICAgc2V0SW50ZXJuYWxTdGF0ZSh0aGF0LCB7XG4gICAgICAgIHR5cGU6IENPTlNUUlVDVE9SX05BTUUsXG4gICAgICAgIGluZGV4OiBjcmVhdGUobnVsbCksXG4gICAgICAgIGZpcnN0OiB1bmRlZmluZWQsXG4gICAgICAgIGxhc3Q6IHVuZGVmaW5lZCxcbiAgICAgICAgc2l6ZTogMFxuICAgICAgfSk7XG4gICAgICBpZiAoIURFU0NSSVBUT1JTKSB0aGF0LnNpemUgPSAwO1xuICAgICAgaWYgKGl0ZXJhYmxlICE9IHVuZGVmaW5lZCkgaXRlcmF0ZShpdGVyYWJsZSwgdGhhdFtBRERFUl0sIHsgdGhhdDogdGhhdCwgQVNfRU5UUklFUzogSVNfTUFQIH0pO1xuICAgIH0pO1xuXG4gICAgdmFyIGdldEludGVybmFsU3RhdGUgPSBpbnRlcm5hbFN0YXRlR2V0dGVyRm9yKENPTlNUUlVDVE9SX05BTUUpO1xuXG4gICAgdmFyIGRlZmluZSA9IGZ1bmN0aW9uICh0aGF0LCBrZXksIHZhbHVlKSB7XG4gICAgICB2YXIgc3RhdGUgPSBnZXRJbnRlcm5hbFN0YXRlKHRoYXQpO1xuICAgICAgdmFyIGVudHJ5ID0gZ2V0RW50cnkodGhhdCwga2V5KTtcbiAgICAgIHZhciBwcmV2aW91cywgaW5kZXg7XG4gICAgICAvLyBjaGFuZ2UgZXhpc3RpbmcgZW50cnlcbiAgICAgIGlmIChlbnRyeSkge1xuICAgICAgICBlbnRyeS52YWx1ZSA9IHZhbHVlO1xuICAgICAgLy8gY3JlYXRlIG5ldyBlbnRyeVxuICAgICAgfSBlbHNlIHtcbiAgICAgICAgc3RhdGUubGFzdCA9IGVudHJ5ID0ge1xuICAgICAgICAgIGluZGV4OiBpbmRleCA9IGZhc3RLZXkoa2V5LCB0cnVlKSxcbiAgICAgICAgICBrZXk6IGtleSxcbiAgICAgICAgICB2YWx1ZTogdmFsdWUsXG4gICAgICAgICAgcHJldmlvdXM6IHByZXZpb3VzID0gc3RhdGUubGFzdCxcbiAgICAgICAgICBuZXh0OiB1bmRlZmluZWQsXG4gICAgICAgICAgcmVtb3ZlZDogZmFsc2VcbiAgICAgICAgfTtcbiAgICAgICAgaWYgKCFzdGF0ZS5maXJzdCkgc3RhdGUuZmlyc3QgPSBlbnRyeTtcbiAgICAgICAgaWYgKHByZXZpb3VzKSBwcmV2aW91cy5uZXh0ID0gZW50cnk7XG4gICAgICAgIGlmIChERVNDUklQVE9SUykgc3RhdGUuc2l6ZSsrO1xuICAgICAgICBlbHNlIHRoYXQuc2l6ZSsrO1xuICAgICAgICAvLyBhZGQgdG8gaW5kZXhcbiAgICAgICAgaWYgKGluZGV4ICE9PSAnRicpIHN0YXRlLmluZGV4W2luZGV4XSA9IGVudHJ5O1xuICAgICAgfSByZXR1cm4gdGhhdDtcbiAgICB9O1xuXG4gICAgdmFyIGdldEVudHJ5ID0gZnVuY3Rpb24gKHRoYXQsIGtleSkge1xuICAgICAgdmFyIHN0YXRlID0gZ2V0SW50ZXJuYWxTdGF0ZSh0aGF0KTtcbiAgICAgIC8vIGZhc3QgY2FzZVxuICAgICAgdmFyIGluZGV4ID0gZmFzdEtleShrZXkpO1xuICAgICAgdmFyIGVudHJ5O1xuICAgICAgaWYgKGluZGV4ICE9PSAnRicpIHJldHVybiBzdGF0ZS5pbmRleFtpbmRleF07XG4gICAgICAvLyBmcm96ZW4gb2JqZWN0IGNhc2VcbiAgICAgIGZvciAoZW50cnkgPSBzdGF0ZS5maXJzdDsgZW50cnk7IGVudHJ5ID0gZW50cnkubmV4dCkge1xuICAgICAgICBpZiAoZW50cnkua2V5ID09IGtleSkgcmV0dXJuIGVudHJ5O1xuICAgICAgfVxuICAgIH07XG5cbiAgICByZWRlZmluZUFsbChDLnByb3RvdHlwZSwge1xuICAgICAgLy8gYHsgTWFwLCBTZXQgfS5wcm90b3R5cGUuY2xlYXIoKWAgbWV0aG9kc1xuICAgICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1tYXAucHJvdG90eXBlLmNsZWFyXG4gICAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXNldC5wcm90b3R5cGUuY2xlYXJcbiAgICAgIGNsZWFyOiBmdW5jdGlvbiBjbGVhcigpIHtcbiAgICAgICAgdmFyIHRoYXQgPSB0aGlzO1xuICAgICAgICB2YXIgc3RhdGUgPSBnZXRJbnRlcm5hbFN0YXRlKHRoYXQpO1xuICAgICAgICB2YXIgZGF0YSA9IHN0YXRlLmluZGV4O1xuICAgICAgICB2YXIgZW50cnkgPSBzdGF0ZS5maXJzdDtcbiAgICAgICAgd2hpbGUgKGVudHJ5KSB7XG4gICAgICAgICAgZW50cnkucmVtb3ZlZCA9IHRydWU7XG4gICAgICAgICAgaWYgKGVudHJ5LnByZXZpb3VzKSBlbnRyeS5wcmV2aW91cyA9IGVudHJ5LnByZXZpb3VzLm5leHQgPSB1bmRlZmluZWQ7XG4gICAgICAgICAgZGVsZXRlIGRhdGFbZW50cnkuaW5kZXhdO1xuICAgICAgICAgIGVudHJ5ID0gZW50cnkubmV4dDtcbiAgICAgICAgfVxuICAgICAgICBzdGF0ZS5maXJzdCA9IHN0YXRlLmxhc3QgPSB1bmRlZmluZWQ7XG4gICAgICAgIGlmIChERVNDUklQVE9SUykgc3RhdGUuc2l6ZSA9IDA7XG4gICAgICAgIGVsc2UgdGhhdC5zaXplID0gMDtcbiAgICAgIH0sXG4gICAgICAvLyBgeyBNYXAsIFNldCB9LnByb3RvdHlwZS5kZWxldGUoa2V5KWAgbWV0aG9kc1xuICAgICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1tYXAucHJvdG90eXBlLmRlbGV0ZVxuICAgICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zZXQucHJvdG90eXBlLmRlbGV0ZVxuICAgICAgJ2RlbGV0ZSc6IGZ1bmN0aW9uIChrZXkpIHtcbiAgICAgICAgdmFyIHRoYXQgPSB0aGlzO1xuICAgICAgICB2YXIgc3RhdGUgPSBnZXRJbnRlcm5hbFN0YXRlKHRoYXQpO1xuICAgICAgICB2YXIgZW50cnkgPSBnZXRFbnRyeSh0aGF0LCBrZXkpO1xuICAgICAgICBpZiAoZW50cnkpIHtcbiAgICAgICAgICB2YXIgbmV4dCA9IGVudHJ5Lm5leHQ7XG4gICAgICAgICAgdmFyIHByZXYgPSBlbnRyeS5wcmV2aW91cztcbiAgICAgICAgICBkZWxldGUgc3RhdGUuaW5kZXhbZW50cnkuaW5kZXhdO1xuICAgICAgICAgIGVudHJ5LnJlbW92ZWQgPSB0cnVlO1xuICAgICAgICAgIGlmIChwcmV2KSBwcmV2Lm5leHQgPSBuZXh0O1xuICAgICAgICAgIGlmIChuZXh0KSBuZXh0LnByZXZpb3VzID0gcHJldjtcbiAgICAgICAgICBpZiAoc3RhdGUuZmlyc3QgPT0gZW50cnkpIHN0YXRlLmZpcnN0ID0gbmV4dDtcbiAgICAgICAgICBpZiAoc3RhdGUubGFzdCA9PSBlbnRyeSkgc3RhdGUubGFzdCA9IHByZXY7XG4gICAgICAgICAgaWYgKERFU0NSSVBUT1JTKSBzdGF0ZS5zaXplLS07XG4gICAgICAgICAgZWxzZSB0aGF0LnNpemUtLTtcbiAgICAgICAgfSByZXR1cm4gISFlbnRyeTtcbiAgICAgIH0sXG4gICAgICAvLyBgeyBNYXAsIFNldCB9LnByb3RvdHlwZS5mb3JFYWNoKGNhbGxiYWNrZm4sIHRoaXNBcmcgPSB1bmRlZmluZWQpYCBtZXRob2RzXG4gICAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC5wcm90b3R5cGUuZm9yZWFjaFxuICAgICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zZXQucHJvdG90eXBlLmZvcmVhY2hcbiAgICAgIGZvckVhY2g6IGZ1bmN0aW9uIGZvckVhY2goY2FsbGJhY2tmbiAvKiAsIHRoYXQgPSB1bmRlZmluZWQgKi8pIHtcbiAgICAgICAgdmFyIHN0YXRlID0gZ2V0SW50ZXJuYWxTdGF0ZSh0aGlzKTtcbiAgICAgICAgdmFyIGJvdW5kRnVuY3Rpb24gPSBiaW5kKGNhbGxiYWNrZm4sIGFyZ3VtZW50cy5sZW5ndGggPiAxID8gYXJndW1lbnRzWzFdIDogdW5kZWZpbmVkLCAzKTtcbiAgICAgICAgdmFyIGVudHJ5O1xuICAgICAgICB3aGlsZSAoZW50cnkgPSBlbnRyeSA/IGVudHJ5Lm5leHQgOiBzdGF0ZS5maXJzdCkge1xuICAgICAgICAgIGJvdW5kRnVuY3Rpb24oZW50cnkudmFsdWUsIGVudHJ5LmtleSwgdGhpcyk7XG4gICAgICAgICAgLy8gcmV2ZXJ0IHRvIHRoZSBsYXN0IGV4aXN0aW5nIGVudHJ5XG4gICAgICAgICAgd2hpbGUgKGVudHJ5ICYmIGVudHJ5LnJlbW92ZWQpIGVudHJ5ID0gZW50cnkucHJldmlvdXM7XG4gICAgICAgIH1cbiAgICAgIH0sXG4gICAgICAvLyBgeyBNYXAsIFNldH0ucHJvdG90eXBlLmhhcyhrZXkpYCBtZXRob2RzXG4gICAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC5wcm90b3R5cGUuaGFzXG4gICAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXNldC5wcm90b3R5cGUuaGFzXG4gICAgICBoYXM6IGZ1bmN0aW9uIGhhcyhrZXkpIHtcbiAgICAgICAgcmV0dXJuICEhZ2V0RW50cnkodGhpcywga2V5KTtcbiAgICAgIH1cbiAgICB9KTtcblxuICAgIHJlZGVmaW5lQWxsKEMucHJvdG90eXBlLCBJU19NQVAgPyB7XG4gICAgICAvLyBgTWFwLnByb3RvdHlwZS5nZXQoa2V5KWAgbWV0aG9kXG4gICAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC5wcm90b3R5cGUuZ2V0XG4gICAgICBnZXQ6IGZ1bmN0aW9uIGdldChrZXkpIHtcbiAgICAgICAgdmFyIGVudHJ5ID0gZ2V0RW50cnkodGhpcywga2V5KTtcbiAgICAgICAgcmV0dXJuIGVudHJ5ICYmIGVudHJ5LnZhbHVlO1xuICAgICAgfSxcbiAgICAgIC8vIGBNYXAucHJvdG90eXBlLnNldChrZXksIHZhbHVlKWAgbWV0aG9kXG4gICAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC5wcm90b3R5cGUuc2V0XG4gICAgICBzZXQ6IGZ1bmN0aW9uIHNldChrZXksIHZhbHVlKSB7XG4gICAgICAgIHJldHVybiBkZWZpbmUodGhpcywga2V5ID09PSAwID8gMCA6IGtleSwgdmFsdWUpO1xuICAgICAgfVxuICAgIH0gOiB7XG4gICAgICAvLyBgU2V0LnByb3RvdHlwZS5hZGQodmFsdWUpYCBtZXRob2RcbiAgICAgIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtc2V0LnByb3RvdHlwZS5hZGRcbiAgICAgIGFkZDogZnVuY3Rpb24gYWRkKHZhbHVlKSB7XG4gICAgICAgIHJldHVybiBkZWZpbmUodGhpcywgdmFsdWUgPSB2YWx1ZSA9PT0gMCA/IDAgOiB2YWx1ZSwgdmFsdWUpO1xuICAgICAgfVxuICAgIH0pO1xuICAgIGlmIChERVNDUklQVE9SUykgZGVmaW5lUHJvcGVydHkoQy5wcm90b3R5cGUsICdzaXplJywge1xuICAgICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICAgIHJldHVybiBnZXRJbnRlcm5hbFN0YXRlKHRoaXMpLnNpemU7XG4gICAgICB9XG4gICAgfSk7XG4gICAgcmV0dXJuIEM7XG4gIH0sXG4gIHNldFN0cm9uZzogZnVuY3Rpb24gKEMsIENPTlNUUlVDVE9SX05BTUUsIElTX01BUCkge1xuICAgIHZhciBJVEVSQVRPUl9OQU1FID0gQ09OU1RSVUNUT1JfTkFNRSArICcgSXRlcmF0b3InO1xuICAgIHZhciBnZXRJbnRlcm5hbENvbGxlY3Rpb25TdGF0ZSA9IGludGVybmFsU3RhdGVHZXR0ZXJGb3IoQ09OU1RSVUNUT1JfTkFNRSk7XG4gICAgdmFyIGdldEludGVybmFsSXRlcmF0b3JTdGF0ZSA9IGludGVybmFsU3RhdGVHZXR0ZXJGb3IoSVRFUkFUT1JfTkFNRSk7XG4gICAgLy8gYHsgTWFwLCBTZXQgfS5wcm90b3R5cGUueyBrZXlzLCB2YWx1ZXMsIGVudHJpZXMsIEBAaXRlcmF0b3IgfSgpYCBtZXRob2RzXG4gICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1tYXAucHJvdG90eXBlLmVudHJpZXNcbiAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC5wcm90b3R5cGUua2V5c1xuICAgIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtbWFwLnByb3RvdHlwZS52YWx1ZXNcbiAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC5wcm90b3R5cGUtQEBpdGVyYXRvclxuICAgIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtc2V0LnByb3RvdHlwZS5lbnRyaWVzXG4gICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zZXQucHJvdG90eXBlLmtleXNcbiAgICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXNldC5wcm90b3R5cGUudmFsdWVzXG4gICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zZXQucHJvdG90eXBlLUBAaXRlcmF0b3JcbiAgICBkZWZpbmVJdGVyYXRvcihDLCBDT05TVFJVQ1RPUl9OQU1FLCBmdW5jdGlvbiAoaXRlcmF0ZWQsIGtpbmQpIHtcbiAgICAgIHNldEludGVybmFsU3RhdGUodGhpcywge1xuICAgICAgICB0eXBlOiBJVEVSQVRPUl9OQU1FLFxuICAgICAgICB0YXJnZXQ6IGl0ZXJhdGVkLFxuICAgICAgICBzdGF0ZTogZ2V0SW50ZXJuYWxDb2xsZWN0aW9uU3RhdGUoaXRlcmF0ZWQpLFxuICAgICAgICBraW5kOiBraW5kLFxuICAgICAgICBsYXN0OiB1bmRlZmluZWRcbiAgICAgIH0pO1xuICAgIH0sIGZ1bmN0aW9uICgpIHtcbiAgICAgIHZhciBzdGF0ZSA9IGdldEludGVybmFsSXRlcmF0b3JTdGF0ZSh0aGlzKTtcbiAgICAgIHZhciBraW5kID0gc3RhdGUua2luZDtcbiAgICAgIHZhciBlbnRyeSA9IHN0YXRlLmxhc3Q7XG4gICAgICAvLyByZXZlcnQgdG8gdGhlIGxhc3QgZXhpc3RpbmcgZW50cnlcbiAgICAgIHdoaWxlIChlbnRyeSAmJiBlbnRyeS5yZW1vdmVkKSBlbnRyeSA9IGVudHJ5LnByZXZpb3VzO1xuICAgICAgLy8gZ2V0IG5leHQgZW50cnlcbiAgICAgIGlmICghc3RhdGUudGFyZ2V0IHx8ICEoc3RhdGUubGFzdCA9IGVudHJ5ID0gZW50cnkgPyBlbnRyeS5uZXh0IDogc3RhdGUuc3RhdGUuZmlyc3QpKSB7XG4gICAgICAgIC8vIG9yIGZpbmlzaCB0aGUgaXRlcmF0aW9uXG4gICAgICAgIHN0YXRlLnRhcmdldCA9IHVuZGVmaW5lZDtcbiAgICAgICAgcmV0dXJuIHsgdmFsdWU6IHVuZGVmaW5lZCwgZG9uZTogdHJ1ZSB9O1xuICAgICAgfVxuICAgICAgLy8gcmV0dXJuIHN0ZXAgYnkga2luZFxuICAgICAgaWYgKGtpbmQgPT0gJ2tleXMnKSByZXR1cm4geyB2YWx1ZTogZW50cnkua2V5LCBkb25lOiBmYWxzZSB9O1xuICAgICAgaWYgKGtpbmQgPT0gJ3ZhbHVlcycpIHJldHVybiB7IHZhbHVlOiBlbnRyeS52YWx1ZSwgZG9uZTogZmFsc2UgfTtcbiAgICAgIHJldHVybiB7IHZhbHVlOiBbZW50cnkua2V5LCBlbnRyeS52YWx1ZV0sIGRvbmU6IGZhbHNlIH07XG4gICAgfSwgSVNfTUFQID8gJ2VudHJpZXMnIDogJ3ZhbHVlcycsICFJU19NQVAsIHRydWUpO1xuXG4gICAgLy8gYHsgTWFwLCBTZXQgfS5wcm90b3R5cGVbQEBzcGVjaWVzXWAgYWNjZXNzb3JzXG4gICAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1nZXQtbWFwLUBAc3BlY2llc1xuICAgIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtZ2V0LXNldC1AQHNwZWNpZXNcbiAgICBzZXRTcGVjaWVzKENPTlNUUlVDVE9SX05BTUUpO1xuICB9XG59O1xuIiwgIid1c2Ugc3RyaWN0JztcbnZhciBjb2xsZWN0aW9uID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NvbGxlY3Rpb24nKTtcbnZhciBjb2xsZWN0aW9uU3Ryb25nID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NvbGxlY3Rpb24tc3Ryb25nJyk7XG5cbi8vIGBNYXBgIGNvbnN0cnVjdG9yXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW1hcC1vYmplY3RzXG5tb2R1bGUuZXhwb3J0cyA9IGNvbGxlY3Rpb24oJ01hcCcsIGZ1bmN0aW9uIChpbml0KSB7XG4gIHJldHVybiBmdW5jdGlvbiBNYXAoKSB7IHJldHVybiBpbml0KHRoaXMsIGFyZ3VtZW50cy5sZW5ndGggPyBhcmd1bWVudHNbMF0gOiB1bmRlZmluZWQpOyB9O1xufSwgY29sbGVjdGlvblN0cm9uZyk7XG4iLCAidmFyIHRvSW50ZWdlciA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1pbnRlZ2VyJyk7XG52YXIgcmVxdWlyZU9iamVjdENvZXJjaWJsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9yZXF1aXJlLW9iamVjdC1jb2VyY2libGUnKTtcblxuLy8gYFN0cmluZy5wcm90b3R5cGUueyBjb2RlUG9pbnRBdCwgYXQgfWAgbWV0aG9kcyBpbXBsZW1lbnRhdGlvblxudmFyIGNyZWF0ZU1ldGhvZCA9IGZ1bmN0aW9uIChDT05WRVJUX1RPX1NUUklORykge1xuICByZXR1cm4gZnVuY3Rpb24gKCR0aGlzLCBwb3MpIHtcbiAgICB2YXIgUyA9IFN0cmluZyhyZXF1aXJlT2JqZWN0Q29lcmNpYmxlKCR0aGlzKSk7XG4gICAgdmFyIHBvc2l0aW9uID0gdG9JbnRlZ2VyKHBvcyk7XG4gICAgdmFyIHNpemUgPSBTLmxlbmd0aDtcbiAgICB2YXIgZmlyc3QsIHNlY29uZDtcbiAgICBpZiAocG9zaXRpb24gPCAwIHx8IHBvc2l0aW9uID49IHNpemUpIHJldHVybiBDT05WRVJUX1RPX1NUUklORyA/ICcnIDogdW5kZWZpbmVkO1xuICAgIGZpcnN0ID0gUy5jaGFyQ29kZUF0KHBvc2l0aW9uKTtcbiAgICByZXR1cm4gZmlyc3QgPCAweEQ4MDAgfHwgZmlyc3QgPiAweERCRkYgfHwgcG9zaXRpb24gKyAxID09PSBzaXplXG4gICAgICB8fCAoc2Vjb25kID0gUy5jaGFyQ29kZUF0KHBvc2l0aW9uICsgMSkpIDwgMHhEQzAwIHx8IHNlY29uZCA+IDB4REZGRlxuICAgICAgICA/IENPTlZFUlRfVE9fU1RSSU5HID8gUy5jaGFyQXQocG9zaXRpb24pIDogZmlyc3RcbiAgICAgICAgOiBDT05WRVJUX1RPX1NUUklORyA/IFMuc2xpY2UocG9zaXRpb24sIHBvc2l0aW9uICsgMikgOiAoZmlyc3QgLSAweEQ4MDAgPDwgMTApICsgKHNlY29uZCAtIDB4REMwMCkgKyAweDEwMDAwO1xuICB9O1xufTtcblxubW9kdWxlLmV4cG9ydHMgPSB7XG4gIC8vIGBTdHJpbmcucHJvdG90eXBlLmNvZGVQb2ludEF0YCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zdHJpbmcucHJvdG90eXBlLmNvZGVwb2ludGF0XG4gIGNvZGVBdDogY3JlYXRlTWV0aG9kKGZhbHNlKSxcbiAgLy8gYFN0cmluZy5wcm90b3R5cGUuYXRgIG1ldGhvZFxuICAvLyBodHRwczovL2dpdGh1Yi5jb20vbWF0aGlhc2J5bmVucy9TdHJpbmcucHJvdG90eXBlLmF0XG4gIGNoYXJBdDogY3JlYXRlTWV0aG9kKHRydWUpXG59O1xuIiwgIi8vIGl0ZXJhYmxlIERPTSBjb2xsZWN0aW9uc1xuLy8gZmxhZyAtIGBpdGVyYWJsZWAgaW50ZXJmYWNlIC0gJ2VudHJpZXMnLCAna2V5cycsICd2YWx1ZXMnLCAnZm9yRWFjaCcgbWV0aG9kc1xubW9kdWxlLmV4cG9ydHMgPSB7XG4gIENTU1J1bGVMaXN0OiAwLFxuICBDU1NTdHlsZURlY2xhcmF0aW9uOiAwLFxuICBDU1NWYWx1ZUxpc3Q6IDAsXG4gIENsaWVudFJlY3RMaXN0OiAwLFxuICBET01SZWN0TGlzdDogMCxcbiAgRE9NU3RyaW5nTGlzdDogMCxcbiAgRE9NVG9rZW5MaXN0OiAxLFxuICBEYXRhVHJhbnNmZXJJdGVtTGlzdDogMCxcbiAgRmlsZUxpc3Q6IDAsXG4gIEhUTUxBbGxDb2xsZWN0aW9uOiAwLFxuICBIVE1MQ29sbGVjdGlvbjogMCxcbiAgSFRNTEZvcm1FbGVtZW50OiAwLFxuICBIVE1MU2VsZWN0RWxlbWVudDogMCxcbiAgTWVkaWFMaXN0OiAwLFxuICBNaW1lVHlwZUFycmF5OiAwLFxuICBOYW1lZE5vZGVNYXA6IDAsXG4gIE5vZGVMaXN0OiAxLFxuICBQYWludFJlcXVlc3RMaXN0OiAwLFxuICBQbHVnaW46IDAsXG4gIFBsdWdpbkFycmF5OiAwLFxuICBTVkdMZW5ndGhMaXN0OiAwLFxuICBTVkdOdW1iZXJMaXN0OiAwLFxuICBTVkdQYXRoU2VnTGlzdDogMCxcbiAgU1ZHUG9pbnRMaXN0OiAwLFxuICBTVkdTdHJpbmdMaXN0OiAwLFxuICBTVkdUcmFuc2Zvcm1MaXN0OiAwLFxuICBTb3VyY2VCdWZmZXJMaXN0OiAwLFxuICBTdHlsZVNoZWV0TGlzdDogMCxcbiAgVGV4dFRyYWNrQ3VlTGlzdDogMCxcbiAgVGV4dFRyYWNrTGlzdDogMCxcbiAgVG91Y2hMaXN0OiAwXG59O1xuIiwgInZhciBjbGFzc29mID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NsYXNzb2YtcmF3Jyk7XG5cbi8vIGBJc0FycmF5YCBhYnN0cmFjdCBvcGVyYXRpb25cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtaXNhcnJheVxuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLWFycmF5LWlzYXJyYXkgLS0gc2FmZVxubW9kdWxlLmV4cG9ydHMgPSBBcnJheS5pc0FycmF5IHx8IGZ1bmN0aW9uIGlzQXJyYXkoYXJnKSB7XG4gIHJldHVybiBjbGFzc29mKGFyZykgPT0gJ0FycmF5Jztcbn07XG4iLCAiLyogZXNsaW50LWRpc2FibGUgZXMvbm8tb2JqZWN0LWdldG93bnByb3BlcnR5bmFtZXMgLS0gc2FmZSAqL1xudmFyIHRvSW5kZXhlZE9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1pbmRleGVkLW9iamVjdCcpO1xudmFyICRnZXRPd25Qcm9wZXJ0eU5hbWVzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1nZXQtb3duLXByb3BlcnR5LW5hbWVzJykuZjtcblxudmFyIHRvU3RyaW5nID0ge30udG9TdHJpbmc7XG5cbnZhciB3aW5kb3dOYW1lcyA9IHR5cGVvZiB3aW5kb3cgPT0gJ29iamVjdCcgJiYgd2luZG93ICYmIE9iamVjdC5nZXRPd25Qcm9wZXJ0eU5hbWVzXG4gID8gT2JqZWN0LmdldE93blByb3BlcnR5TmFtZXMod2luZG93KSA6IFtdO1xuXG52YXIgZ2V0V2luZG93TmFtZXMgPSBmdW5jdGlvbiAoaXQpIHtcbiAgdHJ5IHtcbiAgICByZXR1cm4gJGdldE93blByb3BlcnR5TmFtZXMoaXQpO1xuICB9IGNhdGNoIChlcnJvcikge1xuICAgIHJldHVybiB3aW5kb3dOYW1lcy5zbGljZSgpO1xuICB9XG59O1xuXG4vLyBmYWxsYmFjayBmb3IgSUUxMSBidWdneSBPYmplY3QuZ2V0T3duUHJvcGVydHlOYW1lcyB3aXRoIGlmcmFtZSBhbmQgd2luZG93XG5tb2R1bGUuZXhwb3J0cy5mID0gZnVuY3Rpb24gZ2V0T3duUHJvcGVydHlOYW1lcyhpdCkge1xuICByZXR1cm4gd2luZG93TmFtZXMgJiYgdG9TdHJpbmcuY2FsbChpdCkgPT0gJ1tvYmplY3QgV2luZG93XSdcbiAgICA/IGdldFdpbmRvd05hbWVzKGl0KVxuICAgIDogJGdldE93blByb3BlcnR5TmFtZXModG9JbmRleGVkT2JqZWN0KGl0KSk7XG59O1xuIiwgInZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcblxuZXhwb3J0cy5mID0gd2VsbEtub3duU3ltYm9sO1xuIiwgInZhciBwYXRoID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3BhdGgnKTtcbnZhciBoYXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGFzJyk7XG52YXIgd3JhcHBlZFdlbGxLbm93blN5bWJvbE1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbC13cmFwcGVkJyk7XG52YXIgZGVmaW5lUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0eScpLmY7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKE5BTUUpIHtcbiAgdmFyIFN5bWJvbCA9IHBhdGguU3ltYm9sIHx8IChwYXRoLlN5bWJvbCA9IHt9KTtcbiAgaWYgKCFoYXMoU3ltYm9sLCBOQU1FKSkgZGVmaW5lUHJvcGVydHkoU3ltYm9sLCBOQU1FLCB7XG4gICAgdmFsdWU6IHdyYXBwZWRXZWxsS25vd25TeW1ib2xNb2R1bGUuZihOQU1FKVxuICB9KTtcbn07XG4iLCAidmFyIGlzT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLW9iamVjdCcpO1xudmFyIGlzQXJyYXkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtYXJyYXknKTtcbnZhciB3ZWxsS25vd25TeW1ib2wgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wnKTtcblxudmFyIFNQRUNJRVMgPSB3ZWxsS25vd25TeW1ib2woJ3NwZWNpZXMnKTtcblxuLy8gYEFycmF5U3BlY2llc0NyZWF0ZWAgYWJzdHJhY3Qgb3BlcmF0aW9uXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWFycmF5c3BlY2llc2NyZWF0ZVxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAob3JpZ2luYWxBcnJheSwgbGVuZ3RoKSB7XG4gIHZhciBDO1xuICBpZiAoaXNBcnJheShvcmlnaW5hbEFycmF5KSkge1xuICAgIEMgPSBvcmlnaW5hbEFycmF5LmNvbnN0cnVjdG9yO1xuICAgIC8vIGNyb3NzLXJlYWxtIGZhbGxiYWNrXG4gICAgaWYgKHR5cGVvZiBDID09ICdmdW5jdGlvbicgJiYgKEMgPT09IEFycmF5IHx8IGlzQXJyYXkoQy5wcm90b3R5cGUpKSkgQyA9IHVuZGVmaW5lZDtcbiAgICBlbHNlIGlmIChpc09iamVjdChDKSkge1xuICAgICAgQyA9IENbU1BFQ0lFU107XG4gICAgICBpZiAoQyA9PT0gbnVsbCkgQyA9IHVuZGVmaW5lZDtcbiAgICB9XG4gIH0gcmV0dXJuIG5ldyAoQyA9PT0gdW5kZWZpbmVkID8gQXJyYXkgOiBDKShsZW5ndGggPT09IDAgPyAwIDogbGVuZ3RoKTtcbn07XG4iLCAidmFyIGJpbmQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZnVuY3Rpb24tYmluZC1jb250ZXh0Jyk7XG52YXIgSW5kZXhlZE9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pbmRleGVkLW9iamVjdCcpO1xudmFyIHRvT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLW9iamVjdCcpO1xudmFyIHRvTGVuZ3RoID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWxlbmd0aCcpO1xudmFyIGFycmF5U3BlY2llc0NyZWF0ZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hcnJheS1zcGVjaWVzLWNyZWF0ZScpO1xuXG52YXIgcHVzaCA9IFtdLnB1c2g7XG5cbi8vIGBBcnJheS5wcm90b3R5cGUueyBmb3JFYWNoLCBtYXAsIGZpbHRlciwgc29tZSwgZXZlcnksIGZpbmQsIGZpbmRJbmRleCwgZmlsdGVyT3V0IH1gIG1ldGhvZHMgaW1wbGVtZW50YXRpb25cbnZhciBjcmVhdGVNZXRob2QgPSBmdW5jdGlvbiAoVFlQRSkge1xuICB2YXIgSVNfTUFQID0gVFlQRSA9PSAxO1xuICB2YXIgSVNfRklMVEVSID0gVFlQRSA9PSAyO1xuICB2YXIgSVNfU09NRSA9IFRZUEUgPT0gMztcbiAgdmFyIElTX0VWRVJZID0gVFlQRSA9PSA0O1xuICB2YXIgSVNfRklORF9JTkRFWCA9IFRZUEUgPT0gNjtcbiAgdmFyIElTX0ZJTFRFUl9PVVQgPSBUWVBFID09IDc7XG4gIHZhciBOT19IT0xFUyA9IFRZUEUgPT0gNSB8fCBJU19GSU5EX0lOREVYO1xuICByZXR1cm4gZnVuY3Rpb24gKCR0aGlzLCBjYWxsYmFja2ZuLCB0aGF0LCBzcGVjaWZpY0NyZWF0ZSkge1xuICAgIHZhciBPID0gdG9PYmplY3QoJHRoaXMpO1xuICAgIHZhciBzZWxmID0gSW5kZXhlZE9iamVjdChPKTtcbiAgICB2YXIgYm91bmRGdW5jdGlvbiA9IGJpbmQoY2FsbGJhY2tmbiwgdGhhdCwgMyk7XG4gICAgdmFyIGxlbmd0aCA9IHRvTGVuZ3RoKHNlbGYubGVuZ3RoKTtcbiAgICB2YXIgaW5kZXggPSAwO1xuICAgIHZhciBjcmVhdGUgPSBzcGVjaWZpY0NyZWF0ZSB8fCBhcnJheVNwZWNpZXNDcmVhdGU7XG4gICAgdmFyIHRhcmdldCA9IElTX01BUCA/IGNyZWF0ZSgkdGhpcywgbGVuZ3RoKSA6IElTX0ZJTFRFUiB8fCBJU19GSUxURVJfT1VUID8gY3JlYXRlKCR0aGlzLCAwKSA6IHVuZGVmaW5lZDtcbiAgICB2YXIgdmFsdWUsIHJlc3VsdDtcbiAgICBmb3IgKDtsZW5ndGggPiBpbmRleDsgaW5kZXgrKykgaWYgKE5PX0hPTEVTIHx8IGluZGV4IGluIHNlbGYpIHtcbiAgICAgIHZhbHVlID0gc2VsZltpbmRleF07XG4gICAgICByZXN1bHQgPSBib3VuZEZ1bmN0aW9uKHZhbHVlLCBpbmRleCwgTyk7XG4gICAgICBpZiAoVFlQRSkge1xuICAgICAgICBpZiAoSVNfTUFQKSB0YXJnZXRbaW5kZXhdID0gcmVzdWx0OyAvLyBtYXBcbiAgICAgICAgZWxzZSBpZiAocmVzdWx0KSBzd2l0Y2ggKFRZUEUpIHtcbiAgICAgICAgICBjYXNlIDM6IHJldHVybiB0cnVlOyAgICAgICAgICAgICAgLy8gc29tZVxuICAgICAgICAgIGNhc2UgNTogcmV0dXJuIHZhbHVlOyAgICAgICAgICAgICAvLyBmaW5kXG4gICAgICAgICAgY2FzZSA2OiByZXR1cm4gaW5kZXg7ICAgICAgICAgICAgIC8vIGZpbmRJbmRleFxuICAgICAgICAgIGNhc2UgMjogcHVzaC5jYWxsKHRhcmdldCwgdmFsdWUpOyAvLyBmaWx0ZXJcbiAgICAgICAgfSBlbHNlIHN3aXRjaCAoVFlQRSkge1xuICAgICAgICAgIGNhc2UgNDogcmV0dXJuIGZhbHNlOyAgICAgICAgICAgICAvLyBldmVyeVxuICAgICAgICAgIGNhc2UgNzogcHVzaC5jYWxsKHRhcmdldCwgdmFsdWUpOyAvLyBmaWx0ZXJPdXRcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gSVNfRklORF9JTkRFWCA/IC0xIDogSVNfU09NRSB8fCBJU19FVkVSWSA/IElTX0VWRVJZIDogdGFyZ2V0O1xuICB9O1xufTtcblxubW9kdWxlLmV4cG9ydHMgPSB7XG4gIC8vIGBBcnJheS5wcm90b3R5cGUuZm9yRWFjaGAgbWV0aG9kXG4gIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLmZvcmVhY2hcbiAgZm9yRWFjaDogY3JlYXRlTWV0aG9kKDApLFxuICAvLyBgQXJyYXkucHJvdG90eXBlLm1hcGAgbWV0aG9kXG4gIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLm1hcFxuICBtYXA6IGNyZWF0ZU1ldGhvZCgxKSxcbiAgLy8gYEFycmF5LnByb3RvdHlwZS5maWx0ZXJgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWFycmF5LnByb3RvdHlwZS5maWx0ZXJcbiAgZmlsdGVyOiBjcmVhdGVNZXRob2QoMiksXG4gIC8vIGBBcnJheS5wcm90b3R5cGUuc29tZWAgbWV0aG9kXG4gIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkucHJvdG90eXBlLnNvbWVcbiAgc29tZTogY3JlYXRlTWV0aG9kKDMpLFxuICAvLyBgQXJyYXkucHJvdG90eXBlLmV2ZXJ5YCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuZXZlcnlcbiAgZXZlcnk6IGNyZWF0ZU1ldGhvZCg0KSxcbiAgLy8gYEFycmF5LnByb3RvdHlwZS5maW5kYCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuZmluZFxuICBmaW5kOiBjcmVhdGVNZXRob2QoNSksXG4gIC8vIGBBcnJheS5wcm90b3R5cGUuZmluZEluZGV4YCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuZmluZEluZGV4XG4gIGZpbmRJbmRleDogY3JlYXRlTWV0aG9kKDYpLFxuICAvLyBgQXJyYXkucHJvdG90eXBlLmZpbHRlck91dGAgbWV0aG9kXG4gIC8vIGh0dHBzOi8vZ2l0aHViLmNvbS90YzM5L3Byb3Bvc2FsLWFycmF5LWZpbHRlcmluZ1xuICBmaWx0ZXJPdXQ6IGNyZWF0ZU1ldGhvZCg3KVxufTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgJGZvckVhY2ggPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYXJyYXktaXRlcmF0aW9uJykuZm9yRWFjaDtcbnZhciBhcnJheU1ldGhvZElzU3RyaWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FycmF5LW1ldGhvZC1pcy1zdHJpY3QnKTtcblxudmFyIFNUUklDVF9NRVRIT0QgPSBhcnJheU1ldGhvZElzU3RyaWN0KCdmb3JFYWNoJyk7XG5cbi8vIGBBcnJheS5wcm90b3R5cGUuZm9yRWFjaGAgbWV0aG9kIGltcGxlbWVudGF0aW9uXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWFycmF5LnByb3RvdHlwZS5mb3JlYWNoXG5tb2R1bGUuZXhwb3J0cyA9ICFTVFJJQ1RfTUVUSE9EID8gZnVuY3Rpb24gZm9yRWFjaChjYWxsYmFja2ZuIC8qICwgdGhpc0FyZyAqLykge1xuICByZXR1cm4gJGZvckVhY2godGhpcywgY2FsbGJhY2tmbiwgYXJndW1lbnRzLmxlbmd0aCA+IDEgPyBhcmd1bWVudHNbMV0gOiB1bmRlZmluZWQpO1xuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLWFycmF5LXByb3RvdHlwZS1mb3JlYWNoIC0tIHNhZmVcbn0gOiBbXS5mb3JFYWNoO1xuIiwgInZhciBERVNDUklQVE9SUyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9kZXNjcmlwdG9ycycpO1xudmFyIG9iamVjdEtleXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWtleXMnKTtcbnZhciB0b0luZGV4ZWRPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8taW5kZXhlZC1vYmplY3QnKTtcbnZhciBwcm9wZXJ0eUlzRW51bWVyYWJsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtcHJvcGVydHktaXMtZW51bWVyYWJsZScpLmY7XG5cbi8vIGBPYmplY3QueyBlbnRyaWVzLCB2YWx1ZXMgfWAgbWV0aG9kcyBpbXBsZW1lbnRhdGlvblxudmFyIGNyZWF0ZU1ldGhvZCA9IGZ1bmN0aW9uIChUT19FTlRSSUVTKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoaXQpIHtcbiAgICB2YXIgTyA9IHRvSW5kZXhlZE9iamVjdChpdCk7XG4gICAgdmFyIGtleXMgPSBvYmplY3RLZXlzKE8pO1xuICAgIHZhciBsZW5ndGggPSBrZXlzLmxlbmd0aDtcbiAgICB2YXIgaSA9IDA7XG4gICAgdmFyIHJlc3VsdCA9IFtdO1xuICAgIHZhciBrZXk7XG4gICAgd2hpbGUgKGxlbmd0aCA+IGkpIHtcbiAgICAgIGtleSA9IGtleXNbaSsrXTtcbiAgICAgIGlmICghREVTQ1JJUFRPUlMgfHwgcHJvcGVydHlJc0VudW1lcmFibGUuY2FsbChPLCBrZXkpKSB7XG4gICAgICAgIHJlc3VsdC5wdXNoKFRPX0VOVFJJRVMgPyBba2V5LCBPW2tleV1dIDogT1trZXldKTtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIHJlc3VsdDtcbiAgfTtcbn07XG5cbm1vZHVsZS5leHBvcnRzID0ge1xuICAvLyBgT2JqZWN0LmVudHJpZXNgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5lbnRyaWVzXG4gIGVudHJpZXM6IGNyZWF0ZU1ldGhvZCh0cnVlKSxcbiAgLy8gYE9iamVjdC52YWx1ZXNgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC52YWx1ZXNcbiAgdmFsdWVzOiBjcmVhdGVNZXRob2QoZmFsc2UpXG59O1xuIiwgInZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcbnZhciBjbGFzc29mID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NsYXNzb2YtcmF3Jyk7XG52YXIgd2VsbEtub3duU3ltYm9sID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3dlbGwta25vd24tc3ltYm9sJyk7XG5cbnZhciBNQVRDSCA9IHdlbGxLbm93blN5bWJvbCgnbWF0Y2gnKTtcblxuLy8gYElzUmVnRXhwYCBhYnN0cmFjdCBvcGVyYXRpb25cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtaXNyZWdleHBcbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKGl0KSB7XG4gIHZhciBpc1JlZ0V4cDtcbiAgcmV0dXJuIGlzT2JqZWN0KGl0KSAmJiAoKGlzUmVnRXhwID0gaXRbTUFUQ0hdKSAhPT0gdW5kZWZpbmVkID8gISFpc1JlZ0V4cCA6IGNsYXNzb2YoaXQpID09ICdSZWdFeHAnKTtcbn07XG4iLCAidmFyIGlzUmVnRXhwID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLXJlZ2V4cCcpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChpdCkge1xuICBpZiAoaXNSZWdFeHAoaXQpKSB7XG4gICAgdGhyb3cgVHlwZUVycm9yKFwiVGhlIG1ldGhvZCBkb2Vzbid0IGFjY2VwdCByZWd1bGFyIGV4cHJlc3Npb25zXCIpO1xuICB9IHJldHVybiBpdDtcbn07XG4iLCAidmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xuXG52YXIgTUFUQ0ggPSB3ZWxsS25vd25TeW1ib2woJ21hdGNoJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKE1FVEhPRF9OQU1FKSB7XG4gIHZhciByZWdleHAgPSAvLi87XG4gIHRyeSB7XG4gICAgJy8uLydbTUVUSE9EX05BTUVdKHJlZ2V4cCk7XG4gIH0gY2F0Y2ggKGVycm9yMSkge1xuICAgIHRyeSB7XG4gICAgICByZWdleHBbTUFUQ0hdID0gZmFsc2U7XG4gICAgICByZXR1cm4gJy8uLydbTUVUSE9EX05BTUVdKHJlZ2V4cCk7XG4gICAgfSBjYXRjaCAoZXJyb3IyKSB7IC8qIGVtcHR5ICovIH1cbiAgfSByZXR1cm4gZmFsc2U7XG59O1xuIiwgIid1c2Ugc3RyaWN0JztcbnZhciB0b1ByaW1pdGl2ZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1wcmltaXRpdmUnKTtcbnZhciBkZWZpbmVQcm9wZXJ0eU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZGVmaW5lLXByb3BlcnR5Jyk7XG52YXIgY3JlYXRlUHJvcGVydHlEZXNjcmlwdG9yID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1wcm9wZXJ0eS1kZXNjcmlwdG9yJyk7XG5cbm1vZHVsZS5leHBvcnRzID0gZnVuY3Rpb24gKG9iamVjdCwga2V5LCB2YWx1ZSkge1xuICB2YXIgcHJvcGVydHlLZXkgPSB0b1ByaW1pdGl2ZShrZXkpO1xuICBpZiAocHJvcGVydHlLZXkgaW4gb2JqZWN0KSBkZWZpbmVQcm9wZXJ0eU1vZHVsZS5mKG9iamVjdCwgcHJvcGVydHlLZXksIGNyZWF0ZVByb3BlcnR5RGVzY3JpcHRvcigwLCB2YWx1ZSkpO1xuICBlbHNlIG9iamVjdFtwcm9wZXJ0eUtleV0gPSB2YWx1ZTtcbn07XG4iLCAidmFyIGZhaWxzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2ZhaWxzJyk7XG52YXIgd2VsbEtub3duU3ltYm9sID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3dlbGwta25vd24tc3ltYm9sJyk7XG52YXIgVjhfVkVSU0lPTiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9lbmdpbmUtdjgtdmVyc2lvbicpO1xuXG52YXIgU1BFQ0lFUyA9IHdlbGxLbm93blN5bWJvbCgnc3BlY2llcycpO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGZ1bmN0aW9uIChNRVRIT0RfTkFNRSkge1xuICAvLyBXZSBjYW4ndCB1c2UgdGhpcyBmZWF0dXJlIGRldGVjdGlvbiBpbiBWOCBzaW5jZSBpdCBjYXVzZXNcbiAgLy8gZGVvcHRpbWl6YXRpb24gYW5kIHNlcmlvdXMgcGVyZm9ybWFuY2UgZGVncmFkYXRpb25cbiAgLy8gaHR0cHM6Ly9naXRodWIuY29tL3psb2lyb2NrL2NvcmUtanMvaXNzdWVzLzY3N1xuICByZXR1cm4gVjhfVkVSU0lPTiA+PSA1MSB8fCAhZmFpbHMoZnVuY3Rpb24gKCkge1xuICAgIHZhciBhcnJheSA9IFtdO1xuICAgIHZhciBjb25zdHJ1Y3RvciA9IGFycmF5LmNvbnN0cnVjdG9yID0ge307XG4gICAgY29uc3RydWN0b3JbU1BFQ0lFU10gPSBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4geyBmb286IDEgfTtcbiAgICB9O1xuICAgIHJldHVybiBhcnJheVtNRVRIT0RfTkFNRV0oQm9vbGVhbikuZm9vICE9PSAxO1xuICB9KTtcbn07XG4iLCAidmFyIGFuT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FuLW9iamVjdCcpO1xudmFyIGl0ZXJhdG9yQ2xvc2UgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXRlcmF0b3ItY2xvc2UnKTtcblxuLy8gY2FsbCBzb21ldGhpbmcgb24gaXRlcmF0b3Igc3RlcCB3aXRoIHNhZmUgY2xvc2luZyBvbiBlcnJvclxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiAoaXRlcmF0b3IsIGZuLCB2YWx1ZSwgRU5UUklFUykge1xuICB0cnkge1xuICAgIHJldHVybiBFTlRSSUVTID8gZm4oYW5PYmplY3QodmFsdWUpWzBdLCB2YWx1ZVsxXSkgOiBmbih2YWx1ZSk7XG4gIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgaXRlcmF0b3JDbG9zZShpdGVyYXRvcik7XG4gICAgdGhyb3cgZXJyb3I7XG4gIH1cbn07XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyIGJpbmQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZnVuY3Rpb24tYmluZC1jb250ZXh0Jyk7XG52YXIgdG9PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tb2JqZWN0Jyk7XG52YXIgY2FsbFdpdGhTYWZlSXRlcmF0aW9uQ2xvc2luZyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jYWxsLXdpdGgtc2FmZS1pdGVyYXRpb24tY2xvc2luZycpO1xudmFyIGlzQXJyYXlJdGVyYXRvck1ldGhvZCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1hcnJheS1pdGVyYXRvci1tZXRob2QnKTtcbnZhciB0b0xlbmd0aCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1sZW5ndGgnKTtcbnZhciBjcmVhdGVQcm9wZXJ0eSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jcmVhdGUtcHJvcGVydHknKTtcbnZhciBnZXRJdGVyYXRvck1ldGhvZCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nZXQtaXRlcmF0b3ItbWV0aG9kJyk7XG5cbi8vIGBBcnJheS5mcm9tYCBtZXRob2QgaW1wbGVtZW50YXRpb25cbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtYXJyYXkuZnJvbVxubW9kdWxlLmV4cG9ydHMgPSBmdW5jdGlvbiBmcm9tKGFycmF5TGlrZSAvKiAsIG1hcGZuID0gdW5kZWZpbmVkLCB0aGlzQXJnID0gdW5kZWZpbmVkICovKSB7XG4gIHZhciBPID0gdG9PYmplY3QoYXJyYXlMaWtlKTtcbiAgdmFyIEMgPSB0eXBlb2YgdGhpcyA9PSAnZnVuY3Rpb24nID8gdGhpcyA6IEFycmF5O1xuICB2YXIgYXJndW1lbnRzTGVuZ3RoID0gYXJndW1lbnRzLmxlbmd0aDtcbiAgdmFyIG1hcGZuID0gYXJndW1lbnRzTGVuZ3RoID4gMSA/IGFyZ3VtZW50c1sxXSA6IHVuZGVmaW5lZDtcbiAgdmFyIG1hcHBpbmcgPSBtYXBmbiAhPT0gdW5kZWZpbmVkO1xuICB2YXIgaXRlcmF0b3JNZXRob2QgPSBnZXRJdGVyYXRvck1ldGhvZChPKTtcbiAgdmFyIGluZGV4ID0gMDtcbiAgdmFyIGxlbmd0aCwgcmVzdWx0LCBzdGVwLCBpdGVyYXRvciwgbmV4dCwgdmFsdWU7XG4gIGlmIChtYXBwaW5nKSBtYXBmbiA9IGJpbmQobWFwZm4sIGFyZ3VtZW50c0xlbmd0aCA+IDIgPyBhcmd1bWVudHNbMl0gOiB1bmRlZmluZWQsIDIpO1xuICAvLyBpZiB0aGUgdGFyZ2V0IGlzIG5vdCBpdGVyYWJsZSBvciBpdCdzIGFuIGFycmF5IHdpdGggdGhlIGRlZmF1bHQgaXRlcmF0b3IgLSB1c2UgYSBzaW1wbGUgY2FzZVxuICBpZiAoaXRlcmF0b3JNZXRob2QgIT0gdW5kZWZpbmVkICYmICEoQyA9PSBBcnJheSAmJiBpc0FycmF5SXRlcmF0b3JNZXRob2QoaXRlcmF0b3JNZXRob2QpKSkge1xuICAgIGl0ZXJhdG9yID0gaXRlcmF0b3JNZXRob2QuY2FsbChPKTtcbiAgICBuZXh0ID0gaXRlcmF0b3IubmV4dDtcbiAgICByZXN1bHQgPSBuZXcgQygpO1xuICAgIGZvciAoOyEoc3RlcCA9IG5leHQuY2FsbChpdGVyYXRvcikpLmRvbmU7IGluZGV4KyspIHtcbiAgICAgIHZhbHVlID0gbWFwcGluZyA/IGNhbGxXaXRoU2FmZUl0ZXJhdGlvbkNsb3NpbmcoaXRlcmF0b3IsIG1hcGZuLCBbc3RlcC52YWx1ZSwgaW5kZXhdLCB0cnVlKSA6IHN0ZXAudmFsdWU7XG4gICAgICBjcmVhdGVQcm9wZXJ0eShyZXN1bHQsIGluZGV4LCB2YWx1ZSk7XG4gICAgfVxuICB9IGVsc2Uge1xuICAgIGxlbmd0aCA9IHRvTGVuZ3RoKE8ubGVuZ3RoKTtcbiAgICByZXN1bHQgPSBuZXcgQyhsZW5ndGgpO1xuICAgIGZvciAoO2xlbmd0aCA+IGluZGV4OyBpbmRleCsrKSB7XG4gICAgICB2YWx1ZSA9IG1hcHBpbmcgPyBtYXBmbihPW2luZGV4XSwgaW5kZXgpIDogT1tpbmRleF07XG4gICAgICBjcmVhdGVQcm9wZXJ0eShyZXN1bHQsIGluZGV4LCB2YWx1ZSk7XG4gICAgfVxuICB9XG4gIHJlc3VsdC5sZW5ndGggPSBpbmRleDtcbiAgcmV0dXJuIHJlc3VsdDtcbn07XG4iLCAidmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgc2V0UHJvdG90eXBlT2YgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LXNldC1wcm90b3R5cGUtb2YnKTtcblxuLy8gYE9iamVjdC5zZXRQcm90b3R5cGVPZmAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5zZXRwcm90b3R5cGVvZlxuJCh7IHRhcmdldDogJ09iamVjdCcsIHN0YXQ6IHRydWUgfSwge1xuICBzZXRQcm90b3R5cGVPZjogc2V0UHJvdG90eXBlT2Zcbn0pO1xuIiwgInZhciAkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2V4cG9ydCcpO1xudmFyIGZhaWxzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2ZhaWxzJyk7XG52YXIgdG9PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tb2JqZWN0Jyk7XG52YXIgbmF0aXZlR2V0UHJvdG90eXBlT2YgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWdldC1wcm90b3R5cGUtb2YnKTtcbnZhciBDT1JSRUNUX1BST1RPVFlQRV9HRVRURVIgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY29ycmVjdC1wcm90b3R5cGUtZ2V0dGVyJyk7XG5cbnZhciBGQUlMU19PTl9QUklNSVRJVkVTID0gZmFpbHMoZnVuY3Rpb24gKCkgeyBuYXRpdmVHZXRQcm90b3R5cGVPZigxKTsgfSk7XG5cbi8vIGBPYmplY3QuZ2V0UHJvdG90eXBlT2ZgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1vYmplY3QuZ2V0cHJvdG90eXBlb2ZcbiQoeyB0YXJnZXQ6ICdPYmplY3QnLCBzdGF0OiB0cnVlLCBmb3JjZWQ6IEZBSUxTX09OX1BSSU1JVElWRVMsIHNoYW06ICFDT1JSRUNUX1BST1RPVFlQRV9HRVRURVIgfSwge1xuICBnZXRQcm90b3R5cGVPZjogZnVuY3Rpb24gZ2V0UHJvdG90eXBlT2YoaXQpIHtcbiAgICByZXR1cm4gbmF0aXZlR2V0UHJvdG90eXBlT2YodG9PYmplY3QoaXQpKTtcbiAgfVxufSk7XG5cbiIsICIndXNlIHN0cmljdCc7XG4vKiBlc2xpbnQtZGlzYWJsZSBlcy9uby1hcnJheS1wcm90b3R5cGUtaW5kZXhvZiAtLSByZXF1aXJlZCBmb3IgdGVzdGluZyAqL1xudmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgJGluZGV4T2YgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYXJyYXktaW5jbHVkZXMnKS5pbmRleE9mO1xudmFyIGFycmF5TWV0aG9kSXNTdHJpY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYXJyYXktbWV0aG9kLWlzLXN0cmljdCcpO1xuXG52YXIgbmF0aXZlSW5kZXhPZiA9IFtdLmluZGV4T2Y7XG5cbnZhciBORUdBVElWRV9aRVJPID0gISFuYXRpdmVJbmRleE9mICYmIDEgLyBbMV0uaW5kZXhPZigxLCAtMCkgPCAwO1xudmFyIFNUUklDVF9NRVRIT0QgPSBhcnJheU1ldGhvZElzU3RyaWN0KCdpbmRleE9mJyk7XG5cbi8vIGBBcnJheS5wcm90b3R5cGUuaW5kZXhPZmAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWFycmF5LnByb3RvdHlwZS5pbmRleG9mXG4kKHsgdGFyZ2V0OiAnQXJyYXknLCBwcm90bzogdHJ1ZSwgZm9yY2VkOiBORUdBVElWRV9aRVJPIHx8ICFTVFJJQ1RfTUVUSE9EIH0sIHtcbiAgaW5kZXhPZjogZnVuY3Rpb24gaW5kZXhPZihzZWFyY2hFbGVtZW50IC8qICwgZnJvbUluZGV4ID0gMCAqLykge1xuICAgIHJldHVybiBORUdBVElWRV9aRVJPXG4gICAgICAvLyBjb252ZXJ0IC0wIHRvICswXG4gICAgICA/IG5hdGl2ZUluZGV4T2YuYXBwbHkodGhpcywgYXJndW1lbnRzKSB8fCAwXG4gICAgICA6ICRpbmRleE9mKHRoaXMsIHNlYXJjaEVsZW1lbnQsIGFyZ3VtZW50cy5sZW5ndGggPiAxID8gYXJndW1lbnRzWzFdIDogdW5kZWZpbmVkKTtcbiAgfVxufSk7XG4iLCAidmFyIHJlZGVmaW5lID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3JlZGVmaW5lJyk7XG5cbnZhciBEYXRlUHJvdG90eXBlID0gRGF0ZS5wcm90b3R5cGU7XG52YXIgSU5WQUxJRF9EQVRFID0gJ0ludmFsaWQgRGF0ZSc7XG52YXIgVE9fU1RSSU5HID0gJ3RvU3RyaW5nJztcbnZhciBuYXRpdmVEYXRlVG9TdHJpbmcgPSBEYXRlUHJvdG90eXBlW1RPX1NUUklOR107XG52YXIgZ2V0VGltZSA9IERhdGVQcm90b3R5cGUuZ2V0VGltZTtcblxuLy8gYERhdGUucHJvdG90eXBlLnRvU3RyaW5nYCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtZGF0ZS5wcm90b3R5cGUudG9zdHJpbmdcbmlmIChuZXcgRGF0ZShOYU4pICsgJycgIT0gSU5WQUxJRF9EQVRFKSB7XG4gIHJlZGVmaW5lKERhdGVQcm90b3R5cGUsIFRPX1NUUklORywgZnVuY3Rpb24gdG9TdHJpbmcoKSB7XG4gICAgdmFyIHZhbHVlID0gZ2V0VGltZS5jYWxsKHRoaXMpO1xuICAgIC8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBuby1zZWxmLWNvbXBhcmUgLS0gTmFOIGNoZWNrXG4gICAgcmV0dXJuIHZhbHVlID09PSB2YWx1ZSA/IG5hdGl2ZURhdGVUb1N0cmluZy5jYWxsKHRoaXMpIDogSU5WQUxJRF9EQVRFO1xuICB9KTtcbn1cbiIsICJ2YXIgVE9fU1RSSU5HX1RBR19TVVBQT1JUID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLXN0cmluZy10YWctc3VwcG9ydCcpO1xudmFyIHJlZGVmaW5lID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3JlZGVmaW5lJyk7XG52YXIgdG9TdHJpbmcgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LXRvLXN0cmluZycpO1xuXG4vLyBgT2JqZWN0LnByb3RvdHlwZS50b1N0cmluZ2AgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5wcm90b3R5cGUudG9zdHJpbmdcbmlmICghVE9fU1RSSU5HX1RBR19TVVBQT1JUKSB7XG4gIHJlZGVmaW5lKE9iamVjdC5wcm90b3R5cGUsICd0b1N0cmluZycsIHRvU3RyaW5nLCB7IHVuc2FmZTogdHJ1ZSB9KTtcbn1cbiIsICIndXNlIHN0cmljdCc7XG52YXIgcmVkZWZpbmUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVkZWZpbmUnKTtcbnZhciBhbk9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hbi1vYmplY3QnKTtcbnZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xudmFyIGZsYWdzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3JlZ2V4cC1mbGFncycpO1xuXG52YXIgVE9fU1RSSU5HID0gJ3RvU3RyaW5nJztcbnZhciBSZWdFeHBQcm90b3R5cGUgPSBSZWdFeHAucHJvdG90eXBlO1xudmFyIG5hdGl2ZVRvU3RyaW5nID0gUmVnRXhwUHJvdG90eXBlW1RPX1NUUklOR107XG5cbnZhciBOT1RfR0VORVJJQyA9IGZhaWxzKGZ1bmN0aW9uICgpIHsgcmV0dXJuIG5hdGl2ZVRvU3RyaW5nLmNhbGwoeyBzb3VyY2U6ICdhJywgZmxhZ3M6ICdiJyB9KSAhPSAnL2EvYic7IH0pO1xuLy8gRkY0NC0gUmVnRXhwI3RvU3RyaW5nIGhhcyBhIHdyb25nIG5hbWVcbnZhciBJTkNPUlJFQ1RfTkFNRSA9IG5hdGl2ZVRvU3RyaW5nLm5hbWUgIT0gVE9fU1RSSU5HO1xuXG4vLyBgUmVnRXhwLnByb3RvdHlwZS50b1N0cmluZ2AgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXJlZ2V4cC5wcm90b3R5cGUudG9zdHJpbmdcbmlmIChOT1RfR0VORVJJQyB8fCBJTkNPUlJFQ1RfTkFNRSkge1xuICByZWRlZmluZShSZWdFeHAucHJvdG90eXBlLCBUT19TVFJJTkcsIGZ1bmN0aW9uIHRvU3RyaW5nKCkge1xuICAgIHZhciBSID0gYW5PYmplY3QodGhpcyk7XG4gICAgdmFyIHAgPSBTdHJpbmcoUi5zb3VyY2UpO1xuICAgIHZhciByZiA9IFIuZmxhZ3M7XG4gICAgdmFyIGYgPSBTdHJpbmcocmYgPT09IHVuZGVmaW5lZCAmJiBSIGluc3RhbmNlb2YgUmVnRXhwICYmICEoJ2ZsYWdzJyBpbiBSZWdFeHBQcm90b3R5cGUpID8gZmxhZ3MuY2FsbChSKSA6IHJmKTtcbiAgICByZXR1cm4gJy8nICsgcCArICcvJyArIGY7XG4gIH0sIHsgdW5zYWZlOiB0cnVlIH0pO1xufVxuIiwgInZhciAkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2V4cG9ydCcpO1xudmFyIGdldEJ1aWx0SW4gPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2V0LWJ1aWx0LWluJyk7XG52YXIgYUZ1bmN0aW9uID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2EtZnVuY3Rpb24nKTtcbnZhciBhbk9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hbi1vYmplY3QnKTtcbnZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcbnZhciBjcmVhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWNyZWF0ZScpO1xudmFyIGJpbmQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZnVuY3Rpb24tYmluZCcpO1xudmFyIGZhaWxzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2ZhaWxzJyk7XG5cbnZhciBuYXRpdmVDb25zdHJ1Y3QgPSBnZXRCdWlsdEluKCdSZWZsZWN0JywgJ2NvbnN0cnVjdCcpO1xuXG4vLyBgUmVmbGVjdC5jb25zdHJ1Y3RgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1yZWZsZWN0LmNvbnN0cnVjdFxuLy8gTVMgRWRnZSBzdXBwb3J0cyBvbmx5IDIgYXJndW1lbnRzIGFuZCBhcmd1bWVudHNMaXN0IGFyZ3VtZW50IGlzIG9wdGlvbmFsXG4vLyBGRiBOaWdodGx5IHNldHMgdGhpcmQgYXJndW1lbnQgYXMgYG5ldy50YXJnZXRgLCBidXQgZG9lcyBub3QgY3JlYXRlIGB0aGlzYCBmcm9tIGl0XG52YXIgTkVXX1RBUkdFVF9CVUcgPSBmYWlscyhmdW5jdGlvbiAoKSB7XG4gIGZ1bmN0aW9uIEYoKSB7IC8qIGVtcHR5ICovIH1cbiAgcmV0dXJuICEobmF0aXZlQ29uc3RydWN0KGZ1bmN0aW9uICgpIHsgLyogZW1wdHkgKi8gfSwgW10sIEYpIGluc3RhbmNlb2YgRik7XG59KTtcbnZhciBBUkdTX0JVRyA9ICFmYWlscyhmdW5jdGlvbiAoKSB7XG4gIG5hdGl2ZUNvbnN0cnVjdChmdW5jdGlvbiAoKSB7IC8qIGVtcHR5ICovIH0pO1xufSk7XG52YXIgRk9SQ0VEID0gTkVXX1RBUkdFVF9CVUcgfHwgQVJHU19CVUc7XG5cbiQoeyB0YXJnZXQ6ICdSZWZsZWN0Jywgc3RhdDogdHJ1ZSwgZm9yY2VkOiBGT1JDRUQsIHNoYW06IEZPUkNFRCB9LCB7XG4gIGNvbnN0cnVjdDogZnVuY3Rpb24gY29uc3RydWN0KFRhcmdldCwgYXJncyAvKiAsIG5ld1RhcmdldCAqLykge1xuICAgIGFGdW5jdGlvbihUYXJnZXQpO1xuICAgIGFuT2JqZWN0KGFyZ3MpO1xuICAgIHZhciBuZXdUYXJnZXQgPSBhcmd1bWVudHMubGVuZ3RoIDwgMyA/IFRhcmdldCA6IGFGdW5jdGlvbihhcmd1bWVudHNbMl0pO1xuICAgIGlmIChBUkdTX0JVRyAmJiAhTkVXX1RBUkdFVF9CVUcpIHJldHVybiBuYXRpdmVDb25zdHJ1Y3QoVGFyZ2V0LCBhcmdzLCBuZXdUYXJnZXQpO1xuICAgIGlmIChUYXJnZXQgPT0gbmV3VGFyZ2V0KSB7XG4gICAgICAvLyB3L28gYWx0ZXJlZCBuZXdUYXJnZXQsIG9wdGltaXphdGlvbiBmb3IgMC00IGFyZ3VtZW50c1xuICAgICAgc3dpdGNoIChhcmdzLmxlbmd0aCkge1xuICAgICAgICBjYXNlIDA6IHJldHVybiBuZXcgVGFyZ2V0KCk7XG4gICAgICAgIGNhc2UgMTogcmV0dXJuIG5ldyBUYXJnZXQoYXJnc1swXSk7XG4gICAgICAgIGNhc2UgMjogcmV0dXJuIG5ldyBUYXJnZXQoYXJnc1swXSwgYXJnc1sxXSk7XG4gICAgICAgIGNhc2UgMzogcmV0dXJuIG5ldyBUYXJnZXQoYXJnc1swXSwgYXJnc1sxXSwgYXJnc1syXSk7XG4gICAgICAgIGNhc2UgNDogcmV0dXJuIG5ldyBUYXJnZXQoYXJnc1swXSwgYXJnc1sxXSwgYXJnc1syXSwgYXJnc1szXSk7XG4gICAgICB9XG4gICAgICAvLyB3L28gYWx0ZXJlZCBuZXdUYXJnZXQsIGxvdCBvZiBhcmd1bWVudHMgY2FzZVxuICAgICAgdmFyICRhcmdzID0gW251bGxdO1xuICAgICAgJGFyZ3MucHVzaC5hcHBseSgkYXJncywgYXJncyk7XG4gICAgICByZXR1cm4gbmV3IChiaW5kLmFwcGx5KFRhcmdldCwgJGFyZ3MpKSgpO1xuICAgIH1cbiAgICAvLyB3aXRoIGFsdGVyZWQgbmV3VGFyZ2V0LCBub3Qgc3VwcG9ydCBidWlsdC1pbiBjb25zdHJ1Y3RvcnNcbiAgICB2YXIgcHJvdG8gPSBuZXdUYXJnZXQucHJvdG90eXBlO1xuICAgIHZhciBpbnN0YW5jZSA9IGNyZWF0ZShpc09iamVjdChwcm90bykgPyBwcm90byA6IE9iamVjdC5wcm90b3R5cGUpO1xuICAgIHZhciByZXN1bHQgPSBGdW5jdGlvbi5hcHBseS5jYWxsKFRhcmdldCwgaW5zdGFuY2UsIGFyZ3MpO1xuICAgIHJldHVybiBpc09iamVjdChyZXN1bHQpID8gcmVzdWx0IDogaW5zdGFuY2U7XG4gIH1cbn0pO1xuIiwgInZhciAkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2V4cG9ydCcpO1xudmFyIGJpbmQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZnVuY3Rpb24tYmluZCcpO1xuXG4vLyBgRnVuY3Rpb24ucHJvdG90eXBlLmJpbmRgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1mdW5jdGlvbi5wcm90b3R5cGUuYmluZFxuJCh7IHRhcmdldDogJ0Z1bmN0aW9uJywgcHJvdG86IHRydWUgfSwge1xuICBiaW5kOiBiaW5kXG59KTtcbiIsICJmdW5jdGlvbiBfdHlwZW9mKG9iaikgeyBcIkBiYWJlbC9oZWxwZXJzIC0gdHlwZW9mXCI7IGlmICh0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgdHlwZW9mIFN5bWJvbC5pdGVyYXRvciA9PT0gXCJzeW1ib2xcIikgeyBfdHlwZW9mID0gZnVuY3Rpb24gX3R5cGVvZihvYmopIHsgcmV0dXJuIHR5cGVvZiBvYmo7IH07IH0gZWxzZSB7IF90eXBlb2YgPSBmdW5jdGlvbiBfdHlwZW9mKG9iaikgeyByZXR1cm4gb2JqICYmIHR5cGVvZiBTeW1ib2wgPT09IFwiZnVuY3Rpb25cIiAmJiBvYmouY29uc3RydWN0b3IgPT09IFN5bWJvbCAmJiBvYmogIT09IFN5bWJvbC5wcm90b3R5cGUgPyBcInN5bWJvbFwiIDogdHlwZW9mIG9iajsgfTsgfSByZXR1cm4gX3R5cGVvZihvYmopOyB9XG5cbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5vYmplY3Quc2V0LXByb3RvdHlwZS1vZi5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLm9iamVjdC5nZXQtcHJvdG90eXBlLW9mLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMuYXJyYXkuaW5kZXgtb2YuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5kYXRlLnRvLXN0cmluZy5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLm9iamVjdC50by1zdHJpbmcuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5yZWdleHAudG8tc3RyaW5nLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMucmVmbGVjdC5jb25zdHJ1Y3QuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5mdW5jdGlvbi5iaW5kLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMuYXJyYXkuaXRlcmF0b3IuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5tYXAuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5zdHJpbmcuaXRlcmF0b3IuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy93ZWIuZG9tLWNvbGxlY3Rpb25zLml0ZXJhdG9yLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMub2JqZWN0LmNyZWF0ZS5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5kZXNjcmlwdGlvbi5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5pdGVyYXRvci5qc1wiO1xuXG5mdW5jdGlvbiBfY2xhc3NDYWxsQ2hlY2soaW5zdGFuY2UsIENvbnN0cnVjdG9yKSB7IGlmICghKGluc3RhbmNlIGluc3RhbmNlb2YgQ29uc3RydWN0b3IpKSB7IHRocm93IG5ldyBUeXBlRXJyb3IoXCJDYW5ub3QgY2FsbCBhIGNsYXNzIGFzIGEgZnVuY3Rpb25cIik7IH0gfVxuXG5mdW5jdGlvbiBfaW5oZXJpdHMoc3ViQ2xhc3MsIHN1cGVyQ2xhc3MpIHsgaWYgKHR5cGVvZiBzdXBlckNsYXNzICE9PSBcImZ1bmN0aW9uXCIgJiYgc3VwZXJDbGFzcyAhPT0gbnVsbCkgeyB0aHJvdyBuZXcgVHlwZUVycm9yKFwiU3VwZXIgZXhwcmVzc2lvbiBtdXN0IGVpdGhlciBiZSBudWxsIG9yIGEgZnVuY3Rpb25cIik7IH0gc3ViQ2xhc3MucHJvdG90eXBlID0gT2JqZWN0LmNyZWF0ZShzdXBlckNsYXNzICYmIHN1cGVyQ2xhc3MucHJvdG90eXBlLCB7IGNvbnN0cnVjdG9yOiB7IHZhbHVlOiBzdWJDbGFzcywgd3JpdGFibGU6IHRydWUsIGNvbmZpZ3VyYWJsZTogdHJ1ZSB9IH0pOyBpZiAoc3VwZXJDbGFzcykgX3NldFByb3RvdHlwZU9mKHN1YkNsYXNzLCBzdXBlckNsYXNzKTsgfVxuXG5mdW5jdGlvbiBfY3JlYXRlU3VwZXIoRGVyaXZlZCkgeyB2YXIgaGFzTmF0aXZlUmVmbGVjdENvbnN0cnVjdCA9IF9pc05hdGl2ZVJlZmxlY3RDb25zdHJ1Y3QoKTsgcmV0dXJuIGZ1bmN0aW9uIF9jcmVhdGVTdXBlckludGVybmFsKCkgeyB2YXIgU3VwZXIgPSBfZ2V0UHJvdG90eXBlT2YoRGVyaXZlZCksIHJlc3VsdDsgaWYgKGhhc05hdGl2ZVJlZmxlY3RDb25zdHJ1Y3QpIHsgdmFyIE5ld1RhcmdldCA9IF9nZXRQcm90b3R5cGVPZih0aGlzKS5jb25zdHJ1Y3RvcjsgcmVzdWx0ID0gUmVmbGVjdC5jb25zdHJ1Y3QoU3VwZXIsIGFyZ3VtZW50cywgTmV3VGFyZ2V0KTsgfSBlbHNlIHsgcmVzdWx0ID0gU3VwZXIuYXBwbHkodGhpcywgYXJndW1lbnRzKTsgfSByZXR1cm4gX3Bvc3NpYmxlQ29uc3RydWN0b3JSZXR1cm4odGhpcywgcmVzdWx0KTsgfTsgfVxuXG5mdW5jdGlvbiBfcG9zc2libGVDb25zdHJ1Y3RvclJldHVybihzZWxmLCBjYWxsKSB7IGlmIChjYWxsICYmIChfdHlwZW9mKGNhbGwpID09PSBcIm9iamVjdFwiIHx8IHR5cGVvZiBjYWxsID09PSBcImZ1bmN0aW9uXCIpKSB7IHJldHVybiBjYWxsOyB9IHJldHVybiBfYXNzZXJ0VGhpc0luaXRpYWxpemVkKHNlbGYpOyB9XG5cbmZ1bmN0aW9uIF9hc3NlcnRUaGlzSW5pdGlhbGl6ZWQoc2VsZikgeyBpZiAoc2VsZiA9PT0gdm9pZCAwKSB7IHRocm93IG5ldyBSZWZlcmVuY2VFcnJvcihcInRoaXMgaGFzbid0IGJlZW4gaW5pdGlhbGlzZWQgLSBzdXBlcigpIGhhc24ndCBiZWVuIGNhbGxlZFwiKTsgfSByZXR1cm4gc2VsZjsgfVxuXG5mdW5jdGlvbiBfd3JhcE5hdGl2ZVN1cGVyKENsYXNzKSB7IHZhciBfY2FjaGUgPSB0eXBlb2YgTWFwID09PSBcImZ1bmN0aW9uXCIgPyBuZXcgTWFwKCkgOiB1bmRlZmluZWQ7IF93cmFwTmF0aXZlU3VwZXIgPSBmdW5jdGlvbiBfd3JhcE5hdGl2ZVN1cGVyKENsYXNzKSB7IGlmIChDbGFzcyA9PT0gbnVsbCB8fCAhX2lzTmF0aXZlRnVuY3Rpb24oQ2xhc3MpKSByZXR1cm4gQ2xhc3M7IGlmICh0eXBlb2YgQ2xhc3MgIT09IFwiZnVuY3Rpb25cIikgeyB0aHJvdyBuZXcgVHlwZUVycm9yKFwiU3VwZXIgZXhwcmVzc2lvbiBtdXN0IGVpdGhlciBiZSBudWxsIG9yIGEgZnVuY3Rpb25cIik7IH0gaWYgKHR5cGVvZiBfY2FjaGUgIT09IFwidW5kZWZpbmVkXCIpIHsgaWYgKF9jYWNoZS5oYXMoQ2xhc3MpKSByZXR1cm4gX2NhY2hlLmdldChDbGFzcyk7IF9jYWNoZS5zZXQoQ2xhc3MsIFdyYXBwZXIpOyB9IGZ1bmN0aW9uIFdyYXBwZXIoKSB7IHJldHVybiBfY29uc3RydWN0KENsYXNzLCBhcmd1bWVudHMsIF9nZXRQcm90b3R5cGVPZih0aGlzKS5jb25zdHJ1Y3Rvcik7IH0gV3JhcHBlci5wcm90b3R5cGUgPSBPYmplY3QuY3JlYXRlKENsYXNzLnByb3RvdHlwZSwgeyBjb25zdHJ1Y3RvcjogeyB2YWx1ZTogV3JhcHBlciwgZW51bWVyYWJsZTogZmFsc2UsIHdyaXRhYmxlOiB0cnVlLCBjb25maWd1cmFibGU6IHRydWUgfSB9KTsgcmV0dXJuIF9zZXRQcm90b3R5cGVPZihXcmFwcGVyLCBDbGFzcyk7IH07IHJldHVybiBfd3JhcE5hdGl2ZVN1cGVyKENsYXNzKTsgfVxuXG5mdW5jdGlvbiBfY29uc3RydWN0KFBhcmVudCwgYXJncywgQ2xhc3MpIHsgaWYgKF9pc05hdGl2ZVJlZmxlY3RDb25zdHJ1Y3QoKSkgeyBfY29uc3RydWN0ID0gUmVmbGVjdC5jb25zdHJ1Y3Q7IH0gZWxzZSB7IF9jb25zdHJ1Y3QgPSBmdW5jdGlvbiBfY29uc3RydWN0KFBhcmVudCwgYXJncywgQ2xhc3MpIHsgdmFyIGEgPSBbbnVsbF07IGEucHVzaC5hcHBseShhLCBhcmdzKTsgdmFyIENvbnN0cnVjdG9yID0gRnVuY3Rpb24uYmluZC5hcHBseShQYXJlbnQsIGEpOyB2YXIgaW5zdGFuY2UgPSBuZXcgQ29uc3RydWN0b3IoKTsgaWYgKENsYXNzKSBfc2V0UHJvdG90eXBlT2YoaW5zdGFuY2UsIENsYXNzLnByb3RvdHlwZSk7IHJldHVybiBpbnN0YW5jZTsgfTsgfSByZXR1cm4gX2NvbnN0cnVjdC5hcHBseShudWxsLCBhcmd1bWVudHMpOyB9XG5cbmZ1bmN0aW9uIF9pc05hdGl2ZVJlZmxlY3RDb25zdHJ1Y3QoKSB7IGlmICh0eXBlb2YgUmVmbGVjdCA9PT0gXCJ1bmRlZmluZWRcIiB8fCAhUmVmbGVjdC5jb25zdHJ1Y3QpIHJldHVybiBmYWxzZTsgaWYgKFJlZmxlY3QuY29uc3RydWN0LnNoYW0pIHJldHVybiBmYWxzZTsgaWYgKHR5cGVvZiBQcm94eSA9PT0gXCJmdW5jdGlvblwiKSByZXR1cm4gdHJ1ZTsgdHJ5IHsgQm9vbGVhbi5wcm90b3R5cGUudmFsdWVPZi5jYWxsKFJlZmxlY3QuY29uc3RydWN0KEJvb2xlYW4sIFtdLCBmdW5jdGlvbiAoKSB7fSkpOyByZXR1cm4gdHJ1ZTsgfSBjYXRjaCAoZSkgeyByZXR1cm4gZmFsc2U7IH0gfVxuXG5mdW5jdGlvbiBfaXNOYXRpdmVGdW5jdGlvbihmbikgeyByZXR1cm4gRnVuY3Rpb24udG9TdHJpbmcuY2FsbChmbikuaW5kZXhPZihcIltuYXRpdmUgY29kZV1cIikgIT09IC0xOyB9XG5cbmZ1bmN0aW9uIF9zZXRQcm90b3R5cGVPZihvLCBwKSB7IF9zZXRQcm90b3R5cGVPZiA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCBmdW5jdGlvbiBfc2V0UHJvdG90eXBlT2YobywgcCkgeyBvLl9fcHJvdG9fXyA9IHA7IHJldHVybiBvOyB9OyByZXR1cm4gX3NldFByb3RvdHlwZU9mKG8sIHApOyB9XG5cbmZ1bmN0aW9uIF9nZXRQcm90b3R5cGVPZihvKSB7IF9nZXRQcm90b3R5cGVPZiA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiA/IE9iamVjdC5nZXRQcm90b3R5cGVPZiA6IGZ1bmN0aW9uIF9nZXRQcm90b3R5cGVPZihvKSB7IHJldHVybiBvLl9fcHJvdG9fXyB8fCBPYmplY3QuZ2V0UHJvdG90eXBlT2Yobyk7IH07IHJldHVybiBfZ2V0UHJvdG90eXBlT2Yobyk7IH1cblxuLy8gVE9ETzpcbi8vIDEuIHNob3VsZC9jYW4gd2UgZ2V0IHJpZCBvZiBiczNjb21wYXQgZGVwZW5kZW5jeT9cbi8vIDIuIHNlbGVjdGVkIGF0dHJpYnV0ZSBpcyBncmVhdCBmb3IgdXNpbmcgY29tcG9uZW50IGRpcmVjdGx5LCBidXQgZG9lcyBpdCBtYWtlIHNlbnNlIGZvciBxbWQgdXNhZ2U/XG4vLyBVc2FnZTpcbi8vXG4vLyBFYWNoIDxic2xpYi1uYXZzLSo+IGNvbXBvbmVudCBleHBlY3RzIHRvcC1sZXZlbCA8dGVtcGxhdGU+cyB3aXRoXG4vLyBzcGVjaWFsIGNsYXNzZXM6XG4vLyAgKiBuYXY6IHRpdGxlIGF0dHIgZGVmaW5lcyB0aGUgbmF2IGl0ZW0gYW5kIGNvbnRlbnRzIGFyZSBkaXNwbGF5ZWQgd2hlbiBhY3RpdmVcbi8vICAqIG5hdi1pdGVtOiBjb250ZW50cyBhcmUgZGlzcGxheWVkIHZlcmJhdGltIGluIHRoZSBuYXZcbi8vICAqIG5hdi1zcGFjZXI6IGZvciBhZGQgc3BhY2luZyBiZXR3ZWVuIG5hdiBpdGVtcy5cbi8vICAqIG5hdi1tZW51OiBhIGNvbGxlY3Rpb24gb2YgLm5hdi8ubmF2LWl0ZW1zXG4vL1xuLy8gRXhhbXBsZTpcbi8vXG4vLyA8YnNsaWItbmF2cy0qIHNlbGVjdGVkPSd0d28nPlxuLy8gICA8dGVtcGxhdGUgY2xhc3M9J25hdicgdGl0bGU9J1RhYiAxJyB2YWx1ZT0nb25lJz5cbi8vICAgICBUYWIgMSBjb250ZW50XG4vLyAgIDwvdGVtcGxhdGU+XG4vLyAgIDx0ZW1wbGF0ZSBjbGFzcz0nbmF2JyB0aXRsZT0nVGFiIDInIHZhbHVlPSd0d28nPlxuLy8gICAgIFRhYiAyIGNvbnRlbnRcbi8vICAgPC90ZW1wbGF0ZT5cbi8vICAgPHRlbXBsYXRlIGNsYXNzPSduYXYtc3BhY2VyJz48L3RlbXBsYXRlPlxuLy8gICA8dGVtcGxhdGUgY2xhc3M9J25hdi1pdGVtJz5cbi8vICAgICA8YSBocmVmPSdodHRwczovL2dvb2dsZS5jb20nPiBBbiBleHRlcm5hbCBsaW5rIDwvYT5cbi8vICAgPC90ZW1wbGF0ZT5cbi8vICAgPHRlbXBsYXRlIGNsYXNzPSduYXYtbWVudScgdGl0bGU9J01lbnUnIHZhbHVlPSdtZW51Jz5cbi8vICAgICA8dGVtcGxhdGUgY2xhc3M9J25hdicgdGl0bGU9J1RhYiAzJyB2YWx1ZT0ndGhyZWUnPlxuLy8gICAgICAgVGFiIDMgY29udGVudFxuLy8gICAgIDwvdGVtcGxhdGU+XG4vLyAgIDwvdGVtcGxhdGU+XG4vLyA8L2JzbGliLW5hdnMtKj5cbmltcG9ydCB7IHRhZyB9IGZyb20gJy4vdXRpbHMnO1xuaW1wb3J0IHsgY3JlYXRlVGFiRnJhZ21lbnQsIGJ1aWxkVGFic2V0LCBnZXRTZWxlY3RlZCwgcmVwbGFjZUNoaWxkcmVuIH0gZnJvbSAnLi9uYXYtdXRpbHMnO1xuaW1wb3J0IHsgY3JlYXRlQ2FyZCB9IGZyb20gJy4vY2FyZCc7XG5cbnZhciBOYXZzVGFiID0gLyojX19QVVJFX18qL2Z1bmN0aW9uIChfSFRNTEVsZW1lbnQpIHtcbiAgX2luaGVyaXRzKE5hdnNUYWIsIF9IVE1MRWxlbWVudCk7XG5cbiAgdmFyIF9zdXBlciA9IF9jcmVhdGVTdXBlcihOYXZzVGFiKTtcblxuICBmdW5jdGlvbiBOYXZzVGFiKCkge1xuICAgIHZhciBfdGhpcztcblxuICAgIF9jbGFzc0NhbGxDaGVjayh0aGlzLCBOYXZzVGFiKTtcblxuICAgIHNlbGYgPSBfdGhpcyA9IF9zdXBlci5jYWxsKHRoaXMpO1xuICAgIGRlYnVnZ2VyO1xuICAgIHZhciBzZWxlY3RlZCA9IGdldFNlbGVjdGVkKHNlbGYpO1xuICAgIHZhciB0YWJzZXQgPSBidWlsZFRhYnNldChzZWxmLmNoaWxkcmVuLCBzZWxlY3RlZCk7XG4gICAgdmFyIHRhYnMgPSBjcmVhdGVUYWJGcmFnbWVudChzZWxmLCAnbmF2IG5hdi10YWJzJywgdGFic2V0KTtcbiAgICByZXBsYWNlQ2hpbGRyZW4oc2VsZiwgdGFicyk7XG4gICAgcmV0dXJuIF90aGlzO1xuICB9XG5cbiAgcmV0dXJuIE5hdnNUYWI7XG59KCAvKiNfX1BVUkVfXyovX3dyYXBOYXRpdmVTdXBlcihIVE1MRWxlbWVudCkpO1xuXG5jdXN0b21FbGVtZW50cy5kZWZpbmUoJ2JzbGliLW5hdnMtdGFiJywgTmF2c1RhYik7XG5cbnZhciBOYXZzUGlsbCA9IC8qI19fUFVSRV9fKi9mdW5jdGlvbiAoX0hUTUxFbGVtZW50Mikge1xuICBfaW5oZXJpdHMoTmF2c1BpbGwsIF9IVE1MRWxlbWVudDIpO1xuXG4gIHZhciBfc3VwZXIyID0gX2NyZWF0ZVN1cGVyKE5hdnNQaWxsKTtcblxuICBmdW5jdGlvbiBOYXZzUGlsbCgpIHtcbiAgICB2YXIgX3RoaXMyO1xuXG4gICAgX2NsYXNzQ2FsbENoZWNrKHRoaXMsIE5hdnNQaWxsKTtcblxuICAgIHNlbGYgPSBfdGhpczIgPSBfc3VwZXIyLmNhbGwodGhpcyk7XG4gICAgdmFyIHNlbGVjdGVkID0gZ2V0U2VsZWN0ZWQoc2VsZik7XG4gICAgdmFyIHRhYnNldCA9IGJ1aWxkVGFic2V0KHNlbGYuY2hpbGRyZW4sIHNlbGVjdGVkKTtcbiAgICB2YXIgcGlsbHMgPSBjcmVhdGVUYWJGcmFnbWVudChzZWxmLCAnbmF2IG5hdi1waWxscycsIHRhYnNldCk7XG4gICAgcmVwbGFjZUNoaWxkcmVuKHNlbGYsIHBpbGxzKTtcbiAgICByZXR1cm4gX3RoaXMyO1xuICB9XG5cbiAgcmV0dXJuIE5hdnNQaWxsO1xufSggLyojX19QVVJFX18qL193cmFwTmF0aXZlU3VwZXIoSFRNTEVsZW1lbnQpKTtcblxuY3VzdG9tRWxlbWVudHMuZGVmaW5lKCdic2xpYi1uYXZzLXBpbGwnLCBOYXZzUGlsbCk7XG5cbnZhciBOYXZzVGFiQ2FyZCA9IC8qI19fUFVSRV9fKi9mdW5jdGlvbiAoX0hUTUxFbGVtZW50Mykge1xuICBfaW5oZXJpdHMoTmF2c1RhYkNhcmQsIF9IVE1MRWxlbWVudDMpO1xuXG4gIHZhciBfc3VwZXIzID0gX2NyZWF0ZVN1cGVyKE5hdnNUYWJDYXJkKTtcblxuICBmdW5jdGlvbiBOYXZzVGFiQ2FyZCgpIHtcbiAgICB2YXIgX3RoaXMzO1xuXG4gICAgX2NsYXNzQ2FsbENoZWNrKHRoaXMsIE5hdnNUYWJDYXJkKTtcblxuICAgIHNlbGYgPSBfdGhpczMgPSBfc3VwZXIzLmNhbGwodGhpcyk7XG4gICAgdmFyIHNlbGVjdGVkID0gZ2V0U2VsZWN0ZWQoc2VsZik7XG4gICAgdmFyIHRhYnNldCA9IGJ1aWxkVGFic2V0KHNlbGYuY2hpbGRyZW4sIHNlbGVjdGVkKTtcbiAgICB2YXIgdGFicyA9IGNyZWF0ZVRhYkZyYWdtZW50KHNlbGYsICduYXYgbmF2LXRhYnMnLCB0YWJzZXQpO1xuICAgIHZhciBuYXYgPSB0YWJzWzBdO1xuICAgIHZhciBjb250ZW50ID0gdGFic1sxXTsgLy8gaHR0cHM6Ly9nZXRib290c3RyYXAuY29tL2RvY3MvNS4wL2NvbXBvbmVudHMvY2FyZC8jbmF2aWdhdGlvblxuXG4gICAgbmF2LmNsYXNzTGlzdC5hZGQoJ2NhcmQtaGVhZGVyLXRhYnMnKTtcbiAgICB2YXIgY2FyZCA9IGNyZWF0ZUNhcmQoY29udGVudCwgbmF2KTtcbiAgICByZXBsYWNlQ2hpbGRyZW4oc2VsZiwgY2FyZCk7XG4gICAgcmV0dXJuIF90aGlzMztcbiAgfVxuXG4gIHJldHVybiBOYXZzVGFiQ2FyZDtcbn0oIC8qI19fUFVSRV9fKi9fd3JhcE5hdGl2ZVN1cGVyKEhUTUxFbGVtZW50KSk7XG5cbmN1c3RvbUVsZW1lbnRzLmRlZmluZSgnYnNsaWItbmF2cy10YWItY2FyZCcsIE5hdnNUYWJDYXJkKTtcblxudmFyIE5hdnNQaWxsQ2FyZCA9IC8qI19fUFVSRV9fKi9mdW5jdGlvbiAoX0hUTUxFbGVtZW50NCkge1xuICBfaW5oZXJpdHMoTmF2c1BpbGxDYXJkLCBfSFRNTEVsZW1lbnQ0KTtcblxuICB2YXIgX3N1cGVyNCA9IF9jcmVhdGVTdXBlcihOYXZzUGlsbENhcmQpO1xuXG4gIGZ1bmN0aW9uIE5hdnNQaWxsQ2FyZCgpIHtcbiAgICB2YXIgX3RoaXM0O1xuXG4gICAgX2NsYXNzQ2FsbENoZWNrKHRoaXMsIE5hdnNQaWxsQ2FyZCk7XG5cbiAgICBzZWxmID0gX3RoaXM0ID0gX3N1cGVyNC5jYWxsKHRoaXMpO1xuICAgIHZhciBzZWxlY3RlZCA9IGdldFNlbGVjdGVkKHNlbGYpO1xuICAgIHZhciB0YWJzZXQgPSBidWlsZFRhYnNldChzZWxmLmNoaWxkcmVuLCBzZWxlY3RlZCk7XG4gICAgdmFyIHBpbGxzID0gY3JlYXRlVGFiRnJhZ21lbnQoc2VsZiwgJ25hdiBuYXYtcGlsbHMnLCB0YWJzZXQpO1xuICAgIHZhciBuYXYgPSBwaWxsc1swXTtcbiAgICB2YXIgY29udGVudCA9IHBpbGxzWzFdO1xuICAgIHZhciBhYm92ZSA9IHNlbGYuZ2V0QXR0cmlidXRlKCdwbGFjZW1lbnQnKSAhPT0gJ2JlbG93JztcbiAgICBpZiAoYWJvdmUpIG5hdi5jbGFzc0xpc3QuYWRkKCdjYXJkLWhlYWRlci1waWxscycpO1xuICAgIHZhciBjYXJkID0gYWJvdmUgPyBjcmVhdGVDYXJkKGNvbnRlbnQsIG5hdikgOiBjcmVhdGVDYXJkKGNvbnRlbnQsIG51bGwsIG5hdik7XG4gICAgcmVwbGFjZUNoaWxkcmVuKHNlbGYsIGNhcmQpO1xuICAgIHJldHVybiBfdGhpczQ7XG4gIH1cblxuICByZXR1cm4gTmF2c1BpbGxDYXJkO1xufSggLyojX19QVVJFX18qL193cmFwTmF0aXZlU3VwZXIoSFRNTEVsZW1lbnQpKTtcblxuY3VzdG9tRWxlbWVudHMuZGVmaW5lKCdic2xpYi1uYXZzLXBpbGwtY2FyZCcsIE5hdnNQaWxsQ2FyZCk7XG5cbnZhciBOYXZzUGlsbExpc3QgPSAvKiNfX1BVUkVfXyovZnVuY3Rpb24gKF9IVE1MRWxlbWVudDUpIHtcbiAgX2luaGVyaXRzKE5hdnNQaWxsTGlzdCwgX0hUTUxFbGVtZW50NSk7XG5cbiAgdmFyIF9zdXBlcjUgPSBfY3JlYXRlU3VwZXIoTmF2c1BpbGxMaXN0KTtcblxuICBmdW5jdGlvbiBOYXZzUGlsbExpc3QoKSB7XG4gICAgdmFyIF90aGlzNTtcblxuICAgIF9jbGFzc0NhbGxDaGVjayh0aGlzLCBOYXZzUGlsbExpc3QpO1xuXG4gICAgc2VsZiA9IF90aGlzNSA9IF9zdXBlcjUuY2FsbCh0aGlzKTtcbiAgICB2YXIgc2VsZWN0ZWQgPSBnZXRTZWxlY3RlZChzZWxmKTsgLy8gVE9ETzogaW1wbGVtZW50IHRleHRGaWx0ZXIhXG5cbiAgICB2YXIgdGFic2V0ID0gYnVpbGRUYWJzZXQoc2VsZi5jaGlsZHJlbiwgc2VsZWN0ZWQpO1xuICAgIHZhciBwaWxscyA9IGNyZWF0ZVRhYkZyYWdtZW50KHNlbGYsICduYXYgbmF2LXBpbGxzIG5hdi1zdGFja2VkJywgdGFic2V0KTtcbiAgICB2YXIgbmF2ID0gcGlsbHNbMF07XG4gICAgdmFyIGNvbnRlbnQgPSBwaWxsc1sxXTtcbiAgICB2YXIgbmF2Q2xhc3MgPSAnY29sLXNtLScgKyBzZWxmLmdldEF0dHJpYnV0ZSgnd2lkdGhOYXYnKTtcblxuICAgIGlmIChzZWxmLmdldEF0dHJpYnV0ZSgnd2VsbCcpKSB7XG4gICAgICBuYXZDbGFzcyA9IG5hdkNsYXNzICsgJyB3ZWxsJztcbiAgICB9XG5cbiAgICB2YXIgcm93ID0gdGFnKCdkaXYnLCB7XG4gICAgICBcImNsYXNzXCI6ICdyb3cnXG4gICAgfSwgdGFnKCdkaXYnLCB7XG4gICAgICBcImNsYXNzXCI6IG5hdkNsYXNzXG4gICAgfSwgbmF2KSwgdGFnKCdkaXYnLCB7XG4gICAgICBcImNsYXNzXCI6ICdjb2wtc20tJyArIHNlbGYuZ2V0QXR0cmlidXRlKCd3aWR0aENvbnRlbnQnKVxuICAgIH0sIGNvbnRlbnQpKTtcbiAgICByZXBsYWNlQ2hpbGRyZW4oc2VsZiwgcm93KTtcbiAgICByZXR1cm4gX3RoaXM1O1xuICB9XG5cbiAgcmV0dXJuIE5hdnNQaWxsTGlzdDtcbn0oIC8qI19fUFVSRV9fKi9fd3JhcE5hdGl2ZVN1cGVyKEhUTUxFbGVtZW50KSk7XG5cbmN1c3RvbUVsZW1lbnRzLmRlZmluZSgnYnNsaWItbmF2cy1waWxsLWxpc3QnLCBOYXZzUGlsbExpc3QpO1xuXG52YXIgTmF2c0JhciA9IC8qI19fUFVSRV9fKi9mdW5jdGlvbiAoX0hUTUxFbGVtZW50Nikge1xuICBfaW5oZXJpdHMoTmF2c0JhciwgX0hUTUxFbGVtZW50Nik7XG5cbiAgdmFyIF9zdXBlcjYgPSBfY3JlYXRlU3VwZXIoTmF2c0Jhcik7XG5cbiAgZnVuY3Rpb24gTmF2c0JhcigpIHtcbiAgICB2YXIgX3RoaXM2O1xuXG4gICAgX2NsYXNzQ2FsbENoZWNrKHRoaXMsIE5hdnNCYXIpO1xuXG4gICAgc2VsZiA9IF90aGlzNiA9IF9zdXBlcjYuY2FsbCh0aGlzKTtcbiAgICB2YXIgc2VsZWN0ZWQgPSBnZXRTZWxlY3RlZChzZWxmKTtcbiAgICB2YXIgdGFic2V0ID0gYnVpbGRUYWJzZXQoc2VsZi5jaGlsZHJlbiwgc2VsZWN0ZWQpO1xuICAgIHZhciBuYXZiYXIgPSBjcmVhdGVUYWJGcmFnbWVudChzZWxmLCAnbmF2IG5hdmJhci1uYXYnLCB0YWJzZXQpOyAvLyBUT0RPOiBpbXBsZW1lbnQhXG4gICAgLy9jb25zdCBuYXYgPSB0YWcoJ25hdicsIHtyb2xlOiAnbmF2aWdhdGlvbicsIGNsYXNzOiBuYXZiYXJDbGFzc30pO1xuICAgIC8vcmVwbGFjZUNoaWxkcmVuKHNlbGYsIG5hdik7XG5cbiAgICByZXR1cm4gX3RoaXM2O1xuICB9XG5cbiAgcmV0dXJuIE5hdnNCYXI7XG59KCAvKiNfX1BVUkVfXyovX3dyYXBOYXRpdmVTdXBlcihIVE1MRWxlbWVudCkpO1xuXG5jdXN0b21FbGVtZW50cy5kZWZpbmUoJ2JzbGliLW5hdnMtYmFyJywgTmF2c0Jhcik7IiwgIid1c2Ugc3RyaWN0JztcbnZhciBjaGFyQXQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc3RyaW5nLW11bHRpYnl0ZScpLmNoYXJBdDtcbnZhciBJbnRlcm5hbFN0YXRlTW9kdWxlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2ludGVybmFsLXN0YXRlJyk7XG52YXIgZGVmaW5lSXRlcmF0b3IgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZGVmaW5lLWl0ZXJhdG9yJyk7XG5cbnZhciBTVFJJTkdfSVRFUkFUT1IgPSAnU3RyaW5nIEl0ZXJhdG9yJztcbnZhciBzZXRJbnRlcm5hbFN0YXRlID0gSW50ZXJuYWxTdGF0ZU1vZHVsZS5zZXQ7XG52YXIgZ2V0SW50ZXJuYWxTdGF0ZSA9IEludGVybmFsU3RhdGVNb2R1bGUuZ2V0dGVyRm9yKFNUUklOR19JVEVSQVRPUik7XG5cbi8vIGBTdHJpbmcucHJvdG90eXBlW0BAaXRlcmF0b3JdYCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtc3RyaW5nLnByb3RvdHlwZS1AQGl0ZXJhdG9yXG5kZWZpbmVJdGVyYXRvcihTdHJpbmcsICdTdHJpbmcnLCBmdW5jdGlvbiAoaXRlcmF0ZWQpIHtcbiAgc2V0SW50ZXJuYWxTdGF0ZSh0aGlzLCB7XG4gICAgdHlwZTogU1RSSU5HX0lURVJBVE9SLFxuICAgIHN0cmluZzogU3RyaW5nKGl0ZXJhdGVkKSxcbiAgICBpbmRleDogMFxuICB9KTtcbi8vIGAlU3RyaW5nSXRlcmF0b3JQcm90b3R5cGUlLm5leHRgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy0lc3RyaW5naXRlcmF0b3Jwcm90b3R5cGUlLm5leHRcbn0sIGZ1bmN0aW9uIG5leHQoKSB7XG4gIHZhciBzdGF0ZSA9IGdldEludGVybmFsU3RhdGUodGhpcyk7XG4gIHZhciBzdHJpbmcgPSBzdGF0ZS5zdHJpbmc7XG4gIHZhciBpbmRleCA9IHN0YXRlLmluZGV4O1xuICB2YXIgcG9pbnQ7XG4gIGlmIChpbmRleCA+PSBzdHJpbmcubGVuZ3RoKSByZXR1cm4geyB2YWx1ZTogdW5kZWZpbmVkLCBkb25lOiB0cnVlIH07XG4gIHBvaW50ID0gY2hhckF0KHN0cmluZywgaW5kZXgpO1xuICBzdGF0ZS5pbmRleCArPSBwb2ludC5sZW5ndGg7XG4gIHJldHVybiB7IHZhbHVlOiBwb2ludCwgZG9uZTogZmFsc2UgfTtcbn0pO1xuIiwgInZhciBnbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2xvYmFsJyk7XG52YXIgRE9NSXRlcmFibGVzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2RvbS1pdGVyYWJsZXMnKTtcbnZhciBBcnJheUl0ZXJhdG9yTWV0aG9kcyA9IHJlcXVpcmUoJy4uL21vZHVsZXMvZXMuYXJyYXkuaXRlcmF0b3InKTtcbnZhciBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY3JlYXRlLW5vbi1lbnVtZXJhYmxlLXByb3BlcnR5Jyk7XG52YXIgd2VsbEtub3duU3ltYm9sID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3dlbGwta25vd24tc3ltYm9sJyk7XG5cbnZhciBJVEVSQVRPUiA9IHdlbGxLbm93blN5bWJvbCgnaXRlcmF0b3InKTtcbnZhciBUT19TVFJJTkdfVEFHID0gd2VsbEtub3duU3ltYm9sKCd0b1N0cmluZ1RhZycpO1xudmFyIEFycmF5VmFsdWVzID0gQXJyYXlJdGVyYXRvck1ldGhvZHMudmFsdWVzO1xuXG5mb3IgKHZhciBDT0xMRUNUSU9OX05BTUUgaW4gRE9NSXRlcmFibGVzKSB7XG4gIHZhciBDb2xsZWN0aW9uID0gZ2xvYmFsW0NPTExFQ1RJT05fTkFNRV07XG4gIHZhciBDb2xsZWN0aW9uUHJvdG90eXBlID0gQ29sbGVjdGlvbiAmJiBDb2xsZWN0aW9uLnByb3RvdHlwZTtcbiAgaWYgKENvbGxlY3Rpb25Qcm90b3R5cGUpIHtcbiAgICAvLyBzb21lIENocm9tZSB2ZXJzaW9ucyBoYXZlIG5vbi1jb25maWd1cmFibGUgbWV0aG9kcyBvbiBET01Ub2tlbkxpc3RcbiAgICBpZiAoQ29sbGVjdGlvblByb3RvdHlwZVtJVEVSQVRPUl0gIT09IEFycmF5VmFsdWVzKSB0cnkge1xuICAgICAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KENvbGxlY3Rpb25Qcm90b3R5cGUsIElURVJBVE9SLCBBcnJheVZhbHVlcyk7XG4gICAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICAgIENvbGxlY3Rpb25Qcm90b3R5cGVbSVRFUkFUT1JdID0gQXJyYXlWYWx1ZXM7XG4gICAgfVxuICAgIGlmICghQ29sbGVjdGlvblByb3RvdHlwZVtUT19TVFJJTkdfVEFHXSkge1xuICAgICAgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5KENvbGxlY3Rpb25Qcm90b3R5cGUsIFRPX1NUUklOR19UQUcsIENPTExFQ1RJT05fTkFNRSk7XG4gICAgfVxuICAgIGlmIChET01JdGVyYWJsZXNbQ09MTEVDVElPTl9OQU1FXSkgZm9yICh2YXIgTUVUSE9EX05BTUUgaW4gQXJyYXlJdGVyYXRvck1ldGhvZHMpIHtcbiAgICAgIC8vIHNvbWUgQ2hyb21lIHZlcnNpb25zIGhhdmUgbm9uLWNvbmZpZ3VyYWJsZSBtZXRob2RzIG9uIERPTVRva2VuTGlzdFxuICAgICAgaWYgKENvbGxlY3Rpb25Qcm90b3R5cGVbTUVUSE9EX05BTUVdICE9PSBBcnJheUl0ZXJhdG9yTWV0aG9kc1tNRVRIT0RfTkFNRV0pIHRyeSB7XG4gICAgICAgIGNyZWF0ZU5vbkVudW1lcmFibGVQcm9wZXJ0eShDb2xsZWN0aW9uUHJvdG90eXBlLCBNRVRIT0RfTkFNRSwgQXJyYXlJdGVyYXRvck1ldGhvZHNbTUVUSE9EX05BTUVdKTtcbiAgICAgIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgICAgIENvbGxlY3Rpb25Qcm90b3R5cGVbTUVUSE9EX05BTUVdID0gQXJyYXlJdGVyYXRvck1ldGhvZHNbTUVUSE9EX05BTUVdO1xuICAgICAgfVxuICAgIH1cbiAgfVxufVxuIiwgInZhciAkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2V4cG9ydCcpO1xudmFyIERFU0NSSVBUT1JTID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Rlc2NyaXB0b3JzJyk7XG52YXIgY3JlYXRlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1jcmVhdGUnKTtcblxuLy8gYE9iamVjdC5jcmVhdGVgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1vYmplY3QuY3JlYXRlXG4kKHsgdGFyZ2V0OiAnT2JqZWN0Jywgc3RhdDogdHJ1ZSwgc2hhbTogIURFU0NSSVBUT1JTIH0sIHtcbiAgY3JlYXRlOiBjcmVhdGVcbn0pO1xuIiwgIid1c2Ugc3RyaWN0JztcbnZhciAkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2V4cG9ydCcpO1xudmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcbnZhciBnZXRCdWlsdEluID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2dldC1idWlsdC1pbicpO1xudmFyIElTX1BVUkUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtcHVyZScpO1xudmFyIERFU0NSSVBUT1JTID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2Rlc2NyaXB0b3JzJyk7XG52YXIgTkFUSVZFX1NZTUJPTCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9uYXRpdmUtc3ltYm9sJyk7XG52YXIgVVNFX1NZTUJPTF9BU19VSUQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdXNlLXN5bWJvbC1hcy11aWQnKTtcbnZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xudmFyIGhhcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9oYXMnKTtcbnZhciBpc0FycmF5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2lzLWFycmF5Jyk7XG52YXIgaXNPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtb2JqZWN0Jyk7XG52YXIgYW5PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYW4tb2JqZWN0Jyk7XG52YXIgdG9PYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tb2JqZWN0Jyk7XG52YXIgdG9JbmRleGVkT2JqZWN0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWluZGV4ZWQtb2JqZWN0Jyk7XG52YXIgdG9QcmltaXRpdmUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tcHJpbWl0aXZlJyk7XG52YXIgY3JlYXRlUHJvcGVydHlEZXNjcmlwdG9yID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1wcm9wZXJ0eS1kZXNjcmlwdG9yJyk7XG52YXIgbmF0aXZlT2JqZWN0Q3JlYXRlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1jcmVhdGUnKTtcbnZhciBvYmplY3RLZXlzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1rZXlzJyk7XG52YXIgZ2V0T3duUHJvcGVydHlOYW1lc01vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1uYW1lcycpO1xudmFyIGdldE93blByb3BlcnR5TmFtZXNFeHRlcm5hbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1uYW1lcy1leHRlcm5hbCcpO1xudmFyIGdldE93blByb3BlcnR5U3ltYm9sc01vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZ2V0LW93bi1wcm9wZXJ0eS1zeW1ib2xzJyk7XG52YXIgZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yTW9kdWxlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1nZXQtb3duLXByb3BlcnR5LWRlc2NyaXB0b3InKTtcbnZhciBkZWZpbmVQcm9wZXJ0eU1vZHVsZSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9vYmplY3QtZGVmaW5lLXByb3BlcnR5Jyk7XG52YXIgcHJvcGVydHlJc0VudW1lcmFibGVNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LXByb3BlcnR5LWlzLWVudW1lcmFibGUnKTtcbnZhciBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY3JlYXRlLW5vbi1lbnVtZXJhYmxlLXByb3BlcnR5Jyk7XG52YXIgcmVkZWZpbmUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvcmVkZWZpbmUnKTtcbnZhciBzaGFyZWQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvc2hhcmVkJyk7XG52YXIgc2hhcmVkS2V5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3NoYXJlZC1rZXknKTtcbnZhciBoaWRkZW5LZXlzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2hpZGRlbi1rZXlzJyk7XG52YXIgdWlkID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3VpZCcpO1xudmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xudmFyIHdyYXBwZWRXZWxsS25vd25TeW1ib2xNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvd2VsbC1rbm93bi1zeW1ib2wtd3JhcHBlZCcpO1xudmFyIGRlZmluZVdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9kZWZpbmUtd2VsbC1rbm93bi1zeW1ib2wnKTtcbnZhciBzZXRUb1N0cmluZ1RhZyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9zZXQtdG8tc3RyaW5nLXRhZycpO1xudmFyIEludGVybmFsU3RhdGVNb2R1bGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaW50ZXJuYWwtc3RhdGUnKTtcbnZhciAkZm9yRWFjaCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hcnJheS1pdGVyYXRpb24nKS5mb3JFYWNoO1xuXG52YXIgSElEREVOID0gc2hhcmVkS2V5KCdoaWRkZW4nKTtcbnZhciBTWU1CT0wgPSAnU3ltYm9sJztcbnZhciBQUk9UT1RZUEUgPSAncHJvdG90eXBlJztcbnZhciBUT19QUklNSVRJVkUgPSB3ZWxsS25vd25TeW1ib2woJ3RvUHJpbWl0aXZlJyk7XG52YXIgc2V0SW50ZXJuYWxTdGF0ZSA9IEludGVybmFsU3RhdGVNb2R1bGUuc2V0O1xudmFyIGdldEludGVybmFsU3RhdGUgPSBJbnRlcm5hbFN0YXRlTW9kdWxlLmdldHRlckZvcihTWU1CT0wpO1xudmFyIE9iamVjdFByb3RvdHlwZSA9IE9iamVjdFtQUk9UT1RZUEVdO1xudmFyICRTeW1ib2wgPSBnbG9iYWwuU3ltYm9sO1xudmFyICRzdHJpbmdpZnkgPSBnZXRCdWlsdEluKCdKU09OJywgJ3N0cmluZ2lmeScpO1xudmFyIG5hdGl2ZUdldE93blByb3BlcnR5RGVzY3JpcHRvciA9IGdldE93blByb3BlcnR5RGVzY3JpcHRvck1vZHVsZS5mO1xudmFyIG5hdGl2ZURlZmluZVByb3BlcnR5ID0gZGVmaW5lUHJvcGVydHlNb2R1bGUuZjtcbnZhciBuYXRpdmVHZXRPd25Qcm9wZXJ0eU5hbWVzID0gZ2V0T3duUHJvcGVydHlOYW1lc0V4dGVybmFsLmY7XG52YXIgbmF0aXZlUHJvcGVydHlJc0VudW1lcmFibGUgPSBwcm9wZXJ0eUlzRW51bWVyYWJsZU1vZHVsZS5mO1xudmFyIEFsbFN5bWJvbHMgPSBzaGFyZWQoJ3N5bWJvbHMnKTtcbnZhciBPYmplY3RQcm90b3R5cGVTeW1ib2xzID0gc2hhcmVkKCdvcC1zeW1ib2xzJyk7XG52YXIgU3RyaW5nVG9TeW1ib2xSZWdpc3RyeSA9IHNoYXJlZCgnc3RyaW5nLXRvLXN5bWJvbC1yZWdpc3RyeScpO1xudmFyIFN5bWJvbFRvU3RyaW5nUmVnaXN0cnkgPSBzaGFyZWQoJ3N5bWJvbC10by1zdHJpbmctcmVnaXN0cnknKTtcbnZhciBXZWxsS25vd25TeW1ib2xzU3RvcmUgPSBzaGFyZWQoJ3drcycpO1xudmFyIFFPYmplY3QgPSBnbG9iYWwuUU9iamVjdDtcbi8vIERvbid0IHVzZSBzZXR0ZXJzIGluIFF0IFNjcmlwdCwgaHR0cHM6Ly9naXRodWIuY29tL3psb2lyb2NrL2NvcmUtanMvaXNzdWVzLzE3M1xudmFyIFVTRV9TRVRURVIgPSAhUU9iamVjdCB8fCAhUU9iamVjdFtQUk9UT1RZUEVdIHx8ICFRT2JqZWN0W1BST1RPVFlQRV0uZmluZENoaWxkO1xuXG4vLyBmYWxsYmFjayBmb3Igb2xkIEFuZHJvaWQsIGh0dHBzOi8vY29kZS5nb29nbGUuY29tL3AvdjgvaXNzdWVzL2RldGFpbD9pZD02ODdcbnZhciBzZXRTeW1ib2xEZXNjcmlwdG9yID0gREVTQ1JJUFRPUlMgJiYgZmFpbHMoZnVuY3Rpb24gKCkge1xuICByZXR1cm4gbmF0aXZlT2JqZWN0Q3JlYXRlKG5hdGl2ZURlZmluZVByb3BlcnR5KHt9LCAnYScsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHsgcmV0dXJuIG5hdGl2ZURlZmluZVByb3BlcnR5KHRoaXMsICdhJywgeyB2YWx1ZTogNyB9KS5hOyB9XG4gIH0pKS5hICE9IDc7XG59KSA/IGZ1bmN0aW9uIChPLCBQLCBBdHRyaWJ1dGVzKSB7XG4gIHZhciBPYmplY3RQcm90b3R5cGVEZXNjcmlwdG9yID0gbmF0aXZlR2V0T3duUHJvcGVydHlEZXNjcmlwdG9yKE9iamVjdFByb3RvdHlwZSwgUCk7XG4gIGlmIChPYmplY3RQcm90b3R5cGVEZXNjcmlwdG9yKSBkZWxldGUgT2JqZWN0UHJvdG90eXBlW1BdO1xuICBuYXRpdmVEZWZpbmVQcm9wZXJ0eShPLCBQLCBBdHRyaWJ1dGVzKTtcbiAgaWYgKE9iamVjdFByb3RvdHlwZURlc2NyaXB0b3IgJiYgTyAhPT0gT2JqZWN0UHJvdG90eXBlKSB7XG4gICAgbmF0aXZlRGVmaW5lUHJvcGVydHkoT2JqZWN0UHJvdG90eXBlLCBQLCBPYmplY3RQcm90b3R5cGVEZXNjcmlwdG9yKTtcbiAgfVxufSA6IG5hdGl2ZURlZmluZVByb3BlcnR5O1xuXG52YXIgd3JhcCA9IGZ1bmN0aW9uICh0YWcsIGRlc2NyaXB0aW9uKSB7XG4gIHZhciBzeW1ib2wgPSBBbGxTeW1ib2xzW3RhZ10gPSBuYXRpdmVPYmplY3RDcmVhdGUoJFN5bWJvbFtQUk9UT1RZUEVdKTtcbiAgc2V0SW50ZXJuYWxTdGF0ZShzeW1ib2wsIHtcbiAgICB0eXBlOiBTWU1CT0wsXG4gICAgdGFnOiB0YWcsXG4gICAgZGVzY3JpcHRpb246IGRlc2NyaXB0aW9uXG4gIH0pO1xuICBpZiAoIURFU0NSSVBUT1JTKSBzeW1ib2wuZGVzY3JpcHRpb24gPSBkZXNjcmlwdGlvbjtcbiAgcmV0dXJuIHN5bWJvbDtcbn07XG5cbnZhciBpc1N5bWJvbCA9IFVTRV9TWU1CT0xfQVNfVUlEID8gZnVuY3Rpb24gKGl0KSB7XG4gIHJldHVybiB0eXBlb2YgaXQgPT0gJ3N5bWJvbCc7XG59IDogZnVuY3Rpb24gKGl0KSB7XG4gIHJldHVybiBPYmplY3QoaXQpIGluc3RhbmNlb2YgJFN5bWJvbDtcbn07XG5cbnZhciAkZGVmaW5lUHJvcGVydHkgPSBmdW5jdGlvbiBkZWZpbmVQcm9wZXJ0eShPLCBQLCBBdHRyaWJ1dGVzKSB7XG4gIGlmIChPID09PSBPYmplY3RQcm90b3R5cGUpICRkZWZpbmVQcm9wZXJ0eShPYmplY3RQcm90b3R5cGVTeW1ib2xzLCBQLCBBdHRyaWJ1dGVzKTtcbiAgYW5PYmplY3QoTyk7XG4gIHZhciBrZXkgPSB0b1ByaW1pdGl2ZShQLCB0cnVlKTtcbiAgYW5PYmplY3QoQXR0cmlidXRlcyk7XG4gIGlmIChoYXMoQWxsU3ltYm9scywga2V5KSkge1xuICAgIGlmICghQXR0cmlidXRlcy5lbnVtZXJhYmxlKSB7XG4gICAgICBpZiAoIWhhcyhPLCBISURERU4pKSBuYXRpdmVEZWZpbmVQcm9wZXJ0eShPLCBISURERU4sIGNyZWF0ZVByb3BlcnR5RGVzY3JpcHRvcigxLCB7fSkpO1xuICAgICAgT1tISURERU5dW2tleV0gPSB0cnVlO1xuICAgIH0gZWxzZSB7XG4gICAgICBpZiAoaGFzKE8sIEhJRERFTikgJiYgT1tISURERU5dW2tleV0pIE9bSElEREVOXVtrZXldID0gZmFsc2U7XG4gICAgICBBdHRyaWJ1dGVzID0gbmF0aXZlT2JqZWN0Q3JlYXRlKEF0dHJpYnV0ZXMsIHsgZW51bWVyYWJsZTogY3JlYXRlUHJvcGVydHlEZXNjcmlwdG9yKDAsIGZhbHNlKSB9KTtcbiAgICB9IHJldHVybiBzZXRTeW1ib2xEZXNjcmlwdG9yKE8sIGtleSwgQXR0cmlidXRlcyk7XG4gIH0gcmV0dXJuIG5hdGl2ZURlZmluZVByb3BlcnR5KE8sIGtleSwgQXR0cmlidXRlcyk7XG59O1xuXG52YXIgJGRlZmluZVByb3BlcnRpZXMgPSBmdW5jdGlvbiBkZWZpbmVQcm9wZXJ0aWVzKE8sIFByb3BlcnRpZXMpIHtcbiAgYW5PYmplY3QoTyk7XG4gIHZhciBwcm9wZXJ0aWVzID0gdG9JbmRleGVkT2JqZWN0KFByb3BlcnRpZXMpO1xuICB2YXIga2V5cyA9IG9iamVjdEtleXMocHJvcGVydGllcykuY29uY2F0KCRnZXRPd25Qcm9wZXJ0eVN5bWJvbHMocHJvcGVydGllcykpO1xuICAkZm9yRWFjaChrZXlzLCBmdW5jdGlvbiAoa2V5KSB7XG4gICAgaWYgKCFERVNDUklQVE9SUyB8fCAkcHJvcGVydHlJc0VudW1lcmFibGUuY2FsbChwcm9wZXJ0aWVzLCBrZXkpKSAkZGVmaW5lUHJvcGVydHkoTywga2V5LCBwcm9wZXJ0aWVzW2tleV0pO1xuICB9KTtcbiAgcmV0dXJuIE87XG59O1xuXG52YXIgJGNyZWF0ZSA9IGZ1bmN0aW9uIGNyZWF0ZShPLCBQcm9wZXJ0aWVzKSB7XG4gIHJldHVybiBQcm9wZXJ0aWVzID09PSB1bmRlZmluZWQgPyBuYXRpdmVPYmplY3RDcmVhdGUoTykgOiAkZGVmaW5lUHJvcGVydGllcyhuYXRpdmVPYmplY3RDcmVhdGUoTyksIFByb3BlcnRpZXMpO1xufTtcblxudmFyICRwcm9wZXJ0eUlzRW51bWVyYWJsZSA9IGZ1bmN0aW9uIHByb3BlcnR5SXNFbnVtZXJhYmxlKFYpIHtcbiAgdmFyIFAgPSB0b1ByaW1pdGl2ZShWLCB0cnVlKTtcbiAgdmFyIGVudW1lcmFibGUgPSBuYXRpdmVQcm9wZXJ0eUlzRW51bWVyYWJsZS5jYWxsKHRoaXMsIFApO1xuICBpZiAodGhpcyA9PT0gT2JqZWN0UHJvdG90eXBlICYmIGhhcyhBbGxTeW1ib2xzLCBQKSAmJiAhaGFzKE9iamVjdFByb3RvdHlwZVN5bWJvbHMsIFApKSByZXR1cm4gZmFsc2U7XG4gIHJldHVybiBlbnVtZXJhYmxlIHx8ICFoYXModGhpcywgUCkgfHwgIWhhcyhBbGxTeW1ib2xzLCBQKSB8fCBoYXModGhpcywgSElEREVOKSAmJiB0aGlzW0hJRERFTl1bUF0gPyBlbnVtZXJhYmxlIDogdHJ1ZTtcbn07XG5cbnZhciAkZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yID0gZnVuY3Rpb24gZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yKE8sIFApIHtcbiAgdmFyIGl0ID0gdG9JbmRleGVkT2JqZWN0KE8pO1xuICB2YXIga2V5ID0gdG9QcmltaXRpdmUoUCwgdHJ1ZSk7XG4gIGlmIChpdCA9PT0gT2JqZWN0UHJvdG90eXBlICYmIGhhcyhBbGxTeW1ib2xzLCBrZXkpICYmICFoYXMoT2JqZWN0UHJvdG90eXBlU3ltYm9scywga2V5KSkgcmV0dXJuO1xuICB2YXIgZGVzY3JpcHRvciA9IG5hdGl2ZUdldE93blByb3BlcnR5RGVzY3JpcHRvcihpdCwga2V5KTtcbiAgaWYgKGRlc2NyaXB0b3IgJiYgaGFzKEFsbFN5bWJvbHMsIGtleSkgJiYgIShoYXMoaXQsIEhJRERFTikgJiYgaXRbSElEREVOXVtrZXldKSkge1xuICAgIGRlc2NyaXB0b3IuZW51bWVyYWJsZSA9IHRydWU7XG4gIH1cbiAgcmV0dXJuIGRlc2NyaXB0b3I7XG59O1xuXG52YXIgJGdldE93blByb3BlcnR5TmFtZXMgPSBmdW5jdGlvbiBnZXRPd25Qcm9wZXJ0eU5hbWVzKE8pIHtcbiAgdmFyIG5hbWVzID0gbmF0aXZlR2V0T3duUHJvcGVydHlOYW1lcyh0b0luZGV4ZWRPYmplY3QoTykpO1xuICB2YXIgcmVzdWx0ID0gW107XG4gICRmb3JFYWNoKG5hbWVzLCBmdW5jdGlvbiAoa2V5KSB7XG4gICAgaWYgKCFoYXMoQWxsU3ltYm9scywga2V5KSAmJiAhaGFzKGhpZGRlbktleXMsIGtleSkpIHJlc3VsdC5wdXNoKGtleSk7XG4gIH0pO1xuICByZXR1cm4gcmVzdWx0O1xufTtcblxudmFyICRnZXRPd25Qcm9wZXJ0eVN5bWJvbHMgPSBmdW5jdGlvbiBnZXRPd25Qcm9wZXJ0eVN5bWJvbHMoTykge1xuICB2YXIgSVNfT0JKRUNUX1BST1RPVFlQRSA9IE8gPT09IE9iamVjdFByb3RvdHlwZTtcbiAgdmFyIG5hbWVzID0gbmF0aXZlR2V0T3duUHJvcGVydHlOYW1lcyhJU19PQkpFQ1RfUFJPVE9UWVBFID8gT2JqZWN0UHJvdG90eXBlU3ltYm9scyA6IHRvSW5kZXhlZE9iamVjdChPKSk7XG4gIHZhciByZXN1bHQgPSBbXTtcbiAgJGZvckVhY2gobmFtZXMsIGZ1bmN0aW9uIChrZXkpIHtcbiAgICBpZiAoaGFzKEFsbFN5bWJvbHMsIGtleSkgJiYgKCFJU19PQkpFQ1RfUFJPVE9UWVBFIHx8IGhhcyhPYmplY3RQcm90b3R5cGUsIGtleSkpKSB7XG4gICAgICByZXN1bHQucHVzaChBbGxTeW1ib2xzW2tleV0pO1xuICAgIH1cbiAgfSk7XG4gIHJldHVybiByZXN1bHQ7XG59O1xuXG4vLyBgU3ltYm9sYCBjb25zdHJ1Y3RvclxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zeW1ib2wtY29uc3RydWN0b3JcbmlmICghTkFUSVZFX1NZTUJPTCkge1xuICAkU3ltYm9sID0gZnVuY3Rpb24gU3ltYm9sKCkge1xuICAgIGlmICh0aGlzIGluc3RhbmNlb2YgJFN5bWJvbCkgdGhyb3cgVHlwZUVycm9yKCdTeW1ib2wgaXMgbm90IGEgY29uc3RydWN0b3InKTtcbiAgICB2YXIgZGVzY3JpcHRpb24gPSAhYXJndW1lbnRzLmxlbmd0aCB8fCBhcmd1bWVudHNbMF0gPT09IHVuZGVmaW5lZCA/IHVuZGVmaW5lZCA6IFN0cmluZyhhcmd1bWVudHNbMF0pO1xuICAgIHZhciB0YWcgPSB1aWQoZGVzY3JpcHRpb24pO1xuICAgIHZhciBzZXR0ZXIgPSBmdW5jdGlvbiAodmFsdWUpIHtcbiAgICAgIGlmICh0aGlzID09PSBPYmplY3RQcm90b3R5cGUpIHNldHRlci5jYWxsKE9iamVjdFByb3RvdHlwZVN5bWJvbHMsIHZhbHVlKTtcbiAgICAgIGlmIChoYXModGhpcywgSElEREVOKSAmJiBoYXModGhpc1tISURERU5dLCB0YWcpKSB0aGlzW0hJRERFTl1bdGFnXSA9IGZhbHNlO1xuICAgICAgc2V0U3ltYm9sRGVzY3JpcHRvcih0aGlzLCB0YWcsIGNyZWF0ZVByb3BlcnR5RGVzY3JpcHRvcigxLCB2YWx1ZSkpO1xuICAgIH07XG4gICAgaWYgKERFU0NSSVBUT1JTICYmIFVTRV9TRVRURVIpIHNldFN5bWJvbERlc2NyaXB0b3IoT2JqZWN0UHJvdG90eXBlLCB0YWcsIHsgY29uZmlndXJhYmxlOiB0cnVlLCBzZXQ6IHNldHRlciB9KTtcbiAgICByZXR1cm4gd3JhcCh0YWcsIGRlc2NyaXB0aW9uKTtcbiAgfTtcblxuICByZWRlZmluZSgkU3ltYm9sW1BST1RPVFlQRV0sICd0b1N0cmluZycsIGZ1bmN0aW9uIHRvU3RyaW5nKCkge1xuICAgIHJldHVybiBnZXRJbnRlcm5hbFN0YXRlKHRoaXMpLnRhZztcbiAgfSk7XG5cbiAgcmVkZWZpbmUoJFN5bWJvbCwgJ3dpdGhvdXRTZXR0ZXInLCBmdW5jdGlvbiAoZGVzY3JpcHRpb24pIHtcbiAgICByZXR1cm4gd3JhcCh1aWQoZGVzY3JpcHRpb24pLCBkZXNjcmlwdGlvbik7XG4gIH0pO1xuXG4gIHByb3BlcnR5SXNFbnVtZXJhYmxlTW9kdWxlLmYgPSAkcHJvcGVydHlJc0VudW1lcmFibGU7XG4gIGRlZmluZVByb3BlcnR5TW9kdWxlLmYgPSAkZGVmaW5lUHJvcGVydHk7XG4gIGdldE93blByb3BlcnR5RGVzY3JpcHRvck1vZHVsZS5mID0gJGdldE93blByb3BlcnR5RGVzY3JpcHRvcjtcbiAgZ2V0T3duUHJvcGVydHlOYW1lc01vZHVsZS5mID0gZ2V0T3duUHJvcGVydHlOYW1lc0V4dGVybmFsLmYgPSAkZ2V0T3duUHJvcGVydHlOYW1lcztcbiAgZ2V0T3duUHJvcGVydHlTeW1ib2xzTW9kdWxlLmYgPSAkZ2V0T3duUHJvcGVydHlTeW1ib2xzO1xuXG4gIHdyYXBwZWRXZWxsS25vd25TeW1ib2xNb2R1bGUuZiA9IGZ1bmN0aW9uIChuYW1lKSB7XG4gICAgcmV0dXJuIHdyYXAod2VsbEtub3duU3ltYm9sKG5hbWUpLCBuYW1lKTtcbiAgfTtcblxuICBpZiAoREVTQ1JJUFRPUlMpIHtcbiAgICAvLyBodHRwczovL2dpdGh1Yi5jb20vdGMzOS9wcm9wb3NhbC1TeW1ib2wtZGVzY3JpcHRpb25cbiAgICBuYXRpdmVEZWZpbmVQcm9wZXJ0eSgkU3ltYm9sW1BST1RPVFlQRV0sICdkZXNjcmlwdGlvbicsIHtcbiAgICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZSxcbiAgICAgIGdldDogZnVuY3Rpb24gZGVzY3JpcHRpb24oKSB7XG4gICAgICAgIHJldHVybiBnZXRJbnRlcm5hbFN0YXRlKHRoaXMpLmRlc2NyaXB0aW9uO1xuICAgICAgfVxuICAgIH0pO1xuICAgIGlmICghSVNfUFVSRSkge1xuICAgICAgcmVkZWZpbmUoT2JqZWN0UHJvdG90eXBlLCAncHJvcGVydHlJc0VudW1lcmFibGUnLCAkcHJvcGVydHlJc0VudW1lcmFibGUsIHsgdW5zYWZlOiB0cnVlIH0pO1xuICAgIH1cbiAgfVxufVxuXG4kKHsgZ2xvYmFsOiB0cnVlLCB3cmFwOiB0cnVlLCBmb3JjZWQ6ICFOQVRJVkVfU1lNQk9MLCBzaGFtOiAhTkFUSVZFX1NZTUJPTCB9LCB7XG4gIFN5bWJvbDogJFN5bWJvbFxufSk7XG5cbiRmb3JFYWNoKG9iamVjdEtleXMoV2VsbEtub3duU3ltYm9sc1N0b3JlKSwgZnVuY3Rpb24gKG5hbWUpIHtcbiAgZGVmaW5lV2VsbEtub3duU3ltYm9sKG5hbWUpO1xufSk7XG5cbiQoeyB0YXJnZXQ6IFNZTUJPTCwgc3RhdDogdHJ1ZSwgZm9yY2VkOiAhTkFUSVZFX1NZTUJPTCB9LCB7XG4gIC8vIGBTeW1ib2wuZm9yYCBtZXRob2RcbiAgLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zeW1ib2wuZm9yXG4gICdmb3InOiBmdW5jdGlvbiAoa2V5KSB7XG4gICAgdmFyIHN0cmluZyA9IFN0cmluZyhrZXkpO1xuICAgIGlmIChoYXMoU3RyaW5nVG9TeW1ib2xSZWdpc3RyeSwgc3RyaW5nKSkgcmV0dXJuIFN0cmluZ1RvU3ltYm9sUmVnaXN0cnlbc3RyaW5nXTtcbiAgICB2YXIgc3ltYm9sID0gJFN5bWJvbChzdHJpbmcpO1xuICAgIFN0cmluZ1RvU3ltYm9sUmVnaXN0cnlbc3RyaW5nXSA9IHN5bWJvbDtcbiAgICBTeW1ib2xUb1N0cmluZ1JlZ2lzdHJ5W3N5bWJvbF0gPSBzdHJpbmc7XG4gICAgcmV0dXJuIHN5bWJvbDtcbiAgfSxcbiAgLy8gYFN5bWJvbC5rZXlGb3JgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXN5bWJvbC5rZXlmb3JcbiAga2V5Rm9yOiBmdW5jdGlvbiBrZXlGb3Ioc3ltKSB7XG4gICAgaWYgKCFpc1N5bWJvbChzeW0pKSB0aHJvdyBUeXBlRXJyb3Ioc3ltICsgJyBpcyBub3QgYSBzeW1ib2wnKTtcbiAgICBpZiAoaGFzKFN5bWJvbFRvU3RyaW5nUmVnaXN0cnksIHN5bSkpIHJldHVybiBTeW1ib2xUb1N0cmluZ1JlZ2lzdHJ5W3N5bV07XG4gIH0sXG4gIHVzZVNldHRlcjogZnVuY3Rpb24gKCkgeyBVU0VfU0VUVEVSID0gdHJ1ZTsgfSxcbiAgdXNlU2ltcGxlOiBmdW5jdGlvbiAoKSB7IFVTRV9TRVRURVIgPSBmYWxzZTsgfVxufSk7XG5cbiQoeyB0YXJnZXQ6ICdPYmplY3QnLCBzdGF0OiB0cnVlLCBmb3JjZWQ6ICFOQVRJVkVfU1lNQk9MLCBzaGFtOiAhREVTQ1JJUFRPUlMgfSwge1xuICAvLyBgT2JqZWN0LmNyZWF0ZWAgbWV0aG9kXG4gIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtb2JqZWN0LmNyZWF0ZVxuICBjcmVhdGU6ICRjcmVhdGUsXG4gIC8vIGBPYmplY3QuZGVmaW5lUHJvcGVydHlgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5kZWZpbmVwcm9wZXJ0eVxuICBkZWZpbmVQcm9wZXJ0eTogJGRlZmluZVByb3BlcnR5LFxuICAvLyBgT2JqZWN0LmRlZmluZVByb3BlcnRpZXNgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5kZWZpbmVwcm9wZXJ0aWVzXG4gIGRlZmluZVByb3BlcnRpZXM6ICRkZWZpbmVQcm9wZXJ0aWVzLFxuICAvLyBgT2JqZWN0LmdldE93blByb3BlcnR5RGVzY3JpcHRvcmAgbWV0aG9kXG4gIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtb2JqZWN0LmdldG93bnByb3BlcnR5ZGVzY3JpcHRvcnNcbiAgZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yOiAkZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yXG59KTtcblxuJCh7IHRhcmdldDogJ09iamVjdCcsIHN0YXQ6IHRydWUsIGZvcmNlZDogIU5BVElWRV9TWU1CT0wgfSwge1xuICAvLyBgT2JqZWN0LmdldE93blByb3BlcnR5TmFtZXNgIG1ldGhvZFxuICAvLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLW9iamVjdC5nZXRvd25wcm9wZXJ0eW5hbWVzXG4gIGdldE93blByb3BlcnR5TmFtZXM6ICRnZXRPd25Qcm9wZXJ0eU5hbWVzLFxuICAvLyBgT2JqZWN0LmdldE93blByb3BlcnR5U3ltYm9sc2AgbWV0aG9kXG4gIC8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtb2JqZWN0LmdldG93bnByb3BlcnR5c3ltYm9sc1xuICBnZXRPd25Qcm9wZXJ0eVN5bWJvbHM6ICRnZXRPd25Qcm9wZXJ0eVN5bWJvbHNcbn0pO1xuXG4vLyBDaHJvbWUgMzggYW5kIDM5IGBPYmplY3QuZ2V0T3duUHJvcGVydHlTeW1ib2xzYCBmYWlscyBvbiBwcmltaXRpdmVzXG4vLyBodHRwczovL2J1Z3MuY2hyb21pdW0ub3JnL3AvdjgvaXNzdWVzL2RldGFpbD9pZD0zNDQzXG4kKHsgdGFyZ2V0OiAnT2JqZWN0Jywgc3RhdDogdHJ1ZSwgZm9yY2VkOiBmYWlscyhmdW5jdGlvbiAoKSB7IGdldE93blByb3BlcnR5U3ltYm9sc01vZHVsZS5mKDEpOyB9KSB9LCB7XG4gIGdldE93blByb3BlcnR5U3ltYm9sczogZnVuY3Rpb24gZ2V0T3duUHJvcGVydHlTeW1ib2xzKGl0KSB7XG4gICAgcmV0dXJuIGdldE93blByb3BlcnR5U3ltYm9sc01vZHVsZS5mKHRvT2JqZWN0KGl0KSk7XG4gIH1cbn0pO1xuXG4vLyBgSlNPTi5zdHJpbmdpZnlgIG1ldGhvZCBiZWhhdmlvciB3aXRoIHN5bWJvbHNcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtanNvbi5zdHJpbmdpZnlcbmlmICgkc3RyaW5naWZ5KSB7XG4gIHZhciBGT1JDRURfSlNPTl9TVFJJTkdJRlkgPSAhTkFUSVZFX1NZTUJPTCB8fCBmYWlscyhmdW5jdGlvbiAoKSB7XG4gICAgdmFyIHN5bWJvbCA9ICRTeW1ib2woKTtcbiAgICAvLyBNUyBFZGdlIGNvbnZlcnRzIHN5bWJvbCB2YWx1ZXMgdG8gSlNPTiBhcyB7fVxuICAgIHJldHVybiAkc3RyaW5naWZ5KFtzeW1ib2xdKSAhPSAnW251bGxdJ1xuICAgICAgLy8gV2ViS2l0IGNvbnZlcnRzIHN5bWJvbCB2YWx1ZXMgdG8gSlNPTiBhcyBudWxsXG4gICAgICB8fCAkc3RyaW5naWZ5KHsgYTogc3ltYm9sIH0pICE9ICd7fSdcbiAgICAgIC8vIFY4IHRocm93cyBvbiBib3hlZCBzeW1ib2xzXG4gICAgICB8fCAkc3RyaW5naWZ5KE9iamVjdChzeW1ib2wpKSAhPSAne30nO1xuICB9KTtcblxuICAkKHsgdGFyZ2V0OiAnSlNPTicsIHN0YXQ6IHRydWUsIGZvcmNlZDogRk9SQ0VEX0pTT05fU1RSSU5HSUZZIH0sIHtcbiAgICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgbm8tdW51c2VkLXZhcnMgLS0gcmVxdWlyZWQgZm9yIGAubGVuZ3RoYFxuICAgIHN0cmluZ2lmeTogZnVuY3Rpb24gc3RyaW5naWZ5KGl0LCByZXBsYWNlciwgc3BhY2UpIHtcbiAgICAgIHZhciBhcmdzID0gW2l0XTtcbiAgICAgIHZhciBpbmRleCA9IDE7XG4gICAgICB2YXIgJHJlcGxhY2VyO1xuICAgICAgd2hpbGUgKGFyZ3VtZW50cy5sZW5ndGggPiBpbmRleCkgYXJncy5wdXNoKGFyZ3VtZW50c1tpbmRleCsrXSk7XG4gICAgICAkcmVwbGFjZXIgPSByZXBsYWNlcjtcbiAgICAgIGlmICghaXNPYmplY3QocmVwbGFjZXIpICYmIGl0ID09PSB1bmRlZmluZWQgfHwgaXNTeW1ib2woaXQpKSByZXR1cm47IC8vIElFOCByZXR1cm5zIHN0cmluZyBvbiB1bmRlZmluZWRcbiAgICAgIGlmICghaXNBcnJheShyZXBsYWNlcikpIHJlcGxhY2VyID0gZnVuY3Rpb24gKGtleSwgdmFsdWUpIHtcbiAgICAgICAgaWYgKHR5cGVvZiAkcmVwbGFjZXIgPT0gJ2Z1bmN0aW9uJykgdmFsdWUgPSAkcmVwbGFjZXIuY2FsbCh0aGlzLCBrZXksIHZhbHVlKTtcbiAgICAgICAgaWYgKCFpc1N5bWJvbCh2YWx1ZSkpIHJldHVybiB2YWx1ZTtcbiAgICAgIH07XG4gICAgICBhcmdzWzFdID0gcmVwbGFjZXI7XG4gICAgICByZXR1cm4gJHN0cmluZ2lmeS5hcHBseShudWxsLCBhcmdzKTtcbiAgICB9XG4gIH0pO1xufVxuXG4vLyBgU3ltYm9sLnByb3RvdHlwZVtAQHRvUHJpbWl0aXZlXWAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLXN5bWJvbC5wcm90b3R5cGUtQEB0b3ByaW1pdGl2ZVxuaWYgKCEkU3ltYm9sW1BST1RPVFlQRV1bVE9fUFJJTUlUSVZFXSkge1xuICBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkoJFN5bWJvbFtQUk9UT1RZUEVdLCBUT19QUklNSVRJVkUsICRTeW1ib2xbUFJPVE9UWVBFXS52YWx1ZU9mKTtcbn1cbi8vIGBTeW1ib2wucHJvdG90eXBlW0BAdG9TdHJpbmdUYWddYCBwcm9wZXJ0eVxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zeW1ib2wucHJvdG90eXBlLUBAdG9zdHJpbmd0YWdcbnNldFRvU3RyaW5nVGFnKCRTeW1ib2wsIFNZTUJPTCk7XG5cbmhpZGRlbktleXNbSElEREVOXSA9IHRydWU7XG4iLCAiLy8gYFN5bWJvbC5wcm90b3R5cGUuZGVzY3JpcHRpb25gIGdldHRlclxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zeW1ib2wucHJvdG90eXBlLmRlc2NyaXB0aW9uXG4ndXNlIHN0cmljdCc7XG52YXIgJCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9leHBvcnQnKTtcbnZhciBERVNDUklQVE9SUyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9kZXNjcmlwdG9ycycpO1xudmFyIGdsb2JhbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9nbG9iYWwnKTtcbnZhciBoYXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaGFzJyk7XG52YXIgaXNPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtb2JqZWN0Jyk7XG52YXIgZGVmaW5lUHJvcGVydHkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWRlZmluZS1wcm9wZXJ0eScpLmY7XG52YXIgY29weUNvbnN0cnVjdG9yUHJvcGVydGllcyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jb3B5LWNvbnN0cnVjdG9yLXByb3BlcnRpZXMnKTtcblxudmFyIE5hdGl2ZVN5bWJvbCA9IGdsb2JhbC5TeW1ib2w7XG5cbmlmIChERVNDUklQVE9SUyAmJiB0eXBlb2YgTmF0aXZlU3ltYm9sID09ICdmdW5jdGlvbicgJiYgKCEoJ2Rlc2NyaXB0aW9uJyBpbiBOYXRpdmVTeW1ib2wucHJvdG90eXBlKSB8fFxuICAvLyBTYWZhcmkgMTIgYnVnXG4gIE5hdGl2ZVN5bWJvbCgpLmRlc2NyaXB0aW9uICE9PSB1bmRlZmluZWRcbikpIHtcbiAgdmFyIEVtcHR5U3RyaW5nRGVzY3JpcHRpb25TdG9yZSA9IHt9O1xuICAvLyB3cmFwIFN5bWJvbCBjb25zdHJ1Y3RvciBmb3IgY29ycmVjdCB3b3JrIHdpdGggdW5kZWZpbmVkIGRlc2NyaXB0aW9uXG4gIHZhciBTeW1ib2xXcmFwcGVyID0gZnVuY3Rpb24gU3ltYm9sKCkge1xuICAgIHZhciBkZXNjcmlwdGlvbiA9IGFyZ3VtZW50cy5sZW5ndGggPCAxIHx8IGFyZ3VtZW50c1swXSA9PT0gdW5kZWZpbmVkID8gdW5kZWZpbmVkIDogU3RyaW5nKGFyZ3VtZW50c1swXSk7XG4gICAgdmFyIHJlc3VsdCA9IHRoaXMgaW5zdGFuY2VvZiBTeW1ib2xXcmFwcGVyXG4gICAgICA/IG5ldyBOYXRpdmVTeW1ib2woZGVzY3JpcHRpb24pXG4gICAgICAvLyBpbiBFZGdlIDEzLCBTdHJpbmcoU3ltYm9sKHVuZGVmaW5lZCkpID09PSAnU3ltYm9sKHVuZGVmaW5lZCknXG4gICAgICA6IGRlc2NyaXB0aW9uID09PSB1bmRlZmluZWQgPyBOYXRpdmVTeW1ib2woKSA6IE5hdGl2ZVN5bWJvbChkZXNjcmlwdGlvbik7XG4gICAgaWYgKGRlc2NyaXB0aW9uID09PSAnJykgRW1wdHlTdHJpbmdEZXNjcmlwdGlvblN0b3JlW3Jlc3VsdF0gPSB0cnVlO1xuICAgIHJldHVybiByZXN1bHQ7XG4gIH07XG4gIGNvcHlDb25zdHJ1Y3RvclByb3BlcnRpZXMoU3ltYm9sV3JhcHBlciwgTmF0aXZlU3ltYm9sKTtcbiAgdmFyIHN5bWJvbFByb3RvdHlwZSA9IFN5bWJvbFdyYXBwZXIucHJvdG90eXBlID0gTmF0aXZlU3ltYm9sLnByb3RvdHlwZTtcbiAgc3ltYm9sUHJvdG90eXBlLmNvbnN0cnVjdG9yID0gU3ltYm9sV3JhcHBlcjtcblxuICB2YXIgc3ltYm9sVG9TdHJpbmcgPSBzeW1ib2xQcm90b3R5cGUudG9TdHJpbmc7XG4gIHZhciBuYXRpdmUgPSBTdHJpbmcoTmF0aXZlU3ltYm9sKCd0ZXN0JykpID09ICdTeW1ib2wodGVzdCknO1xuICB2YXIgcmVnZXhwID0gL15TeW1ib2xcXCgoLiopXFwpW14pXSskLztcbiAgZGVmaW5lUHJvcGVydHkoc3ltYm9sUHJvdG90eXBlLCAnZGVzY3JpcHRpb24nLCB7XG4gICAgY29uZmlndXJhYmxlOiB0cnVlLFxuICAgIGdldDogZnVuY3Rpb24gZGVzY3JpcHRpb24oKSB7XG4gICAgICB2YXIgc3ltYm9sID0gaXNPYmplY3QodGhpcykgPyB0aGlzLnZhbHVlT2YoKSA6IHRoaXM7XG4gICAgICB2YXIgc3RyaW5nID0gc3ltYm9sVG9TdHJpbmcuY2FsbChzeW1ib2wpO1xuICAgICAgaWYgKGhhcyhFbXB0eVN0cmluZ0Rlc2NyaXB0aW9uU3RvcmUsIHN5bWJvbCkpIHJldHVybiAnJztcbiAgICAgIHZhciBkZXNjID0gbmF0aXZlID8gc3RyaW5nLnNsaWNlKDcsIC0xKSA6IHN0cmluZy5yZXBsYWNlKHJlZ2V4cCwgJyQxJyk7XG4gICAgICByZXR1cm4gZGVzYyA9PT0gJycgPyB1bmRlZmluZWQgOiBkZXNjO1xuICAgIH1cbiAgfSk7XG5cbiAgJCh7IGdsb2JhbDogdHJ1ZSwgZm9yY2VkOiB0cnVlIH0sIHtcbiAgICBTeW1ib2w6IFN5bWJvbFdyYXBwZXJcbiAgfSk7XG59XG4iLCAidmFyIGRlZmluZVdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9kZWZpbmUtd2VsbC1rbm93bi1zeW1ib2wnKTtcblxuLy8gYFN5bWJvbC5pdGVyYXRvcmAgd2VsbC1rbm93biBzeW1ib2xcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtc3ltYm9sLml0ZXJhdG9yXG5kZWZpbmVXZWxsS25vd25TeW1ib2woJ2l0ZXJhdG9yJyk7XG4iLCAiJ3VzZSBzdHJpY3QnO1xudmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgZm9yRWFjaCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9hcnJheS1mb3ItZWFjaCcpO1xuXG4vLyBgQXJyYXkucHJvdG90eXBlLmZvckVhY2hgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuZm9yZWFjaFxuLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLWFycmF5LXByb3RvdHlwZS1mb3JlYWNoIC0tIHNhZmVcbiQoeyB0YXJnZXQ6ICdBcnJheScsIHByb3RvOiB0cnVlLCBmb3JjZWQ6IFtdLmZvckVhY2ggIT0gZm9yRWFjaCB9LCB7XG4gIGZvckVhY2g6IGZvckVhY2hcbn0pO1xuIiwgInZhciBnbG9iYWwgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZ2xvYmFsJyk7XG52YXIgRE9NSXRlcmFibGVzID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2RvbS1pdGVyYWJsZXMnKTtcbnZhciBmb3JFYWNoID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FycmF5LWZvci1lYWNoJyk7XG52YXIgY3JlYXRlTm9uRW51bWVyYWJsZVByb3BlcnR5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1ub24tZW51bWVyYWJsZS1wcm9wZXJ0eScpO1xuXG5mb3IgKHZhciBDT0xMRUNUSU9OX05BTUUgaW4gRE9NSXRlcmFibGVzKSB7XG4gIHZhciBDb2xsZWN0aW9uID0gZ2xvYmFsW0NPTExFQ1RJT05fTkFNRV07XG4gIHZhciBDb2xsZWN0aW9uUHJvdG90eXBlID0gQ29sbGVjdGlvbiAmJiBDb2xsZWN0aW9uLnByb3RvdHlwZTtcbiAgLy8gc29tZSBDaHJvbWUgdmVyc2lvbnMgaGF2ZSBub24tY29uZmlndXJhYmxlIG1ldGhvZHMgb24gRE9NVG9rZW5MaXN0XG4gIGlmIChDb2xsZWN0aW9uUHJvdG90eXBlICYmIENvbGxlY3Rpb25Qcm90b3R5cGUuZm9yRWFjaCAhPT0gZm9yRWFjaCkgdHJ5IHtcbiAgICBjcmVhdGVOb25FbnVtZXJhYmxlUHJvcGVydHkoQ29sbGVjdGlvblByb3RvdHlwZSwgJ2ZvckVhY2gnLCBmb3JFYWNoKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBDb2xsZWN0aW9uUHJvdG90eXBlLmZvckVhY2ggPSBmb3JFYWNoO1xuICB9XG59XG4iLCAidmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgJGVudHJpZXMgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LXRvLWFycmF5JykuZW50cmllcztcblxuLy8gYE9iamVjdC5lbnRyaWVzYCBtZXRob2Rcbi8vIGh0dHBzOi8vdGMzOS5lcy9lY21hMjYyLyNzZWMtb2JqZWN0LmVudHJpZXNcbiQoeyB0YXJnZXQ6ICdPYmplY3QnLCBzdGF0OiB0cnVlIH0sIHtcbiAgZW50cmllczogZnVuY3Rpb24gZW50cmllcyhPKSB7XG4gICAgcmV0dXJuICRlbnRyaWVzKE8pO1xuICB9XG59KTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgJCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9leHBvcnQnKTtcbnZhciBnZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvb2JqZWN0LWdldC1vd24tcHJvcGVydHktZGVzY3JpcHRvcicpLmY7XG52YXIgdG9MZW5ndGggPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvdG8tbGVuZ3RoJyk7XG52YXIgbm90QVJlZ0V4cCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9ub3QtYS1yZWdleHAnKTtcbnZhciByZXF1aXJlT2JqZWN0Q29lcmNpYmxlID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3JlcXVpcmUtb2JqZWN0LWNvZXJjaWJsZScpO1xudmFyIGNvcnJlY3RJc1JlZ0V4cExvZ2ljID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NvcnJlY3QtaXMtcmVnZXhwLWxvZ2ljJyk7XG52YXIgSVNfUFVSRSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1wdXJlJyk7XG5cbi8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBlcy9uby1zdHJpbmctcHJvdG90eXBlLXN0YXJ0c3dpdGggLS0gc2FmZVxudmFyICRzdGFydHNXaXRoID0gJycuc3RhcnRzV2l0aDtcbnZhciBtaW4gPSBNYXRoLm1pbjtcblxudmFyIENPUlJFQ1RfSVNfUkVHRVhQX0xPR0lDID0gY29ycmVjdElzUmVnRXhwTG9naWMoJ3N0YXJ0c1dpdGgnKTtcbi8vIGh0dHBzOi8vZ2l0aHViLmNvbS96bG9pcm9jay9jb3JlLWpzL3B1bGwvNzAyXG52YXIgTUROX1BPTFlGSUxMX0JVRyA9ICFJU19QVVJFICYmICFDT1JSRUNUX0lTX1JFR0VYUF9MT0dJQyAmJiAhIWZ1bmN0aW9uICgpIHtcbiAgdmFyIGRlc2NyaXB0b3IgPSBnZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IoU3RyaW5nLnByb3RvdHlwZSwgJ3N0YXJ0c1dpdGgnKTtcbiAgcmV0dXJuIGRlc2NyaXB0b3IgJiYgIWRlc2NyaXB0b3Iud3JpdGFibGU7XG59KCk7XG5cbi8vIGBTdHJpbmcucHJvdG90eXBlLnN0YXJ0c1dpdGhgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1zdHJpbmcucHJvdG90eXBlLnN0YXJ0c3dpdGhcbiQoeyB0YXJnZXQ6ICdTdHJpbmcnLCBwcm90bzogdHJ1ZSwgZm9yY2VkOiAhTUROX1BPTFlGSUxMX0JVRyAmJiAhQ09SUkVDVF9JU19SRUdFWFBfTE9HSUMgfSwge1xuICBzdGFydHNXaXRoOiBmdW5jdGlvbiBzdGFydHNXaXRoKHNlYXJjaFN0cmluZyAvKiAsIHBvc2l0aW9uID0gMCAqLykge1xuICAgIHZhciB0aGF0ID0gU3RyaW5nKHJlcXVpcmVPYmplY3RDb2VyY2libGUodGhpcykpO1xuICAgIG5vdEFSZWdFeHAoc2VhcmNoU3RyaW5nKTtcbiAgICB2YXIgaW5kZXggPSB0b0xlbmd0aChtaW4oYXJndW1lbnRzLmxlbmd0aCA+IDEgPyBhcmd1bWVudHNbMV0gOiB1bmRlZmluZWQsIHRoYXQubGVuZ3RoKSk7XG4gICAgdmFyIHNlYXJjaCA9IFN0cmluZyhzZWFyY2hTdHJpbmcpO1xuICAgIHJldHVybiAkc3RhcnRzV2l0aFxuICAgICAgPyAkc3RhcnRzV2l0aC5jYWxsKHRoYXQsIHNlYXJjaCwgaW5kZXgpXG4gICAgICA6IHRoYXQuc2xpY2UoaW5kZXgsIGluZGV4ICsgc2VhcmNoLmxlbmd0aCkgPT09IHNlYXJjaDtcbiAgfVxufSk7XG4iLCAidmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgaXNBcnJheSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1hcnJheScpO1xuXG4vLyBgQXJyYXkuaXNBcnJheWAgbWV0aG9kXG4vLyBodHRwczovL3RjMzkuZXMvZWNtYTI2Mi8jc2VjLWFycmF5LmlzYXJyYXlcbiQoeyB0YXJnZXQ6ICdBcnJheScsIHN0YXQ6IHRydWUgfSwge1xuICBpc0FycmF5OiBpc0FycmF5XG59KTtcbiIsICJmdW5jdGlvbiBfc2xpY2VkVG9BcnJheShhcnIsIGkpIHsgcmV0dXJuIF9hcnJheVdpdGhIb2xlcyhhcnIpIHx8IF9pdGVyYWJsZVRvQXJyYXlMaW1pdChhcnIsIGkpIHx8IF91bnN1cHBvcnRlZEl0ZXJhYmxlVG9BcnJheShhcnIsIGkpIHx8IF9ub25JdGVyYWJsZVJlc3QoKTsgfVxuXG5mdW5jdGlvbiBfbm9uSXRlcmFibGVSZXN0KCkgeyB0aHJvdyBuZXcgVHlwZUVycm9yKFwiSW52YWxpZCBhdHRlbXB0IHRvIGRlc3RydWN0dXJlIG5vbi1pdGVyYWJsZSBpbnN0YW5jZS5cXG5JbiBvcmRlciB0byBiZSBpdGVyYWJsZSwgbm9uLWFycmF5IG9iamVjdHMgbXVzdCBoYXZlIGEgW1N5bWJvbC5pdGVyYXRvcl0oKSBtZXRob2QuXCIpOyB9XG5cbmZ1bmN0aW9uIF91bnN1cHBvcnRlZEl0ZXJhYmxlVG9BcnJheShvLCBtaW5MZW4pIHsgaWYgKCFvKSByZXR1cm47IGlmICh0eXBlb2YgbyA9PT0gXCJzdHJpbmdcIikgcmV0dXJuIF9hcnJheUxpa2VUb0FycmF5KG8sIG1pbkxlbik7IHZhciBuID0gT2JqZWN0LnByb3RvdHlwZS50b1N0cmluZy5jYWxsKG8pLnNsaWNlKDgsIC0xKTsgaWYgKG4gPT09IFwiT2JqZWN0XCIgJiYgby5jb25zdHJ1Y3RvcikgbiA9IG8uY29uc3RydWN0b3IubmFtZTsgaWYgKG4gPT09IFwiTWFwXCIgfHwgbiA9PT0gXCJTZXRcIikgcmV0dXJuIEFycmF5LmZyb20obyk7IGlmIChuID09PSBcIkFyZ3VtZW50c1wiIHx8IC9eKD86VWl8SSludCg/Ojh8MTZ8MzIpKD86Q2xhbXBlZCk/QXJyYXkkLy50ZXN0KG4pKSByZXR1cm4gX2FycmF5TGlrZVRvQXJyYXkobywgbWluTGVuKTsgfVxuXG5mdW5jdGlvbiBfYXJyYXlMaWtlVG9BcnJheShhcnIsIGxlbikgeyBpZiAobGVuID09IG51bGwgfHwgbGVuID4gYXJyLmxlbmd0aCkgbGVuID0gYXJyLmxlbmd0aDsgZm9yICh2YXIgaSA9IDAsIGFycjIgPSBuZXcgQXJyYXkobGVuKTsgaSA8IGxlbjsgaSsrKSB7IGFycjJbaV0gPSBhcnJbaV07IH0gcmV0dXJuIGFycjI7IH1cblxuZnVuY3Rpb24gX2l0ZXJhYmxlVG9BcnJheUxpbWl0KGFyciwgaSkgeyB2YXIgX2kgPSBhcnIgPT0gbnVsbCA/IG51bGwgOiB0eXBlb2YgU3ltYm9sICE9PSBcInVuZGVmaW5lZFwiICYmIGFycltTeW1ib2wuaXRlcmF0b3JdIHx8IGFycltcIkBAaXRlcmF0b3JcIl07IGlmIChfaSA9PSBudWxsKSByZXR1cm47IHZhciBfYXJyID0gW107IHZhciBfbiA9IHRydWU7IHZhciBfZCA9IGZhbHNlOyB2YXIgX3MsIF9lOyB0cnkgeyBmb3IgKF9pID0gX2kuY2FsbChhcnIpOyAhKF9uID0gKF9zID0gX2kubmV4dCgpKS5kb25lKTsgX24gPSB0cnVlKSB7IF9hcnIucHVzaChfcy52YWx1ZSk7IGlmIChpICYmIF9hcnIubGVuZ3RoID09PSBpKSBicmVhazsgfSB9IGNhdGNoIChlcnIpIHsgX2QgPSB0cnVlOyBfZSA9IGVycjsgfSBmaW5hbGx5IHsgdHJ5IHsgaWYgKCFfbiAmJiBfaVtcInJldHVyblwiXSAhPSBudWxsKSBfaVtcInJldHVyblwiXSgpOyB9IGZpbmFsbHkgeyBpZiAoX2QpIHRocm93IF9lOyB9IH0gcmV0dXJuIF9hcnI7IH1cblxuZnVuY3Rpb24gX2FycmF5V2l0aEhvbGVzKGFycikgeyBpZiAoQXJyYXkuaXNBcnJheShhcnIpKSByZXR1cm4gYXJyOyB9XG5cbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5hcnJheS5mb3ItZWFjaC5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL3dlYi5kb20tY29sbGVjdGlvbnMuZm9yLWVhY2guanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5vYmplY3QuZW50cmllcy5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN0cmluZy5zdGFydHMtd2l0aC5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLmRhdGUudG8tc3RyaW5nLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMub2JqZWN0LnRvLXN0cmluZy5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnJlZ2V4cC50by1zdHJpbmcuanNcIjtcbmltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5hcnJheS5pcy1hcnJheS5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5kZXNjcmlwdGlvbi5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLnN5bWJvbC5pdGVyYXRvci5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5Lml0ZXJhdG9yLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMuc3RyaW5nLml0ZXJhdG9yLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvd2ViLmRvbS1jb2xsZWN0aW9ucy5pdGVyYXRvci5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5LnNsaWNlLmpzXCI7XG5pbXBvcnQgXCJjb3JlLWpzL21vZHVsZXMvZXMuZnVuY3Rpb24ubmFtZS5qc1wiO1xuaW1wb3J0IFwiY29yZS1qcy9tb2R1bGVzL2VzLmFycmF5LmZyb20uanNcIjtcblxuLy8gc2ltaWxhciB0byBodG1sdG9vbHM6OnRhZygpXG4vLyBuYW1lOiBTdHJpbmdcbi8vIGF0dHJzOiB7fVxuLy8gY2hpbGRyZW46IGFueT9cbmZ1bmN0aW9uIHRhZyhuYW1lLCBhdHRycykge1xuICBmb3IgKHZhciBfbGVuID0gYXJndW1lbnRzLmxlbmd0aCwgY2hpbGRyZW4gPSBuZXcgQXJyYXkoX2xlbiA+IDIgPyBfbGVuIC0gMiA6IDApLCBfa2V5ID0gMjsgX2tleSA8IF9sZW47IF9rZXkrKykge1xuICAgIGNoaWxkcmVuW19rZXkgLSAyXSA9IGFyZ3VtZW50c1tfa2V5XTtcbiAgfVxuXG4gIHZhciBlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQobmFtZSk7XG4gIE9iamVjdC5lbnRyaWVzKGF0dHJzIHx8IHt9KS5mb3JFYWNoKGZ1bmN0aW9uIChfcmVmKSB7XG4gICAgdmFyIF9yZWYyID0gX3NsaWNlZFRvQXJyYXkoX3JlZiwgMiksXG4gICAgICAgIG5tID0gX3JlZjJbMF0sXG4gICAgICAgIHZhbCA9IF9yZWYyWzFdO1xuXG4gICAgbm0uc3RhcnRzV2l0aCgnb24nKSAmJiBubS50b0xvd2VyQ2FzZSgpIGluIHdpbmRvdyA/IGVsLmFkZEV2ZW50TGlzdGVuZXIobm0udG9Mb3dlckNhc2UoKS5zdWJzdHIoMiksIHZhbCkgOiBlbC5zZXRBdHRyaWJ1dGUobm0sIHZhbC50b1N0cmluZygpKTtcbiAgfSk7XG5cbiAgaWYgKCFjaGlsZHJlbikge1xuICAgIHJldHVybiBlbDtcbiAgfVxuXG4gIHRhZ0FwcGVuZENoaWxkKGVsLCBjaGlsZHJlbik7XG4gIHJldHVybiBlbDtcbn0gLy8gc2ltaWxhciB0byBodG1sdG9vbHM6OnRhZ0xpc3QoKVxuXG5cbmZ1bmN0aW9uIHRhZ0xpc3QoKSB7XG4gIGZvciAodmFyIF9sZW4yID0gYXJndW1lbnRzLmxlbmd0aCwgY2hpbGRyZW4gPSBuZXcgQXJyYXkoX2xlbjIpLCBfa2V5MiA9IDA7IF9rZXkyIDwgX2xlbjI7IF9rZXkyKyspIHtcbiAgICBjaGlsZHJlbltfa2V5Ml0gPSBhcmd1bWVudHNbX2tleTJdO1xuICB9XG5cbiAgcmV0dXJuIHRhZyhcInRlbXBsYXRlXCIsIHt9LCBjaGlsZHJlbikuY2hpbGRyZW47XG59IC8vIHNpbWlsYXIgdG8gaHRtbHRvb2xzOjpIVE1MKClcbi8vIHg6IFN0cmluZ1xuXG5cbmZ1bmN0aW9uIEhUTUwoeCkge1xuICB2YXIgZWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KFwidGVtcGxhdGVcIik7XG4gIGVsLmlubmVySFRNTCA9IHg7XG4gIHJldHVybiBlbC5jb250ZW50O1xufSAvLyBzaW1pbGFyIHRvIGh0bWx0b29sczo6dGFnQXBwZW5kQ2hpbGQoKVxuLy8geDogaHR0cHM6Ly9kZXZlbG9wZXIubW96aWxsYS5vcmcvZW4tVVMvZG9jcy9XZWIvQVBJL05vZGVcbi8vIHk6IGFueT9cblxuXG5mdW5jdGlvbiB0YWdBcHBlbmRDaGlsZCh4LCB5KSB7XG4gIGlmICh5IGluc3RhbmNlb2YgSFRNTENvbGxlY3Rpb24pIHtcbiAgICB3aGlsZSAoeS5sZW5ndGggPiAwKSB7XG4gICAgICB4LmFwcGVuZCh5WzBdKTtcbiAgICB9XG4gIH0gZWxzZSBpZiAoQXJyYXkuaXNBcnJheSh5KSkge1xuICAgIHkuZm9yRWFjaChmdW5jdGlvbiAoeikge1xuICAgICAgcmV0dXJuIHRhZ0FwcGVuZENoaWxkKHgsIHopO1xuICAgIH0pO1xuICB9IGVsc2Uge1xuICAgIHguYXBwZW5kKHkpO1xuICB9XG59XG5cbmV4cG9ydCB7IHRhZywgdGFnTGlzdCwgSFRNTCwgdGFnQXBwZW5kQ2hpbGQgfTsiLCAiJ3VzZSBzdHJpY3QnO1xudmFyICQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvZXhwb3J0Jyk7XG52YXIgaXNPYmplY3QgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtb2JqZWN0Jyk7XG52YXIgaXNBcnJheSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1hcnJheScpO1xudmFyIHRvQWJzb2x1dGVJbmRleCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1hYnNvbHV0ZS1pbmRleCcpO1xudmFyIHRvTGVuZ3RoID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3RvLWxlbmd0aCcpO1xudmFyIHRvSW5kZXhlZE9iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1pbmRleGVkLW9iamVjdCcpO1xudmFyIGNyZWF0ZVByb3BlcnR5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2NyZWF0ZS1wcm9wZXJ0eScpO1xudmFyIHdlbGxLbm93blN5bWJvbCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy93ZWxsLWtub3duLXN5bWJvbCcpO1xudmFyIGFycmF5TWV0aG9kSGFzU3BlY2llc1N1cHBvcnQgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYXJyYXktbWV0aG9kLWhhcy1zcGVjaWVzLXN1cHBvcnQnKTtcblxudmFyIEhBU19TUEVDSUVTX1NVUFBPUlQgPSBhcnJheU1ldGhvZEhhc1NwZWNpZXNTdXBwb3J0KCdzbGljZScpO1xuXG52YXIgU1BFQ0lFUyA9IHdlbGxLbm93blN5bWJvbCgnc3BlY2llcycpO1xudmFyIG5hdGl2ZVNsaWNlID0gW10uc2xpY2U7XG52YXIgbWF4ID0gTWF0aC5tYXg7XG5cbi8vIGBBcnJheS5wcm90b3R5cGUuc2xpY2VgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuc2xpY2Vcbi8vIGZhbGxiYWNrIGZvciBub3QgYXJyYXktbGlrZSBFUzMgc3RyaW5ncyBhbmQgRE9NIG9iamVjdHNcbiQoeyB0YXJnZXQ6ICdBcnJheScsIHByb3RvOiB0cnVlLCBmb3JjZWQ6ICFIQVNfU1BFQ0lFU19TVVBQT1JUIH0sIHtcbiAgc2xpY2U6IGZ1bmN0aW9uIHNsaWNlKHN0YXJ0LCBlbmQpIHtcbiAgICB2YXIgTyA9IHRvSW5kZXhlZE9iamVjdCh0aGlzKTtcbiAgICB2YXIgbGVuZ3RoID0gdG9MZW5ndGgoTy5sZW5ndGgpO1xuICAgIHZhciBrID0gdG9BYnNvbHV0ZUluZGV4KHN0YXJ0LCBsZW5ndGgpO1xuICAgIHZhciBmaW4gPSB0b0Fic29sdXRlSW5kZXgoZW5kID09PSB1bmRlZmluZWQgPyBsZW5ndGggOiBlbmQsIGxlbmd0aCk7XG4gICAgLy8gaW5saW5lIGBBcnJheVNwZWNpZXNDcmVhdGVgIGZvciB1c2FnZSBuYXRpdmUgYEFycmF5I3NsaWNlYCB3aGVyZSBpdCdzIHBvc3NpYmxlXG4gICAgdmFyIENvbnN0cnVjdG9yLCByZXN1bHQsIG47XG4gICAgaWYgKGlzQXJyYXkoTykpIHtcbiAgICAgIENvbnN0cnVjdG9yID0gTy5jb25zdHJ1Y3RvcjtcbiAgICAgIC8vIGNyb3NzLXJlYWxtIGZhbGxiYWNrXG4gICAgICBpZiAodHlwZW9mIENvbnN0cnVjdG9yID09ICdmdW5jdGlvbicgJiYgKENvbnN0cnVjdG9yID09PSBBcnJheSB8fCBpc0FycmF5KENvbnN0cnVjdG9yLnByb3RvdHlwZSkpKSB7XG4gICAgICAgIENvbnN0cnVjdG9yID0gdW5kZWZpbmVkO1xuICAgICAgfSBlbHNlIGlmIChpc09iamVjdChDb25zdHJ1Y3RvcikpIHtcbiAgICAgICAgQ29uc3RydWN0b3IgPSBDb25zdHJ1Y3RvcltTUEVDSUVTXTtcbiAgICAgICAgaWYgKENvbnN0cnVjdG9yID09PSBudWxsKSBDb25zdHJ1Y3RvciA9IHVuZGVmaW5lZDtcbiAgICAgIH1cbiAgICAgIGlmIChDb25zdHJ1Y3RvciA9PT0gQXJyYXkgfHwgQ29uc3RydWN0b3IgPT09IHVuZGVmaW5lZCkge1xuICAgICAgICByZXR1cm4gbmF0aXZlU2xpY2UuY2FsbChPLCBrLCBmaW4pO1xuICAgICAgfVxuICAgIH1cbiAgICByZXN1bHQgPSBuZXcgKENvbnN0cnVjdG9yID09PSB1bmRlZmluZWQgPyBBcnJheSA6IENvbnN0cnVjdG9yKShtYXgoZmluIC0gaywgMCkpO1xuICAgIGZvciAobiA9IDA7IGsgPCBmaW47IGsrKywgbisrKSBpZiAoayBpbiBPKSBjcmVhdGVQcm9wZXJ0eShyZXN1bHQsIG4sIE9ba10pO1xuICAgIHJlc3VsdC5sZW5ndGggPSBuO1xuICAgIHJldHVybiByZXN1bHQ7XG4gIH1cbn0pO1xuIiwgInZhciBERVNDUklQVE9SUyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9kZXNjcmlwdG9ycycpO1xudmFyIGRlZmluZVByb3BlcnR5ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL29iamVjdC1kZWZpbmUtcHJvcGVydHknKS5mO1xuXG52YXIgRnVuY3Rpb25Qcm90b3R5cGUgPSBGdW5jdGlvbi5wcm90b3R5cGU7XG52YXIgRnVuY3Rpb25Qcm90b3R5cGVUb1N0cmluZyA9IEZ1bmN0aW9uUHJvdG90eXBlLnRvU3RyaW5nO1xudmFyIG5hbWVSRSA9IC9eXFxzKmZ1bmN0aW9uIChbXiAoXSopLztcbnZhciBOQU1FID0gJ25hbWUnO1xuXG4vLyBGdW5jdGlvbiBpbnN0YW5jZXMgYC5uYW1lYCBwcm9wZXJ0eVxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1mdW5jdGlvbi1pbnN0YW5jZXMtbmFtZVxuaWYgKERFU0NSSVBUT1JTICYmICEoTkFNRSBpbiBGdW5jdGlvblByb3RvdHlwZSkpIHtcbiAgZGVmaW5lUHJvcGVydHkoRnVuY3Rpb25Qcm90b3R5cGUsIE5BTUUsIHtcbiAgICBjb25maWd1cmFibGU6IHRydWUsXG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICB0cnkge1xuICAgICAgICByZXR1cm4gRnVuY3Rpb25Qcm90b3R5cGVUb1N0cmluZy5jYWxsKHRoaXMpLm1hdGNoKG5hbWVSRSlbMV07XG4gICAgICB9IGNhdGNoIChlcnJvcikge1xuICAgICAgICByZXR1cm4gJyc7XG4gICAgICB9XG4gICAgfVxuICB9KTtcbn1cbiIsICJ2YXIgJCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9leHBvcnQnKTtcbnZhciBmcm9tID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FycmF5LWZyb20nKTtcbnZhciBjaGVja0NvcnJlY3RuZXNzT2ZJdGVyYXRpb24gPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvY2hlY2stY29ycmVjdG5lc3Mtb2YtaXRlcmF0aW9uJyk7XG5cbnZhciBJTkNPUlJFQ1RfSVRFUkFUSU9OID0gIWNoZWNrQ29ycmVjdG5lc3NPZkl0ZXJhdGlvbihmdW5jdGlvbiAoaXRlcmFibGUpIHtcbiAgLy8gZXNsaW50LWRpc2FibGUtbmV4dC1saW5lIGVzL25vLWFycmF5LWZyb20gLS0gcmVxdWlyZWQgZm9yIHRlc3RpbmdcbiAgQXJyYXkuZnJvbShpdGVyYWJsZSk7XG59KTtcblxuLy8gYEFycmF5LmZyb21gIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5mcm9tXG4kKHsgdGFyZ2V0OiAnQXJyYXknLCBzdGF0OiB0cnVlLCBmb3JjZWQ6IElOQ09SUkVDVF9JVEVSQVRJT04gfSwge1xuICBmcm9tOiBmcm9tXG59KTtcbiIsICIndXNlIHN0cmljdCc7XG52YXIgJCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9leHBvcnQnKTtcbnZhciBmYWlscyA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9mYWlscycpO1xudmFyIGlzQXJyYXkgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvaXMtYXJyYXknKTtcbnZhciBpc09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9pcy1vYmplY3QnKTtcbnZhciB0b09iamVjdCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1vYmplY3QnKTtcbnZhciB0b0xlbmd0aCA9IHJlcXVpcmUoJy4uL2ludGVybmFscy90by1sZW5ndGgnKTtcbnZhciBjcmVhdGVQcm9wZXJ0eSA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9jcmVhdGUtcHJvcGVydHknKTtcbnZhciBhcnJheVNwZWNpZXNDcmVhdGUgPSByZXF1aXJlKCcuLi9pbnRlcm5hbHMvYXJyYXktc3BlY2llcy1jcmVhdGUnKTtcbnZhciBhcnJheU1ldGhvZEhhc1NwZWNpZXNTdXBwb3J0ID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL2FycmF5LW1ldGhvZC1oYXMtc3BlY2llcy1zdXBwb3J0Jyk7XG52YXIgd2VsbEtub3duU3ltYm9sID0gcmVxdWlyZSgnLi4vaW50ZXJuYWxzL3dlbGwta25vd24tc3ltYm9sJyk7XG52YXIgVjhfVkVSU0lPTiA9IHJlcXVpcmUoJy4uL2ludGVybmFscy9lbmdpbmUtdjgtdmVyc2lvbicpO1xuXG52YXIgSVNfQ09OQ0FUX1NQUkVBREFCTEUgPSB3ZWxsS25vd25TeW1ib2woJ2lzQ29uY2F0U3ByZWFkYWJsZScpO1xudmFyIE1BWF9TQUZFX0lOVEVHRVIgPSAweDFGRkZGRkZGRkZGRkZGO1xudmFyIE1BWElNVU1fQUxMT1dFRF9JTkRFWF9FWENFRURFRCA9ICdNYXhpbXVtIGFsbG93ZWQgaW5kZXggZXhjZWVkZWQnO1xuXG4vLyBXZSBjYW4ndCB1c2UgdGhpcyBmZWF0dXJlIGRldGVjdGlvbiBpbiBWOCBzaW5jZSBpdCBjYXVzZXNcbi8vIGRlb3B0aW1pemF0aW9uIGFuZCBzZXJpb3VzIHBlcmZvcm1hbmNlIGRlZ3JhZGF0aW9uXG4vLyBodHRwczovL2dpdGh1Yi5jb20vemxvaXJvY2svY29yZS1qcy9pc3N1ZXMvNjc5XG52YXIgSVNfQ09OQ0FUX1NQUkVBREFCTEVfU1VQUE9SVCA9IFY4X1ZFUlNJT04gPj0gNTEgfHwgIWZhaWxzKGZ1bmN0aW9uICgpIHtcbiAgdmFyIGFycmF5ID0gW107XG4gIGFycmF5W0lTX0NPTkNBVF9TUFJFQURBQkxFXSA9IGZhbHNlO1xuICByZXR1cm4gYXJyYXkuY29uY2F0KClbMF0gIT09IGFycmF5O1xufSk7XG5cbnZhciBTUEVDSUVTX1NVUFBPUlQgPSBhcnJheU1ldGhvZEhhc1NwZWNpZXNTdXBwb3J0KCdjb25jYXQnKTtcblxudmFyIGlzQ29uY2F0U3ByZWFkYWJsZSA9IGZ1bmN0aW9uIChPKSB7XG4gIGlmICghaXNPYmplY3QoTykpIHJldHVybiBmYWxzZTtcbiAgdmFyIHNwcmVhZGFibGUgPSBPW0lTX0NPTkNBVF9TUFJFQURBQkxFXTtcbiAgcmV0dXJuIHNwcmVhZGFibGUgIT09IHVuZGVmaW5lZCA/ICEhc3ByZWFkYWJsZSA6IGlzQXJyYXkoTyk7XG59O1xuXG52YXIgRk9SQ0VEID0gIUlTX0NPTkNBVF9TUFJFQURBQkxFX1NVUFBPUlQgfHwgIVNQRUNJRVNfU1VQUE9SVDtcblxuLy8gYEFycmF5LnByb3RvdHlwZS5jb25jYXRgIG1ldGhvZFxuLy8gaHR0cHM6Ly90YzM5LmVzL2VjbWEyNjIvI3NlYy1hcnJheS5wcm90b3R5cGUuY29uY2F0XG4vLyB3aXRoIGFkZGluZyBzdXBwb3J0IG9mIEBAaXNDb25jYXRTcHJlYWRhYmxlIGFuZCBAQHNwZWNpZXNcbiQoeyB0YXJnZXQ6ICdBcnJheScsIHByb3RvOiB0cnVlLCBmb3JjZWQ6IEZPUkNFRCB9LCB7XG4gIC8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBuby11bnVzZWQtdmFycyAtLSByZXF1aXJlZCBmb3IgYC5sZW5ndGhgXG4gIGNvbmNhdDogZnVuY3Rpb24gY29uY2F0KGFyZykge1xuICAgIHZhciBPID0gdG9PYmplY3QodGhpcyk7XG4gICAgdmFyIEEgPSBhcnJheVNwZWNpZXNDcmVhdGUoTywgMCk7XG4gICAgdmFyIG4gPSAwO1xuICAgIHZhciBpLCBrLCBsZW5ndGgsIGxlbiwgRTtcbiAgICBmb3IgKGkgPSAtMSwgbGVuZ3RoID0gYXJndW1lbnRzLmxlbmd0aDsgaSA8IGxlbmd0aDsgaSsrKSB7XG4gICAgICBFID0gaSA9PT0gLTEgPyBPIDogYXJndW1lbnRzW2ldO1xuICAgICAgaWYgKGlzQ29uY2F0U3ByZWFkYWJsZShFKSkge1xuICAgICAgICBsZW4gPSB0b0xlbmd0aChFLmxlbmd0aCk7XG4gICAgICAgIGlmIChuICsgbGVuID4gTUFYX1NBRkVfSU5URUdFUikgdGhyb3cgVHlwZUVycm9yKE1BWElNVU1fQUxMT1dFRF9JTkRFWF9FWENFRURFRCk7XG4gICAgICAgIGZvciAoayA9IDA7IGsgPCBsZW47IGsrKywgbisrKSBpZiAoayBpbiBFKSBjcmVhdGVQcm9wZXJ0eShBLCBuLCBFW2tdKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIGlmIChuID49IE1BWF9TQUZFX0lOVEVHRVIpIHRocm93IFR5cGVFcnJvcihNQVhJTVVNX0FMTE9XRURfSU5ERVhfRVhDRUVERUQpO1xuICAgICAgICBjcmVhdGVQcm9wZXJ0eShBLCBuKyssIEUpO1xuICAgICAgfVxuICAgIH1cbiAgICBBLmxlbmd0aCA9IG47XG4gICAgcmV0dXJuIEE7XG4gIH1cbn0pO1xuIiwgImltcG9ydCBcImNvcmUtanMvbW9kdWxlcy9lcy5hcnJheS5jb25jYXQuanNcIjtcbmltcG9ydCB7IHRhZywgdGFnTGlzdCwgSFRNTCwgdGFnQXBwZW5kQ2hpbGQgfSBmcm9tICcuL3V0aWxzJztcblxuZnVuY3Rpb24gY3JlYXRlVGFiRnJhZ21lbnQoc2VsZiwgY2xhc3NOYW1lLCB0YWJzZXQpIHtcbiAgdmFyIHVsQXR0cnMgPSB7XG4gICAgXCJjbGFzc1wiOiBjbGFzc05hbWUsXG4gICAgcm9sZTogJ3RhYmxpc3QnLFxuICAgICdkYXRhLXRhYnNldGlkJzogdGFic2V0LmlkXG4gIH07XG4gIHZhciBpZCA9IHNlbGYuZ2V0QXR0cmlidXRlKCdpZCcpO1xuXG4gIGlmIChpZCkge1xuICAgIHVsQXR0cnMuaWQgPSBpZDtcbiAgICB1bEF0dHJzW1wiY2xhc3NcIl0gPSB1bEF0dHJzW1wiY2xhc3NcIl0gKyAnIHNoaW55LXRhYi1pbnB1dCc7XG4gIH1cblxuICB2YXIgdWxUYWcgPSB0YWcoJ3VsJywgdWxBdHRycywgdGFic2V0LnRhYkxpc3QpOyAvLyBUT0RPOlxuICAvLyAxLiBzaG91bGQgd2UgYmUgd3JhcHBpbmcgaW4gYSByb3c/XG4gIC8vIDIuIENhbiB0aGlzIGJlIGNsZWFuZXI/XG5cbiAgdmFyIGNvbnRlbnRzID0gW107XG4gIHZhciBoZWFkZXIgPSBzZWxmLmdldEF0dHJpYnV0ZSgnaGVhZGVyJyk7XG4gIGlmIChoZWFkZXIpIGNvbnRlbnRzLnB1c2goSFRNTChoZWFkZXIpKTtcbiAgY29udGVudHMucHVzaCh0YWJzZXQudGFiQ29udGVudCk7XG4gIHZhciBmb290ZXIgPSBzZWxmLmdldEF0dHJpYnV0ZSgnZm9vdGVyJyk7XG4gIGlmIChmb290ZXIpIGNvbnRlbnRzLnB1c2goSFRNTChmb290ZXIpKTtcbiAgdmFyIGRpdlRhZyA9IHRhZygnZGl2Jywge1xuICAgIFwiY2xhc3NcIjogJ3RhYi1jb250ZW50JyxcbiAgICAnZGF0YS10YWJzZXRpZCc6IHRhYnNldC5pZFxuICB9LCBjb250ZW50cyk7XG4gIHJldHVybiB0YWdMaXN0KHVsVGFnLCBkaXZUYWcpO1xufVxuXG5mdW5jdGlvbiBidWlsZFRhYnNldChuYXZzLCBzZWxlY3RlZCkge1xuICAvLyBUT0RPOiB1dGlsaXplIHRhZ0xpc3QoKSFcbiAgdmFyIHRhYkxpc3QgPSBuZXcgRG9jdW1lbnRGcmFnbWVudCgpO1xuICB2YXIgdGFiQ29udGVudCA9IG5ldyBEb2N1bWVudEZyYWdtZW50KCk7XG4gIHZhciBpZCA9IE1hdGguZmxvb3IoMTAwMCArIE1hdGgucmFuZG9tKCkgKiA5MDAwKTtcblxuICBmb3IgKHZhciBpID0gMDsgaSA8IG5hdnMubGVuZ3RoOyBpKyspIHtcbiAgICB2YXIgaXRlbSA9IGJ1aWxkVGFiSXRlbShuYXZzW2ldLCBzZWxlY3RlZCwgaWQsIGkgKyAxKTsgLy8gLm5hdi1jb250ZW50IGRvZXNuJ3QgbmVlZCBsaVRhZ1xuXG4gICAgdGFiTGlzdC5hcHBlbmQoaXRlbS5saVRhZyk7IC8vIC5uYXYtaXRlbS8ubmF2LXNwYWNlciBkb24ndCBoYXZlIGRpdlRhZ1xuXG4gICAgaWYgKGl0ZW0uZGl2VGFnKSB0YWJDb250ZW50LmFwcGVuZChpdGVtLmRpdlRhZyk7XG4gIH1cblxuICByZXR1cm4ge1xuICAgIHRhYkxpc3Q6IHRhYkxpc3QsXG4gICAgdGFiQ29udGVudDogdGFiQ29udGVudCxcbiAgICBpZDogaWRcbiAgfTtcbn1cblxuZnVuY3Rpb24gYnVpbGRUYWJJdGVtKG5hdiwgc2VsZWN0ZWQsIGlkLCBpbmRleCkge1xuICB2YXIgbGlUYWcgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdsaScpOyAvL2xpVGFnLmNsYXNzTGlzdC5hZGQoJ25hdi1pdGVtJyk7XG5cbiAgaWYgKG5hdi5jbGFzc0xpc3QuY29udGFpbnMoJ25hdi1zcGFjZXInKSkge1xuICAgIGxpVGFnLmNsYXNzTGlzdC5hZGQoJ2JzbGliLW5hdi1zcGFjZXInKTtcbiAgICByZXR1cm4ge1xuICAgICAgbGlUYWc6IGxpVGFnLFxuICAgICAgZGl2VGFnOiB1bmRlZmluZWRcbiAgICB9O1xuICB9XG5cbiAgaWYgKG5hdi5jbGFzc0xpc3QuY29udGFpbnMoJ25hdi1pdGVtJykpIHtcbiAgICAvLyBUT0RPOiBkcm9wIGZvcm0taW5saW5lIHNpbmNlIEJTNSBkcm9wcGVkIGl0P1xuICAgIC8vIElmIHdlIGRvIHRoYXQgZG8gd2UgbmVlZCBic2xpYi1uYXZzLWJhciB0byBnZW5lcmF0ZSB2YWxpZCBCUzUgbWFya3VwP1xuICAgIGxpVGFnLmNsYXNzTGlzdC5hZGQoJ2Zvcm0taW5saW5lJyk7XG4gICAgbGlUYWcuYXBwZW5kKG5hdi5jb250ZW50KTtcbiAgICByZXR1cm4ge1xuICAgICAgbGlUYWc6IGxpVGFnLFxuICAgICAgZGl2VGFnOiB1bmRlZmluZWRcbiAgICB9O1xuICB9XG5cbiAgaWYgKG5hdi5jbGFzc0xpc3QuY29udGFpbnMoJ25hdi1tZW51JykpIHtcbiAgICBsaVRhZy5jbGFzc0xpc3QuYWRkKCdkcm9wZG93bicpO1xuICAgIHZhciBhdHRycyA9IHtcbiAgICAgIGhyZWY6ICcjJyxcbiAgICAgIFwiY2xhc3NcIjogJ2Ryb3Bkb3duLXRvZ2dsZScsXG4gICAgICAnZGF0YS10b2dnbGUnOiAnZHJvcGRvd24nLFxuICAgICAgJ2RhdGEtdmFsdWUnOiBuYXYuZ2V0QXR0cmlidXRlKCd2YWx1ZScpXG4gICAgfTtcbiAgICB2YXIgdG9nZ2xlID0gdGFnKCdhJywgYXR0cnMsIEhUTUwobmF2LmdldEF0dHJpYnV0ZSgndGl0bGUnKSkpOyAvL3RvZ2dsZS5jbGFzc0xpc3QuYWRkKCduYXYtbGluaycpO1xuXG4gICAgdmFyIG1lbnUgPSB0YWcoJ3VsJywge1xuICAgICAgJ2RhdGEtdGFic2V0aWQnOiBpZCxcbiAgICAgIFwiY2xhc3NcIjogJ2Ryb3Bkb3duLW1lbnUnXG4gICAgfSk7XG5cbiAgICBpZiAobmF2LmdldEF0dHJpYnV0ZSgnYWxpZ24nKSA9PT0gJ3JpZ2h0Jykge1xuICAgICAgbWVudS5jbGFzc0xpc3QuYWRkKCdkcm9wZG93bi1tZW51LXJpZ2h0Jyk7XG4gICAgfVxuXG4gICAgdmFyIG5hdk1lbnUgPSBidWlsZFRhYnNldChuYXYuY29udGVudC5jaGlsZHJlbiwgc2VsZWN0ZWQpOyAvL25hdk1lbnUudGFiTGlzdC5jaGlsZHJlbi5mb3JFYWNoKHggPT4ge1xuICAgIC8vICB4LmNsYXNzTGlzdC5yZW1vdmUoJ25hdi1pdGVtJylcbiAgICAvLyAgbGV0IGxpbmsgPSB4LnF1ZXJ5U2VsZWN0b3IoJy5uYXYtbGluaycpO1xuICAgIC8vICBsaW5rLmNsYXNzTGlzdC5yZW1vdmUoJ25hdi1saW5rJyk7XG4gICAgLy8gIGxpbmsuY2xhc3NMaXN0LmFkZCgnZHJvcGRvd24taXRlbScpO1xuICAgIC8vfSlcblxuICAgIG1lbnUuYXBwZW5kKG5hdk1lbnUudGFiTGlzdCk7XG4gICAgbGlUYWcuYXBwZW5kKHRvZ2dsZSk7XG4gICAgbGlUYWcuYXBwZW5kKG1lbnUpO1xuICAgIHJldHVybiB7XG4gICAgICBsaVRhZzogbGlUYWcsXG4gICAgICBkaXZUYWc6IG5hdk1lbnUudGFiQ29udGVudFxuICAgIH07XG4gIH1cblxuICBpZiAobmF2LmNsYXNzTGlzdC5jb250YWlucygnbmF2JykpIHtcbiAgICB2YXIgdGFiSWQgPSBcInRhYi1cIi5jb25jYXQoaWQsIFwiLVwiKS5jb25jYXQoaW5kZXgpOyAvLyBOT1RFOiB0aGlzIHNob3VsZCByZWFsbHkgYmUgPGJ1dHRvbj4gKG5vdCA8YT4pLCBidXQgU2hpbnknc1xuICAgIC8vIHRhYiB1cGRhdGluZyBsb2dpYyB3b3VsZCBuZWVkIHVwZGF0aW5nIHRvIHN1cHBvcnQgdGhhdFxuICAgIC8vIE5PVEU6IHJlcXVpcmVzIGNvbXBhdGliaWxpdHkgbGF5ZXIuLi5cbiAgICAvL2FUYWcuY2xhc3NMaXN0LmFkZCgnbmF2LWxpbmsnKTtcblxuICAgIHZhciBhVGFnID0gdGFnKCdhJywge1xuICAgICAgaHJlZjogJyMnICsgdGFiSWQsXG4gICAgICByb2xlOiAndGFiJyxcbiAgICAgICdkYXRhLXRvZ2dsZSc6ICd0YWInLFxuICAgICAgJ2RhdGEtdmFsdWUnOiBuYXYuZ2V0QXR0cmlidXRlKCd2YWx1ZScpXG4gICAgfSwgSFRNTChuYXYuZ2V0QXR0cmlidXRlKCd0aXRsZScpKSk7XG4gICAgbGlUYWcuYXBwZW5kKGFUYWcpO1xuICAgIHZhciBkaXZUYWcgPSB0YWcoJ2RpdicsIHtcbiAgICAgIGlkOiB0YWJJZCxcbiAgICAgIFwiY2xhc3NcIjogJ3RhYi1wYW5lJyxcbiAgICAgIHJvbGU6ICd0YWJwYW5lbCdcbiAgICB9LCBuYXYuY29udGVudCk7IC8vIE5PVEU6IHJlcXVpcmVzIGNvbXBhdGliaWxpdHkgbGF5ZXIuLi5cbiAgICAvLyBDYWxsaW5nIHRhYi5zaG93KCkgd291bGQgYmUgYmV0dGVyLCBidXQgcHJvYmFibHkgaGFzIHRvIGJlIGluc2VydGVkIGludG8gRE9NIHRvIHdvcms/XG5cbiAgICBpZiAoc2VsZWN0ZWQgPT09IG5hdi5nZXRBdHRyaWJ1dGUoJ3ZhbHVlJykpIHtcbiAgICAgIGxpVGFnLmNsYXNzTGlzdC5hZGQoJ2FjdGl2ZScpO1xuICAgICAgZGl2VGFnLmNsYXNzTGlzdC5hZGQoJ2FjdGl2ZScpO1xuICAgIH1cblxuICAgIHJldHVybiB7XG4gICAgICBsaVRhZzogbGlUYWcsXG4gICAgICBkaXZUYWc6IGRpdlRhZ1xuICAgIH07XG4gIH1cblxuICB0aHJvdyBuZXcgRXJyb3IoXCJBICd0b3AtbGV2ZWwnIDxcIi5jb25jYXQobmFtZSwgXCI+IHRhZyB3aXRoaW4gPGJzbGliLW5hdnMtdGFiPiBpcyBub3Qgc3VwcG9ydGVkXCIpKTtcbn1cblxuZnVuY3Rpb24gZ2V0U2VsZWN0ZWQoc2VsZikge1xuICB2YXIgc2VsZWN0ZWQgPSBzZWxmLmdldEF0dHJpYnV0ZSgnc2VsZWN0ZWQnKTtcblxuICBpZiAoIXNlbGVjdGVkICYmIHNlbGYuY2hpbGRyZW4ubGVuZ3RoID4gMCkge1xuICAgIHNlbGVjdGVkID0gZmluZEZpcnN0TmF2KHNlbGYuY2hpbGRyZW4pLmdldEF0dHJpYnV0ZSgndmFsdWUnKTtcbiAgfVxuXG4gIHJldHVybiBzZWxlY3RlZDtcbn1cblxuZnVuY3Rpb24gZmluZEZpcnN0TmF2KG5hdnMpIHtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCBuYXZzLmxlbmd0aDsgaSsrKSB7XG4gICAgdmFyIG5hdiA9IG5hdnNbaV07XG5cbiAgICBpZiAobmF2LmNsYXNzTGlzdC5jb250YWlucygnbmF2JykpIHtcbiAgICAgIHJldHVybiBuYXY7XG4gICAgfVxuXG4gICAgaWYgKG5hdi5jbGFzc0xpc3QuY29udGFpbnMoJ25hdi1tZW51JykpIHtcbiAgICAgIGZpbmRGaXJzdE5hdihuYXYpO1xuICAgIH1cbiAgfVxufVxuXG5mdW5jdGlvbiByZXBsYWNlQ2hpbGRyZW4oeCwgeSkge1xuICB3aGlsZSAoeC5maXJzdENoaWxkKSB7XG4gICAgeC5yZW1vdmVDaGlsZCh4Lmxhc3RDaGlsZCk7XG4gIH1cblxuICB0YWdBcHBlbmRDaGlsZCh4LCB5KTtcbn1cblxuZXhwb3J0IHsgY3JlYXRlVGFiRnJhZ21lbnQsIGJ1aWxkVGFic2V0LCBnZXRTZWxlY3RlZCwgcmVwbGFjZUNoaWxkcmVuIH07IiwgImltcG9ydCB7IHRhZyB9IGZyb20gJy4vdXRpbHMnO1xuXG5mdW5jdGlvbiBjcmVhdGVDYXJkKGJvZHksIGhlYWRlciwgZm9vdGVyKSB7XG4gIHZhciBjYXJkID0gdGFnKCdkaXYnLCB7XG4gICAgXCJjbGFzc1wiOiAnY2FyZCdcbiAgfSk7XG5cbiAgaWYgKGhlYWRlcikge1xuICAgIGNhcmQuYXBwZW5kKHRhZygnZGl2Jywge1xuICAgICAgXCJjbGFzc1wiOiAnY2FyZC1oZWFkZXInXG4gICAgfSwgaGVhZGVyKSk7XG4gIH1cblxuICBjYXJkLmFwcGVuZCh0YWcoJ2RpdicsIHtcbiAgICBcImNsYXNzXCI6ICdjYXJkLWJvZHknXG4gIH0sIGJvZHkpKTtcblxuICBpZiAoZm9vdGVyKSB7XG4gICAgY2FyZC5hcHBlbmQodGFnKCdkaXYnLCB7XG4gICAgICBcImNsYXNzXCI6ICdjYXJkLWZvb3RlcidcbiAgICB9LCBmb290ZXIpKTtcbiAgfVxuXG4gIHJldHVybiBjYXJkO1xufVxuXG5leHBvcnQgeyBjcmVhdGVDYXJkIH07Il0sCiAgIm1hcHBpbmdzIjogIjs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FBQUE7QUFBQTtBQUFBLFVBQUksUUFBUSxTQUFVLElBQUk7QUFDeEIsZUFBTyxNQUFNLEdBQUcsUUFBUSxRQUFRO0FBQUE7QUFJbEMsYUFBTyxVQUVMLE1BQU0sT0FBTyxjQUFjLFlBQVksZUFDdkMsTUFBTSxPQUFPLFVBQVUsWUFBWSxXQUVuQyxNQUFNLE9BQU8sUUFBUSxZQUFZLFNBQ2pDLE1BQU0sT0FBTyxVQUFVLFlBQVksV0FFbEMsV0FBWTtBQUFFLGVBQU87QUFBQSxhQUFjLFNBQVM7QUFBQTtBQUFBOzs7QUNiL0M7QUFBQTtBQUFBLGFBQU8sVUFBVSxTQUFVLE1BQU07QUFDL0IsWUFBSTtBQUNGLGlCQUFPLENBQUMsQ0FBQztBQUFBLGlCQUNGLE9BQVA7QUFDQSxpQkFBTztBQUFBO0FBQUE7QUFBQTtBQUFBOzs7QUNKWDtBQUFBO0FBQUEsVUFBSSxTQUFRO0FBR1osYUFBTyxVQUFVLENBQUMsT0FBTSxXQUFZO0FBRWxDLGVBQU8sT0FBTyxlQUFlLElBQUksR0FBRyxFQUFFLEtBQUssV0FBWTtBQUFFLGlCQUFPO0FBQUEsYUFBUSxNQUFNO0FBQUE7QUFBQTtBQUFBOzs7QUNMaEY7QUFBQTtBQUFBO0FBQ0EsVUFBSSx5QkFBd0IsR0FBRztBQUUvQixVQUFJLDRCQUEyQixPQUFPO0FBR3RDLFVBQUksY0FBYyw2QkFBNEIsQ0FBQyx1QkFBc0IsS0FBSyxFQUFFLEdBQUcsS0FBSztBQUlwRixjQUFRLElBQUksY0FBYywrQkFBOEIsR0FBRztBQUN6RCxZQUFJLGFBQWEsMEJBQXlCLE1BQU07QUFDaEQsZUFBTyxDQUFDLENBQUMsY0FBYyxXQUFXO0FBQUEsVUFDaEM7QUFBQTtBQUFBOzs7QUNiSjtBQUFBO0FBQUEsYUFBTyxVQUFVLFNBQVUsUUFBUSxPQUFPO0FBQ3hDLGVBQU87QUFBQSxVQUNMLFlBQVksQ0FBRSxVQUFTO0FBQUEsVUFDdkIsY0FBYyxDQUFFLFVBQVM7QUFBQSxVQUN6QixVQUFVLENBQUUsVUFBUztBQUFBLFVBQ3JCLE9BQU87QUFBQTtBQUFBO0FBQUE7QUFBQTs7O0FDTFg7QUFBQTtBQUFBLFVBQUksWUFBVyxHQUFHO0FBRWxCLGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsZUFBTyxVQUFTLEtBQUssSUFBSSxNQUFNLEdBQUc7QUFBQTtBQUFBO0FBQUE7OztBQ0hwQztBQUFBO0FBQUEsVUFBSSxTQUFRO0FBQ1osVUFBSSxVQUFVO0FBRWQsVUFBSSxRQUFRLEdBQUc7QUFHZixhQUFPLFVBQVUsT0FBTSxXQUFZO0FBR2pDLGVBQU8sQ0FBQyxPQUFPLEtBQUsscUJBQXFCO0FBQUEsV0FDdEMsU0FBVSxJQUFJO0FBQ2pCLGVBQU8sUUFBUSxPQUFPLFdBQVcsTUFBTSxLQUFLLElBQUksTUFBTSxPQUFPO0FBQUEsVUFDM0Q7QUFBQTtBQUFBOzs7QUNaSjtBQUFBO0FBRUEsYUFBTyxVQUFVLFNBQVUsSUFBSTtBQUM3QixZQUFJLE1BQU07QUFBVyxnQkFBTSxVQUFVLDBCQUEwQjtBQUMvRCxlQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNKVDtBQUFBO0FBQ0EsVUFBSSxnQkFBZ0I7QUFDcEIsVUFBSSwwQkFBeUI7QUFFN0IsYUFBTyxVQUFVLFNBQVUsSUFBSTtBQUM3QixlQUFPLGNBQWMsd0JBQXVCO0FBQUE7QUFBQTtBQUFBOzs7QUNMOUM7QUFBQTtBQUFBLGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsZUFBTyxPQUFPLE9BQU8sV0FBVyxPQUFPLE9BQU8sT0FBTyxPQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNEOUQ7QUFBQTtBQUFBLFVBQUksWUFBVztBQU1mLGFBQU8sVUFBVSxTQUFVLE9BQU8sa0JBQWtCO0FBQ2xELFlBQUksQ0FBQyxVQUFTO0FBQVEsaUJBQU87QUFDN0IsWUFBSSxJQUFJO0FBQ1IsWUFBSSxvQkFBb0IsT0FBUSxNQUFLLE1BQU0sYUFBYSxjQUFjLENBQUMsVUFBUyxNQUFNLEdBQUcsS0FBSztBQUFTLGlCQUFPO0FBQzlHLFlBQUksT0FBUSxNQUFLLE1BQU0sWUFBWSxjQUFjLENBQUMsVUFBUyxNQUFNLEdBQUcsS0FBSztBQUFTLGlCQUFPO0FBQ3pGLFlBQUksQ0FBQyxvQkFBb0IsT0FBUSxNQUFLLE1BQU0sYUFBYSxjQUFjLENBQUMsVUFBUyxNQUFNLEdBQUcsS0FBSztBQUFTLGlCQUFPO0FBQy9HLGNBQU0sVUFBVTtBQUFBO0FBQUE7QUFBQTs7O0FDWmxCO0FBQUE7QUFBQSxVQUFJLDBCQUF5QjtBQUk3QixhQUFPLFVBQVUsU0FBVSxVQUFVO0FBQ25DLGVBQU8sT0FBTyx3QkFBdUI7QUFBQTtBQUFBO0FBQUE7OztBQ0x2QztBQUFBO0FBQUEsVUFBSSxZQUFXO0FBRWYsVUFBSSxpQkFBaUIsR0FBRztBQUV4QixhQUFPLFVBQVUsT0FBTyxVQUFVLGdCQUFnQixJQUFJLEtBQUs7QUFDekQsZUFBTyxlQUFlLEtBQUssVUFBUyxLQUFLO0FBQUE7QUFBQTtBQUFBOzs7QUNMM0M7QUFBQTtBQUFBLFVBQUksVUFBUztBQUNiLFVBQUksWUFBVztBQUVmLFVBQUksWUFBVyxRQUFPO0FBRXRCLFVBQUksU0FBUyxVQUFTLGNBQWEsVUFBUyxVQUFTO0FBRXJELGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsZUFBTyxTQUFTLFVBQVMsY0FBYyxNQUFNO0FBQUE7QUFBQTtBQUFBOzs7QUNSL0M7QUFBQTtBQUFBLFVBQUksZUFBYztBQUNsQixVQUFJLFNBQVE7QUFDWixVQUFJLGdCQUFnQjtBQUdwQixhQUFPLFVBQVUsQ0FBQyxnQkFBZSxDQUFDLE9BQU0sV0FBWTtBQUVsRCxlQUFPLE9BQU8sZUFBZSxjQUFjLFFBQVEsS0FBSztBQUFBLFVBQ3RELEtBQUssV0FBWTtBQUFFLG1CQUFPO0FBQUE7QUFBQSxXQUN6QixLQUFLO0FBQUE7QUFBQTtBQUFBOzs7QUNUVjtBQUFBO0FBQUEsVUFBSSxlQUFjO0FBQ2xCLFVBQUksOEJBQTZCO0FBQ2pDLFVBQUksNEJBQTJCO0FBQy9CLFVBQUksbUJBQWtCO0FBQ3RCLFVBQUksZUFBYztBQUNsQixVQUFJLE9BQU07QUFDVixVQUFJLGlCQUFpQjtBQUdyQixVQUFJLDZCQUE0QixPQUFPO0FBSXZDLGNBQVEsSUFBSSxlQUFjLDZCQUE0QixtQ0FBa0MsR0FBRyxHQUFHO0FBQzVGLFlBQUksaUJBQWdCO0FBQ3BCLFlBQUksYUFBWSxHQUFHO0FBQ25CLFlBQUk7QUFBZ0IsY0FBSTtBQUN0QixtQkFBTywyQkFBMEIsR0FBRztBQUFBLG1CQUM3QixPQUFQO0FBQUE7QUFDRixZQUFJLEtBQUksR0FBRztBQUFJLGlCQUFPLDBCQUF5QixDQUFDLDRCQUEyQixFQUFFLEtBQUssR0FBRyxJQUFJLEVBQUU7QUFBQTtBQUFBO0FBQUE7OztBQ25CN0Y7QUFBQTtBQUFBLFVBQUksWUFBVztBQUVmLGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsWUFBSSxDQUFDLFVBQVMsS0FBSztBQUNqQixnQkFBTSxVQUFVLE9BQU8sTUFBTTtBQUFBO0FBQzdCLGVBQU87QUFBQTtBQUFBO0FBQUE7OztBQ0xYO0FBQUE7QUFBQSxVQUFJLGVBQWM7QUFDbEIsVUFBSSxpQkFBaUI7QUFDckIsVUFBSSxZQUFXO0FBQ2YsVUFBSSxlQUFjO0FBR2xCLFVBQUksbUJBQWtCLE9BQU87QUFJN0IsY0FBUSxJQUFJLGVBQWMsbUJBQWtCLHlCQUF3QixHQUFHLEdBQUcsWUFBWTtBQUNwRixrQkFBUztBQUNULFlBQUksYUFBWSxHQUFHO0FBQ25CLGtCQUFTO0FBQ1QsWUFBSTtBQUFnQixjQUFJO0FBQ3RCLG1CQUFPLGlCQUFnQixHQUFHLEdBQUc7QUFBQSxtQkFDdEIsT0FBUDtBQUFBO0FBQ0YsWUFBSSxTQUFTLGNBQWMsU0FBUztBQUFZLGdCQUFNLFVBQVU7QUFDaEUsWUFBSSxXQUFXO0FBQVksWUFBRSxLQUFLLFdBQVc7QUFDN0MsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDbkJUO0FBQUE7QUFBQSxVQUFJLGVBQWM7QUFDbEIsVUFBSSx3QkFBdUI7QUFDM0IsVUFBSSw0QkFBMkI7QUFFL0IsYUFBTyxVQUFVLGVBQWMsU0FBVSxRQUFRLEtBQUssT0FBTztBQUMzRCxlQUFPLHNCQUFxQixFQUFFLFFBQVEsS0FBSywwQkFBeUIsR0FBRztBQUFBLFVBQ3JFLFNBQVUsUUFBUSxLQUFLLE9BQU87QUFDaEMsZUFBTyxPQUFPO0FBQ2QsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDUlQ7QUFBQTtBQUFBLFVBQUksVUFBUztBQUNiLFVBQUksK0JBQThCO0FBRWxDLGFBQU8sVUFBVSxTQUFVLEtBQUssT0FBTztBQUNyQyxZQUFJO0FBQ0YsdUNBQTRCLFNBQVEsS0FBSztBQUFBLGlCQUNsQyxPQUFQO0FBQ0Esa0JBQU8sT0FBTztBQUFBO0FBQ2QsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDUlg7QUFBQTtBQUFBLFVBQUksVUFBUztBQUNiLFVBQUksWUFBWTtBQUVoQixVQUFJLFNBQVM7QUFDYixVQUFJLFFBQVEsUUFBTyxXQUFXLFVBQVUsUUFBUTtBQUVoRCxhQUFPLFVBQVU7QUFBQTtBQUFBOzs7QUNOakI7QUFBQTtBQUFBLFVBQUksUUFBUTtBQUVaLFVBQUksbUJBQW1CLFNBQVM7QUFHaEMsVUFBSSxPQUFPLE1BQU0saUJBQWlCLFlBQVk7QUFDNUMsY0FBTSxnQkFBZ0IsU0FBVSxJQUFJO0FBQ2xDLGlCQUFPLGlCQUFpQixLQUFLO0FBQUE7QUFBQTtBQUlqQyxhQUFPLFVBQVUsTUFBTTtBQUFBO0FBQUE7OztBQ1h2QjtBQUFBO0FBQUEsVUFBSSxVQUFTO0FBQ2IsVUFBSSxnQkFBZ0I7QUFFcEIsVUFBSSxVQUFVLFFBQU87QUFFckIsYUFBTyxVQUFVLE9BQU8sWUFBWSxjQUFjLGNBQWMsS0FBSyxjQUFjO0FBQUE7QUFBQTs7O0FDTG5GO0FBQUE7QUFBQSxhQUFPLFVBQVU7QUFBQTtBQUFBOzs7QUNBakI7QUFBQTtBQUFBLFVBQUksV0FBVTtBQUNkLFVBQUksUUFBUTtBQUVaLE1BQUMsUUFBTyxVQUFVLFNBQVUsS0FBSyxPQUFPO0FBQ3RDLGVBQU8sTUFBTSxRQUFTLE9BQU0sT0FBTyxVQUFVLFNBQVksUUFBUTtBQUFBLFNBQ2hFLFlBQVksSUFBSSxLQUFLO0FBQUEsUUFDdEIsU0FBUztBQUFBLFFBQ1QsTUFBTSxXQUFVLFNBQVM7QUFBQSxRQUN6QixXQUFXO0FBQUE7QUFBQTtBQUFBOzs7QUNSYjtBQUFBO0FBQUEsVUFBSSxLQUFLO0FBQ1QsVUFBSSxVQUFVLEtBQUs7QUFFbkIsYUFBTyxVQUFVLFNBQVUsS0FBSztBQUM5QixlQUFPLFlBQVksT0FBTyxRQUFRLFNBQVksS0FBSyxPQUFPLE9BQVEsR0FBRSxLQUFLLFNBQVMsU0FBUztBQUFBO0FBQUE7QUFBQTs7O0FDSjdGO0FBQUE7QUFBQSxVQUFJLFVBQVM7QUFDYixVQUFJLE9BQU07QUFFVixVQUFJLE9BQU8sUUFBTztBQUVsQixhQUFPLFVBQVUsU0FBVSxLQUFLO0FBQzlCLGVBQU8sS0FBSyxRQUFTLE1BQUssT0FBTyxLQUFJO0FBQUE7QUFBQTtBQUFBOzs7QUNOdkM7QUFBQTtBQUFBLGFBQU8sVUFBVTtBQUFBO0FBQUE7OztBQ0FqQjtBQUFBO0FBQUEsVUFBSSxrQkFBa0I7QUFDdEIsVUFBSSxVQUFTO0FBQ2IsVUFBSSxZQUFXO0FBQ2YsVUFBSSwrQkFBOEI7QUFDbEMsVUFBSSxZQUFZO0FBQ2hCLFVBQUksVUFBUztBQUNiLFVBQUksYUFBWTtBQUNoQixVQUFJLGNBQWE7QUFFakIsVUFBSSw2QkFBNkI7QUFDakMsVUFBSSxVQUFVLFFBQU87QUFDckIsVUFBSTtBQUFKLFVBQVM7QUFBVCxVQUFjO0FBRWQsVUFBSSxVQUFVLFNBQVUsSUFBSTtBQUMxQixlQUFPLEtBQUksTUFBTSxJQUFJLE1BQU0sSUFBSSxJQUFJO0FBQUE7QUFHckMsVUFBSSxZQUFZLFNBQVUsTUFBTTtBQUM5QixlQUFPLFNBQVUsSUFBSTtBQUNuQixjQUFJO0FBQ0osY0FBSSxDQUFDLFVBQVMsT0FBUSxTQUFRLElBQUksS0FBSyxTQUFTLE1BQU07QUFDcEQsa0JBQU0sVUFBVSw0QkFBNEIsT0FBTztBQUFBO0FBQ25ELGlCQUFPO0FBQUE7QUFBQTtBQUliLFVBQUksbUJBQW1CLFFBQU8sT0FBTztBQUMvQixnQkFBUSxRQUFPLFNBQVUsU0FBTyxRQUFRLElBQUk7QUFDNUMsZ0JBQVEsTUFBTTtBQUNkLGdCQUFRLE1BQU07QUFDZCxnQkFBUSxNQUFNO0FBQ2xCLGNBQU0sU0FBVSxJQUFJLFVBQVU7QUFDNUIsY0FBSSxNQUFNLEtBQUssT0FBTztBQUFLLGtCQUFNLElBQUksVUFBVTtBQUMvQyxtQkFBUyxTQUFTO0FBQ2xCLGdCQUFNLEtBQUssT0FBTyxJQUFJO0FBQ3RCLGlCQUFPO0FBQUE7QUFFVCxjQUFNLFNBQVUsSUFBSTtBQUNsQixpQkFBTyxNQUFNLEtBQUssT0FBTyxPQUFPO0FBQUE7QUFFbEMsZUFBTSxTQUFVLElBQUk7QUFDbEIsaUJBQU8sTUFBTSxLQUFLLE9BQU87QUFBQTtBQUFBLGFBRXRCO0FBQ0QsZ0JBQVEsV0FBVTtBQUN0QixvQkFBVyxTQUFTO0FBQ3BCLGNBQU0sU0FBVSxJQUFJLFVBQVU7QUFDNUIsY0FBSSxVQUFVLElBQUk7QUFBUSxrQkFBTSxJQUFJLFVBQVU7QUFDOUMsbUJBQVMsU0FBUztBQUNsQix1Q0FBNEIsSUFBSSxPQUFPO0FBQ3ZDLGlCQUFPO0FBQUE7QUFFVCxjQUFNLFNBQVUsSUFBSTtBQUNsQixpQkFBTyxVQUFVLElBQUksU0FBUyxHQUFHLFNBQVM7QUFBQTtBQUU1QyxlQUFNLFNBQVUsSUFBSTtBQUNsQixpQkFBTyxVQUFVLElBQUk7QUFBQTtBQUFBO0FBN0JuQjtBQUNBO0FBQ0E7QUFDQTtBQWNBO0FBZ0JOLGFBQU8sVUFBVTtBQUFBLFFBQ2YsS0FBSztBQUFBLFFBQ0wsS0FBSztBQUFBLFFBQ0wsS0FBSztBQUFBLFFBQ0wsU0FBUztBQUFBLFFBQ1QsV0FBVztBQUFBO0FBQUE7QUFBQTs7O0FDakViO0FBQUE7QUFBQSxVQUFJLFVBQVM7QUFDYixVQUFJLCtCQUE4QjtBQUNsQyxVQUFJLE9BQU07QUFDVixVQUFJLFlBQVk7QUFDaEIsVUFBSSxnQkFBZ0I7QUFDcEIsVUFBSSx1QkFBc0I7QUFFMUIsVUFBSSxvQkFBbUIscUJBQW9CO0FBQzNDLFVBQUksdUJBQXVCLHFCQUFvQjtBQUMvQyxVQUFJLFdBQVcsT0FBTyxRQUFRLE1BQU07QUFFcEMsTUFBQyxRQUFPLFVBQVUsU0FBVSxHQUFHLEtBQUssT0FBTyxTQUFTO0FBQ2xELFlBQUksU0FBUyxVQUFVLENBQUMsQ0FBQyxRQUFRLFNBQVM7QUFDMUMsWUFBSSxTQUFTLFVBQVUsQ0FBQyxDQUFDLFFBQVEsYUFBYTtBQUM5QyxZQUFJLGNBQWMsVUFBVSxDQUFDLENBQUMsUUFBUSxjQUFjO0FBQ3BELFlBQUk7QUFDSixZQUFJLE9BQU8sU0FBUyxZQUFZO0FBQzlCLGNBQUksT0FBTyxPQUFPLFlBQVksQ0FBQyxLQUFJLE9BQU8sU0FBUztBQUNqRCx5Q0FBNEIsT0FBTyxRQUFRO0FBQUE7QUFFN0Msa0JBQVEscUJBQXFCO0FBQzdCLGNBQUksQ0FBQyxNQUFNLFFBQVE7QUFDakIsa0JBQU0sU0FBUyxTQUFTLEtBQUssT0FBTyxPQUFPLFdBQVcsTUFBTTtBQUFBO0FBQUE7QUFHaEUsWUFBSSxNQUFNLFNBQVE7QUFDaEIsY0FBSTtBQUFRLGNBQUUsT0FBTztBQUFBO0FBQ2hCLHNCQUFVLEtBQUs7QUFDcEI7QUFBQSxtQkFDUyxDQUFDLFFBQVE7QUFDbEIsaUJBQU8sRUFBRTtBQUFBLG1CQUNBLENBQUMsZUFBZSxFQUFFLE1BQU07QUFDakMsbUJBQVM7QUFBQTtBQUVYLFlBQUk7QUFBUSxZQUFFLE9BQU87QUFBQTtBQUNoQix1Q0FBNEIsR0FBRyxLQUFLO0FBQUEsU0FFeEMsU0FBUyxXQUFXLFlBQVkscUJBQW9CO0FBQ3JELGVBQU8sT0FBTyxRQUFRLGNBQWMsa0JBQWlCLE1BQU0sVUFBVSxjQUFjO0FBQUE7QUFBQTtBQUFBOzs7QUN0Q3JGO0FBQUE7QUFBQSxVQUFJLFVBQVM7QUFFYixhQUFPLFVBQVU7QUFBQTtBQUFBOzs7QUNGakI7QUFBQTtBQUFBLFVBQUksT0FBTztBQUNYLFVBQUksVUFBUztBQUViLFVBQUksYUFBWSxTQUFVLFVBQVU7QUFDbEMsZUFBTyxPQUFPLFlBQVksYUFBYSxXQUFXO0FBQUE7QUFHcEQsYUFBTyxVQUFVLFNBQVUsV0FBVyxRQUFRO0FBQzVDLGVBQU8sVUFBVSxTQUFTLElBQUksV0FBVSxLQUFLLGVBQWUsV0FBVSxRQUFPLGNBQ3pFLEtBQUssY0FBYyxLQUFLLFdBQVcsV0FBVyxRQUFPLGNBQWMsUUFBTyxXQUFXO0FBQUE7QUFBQTtBQUFBOzs7QUNUM0Y7QUFBQTtBQUFBLFVBQUksT0FBTyxLQUFLO0FBQ2hCLFVBQUksUUFBUSxLQUFLO0FBSWpCLGFBQU8sVUFBVSxTQUFVLFVBQVU7QUFDbkMsZUFBTyxNQUFNLFdBQVcsQ0FBQyxZQUFZLElBQUssWUFBVyxJQUFJLFFBQVEsTUFBTTtBQUFBO0FBQUE7QUFBQTs7O0FDTnpFO0FBQUE7QUFBQSxVQUFJLFlBQVk7QUFFaEIsVUFBSSxPQUFNLEtBQUs7QUFJZixhQUFPLFVBQVUsU0FBVSxVQUFVO0FBQ25DLGVBQU8sV0FBVyxJQUFJLEtBQUksVUFBVSxXQUFXLG9CQUFvQjtBQUFBO0FBQUE7QUFBQTs7O0FDUHJFO0FBQUE7QUFBQSxVQUFJLFlBQVk7QUFFaEIsVUFBSSxPQUFNLEtBQUs7QUFDZixVQUFJLE9BQU0sS0FBSztBQUtmLGFBQU8sVUFBVSxTQUFVLE9BQU8sUUFBUTtBQUN4QyxZQUFJLFVBQVUsVUFBVTtBQUN4QixlQUFPLFVBQVUsSUFBSSxLQUFJLFVBQVUsUUFBUSxLQUFLLEtBQUksU0FBUztBQUFBO0FBQUE7QUFBQTs7O0FDVi9EO0FBQUE7QUFBQSxVQUFJLG1CQUFrQjtBQUN0QixVQUFJLFlBQVc7QUFDZixVQUFJLG1CQUFrQjtBQUd0QixVQUFJLGVBQWUsU0FBVSxhQUFhO0FBQ3hDLGVBQU8sU0FBVSxPQUFPLElBQUksV0FBVztBQUNyQyxjQUFJLElBQUksaUJBQWdCO0FBQ3hCLGNBQUksU0FBUyxVQUFTLEVBQUU7QUFDeEIsY0FBSSxRQUFRLGlCQUFnQixXQUFXO0FBQ3ZDLGNBQUk7QUFHSixjQUFJLGVBQWUsTUFBTTtBQUFJLG1CQUFPLFNBQVMsT0FBTztBQUNsRCxzQkFBUSxFQUFFO0FBRVYsa0JBQUksU0FBUztBQUFPLHVCQUFPO0FBQUE7QUFBQTtBQUV0QixtQkFBTSxTQUFTLE9BQU8sU0FBUztBQUNwQyxrQkFBSyxnQkFBZSxTQUFTLE1BQU0sRUFBRSxXQUFXO0FBQUksdUJBQU8sZUFBZSxTQUFTO0FBQUE7QUFDbkYsaUJBQU8sQ0FBQyxlQUFlO0FBQUE7QUFBQTtBQUk3QixhQUFPLFVBQVU7QUFBQSxRQUdmLFVBQVUsYUFBYTtBQUFBLFFBR3ZCLFNBQVMsYUFBYTtBQUFBO0FBQUE7QUFBQTs7O0FDOUJ4QjtBQUFBO0FBQUEsVUFBSSxPQUFNO0FBQ1YsVUFBSSxtQkFBa0I7QUFDdEIsVUFBSSxXQUFVLHlCQUF1QztBQUNyRCxVQUFJLGNBQWE7QUFFakIsYUFBTyxVQUFVLFNBQVUsUUFBUSxPQUFPO0FBQ3hDLFlBQUksSUFBSSxpQkFBZ0I7QUFDeEIsWUFBSSxJQUFJO0FBQ1IsWUFBSSxTQUFTO0FBQ2IsWUFBSTtBQUNKLGFBQUssT0FBTztBQUFHLFdBQUMsS0FBSSxhQUFZLFFBQVEsS0FBSSxHQUFHLFFBQVEsT0FBTyxLQUFLO0FBRW5FLGVBQU8sTUFBTSxTQUFTO0FBQUcsY0FBSSxLQUFJLEdBQUcsTUFBTSxNQUFNLE9BQU87QUFDckQsYUFBQyxTQUFRLFFBQVEsUUFBUSxPQUFPLEtBQUs7QUFBQTtBQUV2QyxlQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNmVDtBQUFBO0FBQ0EsYUFBTyxVQUFVO0FBQUEsUUFDZjtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBO0FBQUE7QUFBQTs7O0FDUkY7QUFBQTtBQUFBLFVBQUkscUJBQXFCO0FBQ3pCLFVBQUksY0FBYztBQUVsQixVQUFJLGNBQWEsWUFBWSxPQUFPLFVBQVU7QUFLOUMsY0FBUSxJQUFJLE9BQU8sdUJBQXVCLDhCQUE2QixHQUFHO0FBQ3hFLGVBQU8sbUJBQW1CLEdBQUc7QUFBQTtBQUFBO0FBQUE7OztBQ1QvQjtBQUFBO0FBQ0EsY0FBUSxJQUFJLE9BQU87QUFBQTtBQUFBOzs7QUNEbkI7QUFBQTtBQUFBLFVBQUksY0FBYTtBQUNqQixVQUFJLDZCQUE0QjtBQUNoQyxVQUFJLCtCQUE4QjtBQUNsQyxVQUFJLFlBQVc7QUFHZixhQUFPLFVBQVUsWUFBVyxXQUFXLGNBQWMsaUJBQWlCLElBQUk7QUFDeEUsWUFBSSxPQUFPLDJCQUEwQixFQUFFLFVBQVM7QUFDaEQsWUFBSSx5QkFBd0IsNkJBQTRCO0FBQ3hELGVBQU8seUJBQXdCLEtBQUssT0FBTyx1QkFBc0IsT0FBTztBQUFBO0FBQUE7QUFBQTs7O0FDVDFFO0FBQUE7QUFBQSxVQUFJLE9BQU07QUFDVixVQUFJLFVBQVU7QUFDZCxVQUFJLGtDQUFpQztBQUNyQyxVQUFJLHdCQUF1QjtBQUUzQixhQUFPLFVBQVUsU0FBVSxRQUFRLFFBQVE7QUFDekMsWUFBSSxPQUFPLFFBQVE7QUFDbkIsWUFBSSxrQkFBaUIsc0JBQXFCO0FBQzFDLFlBQUksNEJBQTJCLGdDQUErQjtBQUM5RCxpQkFBUyxJQUFJLEdBQUcsSUFBSSxLQUFLLFFBQVEsS0FBSztBQUNwQyxjQUFJLE1BQU0sS0FBSztBQUNmLGNBQUksQ0FBQyxLQUFJLFFBQVE7QUFBTSw0QkFBZSxRQUFRLEtBQUssMEJBQXlCLFFBQVE7QUFBQTtBQUFBO0FBQUE7QUFBQTs7O0FDWHhGO0FBQUE7QUFBQSxVQUFJLFNBQVE7QUFFWixVQUFJLGNBQWM7QUFFbEIsVUFBSSxXQUFXLFNBQVUsU0FBUyxXQUFXO0FBQzNDLFlBQUksUUFBUSxLQUFLLFVBQVU7QUFDM0IsZUFBTyxTQUFTLFdBQVcsT0FDdkIsU0FBUyxTQUFTLFFBQ2xCLE9BQU8sYUFBYSxhQUFhLE9BQU0sYUFDdkMsQ0FBQyxDQUFDO0FBQUE7QUFHUixVQUFJLFlBQVksU0FBUyxZQUFZLFNBQVUsUUFBUTtBQUNyRCxlQUFPLE9BQU8sUUFBUSxRQUFRLGFBQWEsS0FBSztBQUFBO0FBR2xELFVBQUksT0FBTyxTQUFTLE9BQU87QUFDM0IsVUFBSSxTQUFTLFNBQVMsU0FBUztBQUMvQixVQUFJLFdBQVcsU0FBUyxXQUFXO0FBRW5DLGFBQU8sVUFBVTtBQUFBO0FBQUE7OztBQ3BCakI7QUFBQTtBQUFBLFVBQUksVUFBUztBQUNiLFVBQUksNEJBQTJCLDZDQUEyRDtBQUMxRixVQUFJLCtCQUE4QjtBQUNsQyxVQUFJLFlBQVc7QUFDZixVQUFJLFlBQVk7QUFDaEIsVUFBSSw2QkFBNEI7QUFDaEMsVUFBSSxXQUFXO0FBZ0JmLGFBQU8sVUFBVSxTQUFVLFNBQVMsUUFBUTtBQUMxQyxZQUFJLFNBQVMsUUFBUTtBQUNyQixZQUFJLFNBQVMsUUFBUTtBQUNyQixZQUFJLFNBQVMsUUFBUTtBQUNyQixZQUFJLFNBQVEsUUFBUSxLQUFLLGdCQUFnQixnQkFBZ0I7QUFDekQsWUFBSSxRQUFRO0FBQ1YsbUJBQVM7QUFBQSxtQkFDQSxRQUFRO0FBQ2pCLG1CQUFTLFFBQU8sV0FBVyxVQUFVLFFBQVE7QUFBQSxlQUN4QztBQUNMLG1CQUFVLFNBQU8sV0FBVyxJQUFJO0FBQUE7QUFFbEMsWUFBSTtBQUFRLGVBQUssT0FBTyxRQUFRO0FBQzlCLDZCQUFpQixPQUFPO0FBQ3hCLGdCQUFJLFFBQVEsYUFBYTtBQUN2QiwyQkFBYSwwQkFBeUIsUUFBUTtBQUM5QywrQkFBaUIsY0FBYyxXQUFXO0FBQUE7QUFDckMsK0JBQWlCLE9BQU87QUFDL0Isc0JBQVMsU0FBUyxTQUFTLE1BQU0sU0FBVSxVQUFTLE1BQU0sT0FBTyxLQUFLLFFBQVE7QUFFOUUsZ0JBQUksQ0FBQyxXQUFVLG1CQUFtQixRQUFXO0FBQzNDLGtCQUFJLE9BQU8sbUJBQW1CLE9BQU87QUFBZ0I7QUFDckQseUNBQTBCLGdCQUFnQjtBQUFBO0FBRzVDLGdCQUFJLFFBQVEsUUFBUyxrQkFBa0IsZUFBZSxNQUFPO0FBQzNELDJDQUE0QixnQkFBZ0IsUUFBUTtBQUFBO0FBR3RELHNCQUFTLFFBQVEsS0FBSyxnQkFBZ0I7QUFBQTtBQUFBO0FBQUE7QUFBQTs7O0FDbkQxQztBQUFBO0FBQUEsVUFBSSxZQUFXO0FBRWYsYUFBTyxVQUFVLFNBQVUsSUFBSTtBQUM3QixZQUFJLENBQUMsVUFBUyxPQUFPLE9BQU8sTUFBTTtBQUNoQyxnQkFBTSxVQUFVLGVBQWUsT0FBTyxNQUFNO0FBQUE7QUFDNUMsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDTFg7QUFBQTtBQUNBLFVBQUksWUFBVztBQUNmLFVBQUkscUJBQXFCO0FBTXpCLGFBQU8sVUFBVSxPQUFPLGtCQUFtQixnQkFBZSxLQUFLLFdBQVk7QUFDekUsWUFBSSxpQkFBaUI7QUFDckIsWUFBSSxPQUFPO0FBQ1gsWUFBSTtBQUNKLFlBQUk7QUFFRixtQkFBUyxPQUFPLHlCQUF5QixPQUFPLFdBQVcsYUFBYTtBQUN4RSxpQkFBTyxLQUFLLE1BQU07QUFDbEIsMkJBQWlCLGdCQUFnQjtBQUFBLGlCQUMxQixPQUFQO0FBQUE7QUFDRixlQUFPLHlCQUF3QixHQUFHLE9BQU87QUFDdkMsb0JBQVM7QUFDVCw2QkFBbUI7QUFDbkIsY0FBSTtBQUFnQixtQkFBTyxLQUFLLEdBQUc7QUFBQTtBQUM5QixjQUFFLFlBQVk7QUFDbkIsaUJBQU87QUFBQTtBQUFBLFlBRUw7QUFBQTtBQUFBOzs7QUN6Qk47QUFBQTtBQUFBLFVBQUksU0FBUTtBQUVaLGFBQU8sVUFBVSxDQUFDLE9BQU0sV0FBWTtBQUNsQyxxQkFBYTtBQUFBO0FBQ2IsVUFBRSxVQUFVLGNBQWM7QUFFMUIsZUFBTyxPQUFPLGVBQWUsSUFBSSxTQUFTLEVBQUU7QUFBQTtBQUFBO0FBQUE7OztBQ045QztBQUFBO0FBQUEsVUFBSSxPQUFNO0FBQ1YsVUFBSSxZQUFXO0FBQ2YsVUFBSSxhQUFZO0FBQ2hCLFVBQUksNEJBQTJCO0FBRS9CLFVBQUksV0FBVyxXQUFVO0FBQ3pCLFVBQUksbUJBQWtCLE9BQU87QUFLN0IsYUFBTyxVQUFVLDRCQUEyQixPQUFPLGlCQUFpQixTQUFVLEdBQUc7QUFDL0UsWUFBSSxVQUFTO0FBQ2IsWUFBSSxLQUFJLEdBQUc7QUFBVyxpQkFBTyxFQUFFO0FBQy9CLFlBQUksT0FBTyxFQUFFLGVBQWUsY0FBYyxhQUFhLEVBQUUsYUFBYTtBQUNwRSxpQkFBTyxFQUFFLFlBQVk7QUFBQTtBQUNyQixlQUFPLGFBQWEsU0FBUyxtQkFBa0I7QUFBQTtBQUFBO0FBQUE7OztBQ2hCbkQ7QUFBQTtBQUFBO0FBQ0EsVUFBSSxTQUFRO0FBRVosYUFBTyxVQUFVLFNBQVUsYUFBYSxVQUFVO0FBQ2hELFlBQUksU0FBUyxHQUFHO0FBQ2hCLGVBQU8sQ0FBQyxDQUFDLFVBQVUsT0FBTSxXQUFZO0FBRW5DLGlCQUFPLEtBQUssTUFBTSxZQUFZLFdBQVk7QUFBRSxrQkFBTTtBQUFBLGFBQU07QUFBQTtBQUFBO0FBQUE7QUFBQTs7O0FDUDVEO0FBQUE7QUFBQSxVQUFJLGNBQWE7QUFFakIsYUFBTyxVQUFVLFlBQVcsYUFBYSxnQkFBZ0I7QUFBQTtBQUFBOzs7QUNGekQ7QUFBQTtBQUFBLFVBQUksVUFBUztBQUNiLFVBQUksWUFBWTtBQUVoQixVQUFJLFVBQVUsUUFBTztBQUNyQixVQUFJLFdBQVcsV0FBVyxRQUFRO0FBQ2xDLFVBQUksS0FBSyxZQUFZLFNBQVM7QUFDOUIsVUFBSTtBQUFKLFVBQVc7QUFFWCxVQUFJLElBQUk7QUFDTixnQkFBUSxHQUFHLE1BQU07QUFDakIsa0JBQVUsTUFBTSxLQUFLLElBQUksSUFBSSxNQUFNLEtBQUssTUFBTTtBQUFBLGlCQUNyQyxXQUFXO0FBQ3BCLGdCQUFRLFVBQVUsTUFBTTtBQUN4QixZQUFJLENBQUMsU0FBUyxNQUFNLE1BQU0sSUFBSTtBQUM1QixrQkFBUSxVQUFVLE1BQU07QUFDeEIsY0FBSTtBQUFPLHNCQUFVLE1BQU07QUFBQTtBQUFBO0FBSS9CLGFBQU8sVUFBVSxXQUFXLENBQUM7QUFBQTtBQUFBOzs7QUNuQjdCO0FBQUE7QUFDQSxVQUFJLGNBQWE7QUFDakIsVUFBSSxTQUFRO0FBR1osYUFBTyxVQUFVLENBQUMsQ0FBQyxPQUFPLHlCQUF5QixDQUFDLE9BQU0sV0FBWTtBQUNwRSxZQUFJLFNBQVM7QUFHYixlQUFPLENBQUMsT0FBTyxXQUFXLENBQUUsUUFBTyxtQkFBbUIsV0FFcEQsQ0FBQyxPQUFPLFFBQVEsZUFBYyxjQUFhO0FBQUE7QUFBQTtBQUFBOzs7QUNYL0M7QUFBQTtBQUNBLFVBQUksaUJBQWdCO0FBRXBCLGFBQU8sVUFBVSxrQkFDWixDQUFDLE9BQU8sUUFDUixPQUFPLE9BQU8sWUFBWTtBQUFBO0FBQUE7OztBQ0wvQjtBQUFBO0FBQUEsVUFBSSxVQUFTO0FBQ2IsVUFBSSxVQUFTO0FBQ2IsVUFBSSxPQUFNO0FBQ1YsVUFBSSxPQUFNO0FBQ1YsVUFBSSxpQkFBZ0I7QUFDcEIsVUFBSSxxQkFBb0I7QUFFeEIsVUFBSSx5QkFBd0IsUUFBTztBQUNuQyxVQUFJLFVBQVMsUUFBTztBQUNwQixVQUFJLHdCQUF3QixxQkFBb0IsVUFBUyxXQUFVLFFBQU8saUJBQWlCO0FBRTNGLGFBQU8sVUFBVSxTQUFVLE9BQU07QUFDL0IsWUFBSSxDQUFDLEtBQUksd0JBQXVCLFVBQVMsQ0FBRSxtQkFBaUIsT0FBTyx1QkFBc0IsVUFBUyxXQUFXO0FBQzNHLGNBQUksa0JBQWlCLEtBQUksU0FBUSxRQUFPO0FBQ3RDLG1DQUFzQixTQUFRLFFBQU87QUFBQSxpQkFDaEM7QUFDTCxtQ0FBc0IsU0FBUSxzQkFBc0IsWUFBWTtBQUFBO0FBQUE7QUFFbEUsZUFBTyx1QkFBc0I7QUFBQTtBQUFBO0FBQUE7OztBQ2xCakM7QUFBQTtBQUFBLFVBQUksbUJBQWtCO0FBRXRCLFVBQUksaUJBQWdCLGlCQUFnQjtBQUNwQyxVQUFJLE9BQU87QUFFWCxXQUFLLGtCQUFpQjtBQUV0QixhQUFPLFVBQVUsT0FBTyxVQUFVO0FBQUE7QUFBQTs7O0FDUGxDO0FBQUE7QUFBQSxVQUFJLHlCQUF3QjtBQUM1QixVQUFJLGFBQWE7QUFDakIsVUFBSSxtQkFBa0I7QUFFdEIsVUFBSSxpQkFBZ0IsaUJBQWdCO0FBRXBDLFVBQUksb0JBQW9CLFdBQVcsV0FBWTtBQUFFLGVBQU87QUFBQSxjQUFtQjtBQUczRSxVQUFJLFNBQVMsU0FBVSxJQUFJLEtBQUs7QUFDOUIsWUFBSTtBQUNGLGlCQUFPLEdBQUc7QUFBQSxpQkFDSCxPQUFQO0FBQUE7QUFBQTtBQUlKLGFBQU8sVUFBVSx5QkFBd0IsYUFBYSxTQUFVLElBQUk7QUFDbEUsWUFBSSxHQUFHLE1BQUs7QUFDWixlQUFPLE9BQU8sU0FBWSxjQUFjLE9BQU8sT0FBTyxTQUVsRCxPQUFRLFFBQU0sT0FBTyxJQUFJLE9BQU8sS0FBSyxvQkFBbUIsV0FBVyxPQUVuRSxvQkFBb0IsV0FBVyxLQUU5QixVQUFTLFdBQVcsT0FBTyxZQUFZLE9BQU8sRUFBRSxVQUFVLGFBQWEsY0FBYztBQUFBO0FBQUE7QUFBQTs7O0FDeEI1RjtBQUFBO0FBQUE7QUFDQSxVQUFJLHlCQUF3QjtBQUM1QixVQUFJLFVBQVU7QUFJZCxhQUFPLFVBQVUseUJBQXdCLEdBQUcsV0FBVyxxQkFBb0I7QUFDekUsZUFBTyxhQUFhLFFBQVEsUUFBUTtBQUFBO0FBQUE7QUFBQTs7O0FDUHRDO0FBQUE7QUFBQTtBQUNBLFVBQUksWUFBVztBQUlmLGFBQU8sVUFBVSxXQUFZO0FBQzNCLFlBQUksT0FBTyxVQUFTO0FBQ3BCLFlBQUksU0FBUztBQUNiLFlBQUksS0FBSztBQUFRLG9CQUFVO0FBQzNCLFlBQUksS0FBSztBQUFZLG9CQUFVO0FBQy9CLFlBQUksS0FBSztBQUFXLG9CQUFVO0FBQzlCLFlBQUksS0FBSztBQUFRLG9CQUFVO0FBQzNCLFlBQUksS0FBSztBQUFTLG9CQUFVO0FBQzVCLFlBQUksS0FBSztBQUFRLG9CQUFVO0FBQzNCLGVBQU87QUFBQTtBQUFBO0FBQUE7OztBQ2RUO0FBQUE7QUFBQSxhQUFPLFVBQVUsU0FBVSxJQUFJO0FBQzdCLFlBQUksT0FBTyxNQUFNLFlBQVk7QUFDM0IsZ0JBQU0sVUFBVSxPQUFPLE1BQU07QUFBQTtBQUM3QixlQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNIWDtBQUFBO0FBQUEsVUFBSSxxQkFBcUI7QUFDekIsVUFBSSxjQUFjO0FBS2xCLGFBQU8sVUFBVSxPQUFPLFFBQVEsY0FBYyxHQUFHO0FBQy9DLGVBQU8sbUJBQW1CLEdBQUc7QUFBQTtBQUFBO0FBQUE7OztBQ1AvQjtBQUFBO0FBQUEsVUFBSSxlQUFjO0FBQ2xCLFVBQUksd0JBQXVCO0FBQzNCLFVBQUksWUFBVztBQUNmLFVBQUksY0FBYTtBQUtqQixhQUFPLFVBQVUsZUFBYyxPQUFPLG1CQUFtQiwyQkFBMEIsR0FBRyxZQUFZO0FBQ2hHLGtCQUFTO0FBQ1QsWUFBSSxPQUFPLFlBQVc7QUFDdEIsWUFBSSxTQUFTLEtBQUs7QUFDbEIsWUFBSSxRQUFRO0FBQ1osWUFBSTtBQUNKLGVBQU8sU0FBUztBQUFPLGdDQUFxQixFQUFFLEdBQUcsTUFBTSxLQUFLLFVBQVUsV0FBVztBQUNqRixlQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNmVDtBQUFBO0FBQUEsVUFBSSxjQUFhO0FBRWpCLGFBQU8sVUFBVSxZQUFXLFlBQVk7QUFBQTtBQUFBOzs7QUNGeEM7QUFBQTtBQUFBLFVBQUksWUFBVztBQUNmLFVBQUksb0JBQW1CO0FBQ3ZCLFVBQUksY0FBYztBQUNsQixVQUFJLGNBQWE7QUFDakIsVUFBSSxPQUFPO0FBQ1gsVUFBSSx3QkFBd0I7QUFDNUIsVUFBSSxhQUFZO0FBRWhCLFVBQUksS0FBSztBQUNULFVBQUksS0FBSztBQUNULFVBQUksYUFBWTtBQUNoQixVQUFJLFNBQVM7QUFDYixVQUFJLFdBQVcsV0FBVTtBQUV6QixVQUFJLG1CQUFtQixXQUFZO0FBQUE7QUFFbkMsVUFBSSxZQUFZLFNBQVUsU0FBUztBQUNqQyxlQUFPLEtBQUssU0FBUyxLQUFLLFVBQVUsS0FBSyxNQUFNLFNBQVM7QUFBQTtBQUkxRCxVQUFJLDRCQUE0QixTQUFVLGtCQUFpQjtBQUN6RCx5QkFBZ0IsTUFBTSxVQUFVO0FBQ2hDLHlCQUFnQjtBQUNoQixZQUFJLE9BQU8saUJBQWdCLGFBQWE7QUFDeEMsMkJBQWtCO0FBQ2xCLGVBQU87QUFBQTtBQUlULFVBQUksMkJBQTJCLFdBQVk7QUFFekMsWUFBSSxTQUFTLHNCQUFzQjtBQUNuQyxZQUFJLEtBQUssU0FBUyxTQUFTO0FBQzNCLFlBQUk7QUFDSixlQUFPLE1BQU0sVUFBVTtBQUN2QixhQUFLLFlBQVk7QUFFakIsZUFBTyxNQUFNLE9BQU87QUFDcEIseUJBQWlCLE9BQU8sY0FBYztBQUN0Qyx1QkFBZTtBQUNmLHVCQUFlLE1BQU0sVUFBVTtBQUMvQix1QkFBZTtBQUNmLGVBQU8sZUFBZTtBQUFBO0FBUXhCLFVBQUk7QUFDSixVQUFJLGtCQUFrQixXQUFZO0FBQ2hDLFlBQUk7QUFFRiw0QkFBa0IsU0FBUyxVQUFVLElBQUksY0FBYztBQUFBLGlCQUNoRCxPQUFQO0FBQUE7QUFDRiwwQkFBa0Isa0JBQWtCLDBCQUEwQixtQkFBbUI7QUFDakYsWUFBSSxTQUFTLFlBQVk7QUFDekIsZUFBTztBQUFVLGlCQUFPLGdCQUFnQixZQUFXLFlBQVk7QUFDL0QsZUFBTztBQUFBO0FBR1Qsa0JBQVcsWUFBWTtBQUl2QixhQUFPLFVBQVUsT0FBTyxVQUFVLGlCQUFnQixHQUFHLFlBQVk7QUFDL0QsWUFBSTtBQUNKLFlBQUksTUFBTSxNQUFNO0FBQ2QsMkJBQWlCLGNBQWEsVUFBUztBQUN2QyxtQkFBUyxJQUFJO0FBQ2IsMkJBQWlCLGNBQWE7QUFFOUIsaUJBQU8sWUFBWTtBQUFBO0FBQ2QsbUJBQVM7QUFDaEIsZUFBTyxlQUFlLFNBQVksU0FBUyxrQkFBaUIsUUFBUTtBQUFBO0FBQUE7QUFBQTs7O0FDNUV0RTtBQUFBO0FBQUE7QUFDQSxVQUFJLGFBQVk7QUFDaEIsVUFBSSxZQUFXO0FBRWYsVUFBSSxTQUFRLEdBQUc7QUFDZixVQUFJLFlBQVk7QUFFaEIsVUFBSSxhQUFZLFNBQVUsR0FBRyxZQUFZLE1BQU07QUFDN0MsWUFBSSxDQUFFLGVBQWMsWUFBWTtBQUM5QixtQkFBUyxPQUFPLElBQUksSUFBSSxHQUFHLElBQUksWUFBWTtBQUFLLGlCQUFLLEtBQUssT0FBTyxJQUFJO0FBRXJFLG9CQUFVLGNBQWMsU0FBUyxPQUFPLGtCQUFrQixLQUFLLEtBQUssT0FBTztBQUFBO0FBQzNFLGVBQU8sVUFBVSxZQUFZLEdBQUc7QUFBQTtBQUtwQyxhQUFPLFVBQVUsU0FBUyxRQUFRLGVBQWMsTUFBc0I7QUFDcEUsWUFBSSxLQUFLLFdBQVU7QUFDbkIsWUFBSSxXQUFXLE9BQU0sS0FBSyxXQUFXO0FBQ3JDLFlBQUksZ0JBQWdCLGlCQUE4QjtBQUNoRCxjQUFJLE9BQU8sU0FBUyxPQUFPLE9BQU0sS0FBSztBQUN0QyxpQkFBTyxnQkFBZ0IsZ0JBQWdCLFdBQVUsSUFBSSxLQUFLLFFBQVEsUUFBUSxHQUFHLE1BQU0sTUFBTTtBQUFBO0FBRTNGLFlBQUksVUFBUyxHQUFHO0FBQVksd0JBQWMsWUFBWSxHQUFHO0FBQ3pELGVBQU87QUFBQTtBQUFBO0FBQUE7OztBQ3pCVDtBQUFBO0FBQUEsVUFBSSxtQkFBa0I7QUFDdEIsVUFBSSxVQUFTO0FBQ2IsVUFBSSx3QkFBdUI7QUFFM0IsVUFBSSxjQUFjLGlCQUFnQjtBQUNsQyxVQUFJLGlCQUFpQixNQUFNO0FBSTNCLFVBQUksZUFBZSxnQkFBZ0IsUUFBVztBQUM1Qyw4QkFBcUIsRUFBRSxnQkFBZ0IsYUFBYTtBQUFBLFVBQ2xELGNBQWM7QUFBQSxVQUNkLE9BQU8sUUFBTztBQUFBO0FBQUE7QUFLbEIsYUFBTyxVQUFVLFNBQVUsS0FBSztBQUM5Qix1QkFBZSxhQUFhLE9BQU87QUFBQTtBQUFBO0FBQUE7OztBQ2xCckM7QUFBQTtBQUFBLGFBQU8sVUFBVTtBQUFBO0FBQUE7OztBQ0FqQjtBQUFBO0FBQUE7QUFDQSxVQUFJLFNBQVE7QUFDWixVQUFJLGtCQUFpQjtBQUNyQixVQUFJLCtCQUE4QjtBQUNsQyxVQUFJLE9BQU07QUFDVixVQUFJLG1CQUFrQjtBQUN0QixVQUFJLFdBQVU7QUFFZCxVQUFJLFlBQVcsaUJBQWdCO0FBQy9CLFVBQUkseUJBQXlCO0FBRTdCLFVBQUksYUFBYSxXQUFZO0FBQUUsZUFBTztBQUFBO0FBSXRDLFVBQUk7QUFBSixVQUF1QjtBQUF2QixVQUEwRDtBQUcxRCxVQUFJLEdBQUcsTUFBTTtBQUNYLHdCQUFnQixHQUFHO0FBRW5CLFlBQUksQ0FBRSxXQUFVO0FBQWdCLG1DQUF5QjtBQUFBLGFBQ3BEO0FBQ0gsOENBQW9DLGdCQUFlLGdCQUFlO0FBQ2xFLGNBQUksc0NBQXNDLE9BQU87QUFBVyxnQ0FBb0I7QUFBQTtBQUFBO0FBSXBGLFVBQUkseUJBQXlCLHFCQUFxQixVQUFhLE9BQU0sV0FBWTtBQUMvRSxZQUFJLE9BQU87QUFFWCxlQUFPLGtCQUFrQixXQUFVLEtBQUssVUFBVTtBQUFBO0FBR3BELFVBQUk7QUFBd0IsNEJBQW9CO0FBSWhELFVBQUssRUFBQyxZQUFXLDJCQUEyQixDQUFDLEtBQUksbUJBQW1CLFlBQVc7QUFDN0UscUNBQTRCLG1CQUFtQixXQUFVO0FBQUE7QUFHM0QsYUFBTyxVQUFVO0FBQUEsUUFDZixtQkFBbUI7QUFBQSxRQUNuQix3QkFBd0I7QUFBQTtBQUFBO0FBQUE7OztBQzVDMUI7QUFBQTtBQUFBLFVBQUksa0JBQWlCLGlDQUErQztBQUNwRSxVQUFJLE9BQU07QUFDVixVQUFJLG1CQUFrQjtBQUV0QixVQUFJLGlCQUFnQixpQkFBZ0I7QUFFcEMsYUFBTyxVQUFVLFNBQVUsSUFBSSxLQUFLLFFBQVE7QUFDMUMsWUFBSSxNQUFNLENBQUMsS0FBSSxLQUFLLFNBQVMsS0FBSyxHQUFHLFdBQVcsaUJBQWdCO0FBQzlELDBCQUFlLElBQUksZ0JBQWUsRUFBRSxjQUFjLE1BQU0sT0FBTztBQUFBO0FBQUE7QUFBQTtBQUFBOzs7QUNSbkU7QUFBQTtBQUFBO0FBQ0EsVUFBSSxvQkFBb0IseUJBQXVDO0FBQy9ELFVBQUksVUFBUztBQUNiLFVBQUksNEJBQTJCO0FBQy9CLFVBQUksa0JBQWlCO0FBQ3JCLFVBQUksWUFBWTtBQUVoQixVQUFJLGFBQWEsV0FBWTtBQUFFLGVBQU87QUFBQTtBQUV0QyxhQUFPLFVBQVUsU0FBVSxxQkFBcUIsT0FBTSxPQUFNO0FBQzFELFlBQUksaUJBQWdCLFFBQU87QUFDM0IsNEJBQW9CLFlBQVksUUFBTyxtQkFBbUIsRUFBRSxNQUFNLDBCQUF5QixHQUFHO0FBQzlGLHdCQUFlLHFCQUFxQixnQkFBZSxPQUFPO0FBQzFELGtCQUFVLGtCQUFpQjtBQUMzQixlQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNkVDtBQUFBO0FBQUE7QUFDQSxVQUFJLE1BQUk7QUFDUixVQUFJLDRCQUE0QjtBQUNoQyxVQUFJLGtCQUFpQjtBQUNyQixVQUFJLGtCQUFpQjtBQUNyQixVQUFJLGtCQUFpQjtBQUNyQixVQUFJLCtCQUE4QjtBQUNsQyxVQUFJLFlBQVc7QUFDZixVQUFJLG1CQUFrQjtBQUN0QixVQUFJLFdBQVU7QUFDZCxVQUFJLFlBQVk7QUFDaEIsVUFBSSxnQkFBZ0I7QUFFcEIsVUFBSSxvQkFBb0IsY0FBYztBQUN0QyxVQUFJLHlCQUF5QixjQUFjO0FBQzNDLFVBQUksWUFBVyxpQkFBZ0I7QUFDL0IsVUFBSSxPQUFPO0FBQ1gsVUFBSSxTQUFTO0FBQ2IsVUFBSSxVQUFVO0FBRWQsVUFBSSxhQUFhLFdBQVk7QUFBRSxlQUFPO0FBQUE7QUFFdEMsYUFBTyxVQUFVLFNBQVUsVUFBVSxPQUFNLHFCQUFxQixPQUFNLFNBQVMsUUFBUSxTQUFRO0FBQzdGLGtDQUEwQixxQkFBcUIsT0FBTTtBQUVyRCxZQUFJLHFCQUFxQixTQUFVLE1BQU07QUFDdkMsY0FBSSxTQUFTLFdBQVc7QUFBaUIsbUJBQU87QUFDaEQsY0FBSSxDQUFDLDBCQUEwQixRQUFRO0FBQW1CLG1CQUFPLGtCQUFrQjtBQUNuRixrQkFBUTtBQUFBLGlCQUNEO0FBQU0scUJBQU8sZ0JBQWdCO0FBQUUsdUJBQU8sSUFBSSxvQkFBb0IsTUFBTTtBQUFBO0FBQUEsaUJBQ3BFO0FBQVEscUJBQU8sa0JBQWtCO0FBQUUsdUJBQU8sSUFBSSxvQkFBb0IsTUFBTTtBQUFBO0FBQUEsaUJBQ3hFO0FBQVMscUJBQU8sb0JBQW1CO0FBQUUsdUJBQU8sSUFBSSxvQkFBb0IsTUFBTTtBQUFBO0FBQUE7QUFDL0UsaUJBQU8sV0FBWTtBQUFFLG1CQUFPLElBQUksb0JBQW9CO0FBQUE7QUFBQTtBQUd4RCxZQUFJLGlCQUFnQixRQUFPO0FBQzNCLFlBQUksd0JBQXdCO0FBQzVCLFlBQUksb0JBQW9CLFNBQVM7QUFDakMsWUFBSSxpQkFBaUIsa0JBQWtCLGNBQ2xDLGtCQUFrQixpQkFDbEIsV0FBVyxrQkFBa0I7QUFDbEMsWUFBSSxrQkFBa0IsQ0FBQywwQkFBMEIsa0JBQWtCLG1CQUFtQjtBQUN0RixZQUFJLG9CQUFvQixTQUFRLFVBQVUsa0JBQWtCLFdBQVcsaUJBQWlCO0FBQ3hGLFlBQUksMEJBQTBCLFNBQVM7QUFHdkMsWUFBSSxtQkFBbUI7QUFDckIscUNBQTJCLGdCQUFlLGtCQUFrQixLQUFLLElBQUk7QUFDckUsY0FBSSxzQkFBc0IsT0FBTyxhQUFhLHlCQUF5QixNQUFNO0FBQzNFLGdCQUFJLENBQUMsWUFBVyxnQkFBZSw4QkFBOEIsbUJBQW1CO0FBQzlFLGtCQUFJLGlCQUFnQjtBQUNsQixnQ0FBZSwwQkFBMEI7QUFBQSx5QkFDaEMsT0FBTyx5QkFBeUIsY0FBYSxZQUFZO0FBQ2xFLDZDQUE0QiwwQkFBMEIsV0FBVTtBQUFBO0FBQUE7QUFJcEUsNEJBQWUsMEJBQTBCLGdCQUFlLE1BQU07QUFDOUQsZ0JBQUk7QUFBUyx3QkFBVSxrQkFBaUI7QUFBQTtBQUFBO0FBSzVDLFlBQUksV0FBVyxVQUFVLGtCQUFrQixlQUFlLFNBQVMsUUFBUTtBQUN6RSxrQ0FBd0I7QUFDeEIsNEJBQWtCLGtCQUFrQjtBQUFFLG1CQUFPLGVBQWUsS0FBSztBQUFBO0FBQUE7QUFJbkUsWUFBSyxFQUFDLFlBQVcsWUFBVyxrQkFBa0IsZUFBYyxpQkFBaUI7QUFDM0UsdUNBQTRCLG1CQUFtQixXQUFVO0FBQUE7QUFFM0Qsa0JBQVUsU0FBUTtBQUdsQixZQUFJLFNBQVM7QUFDWCxvQkFBVTtBQUFBLFlBQ1IsUUFBUSxtQkFBbUI7QUFBQSxZQUMzQixNQUFNLFNBQVMsa0JBQWtCLG1CQUFtQjtBQUFBLFlBQ3BELFNBQVMsbUJBQW1CO0FBQUE7QUFFOUIsY0FBSTtBQUFRLGlCQUFLLE9BQU8sU0FBUztBQUMvQixrQkFBSSwwQkFBMEIseUJBQXlCLENBQUUsUUFBTyxvQkFBb0I7QUFDbEYsMEJBQVMsbUJBQW1CLEtBQUssUUFBUTtBQUFBO0FBQUE7QUFBQTtBQUV0QyxnQkFBRSxFQUFFLFFBQVEsT0FBTSxPQUFPLE1BQU0sUUFBUSwwQkFBMEIseUJBQXlCO0FBQUE7QUFHbkcsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDeEZUO0FBQUE7QUFBQTtBQUNBLFVBQUksbUJBQWtCO0FBQ3RCLFVBQUksbUJBQW1CO0FBQ3ZCLFVBQUksWUFBWTtBQUNoQixVQUFJLHVCQUFzQjtBQUMxQixVQUFJLGtCQUFpQjtBQUVyQixVQUFJLGlCQUFpQjtBQUNyQixVQUFJLG9CQUFtQixxQkFBb0I7QUFDM0MsVUFBSSxvQkFBbUIscUJBQW9CLFVBQVU7QUFZckQsYUFBTyxVQUFVLGdCQUFlLE9BQU8sU0FBUyxTQUFVLFVBQVUsTUFBTTtBQUN4RSwwQkFBaUIsTUFBTTtBQUFBLFVBQ3JCLE1BQU07QUFBQSxVQUNOLFFBQVEsaUJBQWdCO0FBQUEsVUFDeEIsT0FBTztBQUFBLFVBQ1AsTUFBTTtBQUFBO0FBQUEsU0FJUCxXQUFZO0FBQ2IsWUFBSSxRQUFRLGtCQUFpQjtBQUM3QixZQUFJLFNBQVMsTUFBTTtBQUNuQixZQUFJLE9BQU8sTUFBTTtBQUNqQixZQUFJLFFBQVEsTUFBTTtBQUNsQixZQUFJLENBQUMsVUFBVSxTQUFTLE9BQU8sUUFBUTtBQUNyQyxnQkFBTSxTQUFTO0FBQ2YsaUJBQU8sRUFBRSxPQUFPLFFBQVcsTUFBTTtBQUFBO0FBRW5DLFlBQUksUUFBUTtBQUFRLGlCQUFPLEVBQUUsT0FBTyxPQUFPLE1BQU07QUFDakQsWUFBSSxRQUFRO0FBQVUsaUJBQU8sRUFBRSxPQUFPLE9BQU8sUUFBUSxNQUFNO0FBQzNELGVBQU8sRUFBRSxPQUFPLENBQUMsT0FBTyxPQUFPLFNBQVMsTUFBTTtBQUFBLFNBQzdDO0FBS0gsZ0JBQVUsWUFBWSxVQUFVO0FBR2hDLHVCQUFpQjtBQUNqQix1QkFBaUI7QUFDakIsdUJBQWlCO0FBQUE7QUFBQTs7O0FDcERqQjtBQUFBO0FBQUEsVUFBSSxTQUFRO0FBRVosYUFBTyxVQUFVLENBQUMsT0FBTSxXQUFZO0FBRWxDLGVBQU8sT0FBTyxhQUFhLE9BQU8sa0JBQWtCO0FBQUE7QUFBQTtBQUFBOzs7QUNKdEQ7QUFBQTtBQUFBLFVBQUksY0FBYTtBQUNqQixVQUFJLFlBQVc7QUFDZixVQUFJLE9BQU07QUFDVixVQUFJLGtCQUFpQixpQ0FBK0M7QUFDcEUsVUFBSSxPQUFNO0FBQ1YsVUFBSSxXQUFXO0FBRWYsVUFBSSxXQUFXLEtBQUk7QUFDbkIsVUFBSSxLQUFLO0FBR1QsVUFBSSxlQUFlLE9BQU8sZ0JBQWdCLFdBQVk7QUFDcEQsZUFBTztBQUFBO0FBR1QsVUFBSSxjQUFjLFNBQVUsSUFBSTtBQUM5Qix3QkFBZSxJQUFJLFVBQVUsRUFBRSxPQUFPO0FBQUEsVUFDcEMsVUFBVSxNQUFNO0FBQUEsVUFDaEIsVUFBVTtBQUFBO0FBQUE7QUFJZCxVQUFJLFVBQVUsU0FBVSxJQUFJLFNBQVE7QUFFbEMsWUFBSSxDQUFDLFVBQVM7QUFBSyxpQkFBTyxPQUFPLE1BQU0sV0FBVyxLQUFNLFFBQU8sTUFBTSxXQUFXLE1BQU0sT0FBTztBQUM3RixZQUFJLENBQUMsS0FBSSxJQUFJLFdBQVc7QUFFdEIsY0FBSSxDQUFDLGFBQWE7QUFBSyxtQkFBTztBQUU5QixjQUFJLENBQUM7QUFBUSxtQkFBTztBQUVwQixzQkFBWTtBQUFBO0FBRVosZUFBTyxHQUFHLFVBQVU7QUFBQTtBQUd4QixVQUFJLGNBQWMsU0FBVSxJQUFJLFNBQVE7QUFDdEMsWUFBSSxDQUFDLEtBQUksSUFBSSxXQUFXO0FBRXRCLGNBQUksQ0FBQyxhQUFhO0FBQUssbUJBQU87QUFFOUIsY0FBSSxDQUFDO0FBQVEsbUJBQU87QUFFcEIsc0JBQVk7QUFBQTtBQUVaLGVBQU8sR0FBRyxVQUFVO0FBQUE7QUFJeEIsVUFBSSxXQUFXLFNBQVUsSUFBSTtBQUMzQixZQUFJLFlBQVksS0FBSyxZQUFZLGFBQWEsT0FBTyxDQUFDLEtBQUksSUFBSTtBQUFXLHNCQUFZO0FBQ3JGLGVBQU87QUFBQTtBQUdULFVBQUksT0FBTyxPQUFPLFVBQVU7QUFBQSxRQUMxQixVQUFVO0FBQUEsUUFDVixTQUFTO0FBQUEsUUFDVCxhQUFhO0FBQUEsUUFDYixVQUFVO0FBQUE7QUFHWixrQkFBVyxZQUFZO0FBQUE7QUFBQTs7O0FDN0R2QjtBQUFBO0FBQUEsVUFBSSxtQkFBa0I7QUFDdEIsVUFBSSxZQUFZO0FBRWhCLFVBQUksWUFBVyxpQkFBZ0I7QUFDL0IsVUFBSSxpQkFBaUIsTUFBTTtBQUczQixhQUFPLFVBQVUsU0FBVSxJQUFJO0FBQzdCLGVBQU8sT0FBTyxVQUFjLFdBQVUsVUFBVSxNQUFNLGVBQWUsZUFBYztBQUFBO0FBQUE7QUFBQTs7O0FDUnJGO0FBQUE7QUFBQSxVQUFJLGFBQVk7QUFHaEIsYUFBTyxVQUFVLFNBQVUsSUFBSSxNQUFNLFFBQVE7QUFDM0MsbUJBQVU7QUFDVixZQUFJLFNBQVM7QUFBVyxpQkFBTztBQUMvQixnQkFBUTtBQUFBLGVBQ0Q7QUFBRyxtQkFBTyxXQUFZO0FBQ3pCLHFCQUFPLEdBQUcsS0FBSztBQUFBO0FBQUEsZUFFWjtBQUFHLG1CQUFPLFNBQVUsR0FBRztBQUMxQixxQkFBTyxHQUFHLEtBQUssTUFBTTtBQUFBO0FBQUEsZUFFbEI7QUFBRyxtQkFBTyxTQUFVLEdBQUcsR0FBRztBQUM3QixxQkFBTyxHQUFHLEtBQUssTUFBTSxHQUFHO0FBQUE7QUFBQSxlQUVyQjtBQUFHLG1CQUFPLFNBQVUsR0FBRyxHQUFHLEdBQUc7QUFDaEMscUJBQU8sR0FBRyxLQUFLLE1BQU0sR0FBRyxHQUFHO0FBQUE7QUFBQTtBQUcvQixlQUFPLFdBQXlCO0FBQzlCLGlCQUFPLEdBQUcsTUFBTSxNQUFNO0FBQUE7QUFBQTtBQUFBO0FBQUE7OztBQ3JCMUI7QUFBQTtBQUFBLFVBQUksVUFBVTtBQUNkLFVBQUksWUFBWTtBQUNoQixVQUFJLG1CQUFrQjtBQUV0QixVQUFJLFlBQVcsaUJBQWdCO0FBRS9CLGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsWUFBSSxNQUFNO0FBQVcsaUJBQU8sR0FBRyxjQUMxQixHQUFHLGlCQUNILFVBQVUsUUFBUTtBQUFBO0FBQUE7QUFBQTs7O0FDVHpCO0FBQUE7QUFBQSxVQUFJLFlBQVc7QUFFZixhQUFPLFVBQVUsU0FBVSxVQUFVO0FBQ25DLFlBQUksZUFBZSxTQUFTO0FBQzVCLFlBQUksaUJBQWlCLFFBQVc7QUFDOUIsaUJBQU8sVUFBUyxhQUFhLEtBQUssV0FBVztBQUFBO0FBQUE7QUFBQTtBQUFBOzs7QUNMakQ7QUFBQTtBQUFBLFVBQUksWUFBVztBQUNmLFVBQUksd0JBQXdCO0FBQzVCLFVBQUksWUFBVztBQUNmLFVBQUksUUFBTztBQUNYLFVBQUksb0JBQW9CO0FBQ3hCLFVBQUksZ0JBQWdCO0FBRXBCLFVBQUksU0FBUyxTQUFVLFNBQVMsUUFBUTtBQUN0QyxhQUFLLFVBQVU7QUFDZixhQUFLLFNBQVM7QUFBQTtBQUdoQixhQUFPLFVBQVUsU0FBVSxVQUFVLGlCQUFpQixTQUFTO0FBQzdELFlBQUksT0FBTyxXQUFXLFFBQVE7QUFDOUIsWUFBSSxhQUFhLENBQUMsQ0FBRSxZQUFXLFFBQVE7QUFDdkMsWUFBSSxjQUFjLENBQUMsQ0FBRSxZQUFXLFFBQVE7QUFDeEMsWUFBSSxjQUFjLENBQUMsQ0FBRSxZQUFXLFFBQVE7QUFDeEMsWUFBSSxLQUFLLE1BQUssaUJBQWlCLE1BQU0sSUFBSSxhQUFhO0FBQ3RELFlBQUksVUFBVSxRQUFRLE9BQU8sUUFBUSxRQUFRLE9BQU07QUFFbkQsWUFBSSxPQUFPLFNBQVUsV0FBVztBQUM5QixjQUFJO0FBQVUsMEJBQWM7QUFDNUIsaUJBQU8sSUFBSSxPQUFPLE1BQU07QUFBQTtBQUcxQixZQUFJLFNBQVMsU0FBVSxPQUFPO0FBQzVCLGNBQUksWUFBWTtBQUNkLHNCQUFTO0FBQ1QsbUJBQU8sY0FBYyxHQUFHLE1BQU0sSUFBSSxNQUFNLElBQUksUUFBUSxHQUFHLE1BQU0sSUFBSSxNQUFNO0FBQUE7QUFDdkUsaUJBQU8sY0FBYyxHQUFHLE9BQU8sUUFBUSxHQUFHO0FBQUE7QUFHOUMsWUFBSSxhQUFhO0FBQ2YscUJBQVc7QUFBQSxlQUNOO0FBQ0wsbUJBQVMsa0JBQWtCO0FBQzNCLGNBQUksT0FBTyxVQUFVO0FBQVksa0JBQU0sVUFBVTtBQUVqRCxjQUFJLHNCQUFzQixTQUFTO0FBQ2pDLGlCQUFLLFFBQVEsR0FBRyxTQUFTLFVBQVMsU0FBUyxTQUFTLFNBQVMsT0FBTyxTQUFTO0FBQzNFLHVCQUFTLE9BQU8sU0FBUztBQUN6QixrQkFBSSxVQUFVLGtCQUFrQjtBQUFRLHVCQUFPO0FBQUE7QUFDL0MsbUJBQU8sSUFBSSxPQUFPO0FBQUE7QUFFdEIscUJBQVcsT0FBTyxLQUFLO0FBQUE7QUFHekIsZ0JBQU8sU0FBUztBQUNoQixlQUFPLENBQUUsUUFBTyxNQUFLLEtBQUssV0FBVyxNQUFNO0FBQ3pDLGNBQUk7QUFDRixxQkFBUyxPQUFPLEtBQUs7QUFBQSxtQkFDZCxPQUFQO0FBQ0EsMEJBQWM7QUFDZCxrQkFBTTtBQUFBO0FBRVIsY0FBSSxPQUFPLFVBQVUsWUFBWSxVQUFVLGtCQUFrQjtBQUFRLG1CQUFPO0FBQUE7QUFDNUUsZUFBTyxJQUFJLE9BQU87QUFBQTtBQUFBO0FBQUE7OztBQ3hEdEI7QUFBQTtBQUFBLGFBQU8sVUFBVSxTQUFVLElBQUksYUFBYSxPQUFNO0FBQ2hELFlBQUksQ0FBRSxlQUFjLGNBQWM7QUFDaEMsZ0JBQU0sVUFBVSxlQUFnQixTQUFPLFFBQU8sTUFBTSxNQUFNO0FBQUE7QUFDMUQsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDSFg7QUFBQTtBQUFBLFVBQUksbUJBQWtCO0FBRXRCLFVBQUksWUFBVyxpQkFBZ0I7QUFDL0IsVUFBSSxlQUFlO0FBRW5CLFVBQUk7QUFDRSxpQkFBUztBQUNULDZCQUFxQjtBQUFBLFVBQ3ZCLE1BQU0sV0FBWTtBQUNoQixtQkFBTyxFQUFFLE1BQU0sQ0FBQyxDQUFDO0FBQUE7QUFBQSxVQUVuQixVQUFVLFdBQVk7QUFDcEIsMkJBQWU7QUFBQTtBQUFBO0FBR25CLDJCQUFtQixhQUFZLFdBQVk7QUFDekMsaUJBQU87QUFBQTtBQUdULGNBQU0sS0FBSyxvQkFBb0IsV0FBWTtBQUFFLGdCQUFNO0FBQUE7QUFBQSxlQUM1QyxPQUFQO0FBQUE7QUFkSTtBQUNBO0FBZU4sYUFBTyxVQUFVLFNBQVUsTUFBTSxjQUFjO0FBQzdDLFlBQUksQ0FBQyxnQkFBZ0IsQ0FBQztBQUFjLGlCQUFPO0FBQzNDLFlBQUksb0JBQW9CO0FBQ3hCLFlBQUk7QUFDRixjQUFJLFNBQVM7QUFDYixpQkFBTyxhQUFZLFdBQVk7QUFDN0IsbUJBQU87QUFBQSxjQUNMLE1BQU0sV0FBWTtBQUNoQix1QkFBTyxFQUFFLE1BQU0sb0JBQW9CO0FBQUE7QUFBQTtBQUFBO0FBSXpDLGVBQUs7QUFBQSxpQkFDRSxPQUFQO0FBQUE7QUFDRixlQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNwQ1Q7QUFBQTtBQUFBLFVBQUksWUFBVztBQUNmLFVBQUksa0JBQWlCO0FBR3JCLGFBQU8sVUFBVSxTQUFVLE9BQU8sT0FBTyxTQUFTO0FBQ2hELFlBQUksV0FBVztBQUNmLFlBRUUsbUJBRUEsT0FBUSxhQUFZLE1BQU0sZ0JBQWdCLGNBQzFDLGNBQWMsV0FDZCxVQUFTLHFCQUFxQixVQUFVLGNBQ3hDLHVCQUF1QixRQUFRO0FBQy9CLDBCQUFlLE9BQU87QUFDeEIsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDZlQ7QUFBQTtBQUFBO0FBQ0EsVUFBSSxNQUFJO0FBQ1IsVUFBSSxVQUFTO0FBQ2IsVUFBSSxXQUFXO0FBQ2YsVUFBSSxZQUFXO0FBQ2YsVUFBSSx5QkFBeUI7QUFDN0IsVUFBSSxVQUFVO0FBQ2QsVUFBSSxhQUFhO0FBQ2pCLFVBQUksWUFBVztBQUNmLFVBQUksU0FBUTtBQUNaLFVBQUksK0JBQThCO0FBQ2xDLFVBQUksa0JBQWlCO0FBQ3JCLFVBQUksb0JBQW9CO0FBRXhCLGFBQU8sVUFBVSxTQUFVLGtCQUFrQixTQUFTLFFBQVE7QUFDNUQsWUFBSSxTQUFTLGlCQUFpQixRQUFRLFdBQVc7QUFDakQsWUFBSSxVQUFVLGlCQUFpQixRQUFRLFlBQVk7QUFDbkQsWUFBSSxRQUFRLFNBQVMsUUFBUTtBQUM3QixZQUFJLG9CQUFvQixRQUFPO0FBQy9CLFlBQUksa0JBQWtCLHFCQUFxQixrQkFBa0I7QUFDN0QsWUFBSSxjQUFjO0FBQ2xCLFlBQUksV0FBVztBQUVmLFlBQUksWUFBWSxTQUFVLEtBQUs7QUFDN0IsY0FBSSxlQUFlLGdCQUFnQjtBQUNuQyxvQkFBUyxpQkFBaUIsS0FDeEIsT0FBTyxRQUFRLGFBQWEsT0FBTztBQUNqQyx5QkFBYSxLQUFLLE1BQU0sVUFBVSxJQUFJLElBQUk7QUFDMUMsbUJBQU87QUFBQSxjQUNMLE9BQU8sV0FBVyxTQUFVLEtBQUs7QUFDbkMsbUJBQU8sV0FBVyxDQUFDLFVBQVMsT0FBTyxRQUFRLGFBQWEsS0FBSyxNQUFNLFFBQVEsSUFBSSxJQUFJO0FBQUEsY0FDakYsT0FBTyxRQUFRLGFBQWEsS0FBSztBQUNuQyxtQkFBTyxXQUFXLENBQUMsVUFBUyxPQUFPLFNBQVksYUFBYSxLQUFLLE1BQU0sUUFBUSxJQUFJLElBQUk7QUFBQSxjQUNyRixPQUFPLFFBQVEsY0FBYSxLQUFLO0FBQ25DLG1CQUFPLFdBQVcsQ0FBQyxVQUFTLE9BQU8sUUFBUSxhQUFhLEtBQUssTUFBTSxRQUFRLElBQUksSUFBSTtBQUFBLGNBQ2pGLGFBQWEsS0FBSyxPQUFPO0FBQzNCLHlCQUFhLEtBQUssTUFBTSxRQUFRLElBQUksSUFBSSxLQUFLO0FBQzdDLG1CQUFPO0FBQUE7QUFBQTtBQUtiLFlBQUksVUFBVSxTQUNaLGtCQUNBLE9BQU8scUJBQXFCLGNBQWMsQ0FBRSxZQUFXLGdCQUFnQixXQUFXLENBQUMsT0FBTSxXQUFZO0FBQ25HLGNBQUksb0JBQW9CLFVBQVU7QUFBQTtBQUl0QyxZQUFJLFNBQVM7QUFFWCx3QkFBYyxPQUFPLGVBQWUsU0FBUyxrQkFBa0IsUUFBUTtBQUN2RSxpQ0FBdUIsV0FBVztBQUFBLG1CQUN6QixTQUFTLGtCQUFrQixPQUFPO0FBQzNDLGNBQUksV0FBVyxJQUFJO0FBRW5CLGNBQUksaUJBQWlCLFNBQVMsT0FBTyxVQUFVLEtBQUssSUFBSSxNQUFNO0FBRTlELGNBQUksdUJBQXVCLE9BQU0sV0FBWTtBQUFFLHFCQUFTLElBQUk7QUFBQTtBQUc1RCxjQUFJLG1CQUFtQiw2QkFBNEIsU0FBVSxVQUFVO0FBQUUsZ0JBQUksa0JBQWtCO0FBQUE7QUFFL0YsY0FBSSxhQUFhLENBQUMsV0FBVyxPQUFNLFdBQVk7QUFFN0MsZ0JBQUksWUFBWSxJQUFJO0FBQ3BCLGdCQUFJLFFBQVE7QUFDWixtQkFBTztBQUFTLHdCQUFVLE9BQU8sT0FBTztBQUN4QyxtQkFBTyxDQUFDLFVBQVUsSUFBSTtBQUFBO0FBR3hCLGNBQUksQ0FBQyxrQkFBa0I7QUFDckIsMEJBQWMsUUFBUSxTQUFVLE9BQU8sVUFBVTtBQUMvQyx5QkFBVyxPQUFPLGFBQWE7QUFDL0Isa0JBQUksT0FBTyxrQkFBa0IsSUFBSSxxQkFBcUIsT0FBTztBQUM3RCxrQkFBSSxZQUFZO0FBQVcsd0JBQVEsVUFBVSxLQUFLLFFBQVEsRUFBRSxNQUFNLE1BQU0sWUFBWTtBQUNwRixxQkFBTztBQUFBO0FBRVQsd0JBQVksWUFBWTtBQUN4Qiw0QkFBZ0IsY0FBYztBQUFBO0FBR2hDLGNBQUksd0JBQXdCLFlBQVk7QUFDdEMsc0JBQVU7QUFDVixzQkFBVTtBQUNWLHNCQUFVLFVBQVU7QUFBQTtBQUd0QixjQUFJLGNBQWM7QUFBZ0Isc0JBQVU7QUFHNUMsY0FBSSxXQUFXLGdCQUFnQjtBQUFPLG1CQUFPLGdCQUFnQjtBQUFBO0FBRy9ELGlCQUFTLG9CQUFvQjtBQUM3QixZQUFFLEVBQUUsUUFBUSxNQUFNLFFBQVEsZUFBZSxxQkFBcUI7QUFFOUQsd0JBQWUsYUFBYTtBQUU1QixZQUFJLENBQUM7QUFBUyxpQkFBTyxVQUFVLGFBQWEsa0JBQWtCO0FBRTlELGVBQU87QUFBQTtBQUFBO0FBQUE7OztBQ3JHVDtBQUFBO0FBQUEsVUFBSSxZQUFXO0FBRWYsYUFBTyxVQUFVLFNBQVUsUUFBUSxLQUFLLFNBQVM7QUFDL0MsaUJBQVMsT0FBTztBQUFLLG9CQUFTLFFBQVEsS0FBSyxJQUFJLE1BQU07QUFDckQsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDSlQ7QUFBQTtBQUFBO0FBQ0EsVUFBSSxjQUFhO0FBQ2pCLFVBQUksd0JBQXVCO0FBQzNCLFVBQUksbUJBQWtCO0FBQ3RCLFVBQUksZUFBYztBQUVsQixVQUFJLFdBQVUsaUJBQWdCO0FBRTlCLGFBQU8sVUFBVSxTQUFVLGtCQUFrQjtBQUMzQyxZQUFJLGNBQWMsWUFBVztBQUM3QixZQUFJLGtCQUFpQixzQkFBcUI7QUFFMUMsWUFBSSxnQkFBZSxlQUFlLENBQUMsWUFBWSxXQUFVO0FBQ3ZELDBCQUFlLGFBQWEsVUFBUztBQUFBLFlBQ25DLGNBQWM7QUFBQSxZQUNkLEtBQUssV0FBWTtBQUFFLHFCQUFPO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBOzs7QUNmaEM7QUFBQTtBQUFBO0FBQ0EsVUFBSSxrQkFBaUIsaUNBQStDO0FBQ3BFLFVBQUksVUFBUztBQUNiLFVBQUksY0FBYztBQUNsQixVQUFJLFFBQU87QUFDWCxVQUFJLGFBQWE7QUFDakIsVUFBSSxVQUFVO0FBQ2QsVUFBSSxrQkFBaUI7QUFDckIsVUFBSSxhQUFhO0FBQ2pCLFVBQUksZUFBYztBQUNsQixVQUFJLFVBQVUsNEJBQTBDO0FBQ3hELFVBQUksdUJBQXNCO0FBRTFCLFVBQUksb0JBQW1CLHFCQUFvQjtBQUMzQyxVQUFJLHlCQUF5QixxQkFBb0I7QUFFakQsYUFBTyxVQUFVO0FBQUEsUUFDZixnQkFBZ0IsU0FBVSxTQUFTLGtCQUFrQixRQUFRLE9BQU87QUFDbEUsY0FBSSxJQUFJLFFBQVEsU0FBVSxNQUFNLFVBQVU7QUFDeEMsdUJBQVcsTUFBTSxHQUFHO0FBQ3BCLDhCQUFpQixNQUFNO0FBQUEsY0FDckIsTUFBTTtBQUFBLGNBQ04sT0FBTyxRQUFPO0FBQUEsY0FDZCxPQUFPO0FBQUEsY0FDUCxNQUFNO0FBQUEsY0FDTixNQUFNO0FBQUE7QUFFUixnQkFBSSxDQUFDO0FBQWEsbUJBQUssT0FBTztBQUM5QixnQkFBSSxZQUFZO0FBQVcsc0JBQVEsVUFBVSxLQUFLLFFBQVEsRUFBRSxNQUFNLE1BQU0sWUFBWTtBQUFBO0FBR3RGLGNBQUksb0JBQW1CLHVCQUF1QjtBQUU5QyxjQUFJLFNBQVMsU0FBVSxNQUFNLEtBQUssT0FBTztBQUN2QyxnQkFBSSxRQUFRLGtCQUFpQjtBQUM3QixnQkFBSSxRQUFRLFNBQVMsTUFBTTtBQUMzQixnQkFBSSxVQUFVO0FBRWQsZ0JBQUksT0FBTztBQUNULG9CQUFNLFFBQVE7QUFBQSxtQkFFVDtBQUNMLG9CQUFNLE9BQU8sUUFBUTtBQUFBLGdCQUNuQixPQUFPLFFBQVEsUUFBUSxLQUFLO0FBQUEsZ0JBQzVCLEtBQUs7QUFBQSxnQkFDTCxPQUFPO0FBQUEsZ0JBQ1AsVUFBVSxXQUFXLE1BQU07QUFBQSxnQkFDM0IsTUFBTTtBQUFBLGdCQUNOLFNBQVM7QUFBQTtBQUVYLGtCQUFJLENBQUMsTUFBTTtBQUFPLHNCQUFNLFFBQVE7QUFDaEMsa0JBQUk7QUFBVSx5QkFBUyxPQUFPO0FBQzlCLGtCQUFJO0FBQWEsc0JBQU07QUFBQTtBQUNsQixxQkFBSztBQUVWLGtCQUFJLFVBQVU7QUFBSyxzQkFBTSxNQUFNLFNBQVM7QUFBQTtBQUN4QyxtQkFBTztBQUFBO0FBR1gsY0FBSSxXQUFXLFNBQVUsTUFBTSxLQUFLO0FBQ2xDLGdCQUFJLFFBQVEsa0JBQWlCO0FBRTdCLGdCQUFJLFFBQVEsUUFBUTtBQUNwQixnQkFBSTtBQUNKLGdCQUFJLFVBQVU7QUFBSyxxQkFBTyxNQUFNLE1BQU07QUFFdEMsaUJBQUssUUFBUSxNQUFNLE9BQU8sT0FBTyxRQUFRLE1BQU0sTUFBTTtBQUNuRCxrQkFBSSxNQUFNLE9BQU87QUFBSyx1QkFBTztBQUFBO0FBQUE7QUFJakMsc0JBQVksRUFBRSxXQUFXO0FBQUEsWUFJdkIsT0FBTyxpQkFBaUI7QUFDdEIsa0JBQUksT0FBTztBQUNYLGtCQUFJLFFBQVEsa0JBQWlCO0FBQzdCLGtCQUFJLE9BQU8sTUFBTTtBQUNqQixrQkFBSSxRQUFRLE1BQU07QUFDbEIscUJBQU8sT0FBTztBQUNaLHNCQUFNLFVBQVU7QUFDaEIsb0JBQUksTUFBTTtBQUFVLHdCQUFNLFdBQVcsTUFBTSxTQUFTLE9BQU87QUFDM0QsdUJBQU8sS0FBSyxNQUFNO0FBQ2xCLHdCQUFRLE1BQU07QUFBQTtBQUVoQixvQkFBTSxRQUFRLE1BQU0sT0FBTztBQUMzQixrQkFBSTtBQUFhLHNCQUFNLE9BQU87QUFBQTtBQUN6QixxQkFBSyxPQUFPO0FBQUE7QUFBQSxZQUtuQixVQUFVLFNBQVUsS0FBSztBQUN2QixrQkFBSSxPQUFPO0FBQ1gsa0JBQUksUUFBUSxrQkFBaUI7QUFDN0Isa0JBQUksUUFBUSxTQUFTLE1BQU07QUFDM0Isa0JBQUksT0FBTztBQUNULG9CQUFJLFFBQU8sTUFBTTtBQUNqQixvQkFBSSxPQUFPLE1BQU07QUFDakIsdUJBQU8sTUFBTSxNQUFNLE1BQU07QUFDekIsc0JBQU0sVUFBVTtBQUNoQixvQkFBSTtBQUFNLHVCQUFLLE9BQU87QUFDdEIsb0JBQUk7QUFBTSx3QkFBSyxXQUFXO0FBQzFCLG9CQUFJLE1BQU0sU0FBUztBQUFPLHdCQUFNLFFBQVE7QUFDeEMsb0JBQUksTUFBTSxRQUFRO0FBQU8sd0JBQU0sT0FBTztBQUN0QyxvQkFBSTtBQUFhLHdCQUFNO0FBQUE7QUFDbEIsdUJBQUs7QUFBQTtBQUNWLHFCQUFPLENBQUMsQ0FBQztBQUFBO0FBQUEsWUFLYixTQUFTLGtCQUFpQixZQUFxQztBQUM3RCxrQkFBSSxRQUFRLGtCQUFpQjtBQUM3QixrQkFBSSxnQkFBZ0IsTUFBSyxZQUFZLFVBQVUsU0FBUyxJQUFJLFVBQVUsS0FBSyxRQUFXO0FBQ3RGLGtCQUFJO0FBQ0oscUJBQU8sUUFBUSxRQUFRLE1BQU0sT0FBTyxNQUFNLE9BQU87QUFDL0MsOEJBQWMsTUFBTSxPQUFPLE1BQU0sS0FBSztBQUV0Qyx1QkFBTyxTQUFTLE1BQU07QUFBUywwQkFBUSxNQUFNO0FBQUE7QUFBQTtBQUFBLFlBTWpELEtBQUssY0FBYSxLQUFLO0FBQ3JCLHFCQUFPLENBQUMsQ0FBQyxTQUFTLE1BQU07QUFBQTtBQUFBO0FBSTVCLHNCQUFZLEVBQUUsV0FBVyxTQUFTO0FBQUEsWUFHaEMsS0FBSyxhQUFhLEtBQUs7QUFDckIsa0JBQUksUUFBUSxTQUFTLE1BQU07QUFDM0IscUJBQU8sU0FBUyxNQUFNO0FBQUE7QUFBQSxZQUl4QixLQUFLLGFBQWEsS0FBSyxPQUFPO0FBQzVCLHFCQUFPLE9BQU8sTUFBTSxRQUFRLElBQUksSUFBSSxLQUFLO0FBQUE7QUFBQSxjQUV6QztBQUFBLFlBR0YsS0FBSyxhQUFhLE9BQU87QUFDdkIscUJBQU8sT0FBTyxNQUFNLFFBQVEsVUFBVSxJQUFJLElBQUksT0FBTztBQUFBO0FBQUE7QUFHekQsY0FBSTtBQUFhLDRCQUFlLEVBQUUsV0FBVyxRQUFRO0FBQUEsY0FDbkQsS0FBSyxXQUFZO0FBQ2YsdUJBQU8sa0JBQWlCLE1BQU07QUFBQTtBQUFBO0FBR2xDLGlCQUFPO0FBQUE7QUFBQSxRQUVULFdBQVcsU0FBVSxHQUFHLGtCQUFrQixRQUFRO0FBQ2hELGNBQUksZ0JBQWdCLG1CQUFtQjtBQUN2QyxjQUFJLDZCQUE2Qix1QkFBdUI7QUFDeEQsY0FBSSwyQkFBMkIsdUJBQXVCO0FBVXRELDBCQUFlLEdBQUcsa0JBQWtCLFNBQVUsVUFBVSxNQUFNO0FBQzVELDhCQUFpQixNQUFNO0FBQUEsY0FDckIsTUFBTTtBQUFBLGNBQ04sUUFBUTtBQUFBLGNBQ1IsT0FBTywyQkFBMkI7QUFBQSxjQUNsQyxNQUFNO0FBQUEsY0FDTixNQUFNO0FBQUE7QUFBQSxhQUVQLFdBQVk7QUFDYixnQkFBSSxRQUFRLHlCQUF5QjtBQUNyQyxnQkFBSSxPQUFPLE1BQU07QUFDakIsZ0JBQUksUUFBUSxNQUFNO0FBRWxCLG1CQUFPLFNBQVMsTUFBTTtBQUFTLHNCQUFRLE1BQU07QUFFN0MsZ0JBQUksQ0FBQyxNQUFNLFVBQVUsQ0FBRSxPQUFNLE9BQU8sUUFBUSxRQUFRLE1BQU0sT0FBTyxNQUFNLE1BQU0sUUFBUTtBQUVuRixvQkFBTSxTQUFTO0FBQ2YscUJBQU8sRUFBRSxPQUFPLFFBQVcsTUFBTTtBQUFBO0FBR25DLGdCQUFJLFFBQVE7QUFBUSxxQkFBTyxFQUFFLE9BQU8sTUFBTSxLQUFLLE1BQU07QUFDckQsZ0JBQUksUUFBUTtBQUFVLHFCQUFPLEVBQUUsT0FBTyxNQUFNLE9BQU8sTUFBTTtBQUN6RCxtQkFBTyxFQUFFLE9BQU8sQ0FBQyxNQUFNLEtBQUssTUFBTSxRQUFRLE1BQU07QUFBQSxhQUMvQyxTQUFTLFlBQVksVUFBVSxDQUFDLFFBQVE7QUFLM0MscUJBQVc7QUFBQTtBQUFBO0FBQUE7QUFBQTs7O0FDdk1mO0FBQUE7QUFBQTtBQUNBLFVBQUksYUFBYTtBQUNqQixVQUFJLG1CQUFtQjtBQUl2QixhQUFPLFVBQVUsV0FBVyxPQUFPLFNBQVUsTUFBTTtBQUNqRCxlQUFPLGdCQUFlO0FBQUUsaUJBQU8sS0FBSyxNQUFNLFVBQVUsU0FBUyxVQUFVLEtBQUs7QUFBQTtBQUFBLFNBQzNFO0FBQUE7QUFBQTs7O0FDUkg7QUFBQTtBQUFBLFVBQUksWUFBWTtBQUNoQixVQUFJLDBCQUF5QjtBQUc3QixVQUFJLGVBQWUsU0FBVSxtQkFBbUI7QUFDOUMsZUFBTyxTQUFVLE9BQU8sS0FBSztBQUMzQixjQUFJLElBQUksT0FBTyx3QkFBdUI7QUFDdEMsY0FBSSxXQUFXLFVBQVU7QUFDekIsY0FBSSxPQUFPLEVBQUU7QUFDYixjQUFJLE9BQU87QUFDWCxjQUFJLFdBQVcsS0FBSyxZQUFZO0FBQU0sbUJBQU8sb0JBQW9CLEtBQUs7QUFDdEUsa0JBQVEsRUFBRSxXQUFXO0FBQ3JCLGlCQUFPLFFBQVEsU0FBVSxRQUFRLFNBQVUsV0FBVyxNQUFNLFFBQ3RELFVBQVMsRUFBRSxXQUFXLFdBQVcsTUFBTSxTQUFVLFNBQVMsUUFDMUQsb0JBQW9CLEVBQUUsT0FBTyxZQUFZLFFBQ3pDLG9CQUFvQixFQUFFLE1BQU0sVUFBVSxXQUFXLEtBQU0sU0FBUSxTQUFVLE1BQU8sVUFBUyxTQUFVO0FBQUE7QUFBQTtBQUk3RyxhQUFPLFVBQVU7QUFBQSxRQUdmLFFBQVEsYUFBYTtBQUFBLFFBR3JCLFFBQVEsYUFBYTtBQUFBO0FBQUE7QUFBQTs7O0FDekJ2QjtBQUFBO0FBRUEsYUFBTyxVQUFVO0FBQUEsUUFDZixhQUFhO0FBQUEsUUFDYixxQkFBcUI7QUFBQSxRQUNyQixjQUFjO0FBQUEsUUFDZCxnQkFBZ0I7QUFBQSxRQUNoQixhQUFhO0FBQUEsUUFDYixlQUFlO0FBQUEsUUFDZixjQUFjO0FBQUEsUUFDZCxzQkFBc0I7QUFBQSxRQUN0QixVQUFVO0FBQUEsUUFDVixtQkFBbUI7QUFBQSxRQUNuQixnQkFBZ0I7QUFBQSxRQUNoQixpQkFBaUI7QUFBQSxRQUNqQixtQkFBbUI7QUFBQSxRQUNuQixXQUFXO0FBQUEsUUFDWCxlQUFlO0FBQUEsUUFDZixjQUFjO0FBQUEsUUFDZCxVQUFVO0FBQUEsUUFDVixrQkFBa0I7QUFBQSxRQUNsQixRQUFRO0FBQUEsUUFDUixhQUFhO0FBQUEsUUFDYixlQUFlO0FBQUEsUUFDZixlQUFlO0FBQUEsUUFDZixnQkFBZ0I7QUFBQSxRQUNoQixjQUFjO0FBQUEsUUFDZCxlQUFlO0FBQUEsUUFDZixrQkFBa0I7QUFBQSxRQUNsQixrQkFBa0I7QUFBQSxRQUNsQixnQkFBZ0I7QUFBQSxRQUNoQixrQkFBa0I7QUFBQSxRQUNsQixlQUFlO0FBQUEsUUFDZixXQUFXO0FBQUE7QUFBQTtBQUFBOzs7QUNqQ2I7QUFBQTtBQUFBLFVBQUksVUFBVTtBQUtkLGFBQU8sVUFBVSxNQUFNLFdBQVcsa0JBQWlCLEtBQUs7QUFDdEQsZUFBTyxRQUFRLFFBQVE7QUFBQTtBQUFBO0FBQUE7OztBQ056QjtBQUFBO0FBQ0EsVUFBSSxtQkFBa0I7QUFDdEIsVUFBSSx3QkFBdUIsd0NBQXNEO0FBRWpGLFVBQUksWUFBVyxHQUFHO0FBRWxCLFVBQUksY0FBYyxPQUFPLFVBQVUsWUFBWSxVQUFVLE9BQU8sc0JBQzVELE9BQU8sb0JBQW9CLFVBQVU7QUFFekMsVUFBSSxpQkFBaUIsU0FBVSxJQUFJO0FBQ2pDLFlBQUk7QUFDRixpQkFBTyxzQkFBcUI7QUFBQSxpQkFDckIsT0FBUDtBQUNBLGlCQUFPLFlBQVk7QUFBQTtBQUFBO0FBS3ZCLGFBQU8sUUFBUSxJQUFJLDhCQUE2QixJQUFJO0FBQ2xELGVBQU8sZUFBZSxVQUFTLEtBQUssT0FBTyxvQkFDdkMsZUFBZSxNQUNmLHNCQUFxQixpQkFBZ0I7QUFBQTtBQUFBO0FBQUE7OztBQ3JCM0M7QUFBQTtBQUFBLFVBQUksbUJBQWtCO0FBRXRCLGNBQVEsSUFBSTtBQUFBO0FBQUE7OztBQ0ZaO0FBQUE7QUFBQSxVQUFJLE9BQU87QUFDWCxVQUFJLE9BQU07QUFDVixVQUFJLGdDQUErQjtBQUNuQyxVQUFJLGtCQUFpQixpQ0FBK0M7QUFFcEUsYUFBTyxVQUFVLFNBQVUsT0FBTTtBQUMvQixZQUFJLFVBQVMsS0FBSyxVQUFXLE1BQUssU0FBUztBQUMzQyxZQUFJLENBQUMsS0FBSSxTQUFRO0FBQU8sMEJBQWUsU0FBUSxPQUFNO0FBQUEsWUFDbkQsT0FBTyw4QkFBNkIsRUFBRTtBQUFBO0FBQUE7QUFBQTtBQUFBOzs7QUNSMUM7QUFBQTtBQUFBLFVBQUksWUFBVztBQUNmLFVBQUksV0FBVTtBQUNkLFVBQUksbUJBQWtCO0FBRXRCLFVBQUksV0FBVSxpQkFBZ0I7QUFJOUIsYUFBTyxVQUFVLFNBQVUsZUFBZSxRQUFRO0FBQ2hELFlBQUk7QUFDSixZQUFJLFNBQVEsZ0JBQWdCO0FBQzFCLGNBQUksY0FBYztBQUVsQixjQUFJLE9BQU8sS0FBSyxjQUFlLE9BQU0sU0FBUyxTQUFRLEVBQUU7QUFBYSxnQkFBSTtBQUFBLG1CQUNoRSxVQUFTLElBQUk7QUFDcEIsZ0JBQUksRUFBRTtBQUNOLGdCQUFJLE1BQU07QUFBTSxrQkFBSTtBQUFBO0FBQUE7QUFFdEIsZUFBTyxJQUFLLE9BQU0sU0FBWSxRQUFRLEdBQUcsV0FBVyxJQUFJLElBQUk7QUFBQTtBQUFBO0FBQUE7OztBQ2xCaEU7QUFBQTtBQUFBLFVBQUksUUFBTztBQUNYLFVBQUksZ0JBQWdCO0FBQ3BCLFVBQUksWUFBVztBQUNmLFVBQUksWUFBVztBQUNmLFVBQUksc0JBQXFCO0FBRXpCLFVBQUksT0FBTyxHQUFHO0FBR2QsVUFBSSxlQUFlLFNBQVUsTUFBTTtBQUNqQyxZQUFJLFNBQVMsUUFBUTtBQUNyQixZQUFJLFlBQVksUUFBUTtBQUN4QixZQUFJLFVBQVUsUUFBUTtBQUN0QixZQUFJLFdBQVcsUUFBUTtBQUN2QixZQUFJLGdCQUFnQixRQUFRO0FBQzVCLFlBQUksZ0JBQWdCLFFBQVE7QUFDNUIsWUFBSSxXQUFXLFFBQVEsS0FBSztBQUM1QixlQUFPLFNBQVUsT0FBTyxZQUFZLE1BQU0sZ0JBQWdCO0FBQ3hELGNBQUksSUFBSSxVQUFTO0FBQ2pCLGNBQUksUUFBTyxjQUFjO0FBQ3pCLGNBQUksZ0JBQWdCLE1BQUssWUFBWSxNQUFNO0FBQzNDLGNBQUksU0FBUyxVQUFTLE1BQUs7QUFDM0IsY0FBSSxRQUFRO0FBQ1osY0FBSSxVQUFTLGtCQUFrQjtBQUMvQixjQUFJLFNBQVMsU0FBUyxRQUFPLE9BQU8sVUFBVSxhQUFhLGdCQUFnQixRQUFPLE9BQU8sS0FBSztBQUM5RixjQUFJLE9BQU87QUFDWCxpQkFBTSxTQUFTLE9BQU87QUFBUyxnQkFBSSxZQUFZLFNBQVMsT0FBTTtBQUM1RCxzQkFBUSxNQUFLO0FBQ2IsdUJBQVMsY0FBYyxPQUFPLE9BQU87QUFDckMsa0JBQUksTUFBTTtBQUNSLG9CQUFJO0FBQVEseUJBQU8sU0FBUztBQUFBLHlCQUNuQjtBQUFRLDBCQUFRO0FBQUEseUJBQ2xCO0FBQUcsNkJBQU87QUFBQSx5QkFDVjtBQUFHLDZCQUFPO0FBQUEseUJBQ1Y7QUFBRyw2QkFBTztBQUFBLHlCQUNWO0FBQUcsMkJBQUssS0FBSyxRQUFRO0FBQUE7QUFBQTtBQUNyQiwwQkFBUTtBQUFBLHlCQUNSO0FBQUcsNkJBQU87QUFBQSx5QkFDVjtBQUFHLDJCQUFLLEtBQUssUUFBUTtBQUFBO0FBQUE7QUFBQTtBQUloQyxpQkFBTyxnQkFBZ0IsS0FBSyxXQUFXLFdBQVcsV0FBVztBQUFBO0FBQUE7QUFJakUsYUFBTyxVQUFVO0FBQUEsUUFHZixTQUFTLGFBQWE7QUFBQSxRQUd0QixLQUFLLGFBQWE7QUFBQSxRQUdsQixRQUFRLGFBQWE7QUFBQSxRQUdyQixNQUFNLGFBQWE7QUFBQSxRQUduQixPQUFPLGFBQWE7QUFBQSxRQUdwQixNQUFNLGFBQWE7QUFBQSxRQUduQixXQUFXLGFBQWE7QUFBQSxRQUd4QixXQUFXLGFBQWE7QUFBQTtBQUFBO0FBQUE7OztBQ3RFMUI7QUFBQTtBQUFBO0FBQ0EsVUFBSSxZQUFXLDBCQUF3QztBQUN2RCxVQUFJLHVCQUFzQjtBQUUxQixVQUFJLGlCQUFnQixxQkFBb0I7QUFJeEMsYUFBTyxVQUFVLENBQUMsaUJBQWdCLGtCQUFpQixZQUE0QjtBQUM3RSxlQUFPLFVBQVMsTUFBTSxZQUFZLFVBQVUsU0FBUyxJQUFJLFVBQVUsS0FBSztBQUFBLFVBRXRFLEdBQUc7QUFBQTtBQUFBOzs7QUNYUDtBQUFBO0FBQUEsVUFBSSxlQUFjO0FBQ2xCLFVBQUksY0FBYTtBQUNqQixVQUFJLG1CQUFrQjtBQUN0QixVQUFJLHdCQUF1Qix3Q0FBc0Q7QUFHakYsVUFBSSxlQUFlLFNBQVUsWUFBWTtBQUN2QyxlQUFPLFNBQVUsSUFBSTtBQUNuQixjQUFJLElBQUksaUJBQWdCO0FBQ3hCLGNBQUksT0FBTyxZQUFXO0FBQ3RCLGNBQUksU0FBUyxLQUFLO0FBQ2xCLGNBQUksSUFBSTtBQUNSLGNBQUksU0FBUztBQUNiLGNBQUk7QUFDSixpQkFBTyxTQUFTLEdBQUc7QUFDakIsa0JBQU0sS0FBSztBQUNYLGdCQUFJLENBQUMsZ0JBQWUsc0JBQXFCLEtBQUssR0FBRyxNQUFNO0FBQ3JELHFCQUFPLEtBQUssYUFBYSxDQUFDLEtBQUssRUFBRSxRQUFRLEVBQUU7QUFBQTtBQUFBO0FBRy9DLGlCQUFPO0FBQUE7QUFBQTtBQUlYLGFBQU8sVUFBVTtBQUFBLFFBR2YsU0FBUyxhQUFhO0FBQUEsUUFHdEIsUUFBUSxhQUFhO0FBQUE7QUFBQTtBQUFBOzs7QUM5QnZCO0FBQUE7QUFBQSxVQUFJLFlBQVc7QUFDZixVQUFJLFVBQVU7QUFDZCxVQUFJLG1CQUFrQjtBQUV0QixVQUFJLFFBQVEsaUJBQWdCO0FBSTVCLGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsWUFBSTtBQUNKLGVBQU8sVUFBUyxPQUFTLGFBQVcsR0FBRyxZQUFZLFNBQVksQ0FBQyxDQUFDLFdBQVcsUUFBUSxPQUFPO0FBQUE7QUFBQTtBQUFBOzs7QUNWN0Y7QUFBQTtBQUFBLFVBQUksV0FBVztBQUVmLGFBQU8sVUFBVSxTQUFVLElBQUk7QUFDN0IsWUFBSSxTQUFTLEtBQUs7QUFDaEIsZ0JBQU0sVUFBVTtBQUFBO0FBQ2hCLGVBQU87QUFBQTtBQUFBO0FBQUE7OztBQ0xYO0FBQUE7QUFBQSxVQUFJLG1CQUFrQjtBQUV0QixVQUFJLFFBQVEsaUJBQWdCO0FBRTVCLGFBQU8sVUFBVSxTQUFVLGFBQWE7QUFDdEMsWUFBSSxTQUFTO0FBQ2IsWUFBSTtBQUNGLGdCQUFNLGFBQWE7QUFBQSxpQkFDWixRQUFQO0FBQ0EsY0FBSTtBQUNGLG1CQUFPLFNBQVM7QUFDaEIsbUJBQU8sTUFBTSxhQUFhO0FBQUEsbUJBQ25CLFFBQVA7QUFBQTtBQUFBO0FBQ0YsZUFBTztBQUFBO0FBQUE7QUFBQTs7O0FDYlg7QUFBQTtBQUFBO0FBQ0EsVUFBSSxlQUFjO0FBQ2xCLFVBQUksd0JBQXVCO0FBQzNCLFVBQUksNEJBQTJCO0FBRS9CLGFBQU8sVUFBVSxTQUFVLFFBQVEsS0FBSyxPQUFPO0FBQzdDLFlBQUksY0FBYyxhQUFZO0FBQzlCLFlBQUksZUFBZTtBQUFRLGdDQUFxQixFQUFFLFFBQVEsYUFBYSwwQkFBeUIsR0FBRztBQUFBO0FBQzlGLGlCQUFPLGVBQWU7QUFBQTtBQUFBO0FBQUE7OztBQ1I3QjtBQUFBO0FBQUEsVUFBSSxTQUFRO0FBQ1osVUFBSSxtQkFBa0I7QUFDdEIsVUFBSSxjQUFhO0FBRWpCLFVBQUksV0FBVSxpQkFBZ0I7QUFFOUIsYUFBTyxVQUFVLFNBQVUsYUFBYTtBQUl0QyxlQUFPLGVBQWMsTUFBTSxDQUFDLE9BQU0sV0FBWTtBQUM1QyxjQUFJLFFBQVE7QUFDWixjQUFJLGNBQWMsTUFBTSxjQUFjO0FBQ3RDLHNCQUFZLFlBQVcsV0FBWTtBQUNqQyxtQkFBTyxFQUFFLEtBQUs7QUFBQTtBQUVoQixpQkFBTyxNQUFNLGFBQWEsU0FBUyxRQUFRO0FBQUE7QUFBQTtBQUFBO0FBQUE7OztBQ2hCL0M7QUFBQTtBQUFBLFVBQUksWUFBVztBQUNmLFVBQUksZ0JBQWdCO0FBR3BCLGFBQU8sVUFBVSxTQUFVLFVBQVUsSUFBSSxPQUFPLFNBQVM7QUFDdkQsWUFBSTtBQUNGLGlCQUFPLFVBQVUsR0FBRyxVQUFTLE9BQU8sSUFBSSxNQUFNLE1BQU0sR0FBRztBQUFBLGlCQUNoRCxPQUFQO0FBQ0Esd0JBQWM7QUFDZCxnQkFBTTtBQUFBO0FBQUE7QUFBQTtBQUFBOzs7QUNUVjtBQUFBO0FBQUE7QUFDQSxVQUFJLFFBQU87QUFDWCxVQUFJLFlBQVc7QUFDZixVQUFJLCtCQUErQjtBQUNuQyxVQUFJLHdCQUF3QjtBQUM1QixVQUFJLFlBQVc7QUFDZixVQUFJLGtCQUFpQjtBQUNyQixVQUFJLG9CQUFvQjtBQUl4QixhQUFPLFVBQVUsZUFBYyxXQUEwRDtBQUN2RixZQUFJLElBQUksVUFBUztBQUNqQixZQUFJLElBQUksT0FBTyxRQUFRLGFBQWEsT0FBTztBQUMzQyxZQUFJLGtCQUFrQixVQUFVO0FBQ2hDLFlBQUksUUFBUSxrQkFBa0IsSUFBSSxVQUFVLEtBQUs7QUFDakQsWUFBSSxVQUFVLFVBQVU7QUFDeEIsWUFBSSxpQkFBaUIsa0JBQWtCO0FBQ3ZDLFlBQUksUUFBUTtBQUNaLFlBQUksUUFBUSxRQUFRLE1BQU0sVUFBVSxPQUFNO0FBQzFDLFlBQUk7QUFBUyxrQkFBUSxNQUFLLE9BQU8sa0JBQWtCLElBQUksVUFBVSxLQUFLLFFBQVc7QUFFakYsWUFBSSxrQkFBa0IsVUFBYSxDQUFFLE1BQUssU0FBUyxzQkFBc0Isa0JBQWtCO0FBQ3pGLHFCQUFXLGVBQWUsS0FBSztBQUMvQixrQkFBTyxTQUFTO0FBQ2hCLG1CQUFTLElBQUk7QUFDYixpQkFBTSxDQUFFLFFBQU8sTUFBSyxLQUFLLFdBQVcsTUFBTSxTQUFTO0FBQ2pELG9CQUFRLFVBQVUsNkJBQTZCLFVBQVUsT0FBTyxDQUFDLEtBQUssT0FBTyxRQUFRLFFBQVEsS0FBSztBQUNsRyw0QkFBZSxRQUFRLE9BQU87QUFBQTtBQUFBLGVBRTNCO0FBQ0wsbUJBQVMsVUFBUyxFQUFFO0FBQ3BCLG1CQUFTLElBQUksRUFBRTtBQUNmLGlCQUFNLFNBQVMsT0FBTyxTQUFTO0FBQzdCLG9CQUFRLFVBQVUsTUFBTSxFQUFFLFFBQVEsU0FBUyxFQUFFO0FBQzdDLDRCQUFlLFFBQVEsT0FBTztBQUFBO0FBQUE7QUFHbEMsZUFBTyxTQUFTO0FBQ2hCLGVBQU87QUFBQTtBQUFBO0FBQUE7OztBQ3ZDVCxNQUFJLElBQUk7QUFDUixNQUFJLGlCQUFpQjtBQUlyQixJQUFFLEVBQUUsUUFBUSxVQUFVLE1BQU0sUUFBUTtBQUFBLElBQ2xDLGdCQUFnQjtBQUFBOzs7QUNObEIsTUFBSSxLQUFJO0FBQ1IsTUFBSSxRQUFRO0FBQ1osTUFBSSxXQUFXO0FBQ2YsTUFBSSx1QkFBdUI7QUFDM0IsTUFBSSwyQkFBMkI7QUFFL0IsTUFBSSxzQkFBc0IsTUFBTSxXQUFZO0FBQUUseUJBQXFCO0FBQUE7QUFJbkUsS0FBRSxFQUFFLFFBQVEsVUFBVSxNQUFNLE1BQU0sUUFBUSxxQkFBcUIsTUFBTSxDQUFDLDRCQUE0QjtBQUFBLElBQ2hHLGdCQUFnQix3QkFBd0IsSUFBSTtBQUMxQyxhQUFPLHFCQUFxQixTQUFTO0FBQUE7QUFBQTs7O0FDWnpDO0FBRUEsTUFBSSxLQUFJO0FBQ1IsTUFBSSxXQUFXLHlCQUF1QztBQUN0RCxNQUFJLHNCQUFzQjtBQUUxQixNQUFJLGdCQUFnQixHQUFHO0FBRXZCLE1BQUksZ0JBQWdCLENBQUMsQ0FBQyxpQkFBaUIsSUFBSSxDQUFDLEdBQUcsUUFBUSxHQUFHLE1BQU07QUFDaEUsTUFBSSxnQkFBZ0Isb0JBQW9CO0FBSXhDLEtBQUUsRUFBRSxRQUFRLFNBQVMsT0FBTyxNQUFNLFFBQVEsaUJBQWlCLENBQUMsaUJBQWlCO0FBQUEsSUFDM0UsU0FBUyxpQkFBaUIsZUFBcUM7QUFDN0QsYUFBTyxnQkFFSCxjQUFjLE1BQU0sTUFBTSxjQUFjLElBQ3hDLFNBQVMsTUFBTSxlQUFlLFVBQVUsU0FBUyxJQUFJLFVBQVUsS0FBSztBQUFBO0FBQUE7OztBQ2xCNUUsTUFBSSxXQUFXO0FBRWYsTUFBSSxnQkFBZ0IsS0FBSztBQUN6QixNQUFJLGVBQWU7QUFDbkIsTUFBSSxZQUFZO0FBQ2hCLE1BQUkscUJBQXFCLGNBQWM7QUFDdkMsTUFBSSxVQUFVLGNBQWM7QUFJNUIsTUFBSSxJQUFJLEtBQUssT0FBTyxNQUFNLGNBQWM7QUFDdEMsYUFBUyxlQUFlLFdBQVcscUJBQW9CO0FBQ3JELFVBQUksUUFBUSxRQUFRLEtBQUs7QUFFekIsYUFBTyxVQUFVLFFBQVEsbUJBQW1CLEtBQUssUUFBUTtBQUFBO0FBQUE7OztBQ2Q3RCxNQUFJLHdCQUF3QjtBQUM1QixNQUFJLFlBQVc7QUFDZixNQUFJLFdBQVc7QUFJZixNQUFJLENBQUMsdUJBQXVCO0FBQzFCLGNBQVMsT0FBTyxXQUFXLFlBQVksVUFBVSxFQUFFLFFBQVE7QUFBQTs7O0FDUDdEO0FBQ0EsTUFBSSxZQUFXO0FBQ2YsTUFBSSxXQUFXO0FBQ2YsTUFBSSxTQUFRO0FBQ1osTUFBSSxRQUFRO0FBRVosTUFBSSxhQUFZO0FBQ2hCLE1BQUksa0JBQWtCLE9BQU87QUFDN0IsTUFBSSxpQkFBaUIsZ0JBQWdCO0FBRXJDLE1BQUksY0FBYyxPQUFNLFdBQVk7QUFBRSxXQUFPLGVBQWUsS0FBSyxFQUFFLFFBQVEsS0FBSyxPQUFPLFVBQVU7QUFBQTtBQUVqRyxNQUFJLGlCQUFpQixlQUFlLFFBQVE7QUFJNUMsTUFBSSxlQUFlLGdCQUFnQjtBQUNqQyxjQUFTLE9BQU8sV0FBVyxZQUFXLHFCQUFvQjtBQUN4RCxVQUFJLElBQUksU0FBUztBQUNqQixVQUFJLElBQUksT0FBTyxFQUFFO0FBQ2pCLFVBQUksS0FBSyxFQUFFO0FBQ1gsVUFBSSxJQUFJLE9BQU8sT0FBTyxVQUFhLGFBQWEsVUFBVSxDQUFFLFlBQVcsbUJBQW1CLE1BQU0sS0FBSyxLQUFLO0FBQzFHLGFBQU8sTUFBTSxJQUFJLE1BQU07QUFBQSxPQUN0QixFQUFFLFFBQVE7QUFBQTs7O0FDdkJmLE1BQUksS0FBSTtBQUNSLE1BQUksYUFBYTtBQUNqQixNQUFJLFlBQVk7QUFDaEIsTUFBSSxZQUFXO0FBQ2YsTUFBSSxXQUFXO0FBQ2YsTUFBSSxTQUFTO0FBQ2IsTUFBSSxPQUFPO0FBQ1gsTUFBSSxTQUFRO0FBRVosTUFBSSxrQkFBa0IsV0FBVyxXQUFXO0FBTTVDLE1BQUksaUJBQWlCLE9BQU0sV0FBWTtBQUNyQyxpQkFBYTtBQUFBO0FBQ2IsV0FBTyxDQUFFLGlCQUFnQixXQUFZO0FBQUEsT0FBaUIsSUFBSSxjQUFjO0FBQUE7QUFFMUUsTUFBSSxXQUFXLENBQUMsT0FBTSxXQUFZO0FBQ2hDLG9CQUFnQixXQUFZO0FBQUE7QUFBQTtBQUU5QixNQUFJLFNBQVMsa0JBQWtCO0FBRS9CLEtBQUUsRUFBRSxRQUFRLFdBQVcsTUFBTSxNQUFNLFFBQVEsUUFBUSxNQUFNLFVBQVU7QUFBQSxJQUNqRSxXQUFXLG1CQUFtQixRQUFRLE1BQXdCO0FBQzVELGdCQUFVO0FBQ1YsZ0JBQVM7QUFDVCxVQUFJLFlBQVksVUFBVSxTQUFTLElBQUksU0FBUyxVQUFVLFVBQVU7QUFDcEUsVUFBSSxZQUFZLENBQUM7QUFBZ0IsZUFBTyxnQkFBZ0IsUUFBUSxNQUFNO0FBQ3RFLFVBQUksVUFBVSxXQUFXO0FBRXZCLGdCQUFRLEtBQUs7QUFBQSxlQUNOO0FBQUcsbUJBQU8sSUFBSTtBQUFBLGVBQ2Q7QUFBRyxtQkFBTyxJQUFJLE9BQU8sS0FBSztBQUFBLGVBQzFCO0FBQUcsbUJBQU8sSUFBSSxPQUFPLEtBQUssSUFBSSxLQUFLO0FBQUEsZUFDbkM7QUFBRyxtQkFBTyxJQUFJLE9BQU8sS0FBSyxJQUFJLEtBQUssSUFBSSxLQUFLO0FBQUEsZUFDNUM7QUFBRyxtQkFBTyxJQUFJLE9BQU8sS0FBSyxJQUFJLEtBQUssSUFBSSxLQUFLLElBQUksS0FBSztBQUFBO0FBRzVELFlBQUksUUFBUSxDQUFDO0FBQ2IsY0FBTSxLQUFLLE1BQU0sT0FBTztBQUN4QixlQUFPLElBQUssTUFBSyxNQUFNLFFBQVE7QUFBQTtBQUdqQyxVQUFJLFFBQVEsVUFBVTtBQUN0QixVQUFJLFdBQVcsT0FBTyxTQUFTLFNBQVMsUUFBUSxPQUFPO0FBQ3ZELFVBQUksU0FBUyxTQUFTLE1BQU0sS0FBSyxRQUFRLFVBQVU7QUFDbkQsYUFBTyxTQUFTLFVBQVUsU0FBUztBQUFBO0FBQUE7OztBQ2hEdkMsTUFBSSxLQUFJO0FBQ1IsTUFBSSxRQUFPO0FBSVgsS0FBRSxFQUFFLFFBQVEsWUFBWSxPQUFPLFFBQVE7QUFBQSxJQUNyQyxNQUFNO0FBQUE7OztBQ0lSLGtDQUFPO0FBQ1Asc0JBQU87OztBQ1hQO0FBQ0EsTUFBSSxTQUFTLDJCQUF5QztBQUN0RCxNQUFJLHNCQUFzQjtBQUMxQixNQUFJLGlCQUFpQjtBQUVyQixNQUFJLGtCQUFrQjtBQUN0QixNQUFJLG1CQUFtQixvQkFBb0I7QUFDM0MsTUFBSSxtQkFBbUIsb0JBQW9CLFVBQVU7QUFJckQsaUJBQWUsUUFBUSxVQUFVLFNBQVUsVUFBVTtBQUNuRCxxQkFBaUIsTUFBTTtBQUFBLE1BQ3JCLE1BQU07QUFBQSxNQUNOLFFBQVEsT0FBTztBQUFBLE1BQ2YsT0FBTztBQUFBO0FBQUEsS0FJUixnQkFBZ0I7QUFDakIsUUFBSSxRQUFRLGlCQUFpQjtBQUM3QixRQUFJLFNBQVMsTUFBTTtBQUNuQixRQUFJLFFBQVEsTUFBTTtBQUNsQixRQUFJO0FBQ0osUUFBSSxTQUFTLE9BQU87QUFBUSxhQUFPLEVBQUUsT0FBTyxRQUFXLE1BQU07QUFDN0QsWUFBUSxPQUFPLFFBQVE7QUFDdkIsVUFBTSxTQUFTLE1BQU07QUFDckIsV0FBTyxFQUFFLE9BQU8sT0FBTyxNQUFNO0FBQUE7OztBQzNCL0IsTUFBSSxVQUFTO0FBQ2IsTUFBSSxlQUFlO0FBQ25CLE1BQUksdUJBQXVCO0FBQzNCLE1BQUksOEJBQThCO0FBQ2xDLE1BQUksa0JBQWtCO0FBRXRCLE1BQUksV0FBVyxnQkFBZ0I7QUFDL0IsTUFBSSxnQkFBZ0IsZ0JBQWdCO0FBQ3BDLE1BQUksY0FBYyxxQkFBcUI7QUFFdkMsV0FBUyxtQkFBbUIsY0FBYztBQUNwQyxpQkFBYSxRQUFPO0FBQ3BCLDBCQUFzQixjQUFjLFdBQVc7QUFDbkQsUUFBSSxxQkFBcUI7QUFFdkIsVUFBSSxvQkFBb0IsY0FBYztBQUFhLFlBQUk7QUFDckQsc0NBQTRCLHFCQUFxQixVQUFVO0FBQUEsaUJBQ3BELE9BQVA7QUFDQSw4QkFBb0IsWUFBWTtBQUFBO0FBRWxDLFVBQUksQ0FBQyxvQkFBb0IsZ0JBQWdCO0FBQ3ZDLG9DQUE0QixxQkFBcUIsZUFBZTtBQUFBO0FBRWxFLFVBQUksYUFBYTtBQUFrQixhQUFTLGVBQWUsc0JBQXNCO0FBRS9FLGNBQUksb0JBQW9CLGlCQUFpQixxQkFBcUI7QUFBYyxnQkFBSTtBQUM5RSwwQ0FBNEIscUJBQXFCLGFBQWEscUJBQXFCO0FBQUEscUJBQzVFLE9BQVA7QUFDQSxrQ0FBb0IsZUFBZSxxQkFBcUI7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQWpCMUQ7QUFDQTtBQVcwQzs7O0FDdkJoRCxNQUFJLEtBQUk7QUFDUixNQUFJLGNBQWM7QUFDbEIsTUFBSSxVQUFTO0FBSWIsS0FBRSxFQUFFLFFBQVEsVUFBVSxNQUFNLE1BQU0sTUFBTSxDQUFDLGVBQWU7QUFBQSxJQUN0RCxRQUFRO0FBQUE7OztBQ1BWO0FBQ0EsTUFBSSxLQUFJO0FBQ1IsTUFBSSxVQUFTO0FBQ2IsTUFBSSxjQUFhO0FBQ2pCLE1BQUksVUFBVTtBQUNkLE1BQUksZUFBYztBQUNsQixNQUFJLGdCQUFnQjtBQUNwQixNQUFJLG9CQUFvQjtBQUN4QixNQUFJLFNBQVE7QUFDWixNQUFJLE1BQU07QUFDVixNQUFJLFVBQVU7QUFDZCxNQUFJLFlBQVc7QUFDZixNQUFJLFlBQVc7QUFDZixNQUFJLFlBQVc7QUFDZixNQUFJLGtCQUFrQjtBQUN0QixNQUFJLGNBQWM7QUFDbEIsTUFBSSwyQkFBMkI7QUFDL0IsTUFBSSxxQkFBcUI7QUFDekIsTUFBSSxhQUFhO0FBQ2pCLE1BQUksNEJBQTRCO0FBQ2hDLE1BQUksOEJBQThCO0FBQ2xDLE1BQUksOEJBQThCO0FBQ2xDLE1BQUksaUNBQWlDO0FBQ3JDLE1BQUksdUJBQXVCO0FBQzNCLE1BQUksNkJBQTZCO0FBQ2pDLE1BQUksK0JBQThCO0FBQ2xDLE1BQUksWUFBVztBQUNmLE1BQUksU0FBUztBQUNiLE1BQUksWUFBWTtBQUNoQixNQUFJLGFBQWE7QUFDakIsTUFBSSxNQUFNO0FBQ1YsTUFBSSxtQkFBa0I7QUFDdEIsTUFBSSwrQkFBK0I7QUFDbkMsTUFBSSx3QkFBd0I7QUFDNUIsTUFBSSxpQkFBaUI7QUFDckIsTUFBSSx1QkFBc0I7QUFDMUIsTUFBSSxXQUFXLDBCQUF3QztBQUV2RCxNQUFJLFNBQVMsVUFBVTtBQUN2QixNQUFJLFNBQVM7QUFDYixNQUFJLFlBQVk7QUFDaEIsTUFBSSxlQUFlLGlCQUFnQjtBQUNuQyxNQUFJLG9CQUFtQixxQkFBb0I7QUFDM0MsTUFBSSxvQkFBbUIscUJBQW9CLFVBQVU7QUFDckQsTUFBSSxrQkFBa0IsT0FBTztBQUM3QixNQUFJLFVBQVUsUUFBTztBQUNyQixNQUFJLGFBQWEsWUFBVyxRQUFRO0FBQ3BDLE1BQUksaUNBQWlDLCtCQUErQjtBQUNwRSxNQUFJLHVCQUF1QixxQkFBcUI7QUFDaEQsTUFBSSw0QkFBNEIsNEJBQTRCO0FBQzVELE1BQUksNkJBQTZCLDJCQUEyQjtBQUM1RCxNQUFJLGFBQWEsT0FBTztBQUN4QixNQUFJLHlCQUF5QixPQUFPO0FBQ3BDLE1BQUkseUJBQXlCLE9BQU87QUFDcEMsTUFBSSx5QkFBeUIsT0FBTztBQUNwQyxNQUFJLHdCQUF3QixPQUFPO0FBQ25DLE1BQUksVUFBVSxRQUFPO0FBRXJCLE1BQUksYUFBYSxDQUFDLFdBQVcsQ0FBQyxRQUFRLGNBQWMsQ0FBQyxRQUFRLFdBQVc7QUFHeEUsTUFBSSxzQkFBc0IsZ0JBQWUsT0FBTSxXQUFZO0FBQ3pELFdBQU8sbUJBQW1CLHFCQUFxQixJQUFJLEtBQUs7QUFBQSxNQUN0RCxLQUFLLFdBQVk7QUFBRSxlQUFPLHFCQUFxQixNQUFNLEtBQUssRUFBRSxPQUFPLEtBQUs7QUFBQTtBQUFBLFFBQ3RFLEtBQUs7QUFBQSxPQUNOLFNBQVUsR0FBRyxHQUFHLFlBQVk7QUFDL0IsUUFBSSw0QkFBNEIsK0JBQStCLGlCQUFpQjtBQUNoRixRQUFJO0FBQTJCLGFBQU8sZ0JBQWdCO0FBQ3RELHlCQUFxQixHQUFHLEdBQUc7QUFDM0IsUUFBSSw2QkFBNkIsTUFBTSxpQkFBaUI7QUFDdEQsMkJBQXFCLGlCQUFpQixHQUFHO0FBQUE7QUFBQSxNQUV6QztBQUVKLE1BQUksT0FBTyxTQUFVLE1BQUssYUFBYTtBQUNyQyxRQUFJLFNBQVMsV0FBVyxRQUFPLG1CQUFtQixRQUFRO0FBQzFELHNCQUFpQixRQUFRO0FBQUEsTUFDdkIsTUFBTTtBQUFBLE1BQ04sS0FBSztBQUFBLE1BQ0wsYUFBYTtBQUFBO0FBRWYsUUFBSSxDQUFDO0FBQWEsYUFBTyxjQUFjO0FBQ3ZDLFdBQU87QUFBQTtBQUdULE1BQUksV0FBVyxvQkFBb0IsU0FBVSxJQUFJO0FBQy9DLFdBQU8sT0FBTyxNQUFNO0FBQUEsTUFDbEIsU0FBVSxJQUFJO0FBQ2hCLFdBQU8sT0FBTyxlQUFlO0FBQUE7QUFHL0IsTUFBSSxrQkFBa0Isd0JBQXdCLEdBQUcsR0FBRyxZQUFZO0FBQzlELFFBQUksTUFBTTtBQUFpQixzQkFBZ0Isd0JBQXdCLEdBQUc7QUFDdEUsY0FBUztBQUNULFFBQUksTUFBTSxZQUFZLEdBQUc7QUFDekIsY0FBUztBQUNULFFBQUksSUFBSSxZQUFZLE1BQU07QUFDeEIsVUFBSSxDQUFDLFdBQVcsWUFBWTtBQUMxQixZQUFJLENBQUMsSUFBSSxHQUFHO0FBQVMsK0JBQXFCLEdBQUcsUUFBUSx5QkFBeUIsR0FBRztBQUNqRixVQUFFLFFBQVEsT0FBTztBQUFBLGFBQ1o7QUFDTCxZQUFJLElBQUksR0FBRyxXQUFXLEVBQUUsUUFBUTtBQUFNLFlBQUUsUUFBUSxPQUFPO0FBQ3ZELHFCQUFhLG1CQUFtQixZQUFZLEVBQUUsWUFBWSx5QkFBeUIsR0FBRztBQUFBO0FBQ3RGLGFBQU8sb0JBQW9CLEdBQUcsS0FBSztBQUFBO0FBQ3JDLFdBQU8scUJBQXFCLEdBQUcsS0FBSztBQUFBO0FBR3hDLE1BQUksb0JBQW9CLDBCQUEwQixHQUFHLFlBQVk7QUFDL0QsY0FBUztBQUNULFFBQUksYUFBYSxnQkFBZ0I7QUFDakMsUUFBSSxPQUFPLFdBQVcsWUFBWSxPQUFPLHVCQUF1QjtBQUNoRSxhQUFTLE1BQU0sU0FBVSxLQUFLO0FBQzVCLFVBQUksQ0FBQyxnQkFBZSxzQkFBc0IsS0FBSyxZQUFZO0FBQU0sd0JBQWdCLEdBQUcsS0FBSyxXQUFXO0FBQUE7QUFFdEcsV0FBTztBQUFBO0FBR1QsTUFBSSxVQUFVLGlCQUFnQixHQUFHLFlBQVk7QUFDM0MsV0FBTyxlQUFlLFNBQVksbUJBQW1CLEtBQUssa0JBQWtCLG1CQUFtQixJQUFJO0FBQUE7QUFHckcsTUFBSSx3QkFBd0IsOEJBQThCLEdBQUc7QUFDM0QsUUFBSSxJQUFJLFlBQVksR0FBRztBQUN2QixRQUFJLGFBQWEsMkJBQTJCLEtBQUssTUFBTTtBQUN2RCxRQUFJLFNBQVMsbUJBQW1CLElBQUksWUFBWSxNQUFNLENBQUMsSUFBSSx3QkFBd0I7QUFBSSxhQUFPO0FBQzlGLFdBQU8sY0FBYyxDQUFDLElBQUksTUFBTSxNQUFNLENBQUMsSUFBSSxZQUFZLE1BQU0sSUFBSSxNQUFNLFdBQVcsS0FBSyxRQUFRLEtBQUssYUFBYTtBQUFBO0FBR25ILE1BQUksNEJBQTRCLGtDQUFrQyxHQUFHLEdBQUc7QUFDdEUsUUFBSSxLQUFLLGdCQUFnQjtBQUN6QixRQUFJLE1BQU0sWUFBWSxHQUFHO0FBQ3pCLFFBQUksT0FBTyxtQkFBbUIsSUFBSSxZQUFZLFFBQVEsQ0FBQyxJQUFJLHdCQUF3QjtBQUFNO0FBQ3pGLFFBQUksYUFBYSwrQkFBK0IsSUFBSTtBQUNwRCxRQUFJLGNBQWMsSUFBSSxZQUFZLFFBQVEsQ0FBRSxLQUFJLElBQUksV0FBVyxHQUFHLFFBQVEsT0FBTztBQUMvRSxpQkFBVyxhQUFhO0FBQUE7QUFFMUIsV0FBTztBQUFBO0FBR1QsTUFBSSx1QkFBdUIsNkJBQTZCLEdBQUc7QUFDekQsUUFBSSxRQUFRLDBCQUEwQixnQkFBZ0I7QUFDdEQsUUFBSSxTQUFTO0FBQ2IsYUFBUyxPQUFPLFNBQVUsS0FBSztBQUM3QixVQUFJLENBQUMsSUFBSSxZQUFZLFFBQVEsQ0FBQyxJQUFJLFlBQVk7QUFBTSxlQUFPLEtBQUs7QUFBQTtBQUVsRSxXQUFPO0FBQUE7QUFHVCxNQUFJLHlCQUF5QiwrQkFBK0IsR0FBRztBQUM3RCxRQUFJLHNCQUFzQixNQUFNO0FBQ2hDLFFBQUksUUFBUSwwQkFBMEIsc0JBQXNCLHlCQUF5QixnQkFBZ0I7QUFDckcsUUFBSSxTQUFTO0FBQ2IsYUFBUyxPQUFPLFNBQVUsS0FBSztBQUM3QixVQUFJLElBQUksWUFBWSxRQUFTLEVBQUMsdUJBQXVCLElBQUksaUJBQWlCLE9BQU87QUFDL0UsZUFBTyxLQUFLLFdBQVc7QUFBQTtBQUFBO0FBRzNCLFdBQU87QUFBQTtBQUtULE1BQUksQ0FBQyxlQUFlO0FBQ2xCLGNBQVUsbUJBQWtCO0FBQzFCLFVBQUksZ0JBQWdCO0FBQVMsY0FBTSxVQUFVO0FBQzdDLFVBQUksY0FBYyxDQUFDLFVBQVUsVUFBVSxVQUFVLE9BQU8sU0FBWSxTQUFZLE9BQU8sVUFBVTtBQUNqRyxVQUFJLE9BQU0sSUFBSTtBQUNkLFVBQUksU0FBUyxTQUFVLE9BQU87QUFDNUIsWUFBSSxTQUFTO0FBQWlCLGlCQUFPLEtBQUssd0JBQXdCO0FBQ2xFLFlBQUksSUFBSSxNQUFNLFdBQVcsSUFBSSxLQUFLLFNBQVM7QUFBTSxlQUFLLFFBQVEsUUFBTztBQUNyRSw0QkFBb0IsTUFBTSxNQUFLLHlCQUF5QixHQUFHO0FBQUE7QUFFN0QsVUFBSSxnQkFBZTtBQUFZLDRCQUFvQixpQkFBaUIsTUFBSyxFQUFFLGNBQWMsTUFBTSxLQUFLO0FBQ3BHLGFBQU8sS0FBSyxNQUFLO0FBQUE7QUFHbkIsY0FBUyxRQUFRLFlBQVksWUFBWSxxQkFBb0I7QUFDM0QsYUFBTyxrQkFBaUIsTUFBTTtBQUFBO0FBR2hDLGNBQVMsU0FBUyxpQkFBaUIsU0FBVSxhQUFhO0FBQ3hELGFBQU8sS0FBSyxJQUFJLGNBQWM7QUFBQTtBQUdoQywrQkFBMkIsSUFBSTtBQUMvQix5QkFBcUIsSUFBSTtBQUN6QixtQ0FBK0IsSUFBSTtBQUNuQyw4QkFBMEIsSUFBSSw0QkFBNEIsSUFBSTtBQUM5RCxnQ0FBNEIsSUFBSTtBQUVoQyxpQ0FBNkIsSUFBSSxTQUFVLE9BQU07QUFDL0MsYUFBTyxLQUFLLGlCQUFnQixRQUFPO0FBQUE7QUFHckMsUUFBSSxjQUFhO0FBRWYsMkJBQXFCLFFBQVEsWUFBWSxlQUFlO0FBQUEsUUFDdEQsY0FBYztBQUFBLFFBQ2QsS0FBSyx1QkFBdUI7QUFDMUIsaUJBQU8sa0JBQWlCLE1BQU07QUFBQTtBQUFBO0FBR2xDLFVBQUksQ0FBQyxTQUFTO0FBQ1osa0JBQVMsaUJBQWlCLHdCQUF3Qix1QkFBdUIsRUFBRSxRQUFRO0FBQUE7QUFBQTtBQUFBO0FBS3pGLEtBQUUsRUFBRSxRQUFRLE1BQU0sTUFBTSxNQUFNLFFBQVEsQ0FBQyxlQUFlLE1BQU0sQ0FBQyxpQkFBaUI7QUFBQSxJQUM1RSxRQUFRO0FBQUE7QUFHVixXQUFTLFdBQVcsd0JBQXdCLFNBQVUsT0FBTTtBQUMxRCwwQkFBc0I7QUFBQTtBQUd4QixLQUFFLEVBQUUsUUFBUSxRQUFRLE1BQU0sTUFBTSxRQUFRLENBQUMsaUJBQWlCO0FBQUEsSUFHeEQsT0FBTyxTQUFVLEtBQUs7QUFDcEIsVUFBSSxTQUFTLE9BQU87QUFDcEIsVUFBSSxJQUFJLHdCQUF3QjtBQUFTLGVBQU8sdUJBQXVCO0FBQ3ZFLFVBQUksU0FBUyxRQUFRO0FBQ3JCLDZCQUF1QixVQUFVO0FBQ2pDLDZCQUF1QixVQUFVO0FBQ2pDLGFBQU87QUFBQTtBQUFBLElBSVQsUUFBUSxnQkFBZ0IsS0FBSztBQUMzQixVQUFJLENBQUMsU0FBUztBQUFNLGNBQU0sVUFBVSxNQUFNO0FBQzFDLFVBQUksSUFBSSx3QkFBd0I7QUFBTSxlQUFPLHVCQUF1QjtBQUFBO0FBQUEsSUFFdEUsV0FBVyxXQUFZO0FBQUUsbUJBQWE7QUFBQTtBQUFBLElBQ3RDLFdBQVcsV0FBWTtBQUFFLG1CQUFhO0FBQUE7QUFBQTtBQUd4QyxLQUFFLEVBQUUsUUFBUSxVQUFVLE1BQU0sTUFBTSxRQUFRLENBQUMsZUFBZSxNQUFNLENBQUMsZ0JBQWU7QUFBQSxJQUc5RSxRQUFRO0FBQUEsSUFHUixnQkFBZ0I7QUFBQSxJQUdoQixrQkFBa0I7QUFBQSxJQUdsQiwwQkFBMEI7QUFBQTtBQUc1QixLQUFFLEVBQUUsUUFBUSxVQUFVLE1BQU0sTUFBTSxRQUFRLENBQUMsaUJBQWlCO0FBQUEsSUFHMUQscUJBQXFCO0FBQUEsSUFHckIsdUJBQXVCO0FBQUE7QUFLekIsS0FBRSxFQUFFLFFBQVEsVUFBVSxNQUFNLE1BQU0sUUFBUSxPQUFNLFdBQVk7QUFBRSxnQ0FBNEIsRUFBRTtBQUFBLFFBQVU7QUFBQSxJQUNwRyx1QkFBdUIsZ0NBQStCLElBQUk7QUFDeEQsYUFBTyw0QkFBNEIsRUFBRSxVQUFTO0FBQUE7QUFBQTtBQU1sRCxNQUFJLFlBQVk7QUFDViw0QkFBd0IsQ0FBQyxpQkFBaUIsT0FBTSxXQUFZO0FBQzlELFVBQUksU0FBUztBQUViLGFBQU8sV0FBVyxDQUFDLFlBQVksWUFFMUIsV0FBVyxFQUFFLEdBQUcsYUFBYSxRQUU3QixXQUFXLE9BQU8sWUFBWTtBQUFBO0FBR3JDLE9BQUUsRUFBRSxRQUFRLFFBQVEsTUFBTSxNQUFNLFFBQVEseUJBQXlCO0FBQUEsTUFFL0QsV0FBVyxtQkFBbUIsSUFBSSxVQUFVLE9BQU87QUFDakQsWUFBSSxPQUFPLENBQUM7QUFDWixZQUFJLFFBQVE7QUFDWixZQUFJO0FBQ0osZUFBTyxVQUFVLFNBQVM7QUFBTyxlQUFLLEtBQUssVUFBVTtBQUNyRCxvQkFBWTtBQUNaLFlBQUksQ0FBQyxVQUFTLGFBQWEsT0FBTyxVQUFhLFNBQVM7QUFBSztBQUM3RCxZQUFJLENBQUMsUUFBUTtBQUFXLHFCQUFXLFNBQVUsS0FBSyxPQUFPO0FBQ3ZELGdCQUFJLE9BQU8sYUFBYTtBQUFZLHNCQUFRLFVBQVUsS0FBSyxNQUFNLEtBQUs7QUFDdEUsZ0JBQUksQ0FBQyxTQUFTO0FBQVEscUJBQU87QUFBQTtBQUUvQixhQUFLLEtBQUs7QUFDVixlQUFPLFdBQVcsTUFBTSxNQUFNO0FBQUE7QUFBQTtBQUFBO0FBeEI5QjtBQStCTixNQUFJLENBQUMsUUFBUSxXQUFXLGVBQWU7QUFDckMsaUNBQTRCLFFBQVEsWUFBWSxjQUFjLFFBQVEsV0FBVztBQUFBO0FBSW5GLGlCQUFlLFNBQVM7QUFFeEIsYUFBVyxVQUFVOzs7QUNwVHJCO0FBQ0EsTUFBSSxLQUFJO0FBQ1IsTUFBSSxlQUFjO0FBQ2xCLE1BQUksVUFBUztBQUNiLE1BQUksT0FBTTtBQUNWLE1BQUksWUFBVztBQUNmLE1BQUksa0JBQWlCLGlDQUErQztBQUNwRSxNQUFJLDRCQUE0QjtBQUVoQyxNQUFJLGVBQWUsUUFBTztBQUUxQixNQUFJLGdCQUFlLE9BQU8sZ0JBQWdCLGNBQWUsRUFBRSxrQkFBaUIsYUFBYSxjQUV2RixlQUFlLGdCQUFnQixTQUM5QjtBQUNHLGtDQUE4QjtBQUU5QixvQkFBZ0IsbUJBQWtCO0FBQ3BDLFVBQUksY0FBYyxVQUFVLFNBQVMsS0FBSyxVQUFVLE9BQU8sU0FBWSxTQUFZLE9BQU8sVUFBVTtBQUNwRyxVQUFJLFNBQVMsZ0JBQWdCLGdCQUN6QixJQUFJLGFBQWEsZUFFakIsZ0JBQWdCLFNBQVksaUJBQWlCLGFBQWE7QUFDOUQsVUFBSSxnQkFBZ0I7QUFBSSxvQ0FBNEIsVUFBVTtBQUM5RCxhQUFPO0FBQUE7QUFFVCw4QkFBMEIsZUFBZTtBQUNyQyxzQkFBa0IsY0FBYyxZQUFZLGFBQWE7QUFDN0Qsb0JBQWdCLGNBQWM7QUFFMUIscUJBQWlCLGdCQUFnQjtBQUNqQyxhQUFTLE9BQU8sYUFBYSxZQUFZO0FBQ3pDLGFBQVM7QUFDYixvQkFBZSxpQkFBaUIsZUFBZTtBQUFBLE1BQzdDLGNBQWM7QUFBQSxNQUNkLEtBQUssdUJBQXVCO0FBQzFCLFlBQUksU0FBUyxVQUFTLFFBQVEsS0FBSyxZQUFZO0FBQy9DLFlBQUksU0FBUyxlQUFlLEtBQUs7QUFDakMsWUFBSSxLQUFJLDZCQUE2QjtBQUFTLGlCQUFPO0FBQ3JELFlBQUksT0FBTyxTQUFTLE9BQU8sTUFBTSxHQUFHLE1BQU0sT0FBTyxRQUFRLFFBQVE7QUFDakUsZUFBTyxTQUFTLEtBQUssU0FBWTtBQUFBO0FBQUE7QUFJckMsT0FBRSxFQUFFLFFBQVEsTUFBTSxRQUFRLFFBQVE7QUFBQSxNQUNoQyxRQUFRO0FBQUE7QUFBQTtBQTlCTjtBQUVBO0FBVUE7QUFHQTtBQUNBO0FBQ0E7OztBQ2xDTixNQUFJLHlCQUF3QjtBQUk1Qix5QkFBc0I7OztBQ0p0QjtBQUNBLE1BQUksS0FBSTtBQUNSLE1BQUksVUFBVTtBQUtkLEtBQUUsRUFBRSxRQUFRLFNBQVMsT0FBTyxNQUFNLFFBQVEsR0FBRyxXQUFXLFdBQVc7QUFBQSxJQUNqRSxTQUFTO0FBQUE7OztBQ1JYLE1BQUksVUFBUztBQUNiLE1BQUksZ0JBQWU7QUFDbkIsTUFBSSxXQUFVO0FBQ2QsTUFBSSwrQkFBOEI7QUFFbEMsV0FBUyxtQkFBbUIsZUFBYztBQUNwQyxpQkFBYSxRQUFPO0FBQ3BCLDBCQUFzQixjQUFjLFdBQVc7QUFFbkQsUUFBSSx1QkFBdUIsb0JBQW9CLFlBQVk7QUFBUyxVQUFJO0FBQ3RFLHFDQUE0QixxQkFBcUIsV0FBVztBQUFBLGVBQ3JELE9BQVA7QUFDQSw0QkFBb0IsVUFBVTtBQUFBO0FBQUE7QUFONUI7QUFDQTs7O0FDUE4sTUFBSSxNQUFJO0FBQ1IsTUFBSSxXQUFXLDBCQUF3QztBQUl2RCxNQUFFLEVBQUUsUUFBUSxVQUFVLE1BQU0sUUFBUTtBQUFBLElBQ2xDLFNBQVMsaUJBQWlCLEdBQUc7QUFDM0IsYUFBTyxTQUFTO0FBQUE7QUFBQTs7O0FDUHBCO0FBQ0EsTUFBSSxNQUFJO0FBQ1IsTUFBSSw0QkFBMkIsNkNBQTJEO0FBQzFGLE1BQUksV0FBVztBQUNmLE1BQUksYUFBYTtBQUNqQixNQUFJLHlCQUF5QjtBQUM3QixNQUFJLHVCQUF1QjtBQUMzQixNQUFJLFdBQVU7QUFHZCxNQUFJLGNBQWMsR0FBRztBQUNyQixNQUFJLE1BQU0sS0FBSztBQUVmLE1BQUksMEJBQTBCLHFCQUFxQjtBQUVuRCxNQUFJLG1CQUFtQixDQUFDLFlBQVcsQ0FBQywyQkFBMkIsQ0FBQyxDQUFDLFdBQVk7QUFDM0UsUUFBSSxhQUFhLDBCQUF5QixPQUFPLFdBQVc7QUFDNUQsV0FBTyxjQUFjLENBQUMsV0FBVztBQUFBO0FBS25DLE1BQUUsRUFBRSxRQUFRLFVBQVUsT0FBTyxNQUFNLFFBQVEsQ0FBQyxvQkFBb0IsQ0FBQywyQkFBMkI7QUFBQSxJQUMxRixZQUFZLG9CQUFvQixjQUFtQztBQUNqRSxVQUFJLE9BQU8sT0FBTyx1QkFBdUI7QUFDekMsaUJBQVc7QUFDWCxVQUFJLFFBQVEsU0FBUyxJQUFJLFVBQVUsU0FBUyxJQUFJLFVBQVUsS0FBSyxRQUFXLEtBQUs7QUFDL0UsVUFBSSxTQUFTLE9BQU87QUFDcEIsYUFBTyxjQUNILFlBQVksS0FBSyxNQUFNLFFBQVEsU0FDL0IsS0FBSyxNQUFNLE9BQU8sUUFBUSxPQUFPLFlBQVk7QUFBQTtBQUFBOzs7QUM5QnJELE1BQUksTUFBSTtBQUNSLE1BQUksV0FBVTtBQUlkLE1BQUUsRUFBRSxRQUFRLFNBQVMsTUFBTSxRQUFRO0FBQUEsSUFDakMsU0FBUztBQUFBOzs7QUNpQlgsaUNBQU87OztBQ3ZCUDtBQUNBLE1BQUksTUFBSTtBQUNSLE1BQUksWUFBVztBQUNmLE1BQUksV0FBVTtBQUNkLE1BQUksa0JBQWtCO0FBQ3RCLE1BQUksWUFBVztBQUNmLE1BQUksbUJBQWtCO0FBQ3RCLE1BQUksaUJBQWlCO0FBQ3JCLE1BQUksbUJBQWtCO0FBQ3RCLE1BQUksK0JBQStCO0FBRW5DLE1BQUksc0JBQXNCLDZCQUE2QjtBQUV2RCxNQUFJLFVBQVUsaUJBQWdCO0FBQzlCLE1BQUksY0FBYyxHQUFHO0FBQ3JCLE1BQUksTUFBTSxLQUFLO0FBS2YsTUFBRSxFQUFFLFFBQVEsU0FBUyxPQUFPLE1BQU0sUUFBUSxDQUFDLHVCQUF1QjtBQUFBLElBQ2hFLE9BQU8sZUFBZSxPQUFPLEtBQUs7QUFDaEMsVUFBSSxJQUFJLGlCQUFnQjtBQUN4QixVQUFJLFNBQVMsVUFBUyxFQUFFO0FBQ3hCLFVBQUksSUFBSSxnQkFBZ0IsT0FBTztBQUMvQixVQUFJLE1BQU0sZ0JBQWdCLFFBQVEsU0FBWSxTQUFTLEtBQUs7QUFFNUQsVUFBSSxhQUFhLFFBQVE7QUFDekIsVUFBSSxTQUFRLElBQUk7QUFDZCxzQkFBYyxFQUFFO0FBRWhCLFlBQUksT0FBTyxlQUFlLGNBQWUsaUJBQWdCLFNBQVMsU0FBUSxZQUFZLGFBQWE7QUFDakcsd0JBQWM7QUFBQSxtQkFDTCxVQUFTLGNBQWM7QUFDaEMsd0JBQWMsWUFBWTtBQUMxQixjQUFJLGdCQUFnQjtBQUFNLDBCQUFjO0FBQUE7QUFFMUMsWUFBSSxnQkFBZ0IsU0FBUyxnQkFBZ0IsUUFBVztBQUN0RCxpQkFBTyxZQUFZLEtBQUssR0FBRyxHQUFHO0FBQUE7QUFBQTtBQUdsQyxlQUFTLElBQUssaUJBQWdCLFNBQVksUUFBUSxhQUFhLElBQUksTUFBTSxHQUFHO0FBQzVFLFdBQUssSUFBSSxHQUFHLElBQUksS0FBSyxLQUFLO0FBQUssWUFBSSxLQUFLO0FBQUcseUJBQWUsUUFBUSxHQUFHLEVBQUU7QUFDdkUsYUFBTyxTQUFTO0FBQ2hCLGFBQU87QUFBQTtBQUFBOzs7QUM1Q1gsTUFBSSxlQUFjO0FBQ2xCLE1BQUksa0JBQWlCLGlDQUErQztBQUVwRSxNQUFJLG9CQUFvQixTQUFTO0FBQ2pDLE1BQUksNEJBQTRCLGtCQUFrQjtBQUNsRCxNQUFJLFNBQVM7QUFDYixNQUFJLE9BQU87QUFJWCxNQUFJLGdCQUFlLENBQUUsU0FBUSxvQkFBb0I7QUFDL0Msb0JBQWUsbUJBQW1CLE1BQU07QUFBQSxNQUN0QyxjQUFjO0FBQUEsTUFDZCxLQUFLLFdBQVk7QUFDZixZQUFJO0FBQ0YsaUJBQU8sMEJBQTBCLEtBQUssTUFBTSxNQUFNLFFBQVE7QUFBQSxpQkFDbkQsT0FBUDtBQUNBLGlCQUFPO0FBQUE7QUFBQTtBQUFBO0FBQUE7OztBQ2pCZixNQUFJLE1BQUk7QUFDUixNQUFJLE9BQU87QUFDWCxNQUFJLDhCQUE4QjtBQUVsQyxNQUFJLHNCQUFzQixDQUFDLDRCQUE0QixTQUFVLFVBQVU7QUFFekUsVUFBTSxLQUFLO0FBQUE7QUFLYixNQUFFLEVBQUUsUUFBUSxTQUFTLE1BQU0sTUFBTSxRQUFRLHVCQUF1QjtBQUFBLElBQzlELE1BQU07QUFBQTs7O0FIWlIsMEJBQXdCLEtBQUssR0FBRztBQUFFLFdBQU8sZ0JBQWdCLFFBQVEsc0JBQXNCLEtBQUssTUFBTSw0QkFBNEIsS0FBSyxNQUFNO0FBQUE7QUFFekksOEJBQTRCO0FBQUUsVUFBTSxJQUFJLFVBQVU7QUFBQTtBQUVsRCx1Q0FBcUMsR0FBRyxRQUFRO0FBQUUsUUFBSSxDQUFDO0FBQUc7QUFBUSxRQUFJLE9BQU8sTUFBTTtBQUFVLGFBQU8sa0JBQWtCLEdBQUc7QUFBUyxRQUFJLElBQUksT0FBTyxVQUFVLFNBQVMsS0FBSyxHQUFHLE1BQU0sR0FBRztBQUFLLFFBQUksTUFBTSxZQUFZLEVBQUU7QUFBYSxVQUFJLEVBQUUsWUFBWTtBQUFNLFFBQUksTUFBTSxTQUFTLE1BQU07QUFBTyxhQUFPLE1BQU0sS0FBSztBQUFJLFFBQUksTUFBTSxlQUFlLDJDQUEyQyxLQUFLO0FBQUksYUFBTyxrQkFBa0IsR0FBRztBQUFBO0FBRXRaLDZCQUEyQixLQUFLLEtBQUs7QUFBRSxRQUFJLE9BQU8sUUFBUSxNQUFNLElBQUk7QUFBUSxZQUFNLElBQUk7QUFBUSxhQUFTLElBQUksR0FBRyxPQUFPLElBQUksTUFBTSxNQUFNLElBQUksS0FBSyxLQUFLO0FBQUUsV0FBSyxLQUFLLElBQUk7QUFBQTtBQUFNLFdBQU87QUFBQTtBQUVoTCxpQ0FBK0IsS0FBSyxHQUFHO0FBQUUsUUFBSSxLQUFLLE9BQU8sT0FBTyxPQUFPLE9BQU8sV0FBVyxlQUFlLElBQUksT0FBTyxhQUFhLElBQUk7QUFBZSxRQUFJLE1BQU07QUFBTTtBQUFRLFFBQUksT0FBTztBQUFJLFFBQUksS0FBSztBQUFNLFFBQUksS0FBSztBQUFPLFFBQUksSUFBSTtBQUFJLFFBQUk7QUFBRSxXQUFLLEtBQUssR0FBRyxLQUFLLE1BQU0sQ0FBRSxNQUFNLE1BQUssR0FBRyxRQUFRLE9BQU8sS0FBSyxNQUFNO0FBQUUsYUFBSyxLQUFLLEdBQUc7QUFBUSxZQUFJLEtBQUssS0FBSyxXQUFXO0FBQUc7QUFBQTtBQUFBLGFBQWtCLEtBQVA7QUFBYyxXQUFLO0FBQU0sV0FBSztBQUFBLGNBQU87QUFBVSxVQUFJO0FBQUUsWUFBSSxDQUFDLE1BQU0sR0FBRyxhQUFhO0FBQU0sYUFBRztBQUFBLGdCQUFlO0FBQVUsWUFBSTtBQUFJLGdCQUFNO0FBQUE7QUFBQTtBQUFRLFdBQU87QUFBQTtBQUUxZiwyQkFBeUIsS0FBSztBQUFFLFFBQUksTUFBTSxRQUFRO0FBQU0sYUFBTztBQUFBO0FBd0IvRCxlQUFhLE9BQU0sT0FBTztBQUN4QixhQUFTLE9BQU8sVUFBVSxRQUFRLFdBQVcsSUFBSSxNQUFNLE9BQU8sSUFBSSxPQUFPLElBQUksSUFBSSxPQUFPLEdBQUcsT0FBTyxNQUFNLFFBQVE7QUFDOUcsZUFBUyxPQUFPLEtBQUssVUFBVTtBQUFBO0FBR2pDLFFBQUksS0FBSyxTQUFTLGNBQWM7QUFDaEMsV0FBTyxRQUFRLFNBQVMsSUFBSSxRQUFRLFNBQVUsTUFBTTtBQUNsRCxVQUFJLFFBQVEsZUFBZSxNQUFNLElBQzdCLEtBQUssTUFBTSxJQUNYLE1BQU0sTUFBTTtBQUVoQixTQUFHLFdBQVcsU0FBUyxHQUFHLGlCQUFpQixTQUFTLEdBQUcsaUJBQWlCLEdBQUcsY0FBYyxPQUFPLElBQUksT0FBTyxHQUFHLGFBQWEsSUFBSSxJQUFJO0FBQUE7QUFHckksUUFBSSxDQUFDLFVBQVU7QUFDYixhQUFPO0FBQUE7QUFHVCxtQkFBZSxJQUFJO0FBQ25CLFdBQU87QUFBQTtBQUlULHFCQUFtQjtBQUNqQixhQUFTLFFBQVEsVUFBVSxRQUFRLFdBQVcsSUFBSSxNQUFNLFFBQVEsUUFBUSxHQUFHLFFBQVEsT0FBTyxTQUFTO0FBQ2pHLGVBQVMsU0FBUyxVQUFVO0FBQUE7QUFHOUIsV0FBTyxJQUFJLFlBQVksSUFBSSxVQUFVO0FBQUE7QUFLdkMsZ0JBQWMsR0FBRztBQUNmLFFBQUksS0FBSyxTQUFTLGNBQWM7QUFDaEMsT0FBRyxZQUFZO0FBQ2YsV0FBTyxHQUFHO0FBQUE7QUFNWiwwQkFBd0IsR0FBRyxHQUFHO0FBQzVCLFFBQUksYUFBYSxnQkFBZ0I7QUFDL0IsYUFBTyxFQUFFLFNBQVMsR0FBRztBQUNuQixVQUFFLE9BQU8sRUFBRTtBQUFBO0FBQUEsZUFFSixNQUFNLFFBQVEsSUFBSTtBQUMzQixRQUFFLFFBQVEsU0FBVSxHQUFHO0FBQ3JCLGVBQU8sZUFBZSxHQUFHO0FBQUE7QUFBQSxXQUV0QjtBQUNMLFFBQUUsT0FBTztBQUFBO0FBQUE7OztBSXRGYjtBQUNBLE1BQUksTUFBSTtBQUNSLE1BQUksU0FBUTtBQUNaLE1BQUksV0FBVTtBQUNkLE1BQUksWUFBVztBQUNmLE1BQUksWUFBVztBQUNmLE1BQUksWUFBVztBQUNmLE1BQUksa0JBQWlCO0FBQ3JCLE1BQUkscUJBQXFCO0FBQ3pCLE1BQUksZ0NBQStCO0FBQ25DLE1BQUksbUJBQWtCO0FBQ3RCLE1BQUksYUFBYTtBQUVqQixNQUFJLHVCQUF1QixpQkFBZ0I7QUFDM0MsTUFBSSxtQkFBbUI7QUFDdkIsTUFBSSxpQ0FBaUM7QUFLckMsTUFBSSwrQkFBK0IsY0FBYyxNQUFNLENBQUMsT0FBTSxXQUFZO0FBQ3hFLFFBQUksUUFBUTtBQUNaLFVBQU0sd0JBQXdCO0FBQzlCLFdBQU8sTUFBTSxTQUFTLE9BQU87QUFBQTtBQUcvQixNQUFJLGtCQUFrQiw4QkFBNkI7QUFFbkQsTUFBSSxxQkFBcUIsU0FBVSxHQUFHO0FBQ3BDLFFBQUksQ0FBQyxVQUFTO0FBQUksYUFBTztBQUN6QixRQUFJLGFBQWEsRUFBRTtBQUNuQixXQUFPLGVBQWUsU0FBWSxDQUFDLENBQUMsYUFBYSxTQUFRO0FBQUE7QUFHM0QsTUFBSSxVQUFTLENBQUMsZ0NBQWdDLENBQUM7QUFLL0MsTUFBRSxFQUFFLFFBQVEsU0FBUyxPQUFPLE1BQU0sUUFBUSxXQUFVO0FBQUEsSUFFbEQsUUFBUSxnQkFBZ0IsS0FBSztBQUMzQixVQUFJLElBQUksVUFBUztBQUNqQixVQUFJLElBQUksbUJBQW1CLEdBQUc7QUFDOUIsVUFBSSxJQUFJO0FBQ1IsVUFBSSxHQUFHLEdBQUcsUUFBUSxLQUFLO0FBQ3ZCLFdBQUssSUFBSSxJQUFJLFNBQVMsVUFBVSxRQUFRLElBQUksUUFBUSxLQUFLO0FBQ3ZELFlBQUksTUFBTSxLQUFLLElBQUksVUFBVTtBQUM3QixZQUFJLG1CQUFtQixJQUFJO0FBQ3pCLGdCQUFNLFVBQVMsRUFBRTtBQUNqQixjQUFJLElBQUksTUFBTTtBQUFrQixrQkFBTSxVQUFVO0FBQ2hELGVBQUssSUFBSSxHQUFHLElBQUksS0FBSyxLQUFLO0FBQUssZ0JBQUksS0FBSztBQUFHLDhCQUFlLEdBQUcsR0FBRyxFQUFFO0FBQUEsZUFDN0Q7QUFDTCxjQUFJLEtBQUs7QUFBa0Isa0JBQU0sVUFBVTtBQUMzQywwQkFBZSxHQUFHLEtBQUs7QUFBQTtBQUFBO0FBRzNCLFFBQUUsU0FBUztBQUNYLGFBQU87QUFBQTtBQUFBOzs7QUN2RFgsNkJBQTJCLE9BQU0sV0FBVyxRQUFRO0FBQ2xELFFBQUksVUFBVTtBQUFBLE1BQ1osU0FBUztBQUFBLE1BQ1QsTUFBTTtBQUFBLE1BQ04saUJBQWlCLE9BQU87QUFBQTtBQUUxQixRQUFJLEtBQUssTUFBSyxhQUFhO0FBRTNCLFFBQUksSUFBSTtBQUNOLGNBQVEsS0FBSztBQUNiLGNBQVEsV0FBVyxRQUFRLFdBQVc7QUFBQTtBQUd4QyxRQUFJLFFBQVEsSUFBSSxNQUFNLFNBQVMsT0FBTztBQUl0QyxRQUFJLFdBQVc7QUFDZixRQUFJLFNBQVMsTUFBSyxhQUFhO0FBQy9CLFFBQUk7QUFBUSxlQUFTLEtBQUssS0FBSztBQUMvQixhQUFTLEtBQUssT0FBTztBQUNyQixRQUFJLFNBQVMsTUFBSyxhQUFhO0FBQy9CLFFBQUk7QUFBUSxlQUFTLEtBQUssS0FBSztBQUMvQixRQUFJLFNBQVMsSUFBSSxPQUFPO0FBQUEsTUFDdEIsU0FBUztBQUFBLE1BQ1QsaUJBQWlCLE9BQU87QUFBQSxPQUN2QjtBQUNILFdBQU8sUUFBUSxPQUFPO0FBQUE7QUFHeEIsdUJBQXFCLE1BQU0sVUFBVTtBQUVuQyxRQUFJLFVBQVUsSUFBSTtBQUNsQixRQUFJLGFBQWEsSUFBSTtBQUNyQixRQUFJLEtBQUssS0FBSyxNQUFNLE1BQU8sS0FBSyxXQUFXO0FBRTNDLGFBQVMsSUFBSSxHQUFHLElBQUksS0FBSyxRQUFRLEtBQUs7QUFDcEMsVUFBSSxPQUFPLGFBQWEsS0FBSyxJQUFJLFVBQVUsSUFBSSxJQUFJO0FBRW5ELGNBQVEsT0FBTyxLQUFLO0FBRXBCLFVBQUksS0FBSztBQUFRLG1CQUFXLE9BQU8sS0FBSztBQUFBO0FBRzFDLFdBQU87QUFBQSxNQUNMLFNBQVM7QUFBQSxNQUNULFlBQVk7QUFBQSxNQUNaLElBQUk7QUFBQTtBQUFBO0FBSVIsd0JBQXNCLEtBQUssVUFBVSxJQUFJLE9BQU87QUFDOUMsUUFBSSxRQUFRLFNBQVMsY0FBYztBQUVuQyxRQUFJLElBQUksVUFBVSxTQUFTLGVBQWU7QUFDeEMsWUFBTSxVQUFVLElBQUk7QUFDcEIsYUFBTztBQUFBLFFBQ0wsT0FBTztBQUFBLFFBQ1AsUUFBUTtBQUFBO0FBQUE7QUFJWixRQUFJLElBQUksVUFBVSxTQUFTLGFBQWE7QUFHdEMsWUFBTSxVQUFVLElBQUk7QUFDcEIsWUFBTSxPQUFPLElBQUk7QUFDakIsYUFBTztBQUFBLFFBQ0wsT0FBTztBQUFBLFFBQ1AsUUFBUTtBQUFBO0FBQUE7QUFJWixRQUFJLElBQUksVUFBVSxTQUFTLGFBQWE7QUFDdEMsWUFBTSxVQUFVLElBQUk7QUFDcEIsVUFBSSxRQUFRO0FBQUEsUUFDVixNQUFNO0FBQUEsUUFDTixTQUFTO0FBQUEsUUFDVCxlQUFlO0FBQUEsUUFDZixjQUFjLElBQUksYUFBYTtBQUFBO0FBRWpDLFVBQUksU0FBUyxJQUFJLEtBQUssT0FBTyxLQUFLLElBQUksYUFBYTtBQUVuRCxVQUFJLE9BQU8sSUFBSSxNQUFNO0FBQUEsUUFDbkIsaUJBQWlCO0FBQUEsUUFDakIsU0FBUztBQUFBO0FBR1gsVUFBSSxJQUFJLGFBQWEsYUFBYSxTQUFTO0FBQ3pDLGFBQUssVUFBVSxJQUFJO0FBQUE7QUFHckIsVUFBSSxVQUFVLFlBQVksSUFBSSxRQUFRLFVBQVU7QUFPaEQsV0FBSyxPQUFPLFFBQVE7QUFDcEIsWUFBTSxPQUFPO0FBQ2IsWUFBTSxPQUFPO0FBQ2IsYUFBTztBQUFBLFFBQ0wsT0FBTztBQUFBLFFBQ1AsUUFBUSxRQUFRO0FBQUE7QUFBQTtBQUlwQixRQUFJLElBQUksVUFBVSxTQUFTLFFBQVE7QUFDakMsVUFBSSxRQUFRLE9BQU8sT0FBTyxJQUFJLEtBQUssT0FBTztBQUsxQyxVQUFJLE9BQU8sSUFBSSxLQUFLO0FBQUEsUUFDbEIsTUFBTSxNQUFNO0FBQUEsUUFDWixNQUFNO0FBQUEsUUFDTixlQUFlO0FBQUEsUUFDZixjQUFjLElBQUksYUFBYTtBQUFBLFNBQzlCLEtBQUssSUFBSSxhQUFhO0FBQ3pCLFlBQU0sT0FBTztBQUNiLFVBQUksU0FBUyxJQUFJLE9BQU87QUFBQSxRQUN0QixJQUFJO0FBQUEsUUFDSixTQUFTO0FBQUEsUUFDVCxNQUFNO0FBQUEsU0FDTCxJQUFJO0FBR1AsVUFBSSxhQUFhLElBQUksYUFBYSxVQUFVO0FBQzFDLGNBQU0sVUFBVSxJQUFJO0FBQ3BCLGVBQU8sVUFBVSxJQUFJO0FBQUE7QUFHdkIsYUFBTztBQUFBLFFBQ0wsT0FBTztBQUFBLFFBQ1AsUUFBUTtBQUFBO0FBQUE7QUFJWixVQUFNLElBQUksTUFBTSxrQkFBa0IsT0FBTyxNQUFNO0FBQUE7QUFHakQsdUJBQXFCLE9BQU07QUFDekIsUUFBSSxXQUFXLE1BQUssYUFBYTtBQUVqQyxRQUFJLENBQUMsWUFBWSxNQUFLLFNBQVMsU0FBUyxHQUFHO0FBQ3pDLGlCQUFXLGFBQWEsTUFBSyxVQUFVLGFBQWE7QUFBQTtBQUd0RCxXQUFPO0FBQUE7QUFHVCx3QkFBc0IsTUFBTTtBQUMxQixhQUFTLElBQUksR0FBRyxJQUFJLEtBQUssUUFBUSxLQUFLO0FBQ3BDLFVBQUksTUFBTSxLQUFLO0FBRWYsVUFBSSxJQUFJLFVBQVUsU0FBUyxRQUFRO0FBQ2pDLGVBQU87QUFBQTtBQUdULFVBQUksSUFBSSxVQUFVLFNBQVMsYUFBYTtBQUN0QyxxQkFBYTtBQUFBO0FBQUE7QUFBQTtBQUtuQiwyQkFBeUIsR0FBRyxHQUFHO0FBQzdCLFdBQU8sRUFBRSxZQUFZO0FBQ25CLFFBQUUsWUFBWSxFQUFFO0FBQUE7QUFHbEIsbUJBQWUsR0FBRztBQUFBOzs7QUM1S3BCLHNCQUFvQixNQUFNLFFBQVEsUUFBUTtBQUN4QyxRQUFJLE9BQU8sSUFBSSxPQUFPO0FBQUEsTUFDcEIsU0FBUztBQUFBO0FBR1gsUUFBSSxRQUFRO0FBQ1YsV0FBSyxPQUFPLElBQUksT0FBTztBQUFBLFFBQ3JCLFNBQVM7QUFBQSxTQUNSO0FBQUE7QUFHTCxTQUFLLE9BQU8sSUFBSSxPQUFPO0FBQUEsTUFDckIsU0FBUztBQUFBLE9BQ1I7QUFFSCxRQUFJLFFBQVE7QUFDVixXQUFLLE9BQU8sSUFBSSxPQUFPO0FBQUEsUUFDckIsU0FBUztBQUFBLFNBQ1I7QUFBQTtBQUdMLFdBQU87QUFBQTs7O0FsQnZCVCxtQkFBaUIsS0FBSztBQUFFO0FBQTJCLFFBQUksT0FBTyxXQUFXLGNBQWMsT0FBTyxPQUFPLGFBQWEsVUFBVTtBQUFFLGdCQUFVLGtCQUFpQixNQUFLO0FBQUUsZUFBTyxPQUFPO0FBQUE7QUFBQSxXQUFlO0FBQUUsZ0JBQVUsa0JBQWlCLE1BQUs7QUFBRSxlQUFPLFFBQU8sT0FBTyxXQUFXLGNBQWMsS0FBSSxnQkFBZ0IsVUFBVSxTQUFRLE9BQU8sWUFBWSxXQUFXLE9BQU87QUFBQTtBQUFBO0FBQVUsV0FBTyxRQUFRO0FBQUE7QUFtQm5YLDJCQUF5QixVQUFVLGFBQWE7QUFBRSxRQUFJLENBQUUscUJBQW9CLGNBQWM7QUFBRSxZQUFNLElBQUksVUFBVTtBQUFBO0FBQUE7QUFFaEgscUJBQW1CLFVBQVUsWUFBWTtBQUFFLFFBQUksT0FBTyxlQUFlLGNBQWMsZUFBZSxNQUFNO0FBQUUsWUFBTSxJQUFJLFVBQVU7QUFBQTtBQUF5RCxhQUFTLFlBQVksT0FBTyxPQUFPLGNBQWMsV0FBVyxXQUFXLEVBQUUsYUFBYSxFQUFFLE9BQU8sVUFBVSxVQUFVLE1BQU0sY0FBYztBQUFXLFFBQUk7QUFBWSxzQkFBZ0IsVUFBVTtBQUFBO0FBRW5YLHdCQUFzQixTQUFTO0FBQUUsUUFBSSw0QkFBNEI7QUFBNkIsV0FBTyxnQ0FBZ0M7QUFBRSxVQUFJLFFBQVEsZ0JBQWdCLFVBQVU7QUFBUSxVQUFJLDJCQUEyQjtBQUFFLFlBQUksWUFBWSxnQkFBZ0IsTUFBTTtBQUFhLGlCQUFTLFFBQVEsVUFBVSxPQUFPLFdBQVc7QUFBQSxhQUFtQjtBQUFFLGlCQUFTLE1BQU0sTUFBTSxNQUFNO0FBQUE7QUFBYyxhQUFPLDJCQUEyQixNQUFNO0FBQUE7QUFBQTtBQUU1WixzQ0FBb0MsT0FBTSxNQUFNO0FBQUUsUUFBSSxRQUFTLFNBQVEsVUFBVSxZQUFZLE9BQU8sU0FBUyxhQUFhO0FBQUUsYUFBTztBQUFBO0FBQVEsV0FBTyx1QkFBdUI7QUFBQTtBQUV6SyxrQ0FBZ0MsT0FBTTtBQUFFLFFBQUksVUFBUyxRQUFRO0FBQUUsWUFBTSxJQUFJLGVBQWU7QUFBQTtBQUFnRSxXQUFPO0FBQUE7QUFFL0osNEJBQTBCLE9BQU87QUFBRSxRQUFJLFNBQVMsT0FBTyxRQUFRLGFBQWEsSUFBSSxRQUFRO0FBQVcsdUJBQW1CLDJCQUEwQixRQUFPO0FBQUUsVUFBSSxXQUFVLFFBQVEsQ0FBQyxrQkFBa0I7QUFBUSxlQUFPO0FBQU8sVUFBSSxPQUFPLFdBQVUsWUFBWTtBQUFFLGNBQU0sSUFBSSxVQUFVO0FBQUE7QUFBeUQsVUFBSSxPQUFPLFdBQVcsYUFBYTtBQUFFLFlBQUksT0FBTyxJQUFJO0FBQVEsaUJBQU8sT0FBTyxJQUFJO0FBQVEsZUFBTyxJQUFJLFFBQU87QUFBQTtBQUFZLHlCQUFtQjtBQUFFLGVBQU8sV0FBVyxRQUFPLFdBQVcsZ0JBQWdCLE1BQU07QUFBQTtBQUFnQixjQUFRLFlBQVksT0FBTyxPQUFPLE9BQU0sV0FBVyxFQUFFLGFBQWEsRUFBRSxPQUFPLFNBQVMsWUFBWSxPQUFPLFVBQVUsTUFBTSxjQUFjO0FBQVcsYUFBTyxnQkFBZ0IsU0FBUztBQUFBO0FBQVcsV0FBTyxpQkFBaUI7QUFBQTtBQUU5dUIsc0JBQW9CLFFBQVEsTUFBTSxPQUFPO0FBQUUsUUFBSSw2QkFBNkI7QUFBRSxtQkFBYSxRQUFRO0FBQUEsV0FBa0I7QUFBRSxtQkFBYSxxQkFBb0IsU0FBUSxPQUFNLFFBQU87QUFBRSxZQUFJLElBQUksQ0FBQztBQUFPLFVBQUUsS0FBSyxNQUFNLEdBQUc7QUFBTyxZQUFJLGNBQWMsU0FBUyxLQUFLLE1BQU0sU0FBUTtBQUFJLFlBQUksV0FBVyxJQUFJO0FBQWUsWUFBSTtBQUFPLDBCQUFnQixVQUFVLE9BQU07QUFBWSxlQUFPO0FBQUE7QUFBQTtBQUFlLFdBQU8sV0FBVyxNQUFNLE1BQU07QUFBQTtBQUVyWix1Q0FBcUM7QUFBRSxRQUFJLE9BQU8sWUFBWSxlQUFlLENBQUMsUUFBUTtBQUFXLGFBQU87QUFBTyxRQUFJLFFBQVEsVUFBVTtBQUFNLGFBQU87QUFBTyxRQUFJLE9BQU8sVUFBVTtBQUFZLGFBQU87QUFBTSxRQUFJO0FBQUUsY0FBUSxVQUFVLFFBQVEsS0FBSyxRQUFRLFVBQVUsU0FBUyxJQUFJLFdBQVk7QUFBQTtBQUFNLGFBQU87QUFBQSxhQUFlLEdBQVA7QUFBWSxhQUFPO0FBQUE7QUFBQTtBQUUvVCw2QkFBMkIsSUFBSTtBQUFFLFdBQU8sU0FBUyxTQUFTLEtBQUssSUFBSSxRQUFRLHFCQUFxQjtBQUFBO0FBRWhHLDJCQUF5QixHQUFHLEdBQUc7QUFBRSxzQkFBa0IsT0FBTyxrQkFBa0IsMEJBQXlCLElBQUcsSUFBRztBQUFFLFNBQUUsWUFBWTtBQUFHLGFBQU87QUFBQTtBQUFNLFdBQU8sZ0JBQWdCLEdBQUc7QUFBQTtBQUVySywyQkFBeUIsR0FBRztBQUFFLHNCQUFrQixPQUFPLGlCQUFpQixPQUFPLGlCQUFpQiwwQkFBeUIsSUFBRztBQUFFLGFBQU8sR0FBRSxhQUFhLE9BQU8sZUFBZTtBQUFBO0FBQU8sV0FBTyxnQkFBZ0I7QUFBQTtBQXFDeE0sTUFBSSxVQUF1Qix5QkFBVSxjQUFjO0FBQ2pELGNBQVUsVUFBUztBQUVuQixRQUFJLFNBQVMsYUFBYTtBQUUxQix3QkFBbUI7QUFDakIsVUFBSTtBQUVKLHNCQUFnQixNQUFNO0FBRXRCLGFBQU8sUUFBUSxPQUFPLEtBQUs7QUFDM0I7QUFDQSxVQUFJLFdBQVcsWUFBWTtBQUMzQixVQUFJLFNBQVMsWUFBWSxLQUFLLFVBQVU7QUFDeEMsVUFBSSxPQUFPLGtCQUFrQixNQUFNLGdCQUFnQjtBQUNuRCxzQkFBZ0IsTUFBTTtBQUN0QixhQUFPO0FBQUE7QUFHVCxXQUFPO0FBQUEsSUFDTyxpQ0FBaUI7QUFFakMsaUJBQWUsT0FBTyxrQkFBa0I7QUFFeEMsTUFBSSxXQUF3Qix5QkFBVSxlQUFlO0FBQ25ELGNBQVUsV0FBVTtBQUVwQixRQUFJLFVBQVUsYUFBYTtBQUUzQix5QkFBb0I7QUFDbEIsVUFBSTtBQUVKLHNCQUFnQixNQUFNO0FBRXRCLGFBQU8sU0FBUyxRQUFRLEtBQUs7QUFDN0IsVUFBSSxXQUFXLFlBQVk7QUFDM0IsVUFBSSxTQUFTLFlBQVksS0FBSyxVQUFVO0FBQ3hDLFVBQUksUUFBUSxrQkFBa0IsTUFBTSxpQkFBaUI7QUFDckQsc0JBQWdCLE1BQU07QUFDdEIsYUFBTztBQUFBO0FBR1QsV0FBTztBQUFBLElBQ08saUNBQWlCO0FBRWpDLGlCQUFlLE9BQU8sbUJBQW1CO0FBRXpDLE1BQUksY0FBMkIseUJBQVUsZUFBZTtBQUN0RCxjQUFVLGNBQWE7QUFFdkIsUUFBSSxVQUFVLGFBQWE7QUFFM0IsNEJBQXVCO0FBQ3JCLFVBQUk7QUFFSixzQkFBZ0IsTUFBTTtBQUV0QixhQUFPLFNBQVMsUUFBUSxLQUFLO0FBQzdCLFVBQUksV0FBVyxZQUFZO0FBQzNCLFVBQUksU0FBUyxZQUFZLEtBQUssVUFBVTtBQUN4QyxVQUFJLE9BQU8sa0JBQWtCLE1BQU0sZ0JBQWdCO0FBQ25ELFVBQUksTUFBTSxLQUFLO0FBQ2YsVUFBSSxVQUFVLEtBQUs7QUFFbkIsVUFBSSxVQUFVLElBQUk7QUFDbEIsVUFBSSxPQUFPLFdBQVcsU0FBUztBQUMvQixzQkFBZ0IsTUFBTTtBQUN0QixhQUFPO0FBQUE7QUFHVCxXQUFPO0FBQUEsSUFDTyxpQ0FBaUI7QUFFakMsaUJBQWUsT0FBTyx1QkFBdUI7QUFFN0MsTUFBSSxlQUE0Qix5QkFBVSxlQUFlO0FBQ3ZELGNBQVUsZUFBYztBQUV4QixRQUFJLFVBQVUsYUFBYTtBQUUzQiw2QkFBd0I7QUFDdEIsVUFBSTtBQUVKLHNCQUFnQixNQUFNO0FBRXRCLGFBQU8sU0FBUyxRQUFRLEtBQUs7QUFDN0IsVUFBSSxXQUFXLFlBQVk7QUFDM0IsVUFBSSxTQUFTLFlBQVksS0FBSyxVQUFVO0FBQ3hDLFVBQUksUUFBUSxrQkFBa0IsTUFBTSxpQkFBaUI7QUFDckQsVUFBSSxNQUFNLE1BQU07QUFDaEIsVUFBSSxVQUFVLE1BQU07QUFDcEIsVUFBSSxRQUFRLEtBQUssYUFBYSxpQkFBaUI7QUFDL0MsVUFBSTtBQUFPLFlBQUksVUFBVSxJQUFJO0FBQzdCLFVBQUksT0FBTyxRQUFRLFdBQVcsU0FBUyxPQUFPLFdBQVcsU0FBUyxNQUFNO0FBQ3hFLHNCQUFnQixNQUFNO0FBQ3RCLGFBQU87QUFBQTtBQUdULFdBQU87QUFBQSxJQUNPLGlDQUFpQjtBQUVqQyxpQkFBZSxPQUFPLHdCQUF3QjtBQUU5QyxNQUFJLGVBQTRCLHlCQUFVLGVBQWU7QUFDdkQsY0FBVSxlQUFjO0FBRXhCLFFBQUksVUFBVSxhQUFhO0FBRTNCLDZCQUF3QjtBQUN0QixVQUFJO0FBRUosc0JBQWdCLE1BQU07QUFFdEIsYUFBTyxTQUFTLFFBQVEsS0FBSztBQUM3QixVQUFJLFdBQVcsWUFBWTtBQUUzQixVQUFJLFNBQVMsWUFBWSxLQUFLLFVBQVU7QUFDeEMsVUFBSSxRQUFRLGtCQUFrQixNQUFNLDZCQUE2QjtBQUNqRSxVQUFJLE1BQU0sTUFBTTtBQUNoQixVQUFJLFVBQVUsTUFBTTtBQUNwQixVQUFJLFdBQVcsWUFBWSxLQUFLLGFBQWE7QUFFN0MsVUFBSSxLQUFLLGFBQWEsU0FBUztBQUM3QixtQkFBVyxXQUFXO0FBQUE7QUFHeEIsVUFBSSxNQUFNLElBQUksT0FBTztBQUFBLFFBQ25CLFNBQVM7QUFBQSxTQUNSLElBQUksT0FBTztBQUFBLFFBQ1osU0FBUztBQUFBLFNBQ1IsTUFBTSxJQUFJLE9BQU87QUFBQSxRQUNsQixTQUFTLFlBQVksS0FBSyxhQUFhO0FBQUEsU0FDdEM7QUFDSCxzQkFBZ0IsTUFBTTtBQUN0QixhQUFPO0FBQUE7QUFHVCxXQUFPO0FBQUEsSUFDTyxpQ0FBaUI7QUFFakMsaUJBQWUsT0FBTyx3QkFBd0I7QUFFOUMsTUFBSSxVQUF1Qix5QkFBVSxlQUFlO0FBQ2xELGNBQVUsVUFBUztBQUVuQixRQUFJLFVBQVUsYUFBYTtBQUUzQix3QkFBbUI7QUFDakIsVUFBSTtBQUVKLHNCQUFnQixNQUFNO0FBRXRCLGFBQU8sU0FBUyxRQUFRLEtBQUs7QUFDN0IsVUFBSSxXQUFXLFlBQVk7QUFDM0IsVUFBSSxTQUFTLFlBQVksS0FBSyxVQUFVO0FBQ3hDLFVBQUksU0FBUyxrQkFBa0IsTUFBTSxrQkFBa0I7QUFJdkQsYUFBTztBQUFBO0FBR1QsV0FBTztBQUFBLElBQ08saUNBQWlCO0FBRWpDLGlCQUFlLE9BQU8sa0JBQWtCOyIsCiAgIm5hbWVzIjogW10KfQo=
