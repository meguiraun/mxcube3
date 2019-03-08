import React from 'react';
import { Label } from 'react-bootstrap';


export default class TemperatureController extends React.Component {
  constructor(props) {
    super(props);
    this.setTemperature = this.setTemperature.bind(this);
  }

  setTemperature() {
    if (this.props.onSave !== undefined) {
      this.props.onSave(this.props.pkey, 'in');
    }

    this.refs.overlay.hide();
  }


  render() {
    const msgLabelStyle = { display: 'block', fontSize: '100%',
                            borderRadius: '0px', color: '#000' };
    const value = this.props.data.value;
    return (
      <div>
        <Label
          style={{ display: 'block', marginBottom: '3px' }}
        >
          Temperature
        </Label>
        <Label bsStyle={'success'} style={msgLabelStyle}>{value}</Label>
      </div>
    );
  }
}

TemperatureController.defaultProps = {
  onSave: undefined,
  data: { value: 0.0, state: 'READY', powered: true }
};
