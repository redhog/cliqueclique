dojo.provide("cliqueclique.nodeinfo");

dijit._Widget.prototype.dataRegistry = null;

dijit._Widget.prototype.registerData = function (name, value, isDefault, namespace) {
  if (namespace === undefined)
    namespace = this.declaredClass;
  if (this.dataRegistry == null)
   this.dataRegistry = {values: {}, defaults: {}};
  if (this.dataRegistry.values[namespace + "." + name] == undefined)
    this.dataRegistry.values[namespace + "." + name] = [];
  if (isDefault)
    this.dataRegistry.defaults[namespace + "." + name] = value
  this.dataRegistry.values[namespace + "." + name].push(value);
};

dijit._Widget.prototype.getData = function (name, namespace) {
  if (namespace === undefined)
    namespace = this.declaredClass;
  var parentData = [];
  var parent = this.dataParent || this.getHtmlParent();
  if (parent)
   parentData = parent.getData(name, namespace);
  if (this.dataRegistry == null || this.dataRegistry.values[namespace + "." + name] == undefined)
    return parentData;
  return this.dataRegistry.values[namespace + "." + name].concat(parentData);
};

dijit._Widget.prototype._getDataDefault = function (name, namespace) {
  if (this.dataRegistry == null || this.dataRegistry.defaults[namespace + "." + name] == undefined) {
    var parent = this.dataParent || this.getHtmlParent();
    if (parent)
     return parent._getDataDefault(name, namespace);
    return undefined;
  }
  return this.dataRegistry.defaults[namespace + "." + name];
}

dijit._Widget.prototype.getDataDefault = function (name, namespace) {
  if (namespace === undefined)
    namespace = this.declaredClass;
  var res = this._getDataDefault(name, namespace);
  if (res !== undefined)
    return res;

  res = this.getData(name, namespace)
  if (res.length == 0)
    return undefined;
  return res[0];
};

dijit._Widget.prototype.getHtmlParent = function () {
  function getParent(domNode) {
    while (domNode.parentNode != null && !dijit.byNode(domNode))
      domNode = domNode.parentNode;
    if (domNode.parentNode == null)
      return null;
    return dijit.byNode(domNode);
  }
  return getParent(this.domNode.parentNode);
}
