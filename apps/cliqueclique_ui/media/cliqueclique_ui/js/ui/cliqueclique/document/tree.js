dojo.provide("cliqueclique.document.tree");

dojo.require("dijit.Tree");
dojo.require("cliqueclique.document");


dojo.declare("cliqueclique.document.tree.RootDocumentClass", [cliqueclique.document.Document], {
  constructor: function () { },
  getSubject: function () { return 'The roo'; },
  getDocumentId: function () { return null; },
});
cliqueclique.document.tree.RootDocument = new cliqueclique.document.tree.RootDocumentClass();

dojo.declare("cliqueclique.document.tree.DocumentTreeModel", [], {
  root_query: 'bookmarked',
  child_query: ">",

  fetchItemByIdentity: function (keywordArgs) {},
  getChildren: function (parentItem, onComplete) {
    cliqueclique.document.Document.find(onComplete, parentItem.getDocumentId() ? this.child_query : this.root_query, parentItem.getDocumentId())
  },
  getIdentity: function (item) { return item.getDocumentId(); },
  getLabel: function (item) { return item.getSubject(); },
  getRoot: function (onItem) { onItem(cliqueclique.document.tree.RootDocument); },
  isItem: function (something) { return true; },
  mayHaveChildren: function (item) { return true; },
  newItem: function (args, parent, insertIndex) {},
  pasteItem: function (childItem, oldParentItem, newParentItem, bCopy) {}
});
