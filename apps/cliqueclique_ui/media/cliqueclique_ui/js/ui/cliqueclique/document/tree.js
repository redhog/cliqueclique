dojo.provide("cliqueclique.document.tree");

dojo.require("dijit.Tree");
dojo.require("cliqueclique.document");

dojo.declare("cliqueclique.document.tree.DocumentTreeModel", [], {
  root_query: 'bookmarked',
  child_query: ">",

  fetchItemByIdentity: function (keywordArgs) {},
  getChildren: function (parentItem, onComplete) {
    var url, query;
    if (parentItem.isRoot) {
      url = "/find/json";
      query = this.root_query;
    } else {
      url = "/find/json/" + parentItem.document_id;
      query = this.child_query;
    }

    dojo.xhrGet({
      url: url,
      handleAs: "json",
      content: { query: dojo.toJson(query) },
      load: function (documents) {
	var res = [];
	for (document_id in documents) {
	  res.push(documents[document_id]);
	}
	onComplete(res);
      }
    });
  },
  getIdentity: function (item) {
    if (item.isRoot)
      return null;
    else
      return item.document_id;
  },
  getLabel: function (item) {
    if (item.isRoot)
      return 'The root';
    else if (   typeof(item.content) != "undefined"
	     && typeof(item.content.parts) != "undefined"
	     && item.content.parts.length > 0
	     && typeof(item.content.parts[0].header) != "undefined")
      return item.content.parts[0].header.subject;
    else
      return item.document_id.substring(0, 5);
  },
  getRoot: function (onItem) { onItem({isRoot: true}); },
  isItem: function (something) { return true; },
  mayHaveChildren: function (item) { return true; },
  newItem: function (args, parent, insertIndex) {},
  pasteItem: function (childItem, oldParentItem, newParentItem, bCopy) {}
});
