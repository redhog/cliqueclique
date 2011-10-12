dojo.provide("cliqueclique.ui.modules.view.body");

dojo.require("cliqueclique.document._AbstractDocumentViewBody");
dojo.require("cliqueclique.ui.modules.view.body.text");
dojo.require("cliqueclique.ui.modules.view.body.text:html");

dojo.declare("cliqueclique.ui.modules.view.body.Body", [cliqueclique.document._AbstractDocumentViewBody], {
  widgetsInTemplate: true,
  templateString: "<div class='documentViewBody' dojoAttachPoint='body'></div>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    dojo.query('> *', documentView.body).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    var bodyType = this.getDocumentBodyType(document);
    
    subView = this.getDataDefault(bodyType.type + "/" + bodyType.subtype, "cliqueclique.ui.modules.view.body");
    if (!subView) subView = this.getDataDefault(bodyType.type, "cliqueclique.ui.modules.view.body");
    if (!subView) subView = this.getDataDefault('default', "cliqueclique.ui.modules.view.body");

    subView.load(documentView, document);
  },
});

cliqueclique.ui.modules.view.body.register = function (widget) {
  dojo.forEach(
    [cliqueclique.ui.modules.view.body.text,
     cliqueclique.ui.modules.view.body['text:html']],
    function (item, i) {
      item.register(widget)
    }
  );

  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.view.body.Body();
			dojo.place(subView.domNode, documentView.body);
			subView.attr("document", document);
		      }},
		      false,
		      "cliqueclique.ui.modules.view");
};
