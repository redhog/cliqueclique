dojo.provide("cliqueclique.document.DocumentMenu");

dojo.require("cliqueclique.document");
dojo.require("cliqueclique.document.DocumentLink");

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
