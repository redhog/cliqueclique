dojo.provide("cliqueclique.document.DocumentLink");

dojo.require("cliqueclique.document");

dojo.declare("cliqueclique.document.DocumentLink", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  templateString: "<span><a href='javascript: void(0);' dojoAttachPoint='text' dojoAttachEvent='onclick:onClick'>NO SUBJECT SET YET</a> </span>",

  postCreate: function () {
    var res = this.inherited(arguments);
    var menu = new cliqueclique.document.DocumentMenu({});
    menu.startup();
    menu.bindDomNode(this.text);

    dojo.connect(this.text, 'onClick', this, this.onClick);
    return res;
  },
  onClick: function (e) {
    this.item.getDocumentLink(this)();
  },
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    dojo.html.set(this.text, this.item.getSubject());
  }
});
