dojo.provide("cliqueclique.document.ActionMenu");

dojo.require('dijit.MenuItem');
dojo.require('dijit.Menu');

dojo.declare("cliqueclique.document.ActionMenu", [dijit.Menu], {
  onOpen: function () {
    var menu = this;

    dojo.forEach(menu.getChildren(), function(child, i){
      menu.removeChild(child);
      child.destroyRecursive();
    });

    dojo.forEach(menu.getData("actions", "cliqueclique.ui.Ui"), function (item, i) {
      var item = new dijit.MenuItem(item);
      menu.addChild(item);
      item.connect(item, 'onClick', function (e) { item.perform(); });
    });

    return this.inherited(arguments);
  }
});

