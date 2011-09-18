dojo.provide('cliqueclique.Dialog');

dojo.require('dijit.Dialog');

dojo.declare("cliqueclique.Dialog", [dijit.Dialog], {
  postCreate: function () {
    this.inherited(arguments);
    dojo.body().appendChild(this.domNode);
    this.startup();
  }
});
