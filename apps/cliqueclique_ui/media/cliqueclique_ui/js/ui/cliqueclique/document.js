dojo.provide("cliqueclique.document");

dojo.require("dijit.layout.ContentPane");


dojo.declare("cliqueclique.document.Document", [], {
  constructor: function (json_data) {
    this.json_data = json_data;
  },
  getSubject: function () {
    if (   typeof(this.json_data.content) != "undefined"
	&& typeof(this.json_data.content.parts) != "undefined"
	&& this.json_data.content.parts.length > 0
	&& typeof(this.json_data.content.parts[0].header) != "undefined")
      return this.json_data.content.parts[0].header.subject;
    else
      return this.json_data.document_id.substring(0, 5);
  },
  getDocumentId: function () {
    return this.json_data.document_id;
  },
  getDocumentLink: function (widget) {
    var document = this;
    return function () {
      var link = widget.getDataDefault("documentLink", "cliqueclique.document.DocumentLink");
      if (link) return link(document);
      // Do something intelligent here
    };
  },
  getDocumentMenu: function (widget) {
    var document = this;
    return function () {
      var menu = widget.getData("documentMenu", "cliqueclique.document.DocumentLink");
      // menu is list of dict {name:someMenuName, link:function(document)}
      // create menu here 
    };
  }
});

/*
dojo.declare("cliqueclique.document.DocumentLink", [dijit.layout.ContentPane], {
  constructor: function (document) {
    this.document = document;
    this.content = "<a href='' onclick=''"
  },



});
*/

dojo.declare("cliqueclique.document.DocumentView", [dijit.layout.ContentPane], {
  getDocument: function () { return this.document; },
  setDocument: function (document) {
    this.doc = document;
    this.attr("content", this.doc.getSubject());
  }
});
