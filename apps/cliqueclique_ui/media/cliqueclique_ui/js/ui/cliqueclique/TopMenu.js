dojo.provide("cliqueclique.TopMenu");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document.ActionMenu");
dojo.require('dijit.MenuBar');
dojo.require('dijit.PopupMenuBarItem');

dojo.declare("cliqueclique.TopMenu", [dijit.MenuBar], {
  startup: function () {
    var menu = this;
    var item;
    var submenu;

    submenu = new cliqueclique.document.ActionMenu({dataParent: menu});
    item = new dijit.PopupMenuBarItem({label:"Actions", popup: submenu});
    dojo.place(submenu.domNode, item.domNode);
    menu.addChild(item);

    item = new dijit.MenuBarItem({label:"Help"});
    menu.addChild(item);
    item.connect(item, 'onClick', function (e) { cliqueclique.document.Document.find(function (documents) { documents[0].getDocumentLink(menu)(); }, [], "bc1372209bda29e02a3f692c0a8d5069cf5ba8912119f847d3f95"); });

    this.inherited(arguments);
  }
});
