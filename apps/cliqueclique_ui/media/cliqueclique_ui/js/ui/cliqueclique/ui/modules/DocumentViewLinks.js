dojo.provide("cliqueclique.ui.modules.DocumentViewLinks");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("cliqueclique.document.DocumentLink");
dojo.require("cliqueclique.document.DocumentMenu");

dojo.declare("cliqueclique.ui.modules.DocumentViewLinks", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "" +
    "<div class='documentViewLinks'>" +
    "  <h1 dojoAttachPoint='title'></h1>" +
    "  <div>" +
    "    Parents:" +
    "    <span dojoAttachPoint='parentDocuments'></span>" +
    "  </div>" +
    "  <div>" +
    "    Children:" +
    "    <span dojoAttachPoint='childDocuments'></span>" +
    "  </div>" +
    "  <div>" +
    "    Direct parent links:" +
    "    <span dojoAttachPoint='directParentDocuments'></span>" +
    "  </div>" +
    "  <div>" +
    "    Direct child links:" +
    "    <span dojoAttachPoint='directChildDocuments'></span>" +
    "  </div>" +
    "</div>",
  postCreate: function () {
    var res = this.inherited(arguments);
    var menu = new cliqueclique.document.DocumentMenu({});
    menu.startup();
    menu.bindDomNode(this.title);
    return res;
  },
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    function populateLinks(query, field) {
      cliqueclique.document.Document.find(function (children) {
	dojo.forEach(children, function (child) {
	  var link = new cliqueclique.document.DocumentLink({document: child});
	  dojo.place(link.domNode, documentView[field]);
	});
      }, query, documentView.item.getDocumentId());
    }

    dojo.html.set(this.title, this.item.getSubject());

    populateLinks("->", "childDocuments");
    populateLinks("<-", "parentDocuments");
    populateLinks(">", "directChildDocuments");
    populateLinks("<", "directParentDocuments");
  }
});

cliqueclique.ui.modules.DocumentViewLinks.register = function (widget) {
  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewLinks({document: document});
			dojo.place(subView.domNode, documentView.header);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");
};
