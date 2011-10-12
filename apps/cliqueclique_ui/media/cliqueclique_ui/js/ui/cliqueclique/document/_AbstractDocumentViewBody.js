dojo.provide("cliqueclique.document._AbstractDocumentViewBody");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.document._AbstractDocumentViewBody", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  getDocumentBody: function (document) {
    return document.getParts()[this.displayPart].body;
  },
  getDocumentBodyType: function (document) {
    return cliqueclique.document.Document.parseContentType(document.getParts()[this.displayPart]);
  },
  _setDisplayPartAttr: function (part) {
    this.displayPart = part;
  },
  displayPart: "content"
});
