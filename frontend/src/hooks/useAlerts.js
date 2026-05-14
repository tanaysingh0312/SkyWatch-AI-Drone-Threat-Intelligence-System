import { useReducer, useMemo } from 'react';

const alertReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_ALERT':
      // Prevent duplicates if needed
      if (state.some(a => a.id === action.payload.id)) return state;
      return [action.payload, ...state];
    case 'ACKNOWLEDGE_ALERT':
      return state.map(a => a.id === action.payload ? { ...a, acknowledged: true } : a);
    case 'ACKNOWLEDGE_ALL':
      return state.map(a => ({ ...a, acknowledged: true }));
    case 'CLEAR_ALERTS':
      return [];
    default:
      return state;
  }
};

export function useAlerts() {
  const [alerts, dispatch] = useReducer(alertReducer, []);

  const unacknowledgedCount = useMemo(() => 
    alerts.filter(a => !a.acknowledged).length, 
  [alerts]);

  const criticalCount = useMemo(() => 
    alerts.filter(a => a.severity === 'CRITICAL' && !a.acknowledged).length,
  [alerts]);

  return { 
    alerts, 
    unacknowledgedCount, 
    criticalCount,
    dispatch 
  };
}
