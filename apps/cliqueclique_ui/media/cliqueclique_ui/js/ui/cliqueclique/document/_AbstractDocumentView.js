dojo.provide("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.document._AbstractDocumentView", [], {
  _getDocumentAttr: function () { return this.item; },
  _setDocumentAttr: function (document) { this.item = document; }
});
