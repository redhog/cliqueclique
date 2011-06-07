dojo.provide("cliqueclique.document");

dojo.require("dijit.layout.ContentPane");

dojo.require('dijit.Menu');
dojo.require('dijit.MenuItem');

dojo.declare("cliqueclique.document.Document", [], {
  constructor: function (json_data) {
    this.json_data = json_data;
  },
  getContent: function () {
    try {
      return this.json_data.document.content.parts[0];
    } catch(err) {
      return undefined;
    }
  },
  getParts: function () {
    var content = this.getContent();
    var parts = {};
    try {
      dojo.forEach(content.parts, function (part) {
        parts[part.header['part_type']] = part;
      });
    } catch(err) {
      return undefined;
    }
    return parts;
  },
  getSubject: function () {
    var parts = this.getParts();
    try {
      return parts.content.header.subject;
    } catch(err) {
      try {
	return this.json_data.document.content.parts[0].header.subject;
      } catch(err) {
        try {
          return this.json_data.document.document_id.substring(0, 5);
        } catch(err) {
	  return undefined;
        }
      }
    }
  },
  getParentDocumentId: function () {
    try {
      return this.json_data.document.content.parts[0].header.parent_document_id;
    } catch(err) {
      return undefined;
    }
  },
  getChildDocumentId: function () {
    try {
      return this.json_data.document.content.parts[0].header.child_document_id;
    } catch(err) {
      return undefined;
    }
  },
  getBody: function () {
    var parts = this.getParts();
    try {
      return parts.content.body;
    } catch(err) {
      try {
	return this.json_data.document.content.parts[0].body;
      } catch(err) {
        try {
          return this.json_data.document.content.body;
        } catch(err) {
	  return undefined;
        }
      }
    }
  },
  getDocumentId: function () {
    return this.json_data.document.document_id;
  },
  getDocumentLink: function (widget) {
    var document = this;
    return function () {
      var link = widget.getDataDefault("documentLink", "cliqueclique.document.DocumentLink");
      if (link) return link.load(document);
      // Do something intelligent here
    };
  },
});

cliqueclique.document.Document.post = function (json_data__document, callback) {
  if (callback == undefined)
    callback = function () {};
  dojo.xhrGet({
    url: "/post",
    handleAs: "json",
    content: { document: dojo.toJson(json_data__document) },
    load: function(data) {
      if (data.error != undefined) {
        callback(null, data.error);
      } else {
        cliqueclique.document.Document.updated();
        callback(cliqueclique.document.Document(data));
      }
    },
    error: function(error) {
      callback(null, error);
    }
  });
}

cliqueclique.document.Document.find = function (onComplete, query, context) {
  var url = "/find/json";
  if (context) {
    url = "/find/json/" + context;
  }
  dojo.xhrGet({
    url: url,
    handleAs: "json",
    content: { query: dojo.toJson(query) },
    load: function (documents) {
      if (documents.error !== undefined) {
	console.error(documents.error.type + ": " + documents.error.description + "\n" + documents.error.traceback);
	return;
      }
      var res = [];
      for (document_id in documents) {
	res.push(new cliqueclique.document.Document(documents[document_id]));
      }
      onComplete(res);
    }
  });
}

cliqueclique.document.Document.updated = function () {};


dojo.declare("cliqueclique.document._AbstractDocumentView", [], {
  _getDocumentAttr: function () { return this.item; },
  _setDocumentAttr: function (document) { this.item = document; }
});
