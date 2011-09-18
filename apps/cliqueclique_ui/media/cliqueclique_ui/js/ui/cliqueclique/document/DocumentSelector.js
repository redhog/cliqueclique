dojo.provide("cliqueclique.document.DocumentSelector");

dojo.require("cliqueclique.general.popuptree");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("cliqueclique.document.DocumentTreeModel");
dojo.require("dijit.Tree");
dojo.require("dijit.form.DropDownButton");

dojo.declare("cliqueclique.document.DocumentSelector", [dijit._Widget, dijit._Templated], {
  single: false,
  widgetsInTemplate: true,
  templateString: "<span class='dijitDropDownButton'><span class='dijitButtonNode dijitInline'>" +
		  "  <span dojoType='cliqueclique.document.DocumentTreeModel' jsId='treeModel'></span>" +
		  "  <span dojoAttachPoint='selection'></span>" +
		  "  <div dojoType='dijit.form.DropDownButton' dojoAttachPoint='button'>" +
		  "    <div></div>" +
		  "    <div dojoType='dijit.Tree' model='treeModel' dojoAttachPoint='tree' showRoot='false' style='width: 200px; background: #ffffff;' title='Bookmarks'></div>" +
		  "  </div>" +
		  "</span></span>",
  postCreate: function () {
    dojo.connect(this.tree, "onExecute", this, function (item, node, evt) { this.onSelect(item, node, evt); });
    this.inherited(arguments);
  },
  onSelect: function (item, node, evt) {
    this.addLink(item);
  },
  _getLinksAttr: function () {
    return dojo.map(this.selection.children, function (childNode) {
      return dijit.byNode(childNode).attr("document")
    });
  },
  addLink: function (document) {
    var link;
    if (this.single) {
      this.removeLink();
      link = cliqueclique.document.DocumentLink({document: document});
    } else {
      link = cliqueclique.document.DocumentSelector._SeclectedDocument({document: document});
    }
    dojo.place(link.domNode, this.selection, 'last');
  },
  removeLink: function (document) {
    dojo.forEach(this.selection.children, function (childNode) {
      var child = dijit.byNode(childNode);
      if (document === undefined || child.attr("document") == document)
        child.destroyRecursive();
    });
  }
});

dojo.declare("cliqueclique.document.DocumentSelector._SeclectedDocument", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<span><span dojoType='cliqueclique.document.DocumentLink' dojoAttachPoint='link'></span><button dojoAttachEvent='onclick:onClick' style='display: inline-block;'>X</button> </span>",

  _getDocumentAttr: function () { return this.link.attr("document"); },
  _setDocumentAttr: function (document) { this.link.attr("document", document); },
  onClick: function (e) {
    this.destroyRecursive();
  }
});
