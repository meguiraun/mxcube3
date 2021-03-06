const warn = (values, props) => {
  const warnings = {};
  if (!props.attributes) {
    // for some reason redux-form is loaded before the initial status
    return warnings;
  }
  const energy = parseFloat(values.energy);
  const blEnergy = parseFloat(props.attributes.energy.value);
  const energyThreshold = blEnergy * 0.01;

  const resolution = parseFloat(values.resolution);
  const blResolution = parseFloat(props.attributes.resolution.value);
  const resThreshold = blResolution * 0.01;

  const trans = parseFloat(values.transmission);
  const blTrans = parseFloat(props.attributes.transmission.value);
  const transThreshold = blTrans * 0.01;

  if (blEnergy - energyThreshold > energy || energy > blEnergy + energyThreshold) {
    warnings.energy = 'Energy mismatch';
  }
  if (blResolution - resThreshold > resolution || resolution > blResolution + resThreshold) {
    warnings.resolution = 'resolution mismatch';
  }
  if (blTrans - transThreshold > trans || trans > blTrans + transThreshold) {
    warnings.transmission = 'transmission mismatch';
  }
  return warnings;
};

export default warn;
