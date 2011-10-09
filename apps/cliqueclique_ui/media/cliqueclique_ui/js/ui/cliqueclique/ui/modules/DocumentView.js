dojo.provide("cliqueclique.ui.modules.DocumentView");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("cliqueclique.document.DocumentLink");
dojo.require("cliqueclique.document.DocumentMenu");
dojo.require("dijit.form.CheckBox");

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

dojo.declare("cliqueclique.ui.modules.DocumentViewAttributes", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "" +
    "<div class='actionBox'>" +
    "  <input dojoType='dijit.form.CheckBox' dojoAttachPoint='bookmarkedInput' dojoAttachEvent='onClick:onBookmarkedInputClick'></input><label dojoAttachPoint='bookmarkedLabel'>bookmarked</label>" +
    "  <input dojoType='dijit.form.CheckBox' dojoAttachPoint='readInput' dojoAttachEvent='onClick:onReadInputClick'></input><label dojoAttachPoint='readLabel'>read</label>" +
    "  <input dojoType='dijit.form.CheckBox' dojoAttachPoint='subscribedInput' dojoAttachEvent='onClick:onSubscribedInputClick'></input><label dojoAttachPoint='subscribedInput'>subscribed</label><br>" +
    "  Download: <a dojoAttachPoint='downloadAsMime' target='_new'>as mime</a> or <a dojoAttachPoint='downloadAsJson' target='_new'>as json</a>" +
    "</div>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    if (!this.item.json_data.read) {
      this.item.setAttribute("read", true);
    }

    this.downloadAsMime.href = "/find/mime/" + this.item.getDocumentId();
    this.downloadAsJson.href = "/find/json/" + this.item.getDocumentId();

    this.bookmarkedInput.attr("value", this.item.json_data.bookmarked);
    this.readInput.attr("value", this.item.json_data.read);
    this.subscribedInput.attr("value", this.item.json_data.local_is_subscribed);
  },
  onBookmarkedInputClick: function () {
   this.item.setAttribute("bookmarked");
  },
  onReadInputClick: function () {
   this.item.setAttribute("read");
  },
  onSubscribedInputClick: function () {
   this.item.setAttribute("local_is_subscribed");
  }
});

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

dojo.declare("cliqueclique.ui.modules.DocumentViewEmpty", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<div>No document selected</div>",
});

dojo.declare("cliqueclique.ui.modules.DocumentView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<div class='documentView' dojoAttachPoint='views'></div>",
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

    dojo.query('> *', documentView.views).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    dojo.forEach(this.getData("documentView", "cliqueclique.ui.modules.DocumentView"), function (item, i) {
      item.load(documentView, document);
    });
  },
});


cliqueclique.ui.modules.DocumentView.register = function (widget) {
  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewEmpty();
			dojo.place(subView.domNode, documentView.views);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");

  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewAttributes({document: document});
			dojo.place(subView.domNode, documentView.views);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");

  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewLinks({document: document});
			dojo.place(subView.domNode, documentView.views);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");

  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewBody({document: document});
			dojo.place(subView.domNode, documentView.views);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");

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