dojo.provide("cliqueclique.ui.modules.DocumentView");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.ui.modules.DocumentView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<div class='documentView'><div dojoAttachPoint='title'></div><div dojoAttachPoint='header'></div><div dojoAttachPoint='body'></div><div dojoAttachPoint='footer'></div></div>",
  postCreate: function () {
    var res = this.inherited(arguments);
    // Update stuff if we need to (mainly links)
    dojo.connect(cliqueclique.document.Document, "updated", this, "refresh");
    return res;
  },
  refresh: function () {
    var documentView = this;
    if (!view.attr("document")) return;
    cliqueclique.document.Document.find(function (documents) {
      var document = documents[0];
      // Check that we haven't changed document since the refresh was asked for...
      if (document.getDocumentId() == view.attr("document").getDocumentId())
        documentView.attr("document", document);
    }, [], documentView.attr("document").getDocumentId());
  },
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    dojo.forEach(['title', 'header', 'body', 'footer'], function (item, i) {
      dojo.query('> *', documentView[item]).forEach(function(domNode, index, arr){
        dijit.byNode(domNode).destroyRecursive();
      });
    });

    dojo.forEach(this.getData("documentView", "cliqueclique.ui.modules.DocumentView"), function (item, i) {
      item.load(documentView, document);
    });
  },
});


cliqueclique.ui.modules.DocumentView.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Display',
		       load:function (document) {
			 return widget.docView.attr("document", document);
		      }},
		      true,
		      "cliqueclique.document.DocumentLink");

  widget.docView = cliqueclique.ui.modules.DocumentView({region: 'center'});
  widget.inner.addChild(widget.docView);
  widget.docView.attr("document", undefined);
};
