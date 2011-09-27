dojo.provide("cliqueclique.ui.modules.LeftTree");

dojo.require("cliqueclique.general.OptionalTabContainer");
dojo.require("cliqueclique.document.DocumentMenu");
dojo.require("cliqueclique.document.DocumentTreeModel");
dojo.require("dijit.Tree");
dojo.require("dijit.layout.AccordionContainer");

dojo.declare("cliqueclique.ui.modules.LeftTree", [dijit.layout.AccordionContainer], {
  region: 'left',
  splitter: true,
  minSize: 200,
  startup: function () {
    this.inherited(arguments);
    var left_tree = this;

    left_tree.tree = new dijit.Tree({showRoot: false, model: cliqueclique.document.DocumentTreeModel(), style: "width: 200px;", title: 'Bookmarks'});
    left_tree.addChild(left_tree.tree);
    left_tree.tree.connect(left_tree.tree, 'onClick', function (item, node, evt) { item.getDocumentLink(left_tree.tree)(); });

    left_tree.menu = new cliqueclique.document.DocumentMenu({});
    left_tree.menu.startup();
    left_tree.menu.bindDomNode(left_tree.tree.domNode);
  }
});

cliqueclique.ui.modules.LeftTree.register = function (widget) {
  widget.leftPane = new cliqueclique.ui.modules.LeftTree();
  widget.addChild(widget.leftPane);
}
