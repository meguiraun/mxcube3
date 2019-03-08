import React from 'react';
// import { Label, Button, OverlayTrigger, Popover } from 'react-bootstrap';


export default class SampleChangerSwitch extends React.Component {
  constructor(props) {
    super(props);
    console.log('booo');
  }


  onRightLinkClick(e) {
    this.refs.overlay.handleToggle();
    e.preventDefault();
  }

  render() {
    return (
      <div>
      </div>
    );
  }
}


SampleChangerSwitch.defaultProps = {
  onText: 'PowerOff',
  offText: 'PowerOn',
  labelText: '',
  pkey: undefined,
  onSave: undefined,
  data: 'DISABLED',
};
