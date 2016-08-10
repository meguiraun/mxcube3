import { combineReducers } from 'redux';
import login from './login';
import queue from './queue';
import sampleGrid from './SamplesGrid';
import taskForm from './taskForm';
import sampleview from './sampleview';
import general from './general';
import beamline from './beamline';
import logger from './logger';
import { reducer as formReducer } from 'redux-form';

const mxcubeReducer = combineReducers({
  login,
  queue,
  sampleGrid,
  taskForm,
  sampleview,
  logger,
  general,
  beamline,
  form: formReducer
});

const rootReducer = (state, action) => {
  if (action.type === 'SIGNOUT') {
    state = undefined; // eslint-disable-line no-param-reassign
  }

  return mxcubeReducer(state, action);
};

export default rootReducer;

