dojo.provide("cliqueclique.document.DocumentStatView");

dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.document.DocumentStatView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
 templateString: "<iframe dojoAttachPoint='iframe' style='width: 100%; height: 100%;'></iframe>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);
    dojo.attr(this.iframe, "src", "/" + this.item.getDocumentId() +  "/stat");
    this.attr("title", "Stat: " + this.item.getSubject());
  }
});

cliqueclique.document.DocumentStatView.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Stat',
		       load:function (document) {
			 var docStat = new cliqueclique.document.DocumentStatView({document: document});
			 widget.getDataDefault("panels").addChild(docStat);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};