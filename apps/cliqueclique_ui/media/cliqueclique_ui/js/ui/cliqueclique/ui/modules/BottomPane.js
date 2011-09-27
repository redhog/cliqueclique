dojo.provide("cliqueclique.ui.modules.BottomPane");

dojo.require("cliqueclique.general.OptionalTabContainer");

dojo.declare("cliqueclique.ui.modules.BottomPane", [cliqueclique.general.OptionalTabContainer], {
  region:'bottom',
  splitter: true,
  style:'height: 30%;'
});

cliqueclique.ui.modules.BottomPane.register = function (widget) {
  widget.tabCon = new cliqueclique.ui.modules.BottomPane();
  widget.inner.addChild(widget.tabCon);
  widget.tabCon.updateVisibility();

  widget.registerData("panels",
		      {label: 'Bottom pane',
		       addChild: function (sub_widget) {
			 sub_widget.attr("closable", true);
			 sub_widget.attr("style", 'height:100%; overflow: auto;');
			 widget.tabCon.addChild(sub_widget);
		       }},
		       true);
}
