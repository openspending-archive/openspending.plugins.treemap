var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

/*
var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};


var formatNumber = function(n){
  var s = String(n).replace(/\./,",");
  var r = /(\d+)(\d{3})/;
  while (r.test(s)){
    s = s.replace(r,"$1.$2");  
  }
  return s;
};
*/


function init_treemap(json){
  //init TreeMap
  var tm = new $jit.TM.Squarified({
    //where to inject the visualization
    injectInto: 'treemap',
    //show only one tree level
    levelsToShow: 1,
    //parent box title heights
    titleHeight: 0,
    //enable animations
    animate: animate,
    
    //cushion: useGradients,
    //box offsets
    offset: 2,
    //use canvas text
    Label: {
//      type: labelType,
      type: 'HTML',
      size: 12,
      family: 'Tahoma, Verdana, Arial',
      color: '#DDE7F0'
      },
    //enable specific canvas styles
    //when rendering nodes
    Node: {
      color: '#243448',
      CanvasStyles: {
        shadowBlur: 0,
        shadowColor: '#000'
      }
    },
    //Attach left and right click events
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
      //change node styles and canvas styles
      //when hovering a node
      onMouseEnter: function(node, eventInfo) {
        if(node) {
          //add node selected styles and replot node
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
    //duration of the animations
    duration: 1000,
    //Enable tips
    Tips: {
      enable: true,
      type: 'Native',
      //add positioning offsets
      offsetX: 20,
      offsetY: 20,
      //implement the onShow method to
      //add content to the tooltip when a node
      //is hovered
      onShow: function(tip, node, isLeaf, domElement) {
        var html = "<div class=\"tip-title\">" + node.name 
					+ ": " + node.data.printable_value
          + "</div><div class=\"tip-text\">";
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
      var tree = eval('(' + json + ')');  
      var subtree = $jit.json.getSubtree(tree, nodeId);  
      $jit.json.prune(subtree, 1);  
      onComplete.onComplete(nodeId, subtree);  
    },
    //Add the name of the node in the corresponding label
    //This method is called once, on label creation and only for DOM labels.
    onCreateLabel: function(domElement, node){
				//console.log(node);
				if (node.data.show_title) {
        	domElement.innerHTML = "<h2>&nbsp;" + node.data.printable_value + "</h2>" + node.name;
				} else {
					domElement.innerHTML = "&nbsp;";
				}
    }
  });
  tm.loadJSON(json);
  tm.refresh();
}

function init_history(json, color){
	var barChart = new $jit.BarChart({  
	  injectInto: 'history_graph',
	  animate: true,  
	  orientation: 'vertical',  
	  hoveredColor: '#A4CC77',
	  barsOffset: 6,  
	  offset: 8,  
	  labelOffset: 5,  
	  type: 'stacked',  
	  showAggregates:false, 
	  showLabels:true,  
	  Label: {  
	    type: labelType, //Native or HTML  
	    size: 11,  
	    family: 'Arial',  
	    color: '#1B283A'  
	  },  
	  Tips: {  
	    enable: true,  
	    onShow: function(tip, elem, obj) {  
	      tip.innerHTML = "<b>" + obj.name + "</b>: " + formatNumber(elem.value);
	    }  
	  }  
	});  
	barChart.colors = [color];	
	barChart.loadJSON(json);
}

