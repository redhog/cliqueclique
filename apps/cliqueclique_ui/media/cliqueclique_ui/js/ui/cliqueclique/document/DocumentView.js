dojo.provide("cliqueclique.document.DocumentView");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("cliqueclique.document.DocumentLink");
dojo.require("cliqueclique.document.DocumentMenu");

dojo.declare("cliqueclique.document.DocumentView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  templateString: "" +
    "<div>" +
    "  <table>" +
    "    <tr>" +
    "      <th colspan='2' dojoAttachPoint='title'></td>" +
    "    </tr>" +
    "    <tr>" +
    "      <th>Parents:</th>" +
    "      <td dojoAttachPoint='parentDocuments'></td>" +
    "    </tr>" +
    "    <tr>" +
    "      <th>Children:</th>" +
    "      <td dojoAttachPoint='childDocuments'></td>" +
    "    </tr>" +
    "  </table>" +
    "  <p dojoAttachPoint='body'></p>" +
    "</div>",

  postCreate: function () {
    var res = this.inherited(arguments);
    var menu = new cliqueclique.document.DocumentMenu({});
    menu.startup();
    menu.bindDomNode(this.title);

    // Update stuff if we need to (mainly links)
    dojo.connect(cliqueclique.document.Document, "updated", this, function () {
      this.attr("document", this.attr("document"));
    });

    return res;
  },
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);
    dojo.html.set(this.title, this.item.getSubject());
    dojo.html.set(this.body, this.item.getBody());

    dojo.query('> *', documentView.childDocuments).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    cliqueclique.document.Document.find(function (children) {
      dojo.forEach(children, function (child) {
        var link = new cliqueclique.document.DocumentLink({document: child});
        dojo.place(link.domNode, documentView.childDocuments);
      });
    }, "->", this.item.getDocumentId());


    dojo.query('> *', documentView.parentDocuments).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    cliqueclique.document.Document.find(function (parents) {
      dojo.forEach(parents, function (parent) {
        var link = new cliqueclique.document.DocumentLink({document: parent});
        dojo.place(link.domNode, documentView.parentDocuments);
      });
    }, "<-", this.item.getDocumentId());

  }
});
