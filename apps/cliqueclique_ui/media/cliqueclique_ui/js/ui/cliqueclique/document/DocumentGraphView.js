dojo.provide("cliqueclique.document.DocumentGraphView");

dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.document.DocumentGraphView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
 templateString: "<iframe dojoAttachPoint='iframe' style='width: 100%; height: 100%;'></iframe>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);
    dojo.attr(this.iframe, "src", "/" + this.item.getDocumentId() +  "/graph");
    this.attr("title", "Graph: " + this.item.getSubject());
  }
});

cliqueclique.document.DocumentGraphView.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Graph',
		       load:function (document) {
			 var docGraph = new cliqueclique.document.DocumentGraphView({document: document});
			 widget.getDataDefault("panels").addChild(docGraph);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};
