dojo.provide("cliqueclique.general.popuptree");

dojo.require("dijit.Tree");

dijit.Tree.prototype.onExecute = function (item, node, evt) { };
dijit.Tree.prototype.onCancel = function () {};
dijit.Tree.prototype.onClick = function (item, node, evt) { this.onExecute(item, node, evt); };
