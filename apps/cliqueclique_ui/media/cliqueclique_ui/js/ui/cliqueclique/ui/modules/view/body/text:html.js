dojo.provide("cliqueclique.ui.modules.view.body.text:html");

dojo.require("cliqueclique.document._AbstractDocumentViewBodyType");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.ui.modules.view.body.text:html", [cliqueclique.ui.modules._AbstractDocumentViewBodyType], {
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    dojo.html.set(this.body, this.getDocumentBody(document));
  },
});

cliqueclique.ui.modules.view.body["text:html"].register = function (widget) {
  widget.registerData("text/html",
                      {load:function (documentView, document) {
		        var subView = new cliqueclique.ui.modules.view.body["text:html"]({document: document});
			dojo.place(subView.domNode, documentView.body);
		      }},
		      true,
		      "cliqueclique.ui.modules.view.body");
};
