dojo.provide("cliqueclique.ui.modules.view.body.text");

dojo.require("cliqueclique.document._AbstractDocumentViewBodyType");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.ui.modules.view.body.text", [cliqueclique.ui.modules._AbstractDocumentViewBodyType], {
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    dojo.html.set(this.body, "<pre>" + this.getDocumentBody(document) + "</pre>");
  },
});

cliqueclique.ui.modules.view.body.text.register = function (widget) {
  widget.registerData("text",
                      {load:function (documentView, document) {
		        var subView = new cliqueclique.ui.modules.view.body.text({document: document});
			dojo.place(subView.domNode, documentView.body);
		      }},
		      true,
		      "cliqueclique.ui.modules.view.body");
};
