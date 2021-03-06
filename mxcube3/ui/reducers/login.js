const initialState = {
  loginInfo: {},
  loggedIn: false,
  data: {},
  showProposalsForm: false,
  selectedProposal: ''
};

export default (state = initialState, action) => {
  switch (action.type) {
    case 'SET_LOGIN_INFO':
      {
        const data = action.loginInfo.loginRes;
        let loggedIn = false;
        if (Object.keys(data).length > 0) {
          loggedIn = data.status.code === 'ok';
        }
        return Object.assign({}, state,
          {
            loginInfo: action.loginInfo,
            selectedProposal: state.selectedProposal ?
              state.selectedProposal : action.loginInfo.selectedProposal,
            loggedIn,
            data
          });
      }
    case 'SHOW_PROPOSALS_FORM':
      {
        return {
          ...state,
          showProposalsForm: true,
        };
      }
    case 'SELECT_PROPOSAL':
      {
        return {
          ...state,
          selectedProposal: action.proposal,
        };
      }
    case 'HIDE_PROPOSALS_FORM':
      {
        return { ...state, showProposalsForm: false };
      }
    default:
      return state;
  }
};
