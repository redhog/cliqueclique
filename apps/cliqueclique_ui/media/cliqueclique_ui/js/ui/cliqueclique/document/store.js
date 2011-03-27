dojo.provide("cliqueclique.document.store");

dojo.require("cliqueclique.document");

dojo.declare("cliqueclique.document.store.DocumentDataStore", [], {
  /**** dojo.data.api.Read API ****/
  close: function (request) {
  },
  constructor: function () {
  },
  containsValue: function (item, attribute, value) {
    return this.getValue(item, attribute) == value;
  },
  fetch: function (keywordArgs) {
    var args = {
      query: [],
      queryOptions: { ignoreCase: false, deep: false},
      onBegin: function () {},
      onItem: function (item) {},
      onComplete: function () {},
      onError: function (err) { throw err; },
      scope: dojo.global
    };
    for (name in keywordArgs)
      args[name] = keywordArgs[name];
    if (args.query.length == undefined) {
      throw "Unsupported query format";
      /*
      for (name in args.query) {
      args.query = [":", [["=", name, value]
      */
    }
    args.promise = dojo.xhrGet({
      url: "/find/json",
      handleAs: "json",
      content: { query: dojo.toJson(args.query) },
      load: function (documents) {
        if (documents.error) {
          args.onError.call(args.scope, documents.error);
 	  return;
        }
	var res = [];
        args.onBegin.call(args.scope);
	for (document_id in documents) {
	  args.onItem.call(args.scope, new cliqueclique.document.Document(documents[document_id]));
	}
        args.onComplete.call(args.scope);
      },
      error: function (err) {
       args.onError.call(args.scope, err);
      }
    });

    args.cancel = function () { args.promise.cancel(); };

    return args;
  },
  getAttributes: function (item) {
    var res = [];
    for (attr in item) {
      if (attr.substr(0, 3) == "get") {
        var name = attr.substr(3, attr.length-3);
        res.push(name.charAt(0).toLowerCase() + name.slice(1));
      }
    }
    return res;
  },
  getFeatures: function () {
    return {'dojo.data.api.Read': true};
  },
  getLabel: function (item) {
    return item.getLabel();
  },
  getLabelAttributes: function (item) {
    return ["label"];
  },
  getValue: function (item, attribute, defaultValue) {
    var method = "get" + attribute.charAt(0).toUpperCase() + attribute.slice(1);
    if (item[method] == undefined)
      return undefined;
    var res = item[method]();
    if (res != undefined)
      return res;
    return defaultValue;
  },
  getValues: function (item, attribute) {
    var method = "get" + attribute.charAt(0).toUpperCase() + attribute.slice(1);
    if (item[method] == undefined)
      return [];
    var res = item[method]();
    if (res != undefined)
      return [res];
    return [];
  },
  hasAttribute: function (item, attribute) {
    var method = "get" + attribute.charAt(0).toUpperCase() + attribute.slice(1);
    if (item[method] == undefined)
      return false;
    return true;
  },
  isItem: function (something) {
    return true;
  },
  isItemLoaded: function (something) {
    return true;
  },
  loadItem: function (keywordArgs) {
  }
});

