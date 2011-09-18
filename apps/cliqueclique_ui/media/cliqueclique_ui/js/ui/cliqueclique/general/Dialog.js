dojo.provide('cliqueclique.general.Dialog');

dojo.require('dijit.Dialog');

dojo.declare("cliqueclique.general.Dialog", [dijit.Dialog], {
  postCreate: function () {
    this.inherited(arguments);
    dojo.body().appendChild(this.domNode);
    this.startup();
  }
});
