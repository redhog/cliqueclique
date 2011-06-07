dojo.provide("cliqueclique.document.selector");

dojo.require("cliqueclique.popuptree");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("cliqueclique.document.tree");
dojo.require("dijit.Tree");
dojo.require("dijit.form.DropDownButton");

dojo.declare("cliqueclique.document.selector._SeclectedDocument", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "<span><span dojoType='cliqueclique.document.DocumentLink' dojoAttachPoint='link'></span><button dojoAttachEvent='onclick:onClick' style='display: inline-block;'>X</button> </span>",

  _getDocumentAttr: function () { return this.link.attr("document"); },
  _setDocumentAttr: function (document) { this.link.attr("document", document); },
  onClick: function (e) {
    this.destroyRecursive();
  }
}),

dojo.declare("cliqueclique.document.selector.DocumentSelector", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<span class='dijitDropDownButton'><span class='dijitButtonNode dijitInline'>" +
		  "  <span dojoType='cliqueclique.document.tree.DocumentTreeModel' jsId='treeModel'></span>" +
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
    var link = cliqueclique.document.selector._SeclectedDocument({document: document});
    dojo.place(link.domNode, this.selection, 'last');
  },
  removeLink: function (document) {
    dojo.each(this.selection.children, function (childNode) {
      var child = dijit.byNode(childNode);
      if (child.attr("document") == document)
        child.destroyRecursive();
    });
  }
});
