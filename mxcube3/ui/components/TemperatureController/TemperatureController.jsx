import React from 'react';

export default class TemperatureController extends React.Component {
  constructor(props) {
    super(props);
    console.log('boo');
  }

  setTemperature() {
    // TODO
    console.log('baaa');
  }

  render() {
    return (
      <div>
      </div>
    );
  }
  }

TemperatureController.defaultProps = {
  onSave: undefined,
  data: { value: 0.0, state: 'READY', powered: true }
};
