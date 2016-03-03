'use strict';
import './SampleView.css';
import React from 'react'
import {makeCircle, makeLine} from './shapes'

export default class SampleImage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      clickCentring: false,
      pointsCollected : 0,
      canvas: {},
      centringPoint: null,
      selectedPointType: "NONE",
      group: null,
      lightOn: false
    };
  }

  componentDidMount(){

      // Create fabric and set image background to sample
      var canvas = new fabric.Canvas('canvas');

      // Bind leftClick to function
      canvas.on('mouse:down', (option) => this.leftClick(option, canvas));

      // Bind rigth click to functions, this is not supported by fabric.js and has to be added manually with javascript
      document.getElementById('insideWrapper').addEventListener('contextmenu', (e) => this.rightClick(e,canvas), false);

      //Bind canvas to state, this is done to let other functions manipulate the canvas such as removing objecs
      this.setState({canvas: canvas});

      //Save and remove group in state
      canvas.on('selection:created', (e) => this.setState({group: e.target}));
      canvas.on('selection:cleared', () => this.setState({group: null}));

      // Draw canvas and set img size depending on screen size
      this.drawCanvas(canvas);

    }

  drawCanvas(canvas){

      //Getting the size of screen
      var w = document.getElementById('outsideWrapper').clientWidth;
      var h = w/this.props.sampleViewState.ratioWidthHeigth;

      //Canvas
      var canvasWindow = document.getElementById('canvas');
      canvasWindow.width = w;
      canvasWindow.height = h;

      //FabricJS
      canvas.setDimensions({width:w, height: h});
      canvas.renderAll();

      //Image from MD2
      document.getElementById("sample-img").style.height = h + "px";
      document.getElementById("sample-img").style.width = w + "px";
      document.getElementById("insideWrapper").style.height = h + "px";

      this.setState({heightRatio: this.props.sampleViewState.height/h, widthRatio: this.props.sampleViewState.width/w});


    }

   removeObject(){
    this.state.canvas.getActiveObject().remove();
    this.hideContextMenu();
  }

  drawLine(){
    let points = this.state.group.getObjects();
    this.state.canvas.add(makeLine(points[0], points[1]));
    this.hideContextMenu();
  }

  rightClick(e, canvas){
   this.hideContextMenu();
   var objectFound = false;
   var clickPoint = new fabric.Point(e.offsetX, e.offsetY);
   e.preventDefault();
   canvas.forEachObject((obj) => {
    if (!objectFound && obj.containsPoint(clickPoint) && obj.selectable) {
      objectFound = true;

      canvas.setActiveObject(obj);
      this.setState({selectedPointType: obj.type});
      this.showContextMenu(e.offsetX, e.offsetY);
    }
  });

   if(this.state.group && this.state.group.containsPoint(clickPoint)){
    this.showContextMenu(e.offsetX, e.offsetY);
    this.setState({selectedPointType: 'GROUP'});
  }
}

listOptions(type){
  switch (type){
    case 'SAVED':
    {
      return ( [ 
        <li><a onClick={() => this.showModal("characterisation")}>Add Characterisation</a></li>,
        <li><a onClick={() => this.showModal("datacollection")}>Add Datacollection</a></li>,
        <hr />,
        <li><a onClick={() => this.removeObject()}>Delete Point</a></li>
        ]);
    }
    case 'TMP':
    {
     return ( [
      <li><a onClick={() => this.savePoint()}>Save Point</a></li>,
      <li><a onClick={() => this.removeObject()}>Delete Point</a></li>
      ]);
   }
   case 'GROUP':
   {
     return ( [
      <li><a onClick={() => this.drawLine()}>Draw Line</a></li>,
      <hr />,
      <li><a>Delete Selected (NA)</a></li>
      ]);
   }
   case 'LINE':
   {
     return ( [
      <li><a>Add Helical Scan (NA)</a></li>,
      <hr />,
      <li><a onClick={() => this.removeObject()}>Delete Line</a></li>
      ]);
   }    
 }
}


leftClick(option, canvas){

  this.hideContextMenu();
  let pointsCollected = this.state.pointsCollected;

  if(pointsCollected < 3 && this.props.sampleViewState.clickCentring){
    (this.state.centringPoint ? this.state.centringPoint.remove(): '');
    let circle = makeCircle(option.e.layerX, option.e.layerY);
    canvas.add(circle);
    this.props.sampleActions.sendCentringPoint(option.e.layerX * this.state.widthRatio, option.e.layerY  * this.state.heightRatio);
    this.setState({pointsCollected: ++pointsCollected, centringPoint: circle, selectedPoint: circle.type});
  }else if(pointsCollected === 3){
    this.setState({
      pointsCollected: 0
    });
    this.props.sampleActions.StopClickCentring();
  }

}

