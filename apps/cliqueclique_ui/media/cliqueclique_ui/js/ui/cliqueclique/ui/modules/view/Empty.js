dojo.provide("cliqueclique.ui.modules.view.Empty");

dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.ui.modules.view.Empty", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<div>No document selected</div>",
});

cliqueclique.ui.modules.view.Empty.register = function (widget) {
  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (document) return;
		        var subView = new cliqueclique.ui.modules.view.Empty();
			dojo.place(subView.domNode, documentView.body);
		      }},
		      false,
		      "cliqueclique.ui.modules.view");
};
