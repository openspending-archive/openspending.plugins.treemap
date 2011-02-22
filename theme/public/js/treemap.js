var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

function init_treemap(json){
  var tm = new $jit.TM.Squarified({
    injectInto: 'treemap',
    levelsToShow: 1,
    titleHeight: 0,
    animate: animate,
    
    offset: 2,
    Label: {
      type: 'HTML',
      size: 12,
      family: 'Tahoma, Verdana, Arial',
      color: '#DDE7F0'
      },
    Node: {
      color: '#243448',
      CanvasStyles: {
        shadowBlur: 0,
        shadowColor: '#000'
      }
    },
    Events: {
      enable: true,
      onClick: function(node) {
        if(node) {
            document.location = node.data.link;
        }
      },
      onRightClick: function() {
        tm.out();
      },
      onMouseEnter: function(node, eventInfo) {
        if(node) {
          node.setCanvasStyle('shadowBlur', 8);
          node.orig_color = node.getData('color');
          node.setData('color', '#A3B3C7');
          tm.fx.plotNode(node, tm.canvas);
          tm.labels.plotLabel(tm.canvas, node);
        }
      },
      onMouseLeave: function(node) {
        if(node) {
          node.removeData('color');
          node.removeCanvasStyle('shadowBlur');
          node.setData('color', node.orig_color);
          tm.plot();
        }
      }
    },
    duration: 1000,
    Tips: {
      enable: true,
      type: 'Native',
      offsetX: 20,
      offsetY: 20,
      onShow: function(tip, node, isLeaf, domElement) {
        var html = '<div class="tip-title">' + node.name +
            ': ' + node.data.printable_value +
            '</div><div class="tip-text">';
        var data = node.data;
        tip.innerHTML =  html; 
      }  
    },
    //Implement this method for retrieving a requested  
    //subtree that has as root a node with id = nodeId,  
    //and level as depth. This method could also make a server-side  
    //call for the requested subtree. When completed, the onComplete   
    //callback method should be called.  
    request: function(nodeId, level, onComplete){  
      // var tree = eval('(' + json + ')');
      var tree = json;  
      var subtree = $jit.json.getSubtree(tree, nodeId);  
      $jit.json.prune(subtree, 1);  
      onComplete.onComplete(nodeId, subtree);  
    },
    //Add the name of the node in the corresponding label
    //This method is called once, on label creation and only for DOM labels.
    onCreateLabel: function(domElement, node){
	    //console.log(node);
		if (node.data.show_title) {
            domElement.innerHTML = "<div class='desc'><h2>" + node.data.printable_value + "</h2>" + node.name + "</div>";
        } else {
			domElement.innerHTML = "&nbsp;";
        }
    }
  });
  tm.loadJSON(json);
  tm.refresh();
}
