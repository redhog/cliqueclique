dojo.provide("cliqueclique.document");

dojo.require("dijit.layout.ContentPane");

dojo.require('dijit.Menu');
dojo.require('dijit.MenuItem');

dojo.declare("cliqueclique.document.Document", [], {
  constructor: function (json_data) {
    this.json_data = json_data;
  },
  getContent: function () {
    try {
      return this.json_data.document.content.parts[0];
    } catch(err) {
      return undefined;
    }
  },
  getParts: function () {
    var content = this.getContent();
    var parts = {};
    try {
      dojo.forEach(content.parts, function (part) {
        parts[part.header['part_type']] = part;
      });
    } catch(err) {
      return undefined;
    }
    return parts;
  },
  getSubject: function () {
    var parts = this.getParts();
    try {
      return parts.content.header.subject;
    } catch(err) {
      try {
	return this.json_data.document.content.parts[0].header.subject;
      } catch(err) {
        try {
          return this.json_data.document.document_id.substring(0, 5);
        } catch(err) {
	  return undefined;
        }
      }
    }
  },
  getBody: function () {
    var parts = this.getParts();
    try {
      return parts.content.body;
    } catch(err) {
      try {
	return this.json_data.document.content.parts[0].body;
      } catch(err) {
        try {
          return this.json_data.document.content.body;
        } catch(err) {
	  return undefined;
        }
      }
    }
  },
  getDocumentId: function () {
    return this.json_data.document.document_id;
  },
  getDocumentLink: function (widget) {
    var document = this;
    return function () {
      var link = widget.getDataDefault("documentLink", "cliqueclique.document.DocumentLink");
      if (link) return link.load(document);
      // Do something intelligent here
    };
  },
});

cliqueclique.document.Document.post = function (json_data__document, callback) {
  if (callback == undefined)
    callback = function () {};
  dojo.xhrGet({
    url: "/post",
    handleAs: "json",
    content: { document: dojo.toJson(json_data__document) },
    load: function(data) {
      if (data.error != undefined)
        callback(null, data.error);
      else
        callback(cliqueclique.document.Document(data));
    },
    error: function(error) {
      callback(null, error);
    }
  });
}

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

dojo.declare("cliqueclique.document.DocumentView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
 templateString: "<div><h1 dojoAttachPoint='title'></h1><p dojoAttachPoint='body'></p></div>",

  postCreate: function () {
    var res = this.inherited(arguments);
    var menu = new cliqueclique.document.DocumentMenu({});
    menu.startup();
    menu.bindDomNode(this.title);

    return res;
  },
  _setDocumentAttr: function (document) {
    this.inherited(arguments);
    dojo.html.set(this.title, this.item.getSubject());
    dojo.html.set(this.body, this.item.getBody());
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
