const PENDING_REFLECTION_SUBMISSION_PREFIX = 'reflection-submission:pending:';

const getPendingKey = (planId: string): string =>
  `${PENDING_REFLECTION_SUBMISSION_PREFIX}${planId}`;

export const markReflectionSubmissionPending = (planId: string): void => {
  if (typeof window === 'undefined') {
    return;
  }
  window.sessionStorage.setItem(getPendingKey(planId), 'true');
};

export const clearReflectionSubmissionPending = (planId: string): void => {
  if (typeof window === 'undefined') {
    return;
  }
  window.sessionStorage.removeItem(getPendingKey(planId));
};

export const hasPendingReflectionSubmission = (planId: string): boolean => {
  if (typeof window === 'undefined') {
    return false;
  }
  return window.sessionStorage.getItem(getPendingKey(planId)) === 'true';
};
