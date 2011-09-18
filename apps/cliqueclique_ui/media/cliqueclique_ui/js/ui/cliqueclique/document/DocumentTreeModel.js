dojo.provide("cliqueclique.document.DocumentTreeModel");

dojo.require("dijit.Tree");
dojo.require("cliqueclique.document.Document");

dojo.declare("cliqueclique.document.DocumentTreeModel", [], {
  root_query: 'bookmarked',
  child_query: "->",

  constructor: function () {
    var tree = this;
    dojo.connect(cliqueclique.document.Document, "updated", tree, function () {
      tree.getChildren(cliqueclique.document.DocumentTreeModel.RootDocument, function (documents) {
        tree.onRefreshAll()
      });
    });
  },
  onRefreshAll: function () {},

  fetchItemByIdentity: function (keywordArgs) {},
  getChildren: function (parentItem, onComplete) {
    if (parentItem.json_data && !parentItem.json_data.local_is_subscribed) {
      parentItem.setAttribute("local_is_subscribed", true); // Don't signal changes here or we'll get an infinite loop
    }
    cliqueclique.document.Document.find(onComplete, parentItem.getDocumentId() ? this.child_query : this.root_query, parentItem.getDocumentId())
  },
  getIdentity: function (item) { return item.getObjectId(); },
  getLabel: function (item) { return item.getSubject(); },
  getRoot: function (onItem) { onItem(cliqueclique.document.DocumentTreeModel.RootDocument); },
  isItem: function (something) { return true; },
  mayHaveChildren: function (item) { return true; },
  newItem: function (args, parent, insertIndex) {},
  pasteItem: function (childItem, oldParentItem, newParentItem, bCopy) {}
});


cliqueclique.document.DocumentTreeModel.oldTree = dijit.Tree;
dojo.declare("dijit.Tree", [cliqueclique.document.DocumentTreeModel.oldTree], {
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

dojo.declare("cliqueclique.document.DocumentTreeModel.RootDocumentClass", [cliqueclique.document.Document], {
  constructor: function () { },
  getSubject: function () { return 'The root'; },
  getObjectId: function () { return null; },
  getDocumentId: function () { return null; },
});
cliqueclique.document.DocumentTreeModel.RootDocument = new cliqueclique.document.DocumentTreeModel.RootDocumentClass();

