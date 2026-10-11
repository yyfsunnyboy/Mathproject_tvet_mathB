/*
 * ParentNode.replaceChildren for engines without it (Safari < 14, e.g. iOS 12).
 * Must stay ES5 so old WebKit can parse it; never replaces a native implementation.
 */
(function () {
  "use strict";

  function hierarchyError(message) {
    try {
      return new DOMException(message, "HierarchyRequestError");
    } catch (ignore) {
      var error = new Error(message);
      error.name = "HierarchyRequestError";
      return error;
    }
  }

  var INSERTABLE_NODE_TYPES = { 1: true, 3: true, 4: true, 7: true, 8: true, 11: true };

  function replaceChildren() {
    var parent = this;
    var doc = parent.ownerDocument || document;
    var node;
    if (arguments.length === 1 && arguments[0] instanceof Node) {
      node = arguments[0];
    } else {
      // Arguments are collected first (moving them out of their current parents, as native does),
      // so nodes that are already children of `parent` survive the removal below.
      node = doc.createDocumentFragment();
      for (var i = 0; i < arguments.length; i += 1) {
        var item = arguments[i];
        node.appendChild(item instanceof Node ? item : doc.createTextNode(String(item)));
      }
    }
    // Validate before removing anything so a rejected call leaves the DOM untouched.
    if (!INSERTABLE_NODE_TYPES[node.nodeType] || node.contains(parent)) {
      throw hierarchyError("The new child element contains the parent or cannot be inserted.");
    }
    while (parent.lastChild) {
      parent.removeChild(parent.lastChild);
    }
    parent.appendChild(node);
  }

  [typeof Element !== "undefined" && Element, typeof DocumentFragment !== "undefined" && DocumentFragment].forEach(function (ctor) {
    if (!ctor || !ctor.prototype || typeof ctor.prototype.replaceChildren === "function") return;
    Object.defineProperty(ctor.prototype, "replaceChildren", {
      configurable: true,
      enumerable: true,
      writable: true,
      value: replaceChildren
    });
  });
})();
