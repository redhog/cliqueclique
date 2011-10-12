dojo.provide("cliqueclique.ui.modules.view.body.linked.text:html+dojo");

dojo.require("cliqueclique.document._AbstractDocumentViewBodyType");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.ui.modules.view.body.linked.text:html+dojo", [cliqueclique.ui.modules._AbstractDocumentViewBodyType], {
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    dojo.html.set(this.body, this.getDocumentBody(document));

    var linkedView = this;

    cliqueclique.document.Document.find(function (templateDocuments) {
      var templateDocument = templateDocuments[0];

      var template = templateDocument.getParts().template;
      templateContentType = cliqueclique.document.Document.parseContentType(template);

      renderers = ["render:linked:" + templateContentType.type + "/" + templateContentType.subtype,
		   "render:linked:" + templateContentType.type,
		   "render:linked:default"];
      var renderer;
      for (var i = 0; i < renderers.length && renderer === undefined; i++)
	renderer = linkedView[renderers[i]];
      renderer.call(linkedView, contentType, body, templateContentType, template);
    }, [], this.getDocumentBodyType(document));

  },
});

cliqueclique.ui.modules.view.body.linked["text:html+dojo"].register = function (widget) {
  widget.registerData("text/html+dojo",
                      {load:function (documentView, document) {
		        var subView = new cliqueclique.ui.modules.view.body.linked["text:html+dojo"]({document: document});
			dojo.place(subView.domNode, documentView.body);
		      }},
		      true,
		      "cliqueclique.ui.modules.view.body.linked");
};
