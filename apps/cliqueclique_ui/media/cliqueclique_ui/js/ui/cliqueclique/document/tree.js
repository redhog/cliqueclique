dojo.provide("cliqueclique.document.tree");

dojo.require("dijit.Tree");
dojo.require("cliqueclique.document.Document");

cliqueclique.document.tree.oldTree = dijit.Tree;
dojo.declare("dijit.Tree", [cliqueclique.document.tree.oldTree], {
  refresh: function(){
    var model = this.model;
    var node = this.rootNode;

    loaded_items = [node.item];
    unloaded_items = [node.item];

    while((node = this._getNextNode(node)) != null)
      if (node.state == "LOADED")
        loaded_items.push(node.item);
      else
        unloaded_items.push(node.item);
    dojo.forEach(loaded_items, function (item) {
      model.getChildren(item, function (children) {
	model.onChange(item);
	model.onChildrenChange(item, children);
      });
    });
    dojo.forEach(unloaded_items, function (item) {
      model.onChange(item);
    });

  },
  postCreate: function(){
    this.inherited(arguments);
    this.connect(this.model, "onRefreshAll", "refresh");
  }
});

dojo.declare("cliqueclique.document.tree.RootDocumentClass", [cliqueclique.document.Document], {
  constructor: function () { },
  getSubject: function () { return 'The roo'; },
  getObjectId: function () { return null; },
  getDocumentId: function () { return null; },
});
cliqueclique.document.tree.RootDocument = new cliqueclique.document.tree.RootDocumentClass();

dojo.declare("cliqueclique.document.tree.DocumentTreeModel", [], {
  root_query: 'bookmarked',
  child_query: "->",

  constructor: function () {
    var tree = this;
    dojo.connect(cliqueclique.document.Document, "updated", tree, function () {
      tree.getChildren(cliqueclique.document.tree.RootDocument, function (documents) {
        tree.onRefreshAll()
      });
    });
  },
  onRefreshAll: function () {},

  fetchItemByIdentity: function (keywordArgs) {},
  getChildren: function (parentItem, onComplete) {
    cliqueclique.document.Document.find(onComplete, parentItem.getDocumentId() ? this.child_query : this.root_query, parentItem.getDocumentId())
  },
  getIdentity: function (item) { return item.getObjectId(); },
  getLabel: function (item) { return item.getSubject(); },
  getRoot: function (onItem) { onItem(cliqueclique.document.tree.RootDocument); },
  isItem: function (something) { return true; },
  mayHaveChildren: function (item) { return true; },
  newItem: function (args, parent, insertIndex) {},
  pasteItem: function (childItem, oldParentItem, newParentItem, bCopy) {}
});
