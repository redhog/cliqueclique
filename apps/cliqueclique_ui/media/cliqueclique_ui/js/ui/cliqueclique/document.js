dojo.provide("cliqueclique.document");

dojo.require("dijit.layout.ContentPane");

dojo.require('dijit.Menu');
dojo.require('dijit.MenuItem');

dojo.declare("cliqueclique.document.Document", [], {
  constructor: function (json_data) {
    this.json_data = json_data;
  },
  getSubject: function () {
    if (   typeof(this.json_data.content) != "undefined"
	&& typeof(this.json_data.content.parts) != "undefined"
	&& this.json_data.content.parts.length > 0
	&& typeof(this.json_data.content.parts[0].header) != "undefined")
      return this.json_data.content.parts[0].header.subject;
    else
      return this.json_data.document_id.substring(0, 5);
  },
  getDocumentId: function () {
    return this.json_data.document_id;
  },
  getDocumentLink: function (widget) {
    var document = this;
    return function () {
      var link = widget.getDataDefault("documentLink", "cliqueclique.document.DocumentLink");
      if (link) return link.load(document);
      // Do something intelligent here
    };
  }
});

dojo.declare("cliqueclique.document._AbstractDocumentView", [], {
  _getDocumentAttr: function () { return this.item; },
  _setDocumentAttr: function (document) { this.item = document; }
});

dojo.declare("cliqueclique.document.DocumentLink", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  templateString: "<span><a href='javascript: void(0);' dojoAttachPoint='text' dojoAttachEvent='onclick:onClick'></a> </span>",

  postCreate: function () {
    var res = this.inherited(arguments);
    var menu = new cliqueclique.document.DocumentMenu({});
    menu.startup();
    menu.bindDomNode(this.text);

    dojo.connect(this.text, 'onClick', this, this.onClick);
    return res;
  },
  onClick: function (e) {
    this.item.getDocumentLink(this)();
  },
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    dojo.html.set(this.text, this.item.getSubject());
  }
});


dojo.declare("cliqueclique.document.DocumentView", [dijit.layout.ContentPane, cliqueclique.document._AbstractDocumentView], {
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    this.attr("content", this.item.getSubject());
  }
});


dojo.declare("cliqueclique.document.DocumentMenu", [dijit.Menu], {
  _openMyself: function (e) {
    var menu = this;

    dojo.forEach(menu.getChildren(), function(child, i){
      menu.removeChild(child);
      child.destroyRecursive();
    });

    var click = function () { console.log(arguments); };

    var tn = dijit.getEnclosingWidget(e.target);
    dojo.forEach(tn.getData("documentLink", "cliqueclique.document.DocumentLink"), function (item, i) {
      var item = new dijit.MenuItem(item);
      menu.addChild(item);
      item.connect(item, 'onClick', function (e) { item.load(tn.item); });
    });

    console.debug(tn.item.getSubject());

    return this.inherited(arguments);
  }
});


dojo.declare("cliqueclique.document.DocumentEditor", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<div>hello world</div>"
});