showModal(modalName){
  this.props.showForm(modalName, true);
  this.hideContextMenu();
}

savePoint(){
  let point = makeCircle(this.state.centringPoint.left, this.state.centringPoint.top, "green", "SAVED");
  this.state.canvas.add(point);
  this.state.centringPoint.remove();
  this.hideContextMenu();
  this.props.sampleActions.sendSavePoint();

}

showContextMenu(x,y){
  document.getElementById("contextMenu").style.top = y + "px";
  document.getElementById("contextMenu").style.left = x + "px";
  document.getElementById("contextMenu").style.display = "block";
}

hideContextMenu(){
  document.getElementById("contextMenu").style.display = "none";
}

zoomIn(){
  if(this.props.sampleViewState.zoom < 9){
      this.props.sampleActions.sendZoomPos(this.props.sampleViewState.zoom + 1);
  }
}

zoomOut(){
   if(this.props.sampleViewState.zoom > 0){
      this.props.sampleActions.sendZoomPos(this.props.sampleViewState.zoom - 1);
  }
}

takeSnapShot(){
  document.getElementById("downloadLink").href = this.state.canvas.toDataURL();
}

lightOnOff(){
  (this.state.lightOn ? this.props.sampleActions.sendLightOn() : this.props.sampleActions.sendLightOff())
  this.setState({lightOn: !this.state.lightOn});
}


  render() {

    return (
                <div>
                  <ul id="contextMenu" className="dropdown-menu" role="menu">
                          {this.listOptions(this.state.selectedPointType)}
                  </ul>
                  <div className="outsideWrapper" id="outsideWrapper">
                    <div className="insideWrapper" id="insideWrapper">
                      <img id= "sample-img" className='img' src="/mxcube/api/v0.1/sampleview/camera/subscribe" alt="" />
                      <canvas id="canvas" className="coveringCanvas" />
                    </div>
                    <div className="sample-controlls">
                      <div className="text-center"> 
                            <button type="button" data-toggle="tooltip"  title="Take snapshot" className="btn btn-link  pull-center" onClick={() => this.savePoint()}><i className="fa fa-2x fa-fw fa-save"></i></button>                            
                            <button type="button" data-toggle="tooltip"  title="Measure distance" className="btn btn-link  pull-center" onClick={this.measureDistance}><i className="fa fa-2x fa-fw fa-calculator"></i></button>                              
                            <a href="#" id="downloadLink" type="button" data-toggle="tooltip"  title="Take snapshot" className="btn btn-link  pull-center" onClick={() => this.takeSnapShot()} download><i className="fa fa-2x fa-fw fa-camera"></i></a>                            
                            <button type="button" data-toggle="tooltip"  title="Start auto centring" className="btn btn-link  pull-center" onClick={() => this.props.sampleActions.sendStartAutoCentring()}><i className="fa fa-2x fa-fw fa-arrows"></i></button>
                            <button type="button" data-toggle="tooltip"  title="Start 3-click centring" className="btn btn-link  pull-center" onClick={() => this.props.sampleActions.sendStartClickCentring()}><i className="fa fa-2x fa-fw fa-circle-o-notch"></i></button>
                            <button type="button" data-toggle="tooltip"  title="Abort Centring" className="btn btn-link  pull-center" onClick={() => this.props.sampleActions.sendAbortCentring()}><i className="fa fa-2x fa-fw fa-times"></i></button>
                            <button type="button" data-toggle="tooltip"  title="Zoom in" className="btn btn-link  pull-center" onClick={() => this.zoomIn()}><i className="fa fa-2x fa-fw fa fa-search-plus"></i></button>
                            <button type="button" data-toggle="tooltip"  title="Zoom out" className="btn btn-link  pull-center" onClick={() => this.zoomOut()}><i className="fa fa-2x fa-fw fa fa-search-minus"></i></button>
                            <button type="button" data-toggle="tooltip"  title="Light On/Off" className="btn btn-link  pull-center" onClick={() => this.lightOnOff()}><i className="fa fa-2x fa-fw fa fa-lightbulb-o"></i> </button>
                            </div>
                    </div>
                    <div className="sample-controlls">
                            <input type="number" className="camera-controll" id="kappa" placeholder="Kappa" />
                            <input type="number" className="camera-controll" id="omega" placeholder="Omega" />
                            <input type="number" className="camera-controll" id="phi" placeholder="Phi" />
                    </div>
                </div>
              

              </div>
            );        
  }
}



