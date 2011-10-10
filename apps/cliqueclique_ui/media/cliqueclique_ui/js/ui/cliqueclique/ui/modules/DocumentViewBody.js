dojo.provide("cliqueclique.ui.modules.DocumentViewBody");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.ui.modules.DocumentViewBody", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "" +
    "<div class='documentBodyView'>" +
    "  <p dojoAttachPoint='body'></p>" +
    "</div>",
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    var body = {body: '', header: {"Content-Type": 'text/plain'}};
    if (this.item) {
      try {
        body = this.item.getParts()[this.displayPart || this.declaredClass] || body;
      } catch (e) {
      }
    }

    contentType = cliqueclique.document.Document.parseContentType(body);
    renderers = ["render:" + contentType.type + "/" + contentType.subtype,
		 "render:" + contentType.type,
		 "render:default"];
    var renderer;
    for (var i = 0; i < renderers.length && renderer === undefined; i++)
      renderer = this[renderers[i]];
    renderer.call(this, contentType, body);
  },
  "render:default": function (contentType, body) {
    dojo.html.set(this.body, "[UNKNOWN FORMAT]");
  },
  "render:text": function (contentType, body) {
    dojo.html.set(this.body, "<pre>" + body.body + "</pre>");
  },
  "render:text/html": function (contentType, body) {
    dojo.html.set(this.body, body.body);
  },
  "render:linked": function (contentType, body) {
    var document = this;

    cliqueclique.document.Document.find(function (templateDocuments) {
      var templateDocument = templateDocuments[0];

      var template = templateDocument.getParts().template;
      templateContentType = cliqueclique.document.Document.parseContentType(template);

      renderers = ["render:linked:" + templateContentType.type + "/" + templateContentType.subtype,
		   "render:linked:" + templateContentType.type,
		   "render:linked:default"];
      var renderer;
      for (var i = 0; i < renderers.length && renderer === undefined; i++)
	renderer = document[renderers[i]];
      renderer.call(document, contentType, body, templateContentType, template);
    }, [], contentSubtype);
  },
  "render:linked:text/html+dojo": function (document, contentType, body, templateContentType, template) {
    var TemplateWidget = dojo.declare("cliqueclique.document.DocumentBodyView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
      widgetsInTemplate: true,
      templateString: template.body
    });
    var templateWidget = new TemplateWidget({document: document, contentType: contentType});
    dojo.html.set(this.body, "");
    dojo.place(this.body, templateWidget);
  },
  "render:linked:default": function (document, contentType, body, templateContentType, template) {
    dojo.html.set(this.body, "[UNKNOWN TEMPLATE FORMAT]");
  },
  displayPart: "content"
});

/*
dojo.declare("cliqueclique.ui.modules.DocumentViewBody", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<div class='documentViewBody' dojoAttachPoint='views'></div>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    dojo.query('> *', documentView.views).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    dojo.forEach(this.getData("documentViewBody", "cliqueclique.ui.modules.DocumentView"), function (item, i) {
      item.load(documentView, document);
    });
  },
});
*/

cliqueclique.ui.modules.DocumentViewBody.register = function (widget) {
  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewBody({document: document});
			dojo.place(subView.domNode, documentView.body);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");
};
