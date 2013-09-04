//     katan.js 0.0.1
//     (c) 2012 Wei.Zhuo.

(function(){

  // Initial Setup
  // -------------

  // Save a reference to the global object (`window` in the browser, `global`
  // on the server).
  var root = this;

  // The top-level namespace. All public Backbone classes and modules will
  // be attached to this. Exported for both CommonJS and the browser.
  var katan;
  if (typeof exports !== 'undefined') {
    katan = exports;
  } else {
    katan = root.katan = {};
  }

  // Current version of the library. Keep in sync with `package.json`.
  katan.VERSION = '0.0.1';

  // Require Underscore, if we're on the server, and it's not already present.
  var _ = root._;
  if (!_ && (typeof require !== 'undefined')) _ = require('underscore');

  // For Backbone's purposes, jQuery, Zepto, or Ender owns the `$` variable.
  var $ = root.jQuery || root.Zepto || root.ender;

  katan.render_mustache = function(template_id, view){
    var template = document.getElementById(template_id).innerHTML;
    return Mustache.render(template, view);
  };

}).call(this);
