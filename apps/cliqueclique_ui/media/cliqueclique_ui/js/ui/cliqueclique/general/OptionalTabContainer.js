dojo.provide("cliqueclique.general.OptionalTabContainer");

dojo.require("dijit.layout.TabContainer");

dojo.declare("cliqueclique.general.OptionalTabContainer", [dijit.layout.TabContainer], {
  addChild: function(child){
    var res = this.inherited(arguments);
    this.updateVisibility();
    return res;
  },
  removeChild: function(child){
    var res = this.inherited(arguments);
    this.updateVisibility();
    return res;
  },
  updateVisibility: function () {
    if (this.getChildren().length > 0) {
      if (this._parent)
	this._parent.addChild(this);
      this._parent = null;
    } else {
      this._parent = this.getParent();
      if (this._parent)
	this._parent.removeChild(this);
    }
  }
});
