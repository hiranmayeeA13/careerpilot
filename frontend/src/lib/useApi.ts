import { useEffect, useRef, useState, useCallback } from 'react';
import { ApiError } from './api';

interface State<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(fn: () => Promise<T>, deps: unknown[]): State<T> & { refetch: () => void } {
  const [state, setState] = useState<State<T>>({ data: null, loading: true, error: null });
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const run = useCallback(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fnRef
      .current()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((e) => {
        if (!cancelled) {
          const msg = e instanceof ApiError ? e.message : 'Something went wrong.';
          setState({ data: null, loading: false, error: msg });
        }
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);

  return { ...state, refetch: run };
}
