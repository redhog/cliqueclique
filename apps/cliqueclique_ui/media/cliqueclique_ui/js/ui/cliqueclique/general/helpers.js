dojo.provide("cliqueclique.general.helpers");

cliqueclique.general.helpers.splitWithQuotes = function (text, sep) {
  var quoteTokens = text.split('"');
  var tokens = [];
  
  for (var i = 0; i < quoteTokens.length; i++) {
    var quoteToken = quoteTokens[i];
    if (i % 2 == 0) {
      var partTokens = quoteToken.split(sep);
      if (i > 0 && partTokens[0] == '')
        partTokens.splice(0, 1);
      tokens.push.apply(tokens, partTokens);
    } else {
      tokens[tokens.length-1] += quoteToken;
    }
  }

  return tokens;
}

/* Chains together a set of hooks that should run after one another as
   callbacks. Each hook is function(data, next_hook) and should call
   next_hook() as its last action. last_hook is function(data) and is
   called by next_hook() by the last hook. */
cliqueclique.general.helpers.chainFunctions = function (hooks, data, last_hook) {
  var next_hook = function () { last_hook(data); };
  var chainTwoFunctions = function (hook, data, next_hook) {
    return function () {
      return hook(data, next_hook)
    }
  }
  for (var i = 0; i < hooks.length; i++) {
    next_hook = chainTwoFunctions(hooks[i], data, next_hook);
  }
  return next_hook;
}